import pandas as pd
import os
import random
from datetime import datetime, timedelta

def generate_test_csv(filename, num_rows=100):
    """
    Generate a test CSV file with the expected structure
    
    Args:
        filename (str): Name of the file to generate
        num_rows (int): Number of rows to generate
    """
    # Define standard columns
    standard_columns = [
        "Test ID", "Test Label", "Unique ID", "Student ID", "Status", 
        "Progress", "Start Time", "End Time", "Overall Score", 
        "Attempted Score", "Age", "Gender", "Grade", "Language", "Ethnicity", "State"
    ]
    
    # Define some unique test variables
    unique_columns = [
        "Question_1_Response", "Question_2_Response", "Question_3_Response",
        "Comment", "Feedback"
    ]
    
    # All columns
    all_columns = standard_columns + unique_columns
    
    # Generate data
    data = []
    start_date = datetime.now() - timedelta(days=30)
    
    for i in range(num_rows):
        # Generate student ID with teacher prefix (first 3 digits are teacher ID)
        teacher_id = random.randint(100, 999)
        student_number = random.randint(1000, 9999)
        student_id = f"{teacher_id}S{student_number}"
        
        # Generate end time
        end_time = start_date + timedelta(
            days=random.randint(0, 30),
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59)
        )
        
        # Create row data
        row = {
            "Test ID": f"TEST{random.randint(1000, 9999)}",
            "Test Label": f"Assessment {random.randint(1, 10)}",
            "Unique ID": f"UID{random.randint(10000, 99999)}",
            "Student ID": student_id,
            "Status": random.choice(["Completed", "In Progress", "Not Started"]),
            "Progress": random.choice(["100%", "50%", "0%"]),
            "Start Time": (end_time - timedelta(minutes=random.randint(5, 60))).strftime("%Y-%m-%d %H:%M:%S"),
            "End Time": end_time.strftime("%Y-%m-%d %H:%M:%S"),
            "Overall Score": random.randint(0, 100),
            "Attempted Score": random.randint(0, 100),
            "Age": random.randint(18, 25),
            "Gender": random.choice(["Male", "Female", "Other"]),
            "Grade": random.choice(["A", "B", "C", "D", "F"]),
            "Language": random.choice(["English", "Spanish", "French"]),
            "Ethnicity": random.choice(["Caucasian", "African American", "Asian", "Other"]),
            "State": random.choice(["CA", "TX", "FL", "NY", "IL"]),
            # Unique test variables - some will have data, some will be empty
            "Question_1_Response": random.choice([f"Response {random.randint(1, 5)}", "", None]),
            "Question_2_Response": random.choice([f"Answer {random.randint(1, 10)}", "", None]),
            "Question_3_Response": random.choice([f"Choice {random.randint(1, 3)}", "", None]),
            "Comment": random.choice([f"Comment {random.randint(1, 100)}", "", None]),
            "Feedback": random.choice([f"Feedback {random.randint(1, 50)}", "", None])
        }
        
        data.append(row)
    
    # Create DataFrame and save to CSV
    df = pd.DataFrame(data, columns=all_columns)
    df.to_csv(filename, index=False)
    print(f"Generated test file: {filename} with {num_rows} rows")

def generate_multiple_test_files(num_files=3):
    """
    Generate multiple test CSV files
    
    Args:
        num_files (int): Number of files to generate
    """
    os.makedirs("test_data", exist_ok=True)
    
    for i in range(num_files):
        filename = f"test_data/survey_data_{i+1}.csv"
        generate_test_csv(filename, random.randint(50, 150))
    
    print(f"Generated {num_files} test files in 'test_data' directory")

if __name__ == "__main__":
    generate_multiple_test_files(3)