"""Application settings and constants."""
from datetime import date
from typing import List


class Settings:
    """Application-wide settings and constants."""
    
    # Analysis settings
    REFERENCE_DATE = date(2025, 10, 1)  # Reference date for age calculation
    IQR_MULTIPLIER = 1.5  # Multiplier for IQR outlier detection
    
    # Column names
    NUMERIC_COLUMNS: List[str] = ['gpa', 'credits', 'height_cm', 'weight_kg']
    CATEGORICAL_COLUMNS: List[str] = ['gender', 'major', 'province']
    
    # Imputation strategy
    IMPUTE_METHOD = 'median'  # Options: 'median', 'mean', 'mode'
    
    # Report settings
    OUTPUT_CSV = 'student_report.csv'
    TOP_K_STUDENTS = 3  # Number of top students per major
    
    # Data validation
    MIN_GPA = 0.0
    MAX_GPA = 4.0
    MIN_HEIGHT_CM = 100.0
    MAX_HEIGHT_CM = 250.0
    MIN_WEIGHT_KG = 30.0
    MAX_WEIGHT_KG = 200.0
    
    @staticmethod
    def get_zscore_columns() -> List[str]:
        """Get list of columns to calculate z-scores for."""
        return ['gpa', 'credits', 'bmi', 'age']
