import pandas as pd
import os
import logging
from datetime import datetime
from collections import defaultdict

class TeacherTracker:
    def __init__(self, teachers_config_file="teachers.csv"):
        self.teachers_config_file = teachers_config_file
        self.logger = logging.getLogger(__name__)
        self.configured_teachers = set()
        self.load_teacher_config()
        
    def load_teacher_config(self):
        """Load teacher configuration from CSV file"""
        try:
            if os.path.exists(self.teachers_config_file):
                df = pd.read_csv(self.teachers_config_file)
                # Convert teacher_id to string to match processing logic
                self.configured_teachers = set(str(tid) for tid in df['teacher_id'].tolist())
                self.logger.info(f"Loaded {len(self.configured_teachers)} configured teachers: {self.configured_teachers}")
            else:
                self.logger.warning(f"Teacher config file {self.teachers_config_file} not found, using defaults")
                self.configured_teachers = {'100', '101', '102'}
        except Exception as e:
            self.logger.error(f"Error loading teacher config: {str(e)}")
            self.configured_teachers = {'100', '101', '102'}
    
    def classify_file_type(self, file_path):
        """Classify file as pre or post based on filename"""
        filename = os.path.basename(file_path).lower()
        if 'pre' in filename:
            return 'pre'
        elif 'post' in filename:
            return 'post'
        else:
            return 'unknown'
    
    def extract_teacher_id(self, student_id):
        """Extract teacher ID from student ID (first 3 characters if digits)"""
        student_id_str = str(student_id)
        if len(student_id_str) >= 3 and student_id_str[:3].isdigit():
            return student_id_str[:3]
        return "Other"
    
    def process_teacher_data(self, file_paths, progress_callback=None):
        """
        Process files to extract teacher statistics separated by pre/post
        
        Args:
            file_paths (list): List of CSV file paths
            progress_callback (function): Optional progress callback
            
        Returns:
            dict: Teacher statistics organized by teacher_id and assessment_type
        """
        teacher_stats = {}
        
        # Initialize all configured teachers plus "Other"
        all_teachers = list(self.configured_teachers) + ["Other"]
        for teacher_id in all_teachers:
            teacher_stats[teacher_id] = {
                'pre': {'responses': 0, 'dates': []},
                'post': {'responses': 0, 'dates': []}
            }
        
        for i, file_path in enumerate(file_paths):
            if progress_callback:
                progress_callback(f"Processing teacher data from file {i+1}/{len(file_paths)}: {os.path.basename(file_path)}", i+1, len(file_paths))
            
            try:
                file_type = self.classify_file_type(file_path)
                if file_type == 'unknown':
                    self.logger.info(f"Skipping file {file_path} - no pre/post designation in filename")
                    continue
                
                file_teacher_data = self._process_single_file_for_teachers(file_path, file_type)
                
                # Merge with overall stats
                for teacher_id, data in file_teacher_data.items():
                    # Ensure teacher exists in our tracking
                    if teacher_id not in teacher_stats:
                        teacher_stats[teacher_id] = {
                            'pre': {'responses': 0, 'dates': []},
                            'post': {'responses': 0, 'dates': []}
                        }
                    
                    teacher_stats[teacher_id][file_type]['responses'] += data['responses']
                    teacher_stats[teacher_id][file_type]['dates'].extend(data['dates'])
                    
            except Exception as e:
                self.logger.error(f"Error processing file {file_path} for teacher data: {str(e)}")
                if progress_callback:
                    progress_callback(f"Error processing teacher data from: {os.path.basename(file_path)}", i+1, len(file_paths))
        
        # Calculate date ranges and clean up data
        processed_stats = self._calculate_date_ranges(teacher_stats)
        return processed_stats
    
    def _process_single_file_for_teachers(self, file_path, file_type):
        """Process a single file to extract teacher response data"""
        teacher_data = defaultdict(lambda: {'responses': 0, 'dates': []})
        
        try:
            df = pd.read_csv(file_path)
            self.logger.info(f"Processing {file_type} file: {file_path} with {len(df)} rows")
            
            # Validate required columns
            if "Student ID" not in df.columns or "Start Time" not in df.columns:
                raise ValueError("Required columns (Student ID, Start Time) not found in CSV file")
            
            # Find test variable columns (after standard columns)
            standard_columns = [
                "Test ID", "Test Label", "Unique ID", "Student ID", "Status", 
                "Progress", "Start Time", "End Time", "Overall Score", 
                "Attempted Score", "Age", "Gender", "Grade", "Language", "Ethnicity", "State"
            ]
            
            # Find the "Teacher" column (column containing "Teacher" in its name)
            teacher_column = None
            for col in df.columns:
                if "teacher" in col.lower():
                    teacher_column = col
                    break
            
            if teacher_column is None:
                # Use all columns after standard columns as test variables
                test_variable_columns = [col for col in df.columns if col not in standard_columns]
            else:
                # Get columns that come after the teacher column
                teacher_col_index = df.columns.get_loc(teacher_column)
                test_variable_columns = df.columns[teacher_col_index + 1:].tolist()
            
            # Process each row
            for index, row in df.iterrows():
                try:
                    # Extract teacher ID
                    student_id = str(row["Student ID"])
                    teacher_id = self.extract_teacher_id(student_id)
                    
                    # Map to configured teachers or "Other"
                    if teacher_id not in self.configured_teachers:
                        teacher_id = "Other"
                    
                    # Check if any test variable columns have data (responses)
                    has_responses = False
                    for col in test_variable_columns:
                        if col in row and pd.notna(row[col]) and str(row[col]).strip() != "":
                            has_responses = True
                            break
                    
                    # Only count completed responses (those with actual data)
                    if has_responses:
                        # Extract and parse date from Start Time
                        start_time = row["Start Time"]
                        if pd.notna(start_time) and str(start_time).strip() != "":
                            try:
                                date_obj = pd.to_datetime(start_time)
                                date_str = date_obj.strftime("%Y-%m-%d")
                                
                                teacher_data[teacher_id]['responses'] += 1
                                teacher_data[teacher_id]['dates'].append(date_str)
                                
                            except Exception as e:
                                self.logger.warning(f"Could not parse date {start_time}: {str(e)}")
                                continue
                        
                except Exception as e:
                    self.logger.error(f"Error processing row {index} in {file_path}: {str(e)}")
                    continue
                    
        except Exception as e:
            self.logger.error(f"Error reading or processing file {file_path}: {str(e)}")
            raise
        
        return dict(teacher_data)
    
    def _calculate_date_ranges(self, teacher_stats):
        """Calculate first and last dates for each teacher's pre/post data"""
        processed_stats = {}
        
        for teacher_id, data in teacher_stats.items():
            processed_stats[teacher_id] = {}
            
            for assessment_type in ['pre', 'post']:
                dates = data[assessment_type]['dates']
                responses = data[assessment_type]['responses']
                
                if dates:
                    # Sort dates and get first/last
                    sorted_dates = sorted(set(dates))  # Remove duplicates and sort
                    first_date = sorted_dates[0]
                    last_date = sorted_dates[-1]
                else:
                    first_date = ""
                    last_date = ""
                
                processed_stats[teacher_id][assessment_type] = {
                    'responses': responses,
                    'first_date': first_date,
                    'last_date': last_date
                }
        
        return processed_stats
    
    def generate_teacher_report_data(self, teacher_stats):
        """
        Generate report data in the format needed for Excel export
        
        Returns:
            list: List of dictionaries with teacher report data
        """
        report_data = []
        
        # Get all teachers and sort them (configured teachers first, then "Other")
        configured_teachers_sorted = sorted([tid for tid in self.configured_teachers])
        all_teachers = configured_teachers_sorted + (["Other"] if "Other" in teacher_stats else [])
        
        for teacher_id in all_teachers:
            if teacher_id in teacher_stats:
                stats = teacher_stats[teacher_id]
                
                report_data.append({
                    'Teacher ID': teacher_id,
                    'Pre Responses': stats['pre']['responses'],
                    'First Pre Date': stats['pre']['first_date'],
                    'Last Pre Date': stats['pre']['last_date'],
                    'Post Responses': stats['post']['responses'],
                    'First Post Date': stats['post']['first_date'],
                    'Last Post Date': stats['post']['last_date']
                })
            else:
                # Teacher not found in data - create empty row
                report_data.append({
                    'Teacher ID': teacher_id,
                    'Pre Responses': 0,
                    'First Pre Date': "",
                    'Last Pre Date': "",
                    'Post Responses': 0,
                    'First Post Date': "",
                    'Last Post Date': ""
                })
        
        return report_data