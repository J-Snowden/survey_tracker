import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import os
import asyncio
import logging
from datetime import datetime

from web_automation import WebAutomationModule
from csv_processor import CSVProcessor
from report_generator import ReportGenerator

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SurveyDataTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Survey Data Tracker")
        self.root.geometry("800x600")
        
        # Create directories if they don't exist
        self.download_dir = "downloads"
        self.report_dir = "reports"
        os.makedirs(self.download_dir, exist_ok=True)
        os.makedirs(self.report_dir, exist_ok=True)
        
        # Initialize modules
        self.web_module = WebAutomationModule(self.download_dir)
        self.csv_processor = CSVProcessor()
        self.report_generator = ReportGenerator()
        
        # Processing variables
        self.processing_thread = None
        self.stop_processing_flag = False
        
        # Create UI
        self.create_widgets()
        
    def create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="Survey Data Tracker", font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Credentials section
        cred_frame = ttk.LabelFrame(main_frame, text="Authentication", padding="10")
        cred_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        cred_frame.columnconfigure(1, weight=1)
        
        ttk.Label(cred_frame, text="Username:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.username_var = tk.StringVar()
        self.username_entry = ttk.Entry(cred_frame, textvariable=self.username_var, width=30)
        self.username_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=(0, 5))
        
        ttk.Label(cred_frame, text="Password:").grid(row=1, column=0, sticky=tk.W, padx=(0, 10))
        self.password_var = tk.StringVar()
        self.password_entry = ttk.Entry(cred_frame, textvariable=self.password_var, show="*", width=30)
        self.password_entry.grid(row=1, column=1, sticky=(tk.W, tk.E))
        
        # URLs section
        url_frame = ttk.LabelFrame(main_frame, text="Assessment URLs", padding="10")
        url_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        url_frame.columnconfigure(0, weight=1)
        url_frame.rowconfigure(1, weight=1)
        
        ttk.Label(url_frame, text="Enter one URL per line:").grid(row=0, column=0, sticky=tk.W)
        
        self.url_text = tk.Text(url_frame, height=6)
        self.url_text.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(5, 10))
        
        scrollbar = ttk.Scrollbar(url_frame, orient=tk.VERTICAL, command=self.url_text.yview)
        scrollbar.grid(row=1, column=2, sticky=(tk.N, tk.S))
        self.url_text.configure(yscrollcommand=scrollbar.set)
        
        # Progress section
        progress_frame = ttk.LabelFrame(main_frame, text="Progress", padding="10")
        progress_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        progress_frame.columnconfigure(0, weight=1)
        
        self.progress_var = tk.StringVar(value="Ready to start")
        self.progress_label = ttk.Label(progress_frame, textvariable=self.progress_var)
        self.progress_label.grid(row=0, column=0, sticky=tk.W)
        
        self.progress_bar = ttk.Progressbar(progress_frame, mode='indeterminate')
        self.progress_bar.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(5, 0))
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, columnspan=3, pady=(0, 10))
        
        self.start_button = ttk.Button(button_frame, text="Start Processing", command=self.start_processing)
        self.start_button.grid(row=0, column=0, padx=(0, 10))
        
        self.stop_button = ttk.Button(button_frame, text="Stop", command=self.stop_processing, state=tk.DISABLED)
        self.stop_button.grid(row=0, column=1, padx=(0, 10))
        
        self.report_button = ttk.Button(button_frame, text="Open Reports Folder", command=self.open_reports_folder)
        self.report_button.grid(row=0, column=2)
        
        # Status text
        status_frame = ttk.LabelFrame(main_frame, text="Status Log", padding="10")
        status_frame.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        status_frame.columnconfigure(0, weight=1)
        status_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(5, weight=1)
        
        self.status_text = tk.Text(status_frame, height=10)
        self.status_text.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        scrollbar2 = ttk.Scrollbar(status_frame, orient=tk.VERTICAL, command=self.status_text.yview)
        scrollbar2.grid(row=0, column=2, sticky=(tk.N, tk.S))
        self.status_text.configure(yscrollcommand=scrollbar2.set)
        
    def log_message(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.status_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.status_text.see(tk.END)
        self.root.update_idletasks()
        
    def start_processing(self):
        # Get credentials
        username = self.username_var.get().strip()
        password = self.password_var.get()
        
        if not username or not password:
            messagebox.showerror("Error", "Please enter both username and password")
            return
            
        # Get URLs
        urls_text = self.url_text.get("1.0", tk.END).strip()
        if not urls_text:
            messagebox.showerror("Error", "Please enter at least one URL")
            return
            
        urls = [url.strip() for url in urls_text.split('\n') if url.strip()]
        
        # Disable UI elements during processing
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.username_entry.config(state=tk.DISABLED)
        self.password_entry.config(state=tk.DISABLED)
        self.url_text.config(state=tk.DISABLED)
        
        # Start processing in a separate thread
        self.stop_processing_flag = False
        self.processing_thread = threading.Thread(target=self._process_data, args=(username, password, urls))
        self.processing_thread.start()
        
    def stop_processing(self):
        self.stop_processing_flag = True
        self.log_message("Stopping processing...")
        
    def _process_data(self, username, password, urls):
        """Process data in a separate thread"""
        try:
            # Start progress bar
            self.progress_bar.start()
            self.log_message("Starting data processing...")
            
            # Create a new event loop for this thread
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # Step 1: Initialize modules
            self.update_progress("Initializing modules...", 0, 100)
            
            # Initialize web automation module
            web_initialized = loop.run_until_complete(self.web_module.initialize())
            if not web_initialized:
                self.log_message("Failed to initialize web automation module")
                return
                
            # Step 2: Download files
            self.update_progress("Downloading files...", 30, 100)
            downloaded_files = loop.run_until_complete(self.web_module.download_files(
                urls,
                username,
                password,
                progress_callback=self.update_progress
            ))
            
            if not downloaded_files:
                self.log_message("No files were downloaded")
                return
            else:
                self.log_message(f"Downloaded {len(downloaded_files)} files")
                
            # Step 4: Process CSV files
            self.update_progress("Processing CSV files...", 60, 100)
            processed_data = self.csv_processor.process_files(
                downloaded_files,
                progress_callback=self.update_progress
            )
            
            if not processed_data:
                self.log_message("No valid data found in downloaded files")
                return
            else:
                self.log_message(f"Processed data for {len(processed_data)} teacher-date combinations")
                
            # Step 5: Generate report
            self.update_progress("Generating report...", 90, 100)
            report_path = self.report_generator.generate_report(processed_data)
            
            # Generate summary statistics
            summary = self.report_generator.generate_summary_statistics(processed_data)
            self.log_message("Summary Statistics:")
            self.log_message(f"  Total Teachers: {summary['total_teachers']}")
            self.log_message(f"  Total Responses: {summary['total_responses']}")
            self.log_message(f"  Date Range: {summary['date_range']}")
            self.log_message(f"  Avg Responses per Teacher: {summary['avg_responses_per_teacher']}")
            
            self.log_message(f"Report generated successfully: {report_path}")
            self.update_progress("Processing complete!", 100, 100)
            
        except Exception as e:
            self.log_message(f"Error during processing: {str(e)}")
            logger.error(f"Error during processing: {str(e)}", exc_info=True)
        finally:
            # Clean up
            try:
                loop.run_until_complete(self.web_module.close())
                loop.close()
            except Exception as e:
                self.log_message(f"Error during cleanup: {str(e)}")
                
            # Stop progress bar and re-enable UI
            self.progress_bar.stop()
            self.root.after(0, self._enable_ui)
            
    def update_progress(self, message, current, total):
        """Update progress in the UI"""
        if self.stop_processing_flag:
            raise Exception("Processing stopped by user")
            
        progress_percent = int((current / total) * 100) if total > 0 else 0
        self.root.after(0, lambda: self.progress_var.set(f"{message} ({progress_percent}%)"))
        self.log_message(message)
        
    def _enable_ui(self):
        """Re-enable UI elements after processing"""
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.username_entry.config(state=tk.NORMAL)
        self.password_entry.config(state=tk.NORMAL)
        self.url_text.config(state=tk.NORMAL)
        
    def open_reports_folder(self):
        """Open the reports folder in the file explorer"""
        try:
            os.startfile(self.report_dir)
        except Exception as e:
            self.log_message(f"Error opening reports folder: {str(e)}")
            messagebox.showerror("Error", f"Could not open reports folder: {str(e)}")

def main():
    root = tk.Tk()
    app = SurveyDataTracker(root)
    root.mainloop()

if __name__ == "__main__":
    main()