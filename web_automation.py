import asyncio
import os
import logging
from playwright.async_api import async_playwright

class WebAutomationModule:
    def __init__(self, download_dir="downloads"):
        self.download_dir = download_dir
        self.logger = logging.getLogger(__name__)
        self.playwright = None
        self.browser = None
        self.context = None
        
        # Ensure download directory exists
        os.makedirs(self.download_dir, exist_ok=True)
        
    async def initialize(self):
        """Initialize Playwright and browser with download settings"""
        try:
            self.logger.info("Starting Playwright...")
            self.playwright = await async_playwright().start()
            self.logger.info(f"Playwright started: {self.playwright}")
            if self.playwright is None:
                self.logger.error("Failed to start Playwright")
                return False
            
            self.logger.info("Launching browser...")
            self.browser = await self.playwright.chromium.launch(headless=False)
            self.logger.info(f"Browser launched: {self.browser}")
            if self.browser is None:
                self.logger.error("Failed to launch browser")
                return False
                
            self.logger.info("Creating browser context...")
            self.context = await self.browser.new_context(
                accept_downloads=True
            )
            self.logger.info(f"Browser context created: {self.context}")
            if self.context is None:
                self.logger.error("Failed to create browser context")
                return False
            
            # Set download path
            self.logger.info("Setting default timeout...")
            self.context.set_default_timeout(10000)  # 10 second timeout
            self.logger.info("Web automation module initialized successfully")
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize web automation module: {str(e)}", exc_info=True)
            return False
    
    async def download_files(self, urls, username=None, password=None, progress_callback=None):
        """
        Download CSV files from the provided URLs
        
        Args:
            urls (list): List of URLs to download files from
            username (str): Username for authentication (if needed)
            password (str): Password for authentication (if needed)
            progress_callback (function): Callback function to report progress
            
        Returns:
            list: List of downloaded file paths
        """
        downloaded_files = []
        
        try:
            page = await self.context.new_page()
            
            for i, url in enumerate(urls):
                if progress_callback:
                    progress_callback(f"Processing URL {i+1}/{len(urls)}: {url}", i+1, len(urls))
                
                try:
                    # Navigate to the results page
                    await page.goto(url)
                    self.logger.info(f"Navigated to: {url}")
                    
                    # Check if we need to login
                    if username and password:
                        # Check if we're on a login page
                        login_form = await page.query_selector("form")
                        if login_form:
                            self.logger.info("Login form detected, attempting to login...")
                            
                            # Try to fill in username with different possible selectors
                            username_filled = False
                            username_selectors = [
                                "input[name='username']",
                                "input[name='email']",
                                "input[name='user']",
                                "input[type='email']",
                                "input[type='text']",
                                "#username",
                                "#email",
                                "#user"
                            ]
                            
                            for selector in username_selectors:
                                try:
                                    await page.fill(selector, username)
                                    username_filled = True
                                    self.logger.info(f"Username filled using selector: {selector}")
                                    break
                                except Exception as e:
                                    continue
                                    
                            if not username_filled:
                                self.logger.warning("Could not find username field, trying first input field")
                                try:
                                    await page.fill("input", username)
                                except Exception as e:
                                    self.logger.error(f"Failed to fill username field: {str(e)}")
                            
                            # Try to fill in password with different possible selectors
                            password_filled = False
                            password_selectors = [
                                "input[name='password']",
                                "input[type='password']",
                                "#password"
                            ]
                            
                            for selector in password_selectors:
                                try:
                                    await page.fill(selector, password)
                                    password_filled = True
                                    self.logger.info(f"Password filled using selector: {selector}")
                                    break
                                except Exception as e:
                                    continue
                                    
                            if not password_filled:
                                self.logger.warning("Could not find password field")
                            
                            # Try to submit login form with different possible selectors
                            submit_clicked = False
                            submit_selectors = [
                                "input[type='submit']",
                                "button[type='submit']",
                                "button:has-text('Login')",
                                "button:has-text('Sign in')",
                                "input:has-text('Login')",
                                "input:has-text('Sign in')"
                            ]
                            
                            for selector in submit_selectors:
                                try:
                                    await page.click(selector)
                                    submit_clicked = True
                                    self.logger.info(f"Login form submitted using selector: {selector}")
                                    break
                                except Exception as e:
                                    continue
                                    
                            if not submit_clicked:
                                self.logger.warning("Could not find submit button, trying Enter key")
                                try:
                                    await page.press("input", "Enter")
                                except Exception as e:
                                    self.logger.error(f"Failed to submit login form: {str(e)}")
                             
                            # Wait for navigation
                            await page.wait_for_timeout(2000)  # Wait 2 seconds
                    
                    # Wait for the page to load
                    await page.wait_for_timeout(1500)  # Wait 1.5 seconds
                    
                    # Find and click the download button
                    # This is a placeholder - you'll need to adjust the selector based on your platform
                    download_button = await page.query_selector("a:has-text('Download')") or \
                                     await page.query_selector("button:has-text('Download')") or \
                                     await page.query_selector("a:has-text('Download results file')") or \
                                     await page.query_selector("a[href*='download']") or \
                                     await page.query_selector("button[type='submit']")
                    
                    if download_button:
                        # Set up download listener
                        async with page.expect_download() as download_info:
                            await download_button.click()
                            download = await download_info.value
                            
                            # Save the downloaded file with its original name
                            original_filename = download.suggested_filename
                            if not original_filename:
                                original_filename = f"survey_data_{i+1}.csv"
                            file_path = os.path.join(self.download_dir, original_filename)
                            
                            # Save the downloaded file
                            await download.save_as(file_path)
                            downloaded_files.append(file_path)
                            self.logger.info(f"Downloaded file: {file_path}")
                            
                            if progress_callback:
                               progress_callback(f"Downloaded: {original_filename}", i+1, len(urls))
                            await page.wait_for_timeout(1000)  # Wait 1 second between downloads
                    else:
                        self.logger.warning(f"No download button found on page: {url}")
                        if progress_callback:
                            progress_callback(f"No download button found: {url}", i+1, len(urls))
                            
                except Exception as e:
                    self.logger.error(f"Error processing URL {url}: {str(e)}")
                    if progress_callback:
                        progress_callback(f"Error with URL: {url}", i+1, len(urls))
                        
        except Exception as e:
            self.logger.error(f"Error in download_files: {str(e)}")
            
        finally:
            # Close the page
            if 'page' in locals():
                await page.close()
                
        return downloaded_files
    
    async def close(self):
        """Close browser and playwright"""
        try:
            if self.context is not None:
                try:
                    await self.context.close()
                except Exception as e:
                    self.logger.warning(f"Error closing context: {str(e)}")
            if self.browser is not None:
                try:
                    await self.browser.close()
                except Exception as e:
                    self.logger.warning(f"Error closing browser: {str(e)}")
            if self.playwright is not None:
                try:
                    await self.playwright.stop()
                except Exception as e:
                    self.logger.warning(f"Error stopping Playwright: {str(e)}")
            self.logger.info("Web automation module closed successfully")
        except Exception as e:
            self.logger.error(f"Error closing web automation module: {str(e)}")