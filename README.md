# Survey Data Tracker

A desktop application that automatically downloads CSV files from an assessment platform and generates Excel reports showing teacher IDs with dates and response counts.

## Features

- Automated login to assessment platforms
- Automatic downloading of CSV data files
- Processing of survey responses to extract teacher information
- Generation of Excel reports with teacher IDs, dates, and response counts
- **NEW**: Teacher Summary tab with pre/post assessment tracking
- User-friendly graphical interface

## Requirements

- Python 3.8 or higher
- Windows, macOS, or Linux operating system

## Installation

1. Clone or download this repository
2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Install Playwright browsers:
   ```
   playwright install chromium
   ```

## Usage

1. Run the application:
   ```
   python main.py
   ```

2. Enter your assessment platform credentials in the Authentication section

3. Enter the URLs of the assessment results pages (one URL per line)

4. Click "Start Processing" to begin:
   - The application will log into the assessment platform
   - Navigate to each provided URL
   - Download the CSV data files
   - Process the files to extract teacher response data
   - Generate an Excel report in the "reports" folder

5. View the generated report in the "reports" folder or click "Open Reports Folder"

## New Teacher Tracking Feature

The application now includes enhanced teacher tracking capabilities with separate pre/post assessment analysis.

### Teacher Summary Tab

Each generated Excel report now contains two tabs:

1. **Survey Report** - Original functionality showing all responses by teacher and date
2. **Teacher Summary** - NEW tab showing teacher-specific pre/post assessment statistics

### Teacher Summary Columns

The Teacher Summary tab includes the following columns:

- **Teacher ID**: Configured teacher identifiers (e.g., 100, 101, 102) plus "Other"
- **Pre Responses**: Total responses from files with "pre" in the filename
- **First Pre Date**: Earliest response date from pre-assessment files
- **Last Pre Date**: Latest response date from pre-assessment files
- **Post Responses**: Total responses from files with "post" in the filename
- **First Post Date**: Earliest response date from post-assessment files
- **Last Post Date**: Latest response date from post-assessment files

### Teacher Configuration

Teachers are managed through the [`teachers.csv`](teachers.csv) file in the project root:

```csv
teacher_id,teacher_name
100,Teacher 100
101,Teacher 101
102,Teacher 102
```

- Add or remove teachers by editing this CSV file
- Teacher IDs not in this list will be grouped under "Other"
- No code changes needed - configuration is loaded automatically

### File Naming Requirements

For the teacher tracking to work properly:

- **Pre-assessment files**: Must contain "pre" in the filename (e.g., `pre_survey_data.csv`, `assessment_pre_2024.csv`)
- **Post-assessment files**: Must contain "post" in the filename (e.g., `post_survey_data.csv`, `assessment_post_2024.csv`)
- Files without "pre" or "post" in the name will only appear in the original Survey Report tab

### How Teacher Tracking Works

1. **File Classification**: Files are automatically classified as pre/post based on filename
2. **Teacher Extraction**: Teacher IDs are extracted from the first 3 digits of Student IDs
3. **Response Counting**: Only completed responses (with actual test data) are counted
4. **Date Tracking**: Dates are extracted from the "Start Time" column in CSV files
5. **Categorization**: Teachers not in [`teachers.csv`](teachers.csv) are grouped as "Other"

## How It Works

### Performance Improvements

The web automation module has been optimized to reduce unnecessary delays:
- Default timeout reduced from 30 seconds to 10 seconds
- Login submission wait time reduced from 5 seconds to 2 seconds
- Page load wait time reduced from 3 seconds to 1.5 seconds
- Download interval wait time reduced from 2 seconds to 1 second

These changes significantly speed up the login and download process while maintaining reliability.

### Enhanced Report Features

The generated Excel reports now include additional columns in the main "Survey Report" tab:
- **Time**: Indicates whether the data is from a "Pre" or "Post" assessment based on filename
- **Filename**: The name of the source file without the .csv extension

These columns provide better context for the data and make it easier to track the source of each response.

## Data Processing Logic

1. **Teacher ID Extraction**: The first 3 characters of the "Student ID" column are used as the teacher ID
2. **Response Counting**: Only responses with data in unique test variables (columns after the standard set) are counted
3. **Date Extraction**: Dates are extracted from the "Start Time" column


## Standard Columns

The application recognizes these standard columns in the CSV files:
- Test ID
- Test Label
- Unique ID
- Student ID
- Status
- Progress
- Start Time
- End Time
- Overall Score
- Attempted Score
- Age
- Gender
- Grade
- Language
- Ethnicity
- State

Any columns after these are considered unique test variables.

## Report Display Improvements

The Teacher Summary tab now shows blank cells instead of zeros for teachers with no pre or post responses, making the report cleaner and easier to read.

## Configuration

- Downloaded files are saved in the "downloads" folder
- Generated reports are saved in the "reports" folder
- Teacher configuration is managed in [`teachers.csv`](teachers.csv)
- Log files are generated in the application directory

## Troubleshooting

### Common Issues

1. **Login Failures**: Ensure your credentials are correct and the assessment platform is accessible
2. **Download Issues**: Verify that the URLs are correct and lead to pages with download buttons
3. **Processing Errors**: Check that CSV files have the expected structure with required columns

### Browser Automation

The application uses Playwright with Chromium browser for automation. If you encounter issues:
- Ensure Playwright browsers are installed: `playwright install chromium`
- Check that your system meets Playwright requirements

## Security

- Credentials are only stored in memory during the session
- No data is transmitted to external servers
- All processing is done locally on your machine

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.