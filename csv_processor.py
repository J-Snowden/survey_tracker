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
                for (teacher_id, date), counts in file_data.items():
                    if (teacher_id, date) in all_data:
                        all_data[(teacher_id, date)]["responses"] += counts["responses"]
                        all_data[(teacher_id, date)]["blanks"] += counts["blanks"]
                    else:
                        all_data[(teacher_id, date)] = counts.copy()
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
            if "Student ID" not in df.columns or "Start Time" not in df.columns:
                raise ValueError("Required columns (Student ID, Start Time) not found in CSV file")
            
            # Find the "Teacher" column (column containing "Teacher" in its name)
            teacher_column = None
            for col in df.columns:
                if "teacher" in col.lower():
                    teacher_column = col
                    break
            
            if teacher_column is None:
                self.logger.warning(f"No 'Teacher' column found in {file_path}")
                # Use all columns after standard columns as test variables
                test_variable_columns = [col for col in df.columns if col not in self.standard_columns]
            else:
                # Get columns that come after the teacher column
                teacher_col_index = df.columns.get_loc(teacher_column)
                test_variable_columns = df.columns[teacher_col_index + 1:].tolist()
            
            if not test_variable_columns:
                self.logger.warning(f"No test variable columns found in {file_path}")
            
            # Process each row
            for index, row in df.iterrows():
                try:
                    # Extract teacher ID from Student ID
                    student_id = str(row["Student ID"])
                    teacher_id = "Other"  # Default to "Other"
                    
                    # Try to extract first 3 digits as teacher ID
                    if len(student_id) >= 3 and student_id[:3].isdigit():
                        teacher_id = student_id[:3]
                    
                    # Check if any test variable columns have data (responses)
                    has_data = False
                    all_blank = True  # Track if all test variable columns are blank
                    
                    for col in test_variable_columns:
                        if col in row and pd.notna(row[col]) and str(row[col]).strip() != "":
                            has_data = True
                            all_blank = False
                            break
                    
                    # Extract date from Start Time
                    start_time = row["Start Time"]
                    if pd.isna(start_time) or str(start_time).strip() == "":
                        self.logger.warning(f"Empty Start Time for student {student_id}")
                        continue
                        
                    try:
                        # Parse date (assuming format like "YYYY-MM-DD HH:MM:SS")
                        date_obj = pd.to_datetime(start_time)
                        date_str = date_obj.strftime("%Y-%m-%d")
                    except Exception as e:
                        self.logger.warning(f"Could not parse date {start_time}: {str(e)}")
                        continue
                    
                    # Update counts
                    key = (teacher_id, date_str)
                    if key in file_data:
                        if has_data:  # Has responses
                            file_data[key]["responses"] += 1
                        if all_blank:  # All blank (no responses)
                            file_data[key]["blanks"] += 1
                    else:
                        file_data[key] = {"responses": 1 if has_data else 0, "blanks": 1 if all_blank else 0}
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
            required_columns = ["Student ID", "Start Time"]
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                self.logger.error(f"Missing required columns: {missing_columns}")
                return False
                
            return True
        except Exception as e:
            self.logger.error(f"Error validating CSV structure: {str(e)}")
            return False