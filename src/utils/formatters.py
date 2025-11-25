"""Data formatting utilities."""
import pandas as pd
from typing import List
import logging


logger = logging.getLogger(__name__)


class DataFormatter:
    """Formatter for student data display and export."""
    
    @staticmethod
    def format_student_name(name: str) -> str:
        """
        Format student name to title case.
        
        Args:
            name: Student name
            
        Returns:
            Formatted name
        """
        return name.title().strip()
    
    @staticmethod
    def format_phone(phone: str) -> str:
        """
        Format phone number.
        
        Args:
            phone: Phone number string
            
        Returns:
            Formatted phone number
        """
        # Remove non-digit characters
        digits = ''.join(filter(str.isdigit, str(phone)))
        
        # Format as: 0XXX-XXX-XXX
        if len(digits) == 10 and digits.startswith('0'):
            return f"{digits[0:4]}-{digits[4:7]}-{digits[7:]}"
        
        return phone
    
    @staticmethod
    def format_gpa(gpa: float, decimals: int = 2) -> str:
        """
        Format GPA with fixed decimal places.
        
        Args:
            gpa: GPA value
            decimals: Number of decimal places
            
        Returns:
            Formatted GPA string
        """
        return f"{gpa:.{decimals}f}"
    
    @staticmethod
    def format_bmi_category(bmi: float) -> str:
        """
        Categorize BMI into health categories.
        
        Args:
            bmi: BMI value
            
        Returns:
            BMI category string
        """
        if bmi < 18.5:
            return "Underweight"
        elif 18.5 <= bmi < 25:
            return "Normal"
        elif 25 <= bmi < 30:
            return "Overweight"
        else:
            return "Obese"
    
    @staticmethod
    def add_bmi_categories(df: pd.DataFrame) -> pd.DataFrame:
        """
        Add BMI category column to DataFrame.
        
        Args:
            df: DataFrame with 'bmi' column
            
        Returns:
            DataFrame with 'bmi_category' column added
        """
        if 'bmi' not in df.columns:
            logger.warning("'bmi' column not found, skipping category addition")
            return df
        
        df['bmi_category'] = df['bmi'].apply(DataFormatter.format_bmi_category)
        logger.info("Added BMI category column")
        return df
    
    @staticmethod
    def select_columns_for_export(
        df: pd.DataFrame, 
        columns: List[str] = None
    ) -> pd.DataFrame:
        """
        Select specific columns for export.
        
        Args:
            df: Source DataFrame
            columns: List of column names to include (None = all columns)
            
        Returns:
            DataFrame with selected columns
        """
        if columns is None:
            return df
        
        available_columns = [col for col in columns if col in df.columns]
        missing_columns = [col for col in columns if col not in df.columns]
        
        if missing_columns:
            logger.warning(f"Columns not found: {missing_columns}")
        
        return df[available_columns]
    
    @staticmethod
    def format_dataframe_display(df: pd.DataFrame, max_rows: int = 10) -> None:
        """
        Pretty print DataFrame with formatting.
        
        Args:
            df: DataFrame to display
            max_rows: Maximum number of rows to display
        """
        with pd.option_context(
            'display.max_rows', max_rows,
            'display.max_columns', None,
            'display.width', None,
            'display.precision', 2
        ):
            print(df)
    
    @staticmethod
    def create_summary_table(df: pd.DataFrame, group_by: str = 'major') -> pd.DataFrame:
        """
        Create formatted summary table.
        
        Args:
            df: Source DataFrame
            group_by: Column to group by
            
        Returns:
            Formatted summary DataFrame
        """
        if group_by not in df.columns:
            logger.error(f"Column '{group_by}' not found")
            return pd.DataFrame()
        
        summary = df.groupby(group_by).agg({
            'student_id': 'count',
            'gpa': ['mean', 'min', 'max', 'std'],
            'credits': 'mean'
        }).round(2)
        
        # Flatten column names
        summary.columns = ['_'.join(col).strip() for col in summary.columns.values]
        
        return summary.reset_index()
