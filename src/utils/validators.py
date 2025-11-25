"""Data validation utilities."""
import pandas as pd
from typing import List, Dict, Any
import logging

from ..config.settings import Settings


logger = logging.getLogger(__name__)


class DataValidator:
    """Validator for student data."""
    
    @staticmethod
    def validate_gpa(gpa: float) -> bool:
        """
        Validate GPA is within valid range.
        
        Args:
            gpa: GPA value to validate
            
        Returns:
            True if valid, False otherwise
        """
        return Settings.MIN_GPA <= gpa <= Settings.MAX_GPA
    
    @staticmethod
    def validate_height(height_cm: float) -> bool:
        """
        Validate height is within reasonable range.
        
        Args:
            height_cm: Height in centimeters
            
        Returns:
            True if valid, False otherwise
        """
        return Settings.MIN_HEIGHT_CM <= height_cm <= Settings.MAX_HEIGHT_CM
    
    @staticmethod
    def validate_weight(weight_kg: float) -> bool:
        """
        Validate weight is within reasonable range.
        
        Args:
            weight_kg: Weight in kilograms
            
        Returns:
            True if valid, False otherwise
        """
        return Settings.MIN_WEIGHT_KG <= weight_kg <= Settings.MAX_WEIGHT_KG
    
    @staticmethod
    def validate_gender(gender: str) -> bool:
        """
        Validate gender value.
        
        Args:
            gender: Gender value
            
        Returns:
            True if valid, False otherwise
        """
        return gender in ['M', 'F']
    
    @staticmethod
    def validate_dataframe(df: pd.DataFrame) -> Dict[str, Any]:
        """
        Validate entire DataFrame and return validation report.
        
        Args:
            df: DataFrame to validate
            
        Returns:
            Dictionary with validation results
        """
        report = {
            'total_rows': len(df),
            'invalid_gpa': 0,
            'invalid_height': 0,
            'invalid_weight': 0,
            'invalid_gender': 0,
            'missing_required_fields': []
        }
        
        # Check required columns
        required_columns = ['student_id', 'full_name', 'major']
        for col in required_columns:
            if col not in df.columns:
                report['missing_required_fields'].append(col)
        
        # Validate GPA
        if 'gpa' in df.columns:
            invalid_gpa = df[
                (df['gpa'] < Settings.MIN_GPA) | 
                (df['gpa'] > Settings.MAX_GPA)
            ]
            report['invalid_gpa'] = len(invalid_gpa)
        
        # Validate height
        if 'height_cm' in df.columns:
            invalid_height = df[
                (df['height_cm'] < Settings.MIN_HEIGHT_CM) | 
                (df['height_cm'] > Settings.MAX_HEIGHT_CM)
            ]
            report['invalid_height'] = len(invalid_height)
        
        # Validate weight
        if 'weight_kg' in df.columns:
            invalid_weight = df[
                (df['weight_kg'] < Settings.MIN_WEIGHT_KG) | 
                (df['weight_kg'] > Settings.MAX_WEIGHT_KG)
            ]
            report['invalid_weight'] = len(invalid_weight)
        
        # Validate gender
        if 'gender' in df.columns:
            invalid_gender = df[~df['gender'].isin(['M', 'F'])]
            report['invalid_gender'] = len(invalid_gender)
        
        # Log validation report
        logger.info("Data validation report:")
        for key, value in report.items():
            if value:
                logger.warning(f"  {key}: {value}")
        
        return report
    
    @staticmethod
    def check_duplicates(df: pd.DataFrame, column: str = 'student_id') -> pd.DataFrame:
        """
        Check for duplicate values in a column.
        
        Args:
            df: DataFrame to check
            column: Column name to check for duplicates
            
        Returns:
            DataFrame with duplicate rows
        """
        duplicates = df[df.duplicated(subset=[column], keep=False)]
        
        if len(duplicates) > 0:
            logger.warning(f"Found {len(duplicates)} duplicate entries in '{column}'")
        else:
            logger.info(f"No duplicates found in '{column}'")
        
        return duplicates
