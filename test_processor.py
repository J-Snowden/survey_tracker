import os
import sys
from csv_processor import CSVProcessor
from report_generator import ReportGenerator

def test_csv_processing():
    """Test the CSV processing functionality"""
    print("Testing CSV processing...")
    
    # Initialize modules
    processor = CSVProcessor()
    generator = ReportGenerator()
    
    # Check if test data exists
    test_data_dir = "test_data"
    if not os.path.exists(test_data_dir):
        print("Test data directory not found. Generating test data...")
        try:
            from test_data_generator import generate_multiple_test_files
            generate_multiple_test_files(3)
        except ImportError:
            print("Could not generate test data. Please create test CSV files in 'test_data' directory.")
            return
    
    # Get list of test files
    test_files = []
    if os.path.exists(test_data_dir):
        for file in os.listdir(test_data_dir):
            if file.endswith(".csv"):
                test_files.append(os.path.join(test_data_dir, file))
    
    if not test_files:
        print("No test CSV files found in 'test_data' directory.")
        return
    
    print(f"Found {len(test_files)} test files:")
    for file in test_files:
        print(f"  - {file}")
    
    # Process files
    print("\nProcessing files...")
    try:
        processed_data = processor.process_files(test_files)
        print(f"Processed {len(processed_data)} teacher-date combinations")
        
        # Show some sample data
        print("\nSample processed data:")
        count = 0
        for (teacher_id, date), response_count in processed_data.items():
            print(f"  Teacher {teacher_id} on {date}: {response_count} responses")
            count += 1
            if count >= 5:  # Only show first 5
                break
        
        # Generate report
        print("\nGenerating report...")
        report_path = generator.generate_report(processed_data, "test_report.xlsx")
        print(f"Report generated: {report_path}")
        
        # Generate summary statistics
        summary = generator.generate_summary_statistics(processed_data)
        print("\nSummary Statistics:")
        print(f"  Total Teachers: {summary['total_teachers']}")
        print(f"  Total Responses: {summary['total_responses']}")
        print(f"  Date Range: {summary['date_range']}")
        print(f"  Avg Responses per Teacher: {summary['avg_responses_per_teacher']}")
        
        print("\nTest completed successfully!")
        
    except Exception as e:
        print(f"Error during testing: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_csv_processing()