import pandas as pd
import os
import logging
from datetime import datetime
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils.dataframe import dataframe_to_rows

class ReportGenerator:
    def __init__(self, report_dir="reports"):
        self.report_dir = report_dir
        self.logger = logging.getLogger(__name__)
        
        # Ensure report directory exists
        os.makedirs(self.report_dir, exist_ok=True)
        
    def generate_report(self, data, filename=None):
        """
        Generate an Excel report from the processed data
        
        Args:
            data (dict): Aggregated data with teacher IDs, dates, and response counts
            filename (str): Optional filename for the report
            
        Returns:
            str: Path to the generated report file
        """
        try:
            # Create DataFrame from data
            if not data:
                self.logger.warning("No data to generate report from")
                # Create empty DataFrame with proper columns
                df = pd.DataFrame(columns=["Teacher ID", "Date", "Number of Responses"])
            else:
                # Convert data to DataFrame
                report_data = []
                for (teacher_id, date), count in data.items():
                    report_data.append({
                        "Teacher ID": teacher_id,
                        "Date": date,
                        "Number of Responses": count
                    })
                
                df = pd.DataFrame(report_data)
                
                # Sort by Teacher ID and Date
                df = df.sort_values(["Teacher ID", "Date"])
            
            # Generate filename if not provided
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"survey_report_{timestamp}.xlsx"
                
            # Create full file path
            file_path = os.path.join(self.report_dir, filename)
            
            # Generate Excel report
            self._create_excel_report(df, file_path)
            
            self.logger.info(f"Report generated successfully: {file_path}")
            return file_path
            
        except Exception as e:
            self.logger.error(f"Error generating report: {str(e)}")
            raise
    
    def _create_excel_report(self, df, file_path):
        """
        Create an Excel report with formatting
        
        Args:
            df (pandas.DataFrame): DataFrame with report data
            file_path (str): Path to save the Excel file
        """
        try:
            # Create a new workbook and select the active sheet
            wb = Workbook()
            ws = wb.active
            ws.title = "Survey Report"
            
            # Add title row
            title_cell = ws.cell(row=1, column=1, value="Survey Response Report")
            title_cell.font = Font(size=16, bold=True)
            ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=3)
            ws.cell(row=1, column=1).alignment = Alignment(horizontal="center")
            
            # Add generation date
            date_cell = ws.cell(row=2, column=1, value=f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            date_cell.font = Font(italic=True)
            ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=3)
            ws.cell(row=2, column=1).alignment = Alignment(horizontal="center")
            
            # Add headers (row 4)
            headers = ["Teacher ID", "Date", "Number of Responses"]
            header_font = Font(bold=True)
            header_fill = PatternFill(start_color="CCCCCC", end_color="CCCCCC", fill_type="solid")
            
            for col, header in enumerate(headers, 1):
                cell = ws.cell(row=4, column=col, value=header)
                cell.font = header_font
                cell.fill = header_fill
                cell.alignment = Alignment(horizontal="center")
            
            # Add data rows
            for row_idx, row_data in enumerate(dataframe_to_rows(df, index=False, header=False), 5):
                for col_idx, value in enumerate(row_data, 1):
                    ws.cell(row=row_idx, column=col_idx, value=value)
            
            # Auto-adjust column widths
            for column in ws.columns:
                max_length = 0
                # Get the column letter from the first cell that is not merged
                column_letter = None
                for cell in column:
                    try:
                        # Check if the cell has a column_letter attribute (not merged)
                        if hasattr(cell, 'column_letter'):
                            column_letter = cell.column_letter
                            break
                    except:
                        pass
                
                # If we couldn't find a cell with column_letter, skip this column
                if column_letter is None:
                    continue
                    
                # Calculate max length for this column
                for cell in column:
                    try:
                        if cell.value is not None and len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = (max_length + 2)
                ws.column_dimensions[column_letter].width = min(adjusted_width, 50)
            
            # Save the workbook
            wb.save(file_path)
            
        except Exception as e:
            self.logger.error(f"Error creating Excel report: {str(e)}")
            raise
    
    def generate_summary_statistics(self, data):
        """
        Generate summary statistics from the data
        
        Args:
            data (dict): Aggregated data with teacher IDs, dates, and response counts
            
        Returns:
            dict: Summary statistics
        """
        if not data:
            return {
                "total_teachers": 0,
                "total_responses": 0,
                "date_range": "No data",
                "avg_responses_per_teacher": 0
            }
        
        # Extract unique teachers and dates
        teachers = set()
        dates = set()
        total_responses = 0
        
        for (teacher_id, date), count in data.items():
            teachers.add(teacher_id)
            dates.add(date)
            total_responses += count
            
        # Calculate date range
        if dates:
            sorted_dates = sorted(dates)
            date_range = f"{sorted_dates[0]} to {sorted_dates[-1]}"
        else:
            date_range = "No dates"
            
        # Calculate average responses per teacher
        avg_responses = total_responses / len(teachers) if teachers else 0
        
        return {
            "total_teachers": len(teachers),
            "total_responses": total_responses,
            "date_range": date_range,
            "avg_responses_per_teacher": round(avg_responses, 2)
        }