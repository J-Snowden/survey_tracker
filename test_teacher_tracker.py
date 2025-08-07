#!/usr/bin/env python3
"""
Test script for the teacher tracking functionality
"""

import os
import sys
from teacher_tracker import TeacherTracker
from report_generator import ReportGenerator

def test_teacher_tracking():
    """Test the teacher tracking functionality"""
    print("Testing Teacher Tracking Functionality")
    print("=" * 50)
    
    # Initialize teacher tracker
    tracker = TeacherTracker()
    print(f"Configured teachers: {tracker.configured_teachers}")
    
    # Get test files with pre/post in names
    test_files = []
    downloads_dir = "downloads"
    
    for filename in os.listdir(downloads_dir):
        if filename.endswith('.csv') and ('pre' in filename.lower() or 'post' in filename.lower()):
            test_files.append(os.path.join(downloads_dir, filename))
    
    print(f"Found test files: {test_files}")
    
    if not test_files:
        print("No pre/post files found for testing!")
        return False
    
    # Process teacher data
    print("\nProcessing teacher data...")
    teacher_stats = tracker.process_teacher_data(test_files)
    
    print("\nTeacher Statistics:")
    for teacher_id, stats in teacher_stats.items():
        print(f"\nTeacher {teacher_id}:")
        print(f"  Pre: {stats['pre']['responses']} responses, {stats['pre']['first_date']} to {stats['pre']['last_date']}")
        print(f"  Post: {stats['post']['responses']} responses, {stats['post']['first_date']} to {stats['post']['last_date']}")
    
    # Generate report data
    report_data = tracker.generate_teacher_report_data(teacher_stats)
    print(f"\nGenerated report data for {len(report_data)} teachers")
    
    # Test report generation
    print("\nGenerating test report...")
    report_generator = ReportGenerator()
    
    # Create empty regular data for compatibility
    regular_data = {}
    
    # Generate report with teacher data
    report_path = report_generator.generate_report(
        regular_data, 
        filename="test_teacher_report.xlsx",
        teacher_data=report_data
    )
    
    print(f"Test report generated: {report_path}")
    return True

if __name__ == "__main__":
    success = test_teacher_tracking()
    if success:
        print("\n✓ Teacher tracking test completed successfully!")
    else:
        print("\n✗ Teacher tracking test failed!")
        sys.exit(1)