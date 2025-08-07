import pandas as pd
import os
import logging
from datetime import datetime
import re

class CSVProcessor:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        # Define standard columns based on the provided structure
        self.standard_columns = [
            "Test ID", "Test Label", "Unique ID", "Student ID", "Status", 
            "Progress", "Start Time", "End Time", "Overall Score", 
            "Attempted Score", "Age", "Gender", "Grade", "Language", "Ethnicity", "State"
        ]
        
    def process_files(self, file_paths, progress_callback=None):
        """
        Process CSV files and extract teacher response data
        
        Args:
            file_paths (list): List of paths to CSV files
            progress_callback (function): Callback function to report progress
            
        Returns:
            dict: Aggregated data with teacher IDs, dates, and response counts
        """
        all_data = {}
        
        for i, file_path in enumerate(file_paths):
            if progress_callback:
                progress_callback(f"Processing file {i+1}/{len(file_paths)}: {os.path.basename(file_path)}", i+1, len(file_paths))
                
            try:
                # Process individual file
                file_data = self._process_single_file(file_path)
                
                # Merge with overall data
                for (teacher_id, date), count in file_data.items():
                    if (teacher_id, date) in all_data:
                        all_data[(teacher_id, date)] += count
                    else:
                        all_data[(teacher_id, date)] = count
                        
            except Exception as e:
                self.logger.error(f"Error processing file {file_path}: {str(e)}")
                if progress_callback:
                    progress_callback(f"Error processing file: {os.path.basename(file_path)}", i+1, len(file_paths))
                    
        return all_data
    
    def _process_single_file(self, file_path):
        """
        Process a single CSV file and extract teacher response data
        
        Args:
            file_path (str): Path to the CSV file
            
        Returns:
            dict: Data with teacher IDs, dates, and response counts
        """
        file_data = {}
        
        try:
            # Read CSV file
            df = pd.read_csv(file_path)
            self.logger.info(f"Read CSV file: {file_path} with {len(df)} rows")
            
            # Validate that required columns exist
            if "Student ID" not in df.columns or "End Time" not in df.columns:
                raise ValueError("Required columns (Student ID, End Time) not found in CSV file")
            
            # Identify unique test variable columns (columns after standard columns)
            unique_columns = [col for col in df.columns if col not in self.standard_columns]
            
            if not unique_columns:
                self.logger.warning(f"No unique test variable columns found in {file_path}")
            
            # Process each row
            for index, row in df.iterrows():
                try:
                    # Extract teacher ID (first 3 characters of Student ID)
                    student_id = str(row["Student ID"])
                    if len(student_id) < 3:
                        self.logger.warning(f"Student ID too short: {student_id}")
                        continue
                        
                    teacher_id = student_id[:3]
                    
                    # Check if any unique test variable columns have data
                    has_data = False
                    for col in unique_columns:
                        if col in row and pd.notna(row[col]) and str(row[col]).strip() != "":
                            has_data = True
                            break
                    
                    # Only count if there's data in unique test variables
                    if has_data:
                        # Extract date from End Time
                        end_time = row["End Time"]
                        if pd.isna(end_time) or str(end_time).strip() == "":
                            self.logger.warning(f"Empty End Time for student {student_id}")
                            continue
                            
                        try:
                            # Parse date (assuming format like "YYYY-MM-DD HH:MM:SS")
                            date_obj = pd.to_datetime(end_time)
                            date_str = date_obj.strftime("%Y-%m-%d")
                        except Exception as e:
                            self.logger.warning(f"Could not parse date {end_time}: {str(e)}")
                            continue
                        
                        # Update count
                        key = (teacher_id, date_str)
                        if key in file_data:
                            file_data[key] += 1
                        else:
                            file_data[key] = 1
                            
                except Exception as e:
                    self.logger.error(f"Error processing row {index} in {file_path}: {str(e)}")
                    continue
                    
        except Exception as e:
            self.logger.error(f"Error reading or processing file {file_path}: {str(e)}")
            raise
            
        return file_data
    
    def validate_csv_structure(self, file_path):
        """
        Validate that a CSV file has the expected structure
        
        Args:
            file_path (str): Path to the CSV file
            
        Returns:
            bool: True if structure is valid, False otherwise
        """
        try:
            # Read just the header to check columns
            df = pd.read_csv(file_path, nrows=0)
            
            # Check for required columns
            required_columns = ["Student ID", "End Time"]
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                self.logger.error(f"Missing required columns: {missing_columns}")
                return False
                
            return True
        except Exception as e:
            self.logger.error(f"Error validating CSV structure: {str(e)}")
            return False