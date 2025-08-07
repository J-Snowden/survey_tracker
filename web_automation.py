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
        self.is_authenticated = False  # Track authentication state across URLs
        
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
                    # If no credentials provided, wait for user to manually log in
                    elif not username and not password:
                        # Only check login status if we haven't authenticated yet in this session
                        if not self.is_authenticated:
                            self.logger.info("No credentials provided - checking authentication status")
                            logged_in = await self._check_if_logged_in(page)
                            if not logged_in:
                                self.logger.info("Not logged in - waiting for user to log in")
                                # Wait for login with longer timeout and better detection
                                login_successful = await self._wait_for_login_or_timeout(page, 60000)  # Increased to 60s
                                if login_successful:
                                    self.is_authenticated = True
                                    self.logger.info("Authentication successful - session will be maintained")
                            else:
                                self.logger.info("Already logged in - marking session as authenticated")
                                self.is_authenticated = True
                        else:
                            self.logger.info("Session already authenticated - proceeding with download")
                    
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
    
    async def _check_if_logged_in(self, page):
        """Check if user is already logged in by looking for common elements"""
        try:
            # Check for login-related elements (login form indicates NOT logged in)
            login_form = await page.query_selector("form")
            login_inputs = await page.query_selector_all("input[type='password'], input[name*='password'], input[name*='login'], input[name*='email']")
            
            if login_form and login_inputs:
                return False
            
            # Check for download button (presence indicates logged in to results page)
            download_button = await page.query_selector("a:has-text('Download')") or \
                             await page.query_selector("button:has-text('Download')") or \
                             await page.query_selector("a:has-text('Download results file')") or \
                             await page.query_selector("a[href*='download']")
            
            if download_button:
                return True
            
            # Look for common elements that indicate user is logged in
            user_elements = await page.query_selector_all("[data-user], .user-name, .logged-in, [aria-label*='Logout'], [title*='Logout']")
            if user_elements:
                return True
                
            # Check for URL patterns that indicate logged-in state
            current_url = page.url
            logged_in_patterns = ["/dashboard", "/home", "/account", "/profile"]
            for pattern in logged_in_patterns:
                if pattern in current_url:
                    return True
            
            return False
        except Exception as e:
            self.logger.warning(f"Error checking login status: {str(e)}")
            return False
    
    async def _wait_for_login_or_timeout(self, page, timeout_ms):
        """Wait for user to log in or timeout"""
        start_time = asyncio.get_event_loop().time()
        timeout_seconds = timeout_ms / 1000
        check_count = 0
        
        self.logger.info(f"Waiting up to {timeout_seconds:.0f} seconds for user to log in...")
        
        while (asyncio.get_event_loop().time() - start_time) < timeout_seconds:
            check_count += 1
            elapsed = asyncio.get_event_loop().time() - start_time
            
            # Check if user is now logged in
            if await self._check_if_logged_in(page):
                self.logger.info(f"User login detected - proceeding with download")
                return True
                
            # Log progress every 15 seconds
            if check_count % 15 == 0:
                remaining = timeout_seconds - elapsed
                self.logger.info(f"Still waiting for login... {remaining:.0f} seconds remaining")
                
            # Wait a bit before checking again
            await page.wait_for_timeout(1000)  # Check every second
            
        self.logger.info("Login timeout reached - proceeding with download")
        return False