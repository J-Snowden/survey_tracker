import pandas as pd
import os
from csv_processor import CSVProcessor
from report_generator import ReportGenerator

def create_test_csv():
    """Create a test CSV file with the expected structure"""
    # Create test data
    data = {
        "Test ID": ["TEST001", "TEST001", "TEST001", "TEST001", "TEST001"],
        "Test Label": ["Assessment 1", "Assessment 1", "Assessment 1", "Assessment 1", "Assessment 1"],
        "Unique ID": ["UID001", "UID002", "UID003", "UID004", "UID005"],
        "Student ID": ["123S001", "123S002", "456S003", "789S004", "cari"],
        "Status": ["Completed", "Completed", "Completed", "Completed", "Completed"],
        "Progress": ["100%", "100%", "100%", "100%", "100%"],
        "Start Time": ["2025-08-01 10:00:00", "2025-08-01 11:00:00", "2025-08-02 09:00:00", "2025-08-02 10:00:00", "2025-08-03 10:00:00"],
        "End Time": ["2025-08-01 10:30:00", "2025-08-01 11:30:00", "2025-08-02 09:30:00", "2025-08-02 10:30:00", "2025-08-03 10:30:00"],
        "Overall Score": [85, 90, 75, 80, 95],
        "Attempted Score": [85, 90, 75, 80, 95],
        "Age": [20, 21, 19, 20, 22],
        "Gender": ["Female", "Male", "Female", "Male", "Female"],
        "Grade": ["A", "A", "B", "B", "A"],
        "Language": ["English", "English", "English", "English", "English"],
        "Ethnicity": ["Caucasian", "African American", "Asian", "Other", "Caucasian"],
        "State": ["CA", "TX", "FL", "NY", "IL"],
        "Teacher Name": ["Teacher 1", "Teacher 1", "Teacher 2", "Teacher 3", "Teacher Other"],
        "Question_1_Response": ["Answer 1", "Answer 2", "", "Answer 4", ""],
        "Question_2_Response": ["Response 1", "", "Response 3", "Response 4", ""],
        "Comment": ["Good", "Excellent", "", "Average", ""]
    }
    
    # Create DataFrame and save to CSV
    df = pd.DataFrame(data)
    df.to_csv("test_downloads/test_data.csv", index=False)
    print("Created test CSV file: test_downloads/test_data.csv")

def test_csv_processing():
    """Test the CSV processing with new features"""
    print("Testing CSV processing with new features...")
    
    # Initialize modules
    processor = CSVProcessor()
    generator = ReportGenerator()
    
    # Process test file
    test_files = ["test_downloads/test_data.csv"]
    processed_data = processor.process_files(test_files)
    
    print(f"Processed {len(processed_data)} teacher-date combinations")
    
    # Show processed data
    print("\nProcessed data:")
    for (teacher_id, date), counts in processed_data.items():
        print(f"  Teacher {teacher_id} on {date}: {counts['responses']} responses, {counts['blanks']} blanks")
    
    # Generate report
    print("\nGenerating report...")
    report_path = generator.generate_report(processed_data, "test_new_report.xlsx")
    print(f"Report generated: {report_path}")
    
    # Generate summary statistics
    summary = generator.generate_summary_statistics(processed_data)
    print("\nSummary Statistics:")
    print(f"  Total Teachers: {summary['total_teachers']}")
    print(f"  Total Responses: {summary['total_responses']}")
    print(f"  Total Blanks: {summary['total_blanks']}")
    print(f"  Date Range: {summary['date_range']}")
    print(f"  Avg Responses per Teacher: {summary['avg_responses_per_teacher']}")

if __name__ == "__main__":
    # Create test directory if it doesn't exist
    os.makedirs("test_downloads", exist_ok=True)
    
    # Create test CSV file
    create_test_csv()
    
    # Test CSV processing
    test_csv_processing()