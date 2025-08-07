# Survey Data Tracker

A desktop application that automatically downloads CSV files from an assessment platform and generates Excel reports showing teacher IDs with dates and response counts.

## Features

- Automated login to assessment platforms
- Automatic downloading of CSV data files
- Processing of survey responses to extract teacher information
- Generation of Excel reports with teacher IDs, dates, and response counts
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

## How It Works

### Data Processing Logic

1. **Teacher ID Extraction**: The first 3 characters of the "Student ID" column are used as the teacher ID
2. **Response Counting**: Only responses with data in unique test variables (columns after the standard set) are counted
3. **Date Extraction**: Dates are extracted from the "End Time" column

### Standard Columns

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

## Configuration

- Downloaded files are saved in the "downloads" folder
- Generated reports are saved in the "reports" folder
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