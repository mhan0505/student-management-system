"""
Student Analytics Service

Business logic for data processing and analysis.
Designed for UI integration with parameter tuning support.
"""
import pandas as pd
import numpy as np
from datetime import date
import logging

logger = logging.getLogger(__name__)


class StudentAnalyticsService:
    """
    Service layer for student data analytics.
    
    Key Features (Top 0.1% Design):
    - Accepts DataFrame directly (decoupled from repository)
    - Parameterized methods for UI integration
    - Immutable operations (returns new data, doesn't modify original)
    """
    
    def __init__(self, df: pd.DataFrame):
        """
        Initialize service with DataFrame.
        
        Args:
            df: Raw student data DataFrame
        """
        self.df = df.copy()  # Always work on a copy
        self.imputation_stats = {} # Store imputation details
        logger.info(f"Initialized analytics service with {len(self.df)} records")
    
    def get_data(self) -> pd.DataFrame:
        """Get current processed data"""
        return self.df.copy()
    
    def impute_missing(self) -> 'StudentAnalyticsService':
        """
        Impute missing values using grouped median strategy.
        
        Strategy:
        - height_cm, weight_kg: Group by 'gender' (Physical stats differ by gender)
        - gpa, credits: Group by 'major' (Academic stats differ by major)
        
        Returns:
            self for method chaining
        """
        logger.info("Starting missing value imputation")
        
        # Track missing values before imputation
        self.imputation_stats = {
            'height_cm': self.df['height_cm'].isnull().sum(),
            'weight_kg': self.df['weight_kg'].isnull().sum(),
            'gpa': self.df['gpa'].isnull().sum(),
            'credits': self.df['credits'].isnull().sum()
        }

        # 1. Impute physical stats by GENDER
        for col in ['height_cm', 'weight_kg']:
            if col in self.df.columns:
                self.df[col] = self.df[col].fillna(
                    self.df.groupby('gender')[col].transform('median')
                )
        
        # 2. Impute academic stats by MAJOR
        for col in ['gpa', 'credits']:
            if col in self.df.columns:
                self.df[col] = self.df[col].fillna(
                    self.df.groupby('major')[col].transform('median')
                )
        
        logger.info(f"Imputation complete. Remaining NaN: {self.df.isnull().sum().sum()}")
        return self
    
    def add_bmi(self) -> 'StudentAnalyticsService':
        """
        Calculate BMI using vectorized NumPy operations.
        
        Formula: BMI = weight(kg) / (height(m))^2
        
        Returns:
            self for method chaining
        """
        logger.info("Calculating BMI")
        
        height_m = self.df['height_cm'].values / 100
        weight_kg = self.df['weight_kg'].values
        
        # Vectorized calculation
        self.df['bmi'] = weight_kg / np.square(height_m)
        
        logger.info(f"BMI calculated. Mean: {self.df['bmi'].mean():.2f}, Std: {self.df['bmi'].std():.2f}")
        return self
    
    def add_age(self, reference_date: date = None) -> 'StudentAnalyticsService':
        """
        Calculate age from date of birth.
        
        Args:
            reference_date: Reference date for age calculation (default: 2025-10-01)
        
        Returns:
            self for method chaining
        """
        if reference_date is None:
            reference_date = date(2025, 10, 1)
        
        logger.info(f"Calculating age with reference date: {reference_date}")
        
        # Convert to pandas Timestamp to avoid TypeError
        reference_timestamp = pd.Timestamp(reference_date)
        
        # Calculate age in years
        self.df['age'] = (reference_timestamp - pd.to_datetime(self.df['dob'])).dt.days / 365.25
        
        logger.info(f"Age calculated. Mean: {self.df['age'].mean():.2f} years")
        return self
    
    def add_zscores(self, columns: list = None) -> 'StudentAnalyticsService':
        """
        Calculate z-scores for normalization.
        
        Args:
            columns: List of columns to normalize (default: ['gpa', 'credits', 'bmi', 'age'])
        
        Returns:
            self for method chaining
        """
        if columns is None:
            columns = ['gpa', 'credits', 'bmi', 'age']
        
        logger.info(f"Calculating z-scores for columns: {columns}")
        
        for col in columns:
            if col in self.df.columns:
                mean = self.df[col].mean()
                std = self.df[col].std()
                self.df[f'z_{col}'] = (self.df[col] - mean) / std
        
        return self
    
    def detect_outliers_iqr(self, column: str, multiplier: float = 1.5) -> pd.DataFrame:
        """
        Detect outliers using IQR method with custom multiplier.
        
        **KEY FEATURE**: Parameterized multiplier for UI slider integration!
        
        Args:
            column: Column name to check for outliers
            multiplier: IQR multiplier (1.5 = standard, 3.0 = relaxed)
        
        Returns:
            DataFrame containing only outlier rows
        """
        logger.info(f"Detecting outliers in '{column}' using IQR method (multiplier={multiplier})")
        
        Q1 = self.df[column].quantile(0.25)
        Q3 = self.df[column].quantile(0.75)
        IQR = Q3 - Q1
        
        lower_bound = Q1 - multiplier * IQR
        upper_bound = Q3 + multiplier * IQR
        
        outliers = self.df[(self.df[column] < lower_bound) | (self.df[column] > upper_bound)]
        
        logger.info(f"Found {len(outliers)} outliers in '{column}'. Bounds: [{lower_bound:.2f}, {upper_bound:.2f}]")
        
        return outliers
    
    def cap_outliers(self, column: str, multiplier: float = 1.5) -> 'StudentAnalyticsService':
        """
        Cap outliers to IQR bounds (Winsorization).
        
        This method clips extreme values to the upper/lower bounds instead of removing them,
        reducing the impact of outliers while preserving sample size.
        
        Strategy:
        - Values below lower_bound → set to lower_bound
        - Values above upper_bound → set to upper_bound
        - Values within bounds → unchanged
        
        Args:
            column: Column name to cap outliers
            multiplier: IQR multiplier (1.5 = standard, 3.0 = relaxed)
        
        Returns:
            self for method chaining
        """
        logger.info(f"Capping outliers in '{column}' using IQR method (multiplier={multiplier})")
        
        # Calculate IQR bounds
        Q1 = self.df[column].quantile(0.25)
        Q3 = self.df[column].quantile(0.75)
        IQR = Q3 - Q1
        
        lower_bound = Q1 - multiplier * IQR
        upper_bound = Q3 + multiplier * IQR
        
        # Count outliers before capping
        n_below = (self.df[column] < lower_bound).sum()
        n_above = (self.df[column] > upper_bound).sum()
        
        # Cap values using NumPy clip (vectorized operation)
        self.df[column] = np.clip(self.df[column].values, lower_bound, upper_bound)
        
        logger.info(f"Capped {n_below + n_above} outliers in '{column}' "
                   f"({n_below} below {lower_bound:.2f}, {n_above} above {upper_bound:.2f})")
        
        return self
    
    def remove_outliers(self, column: str, multiplier: float = 1.5) -> 'StudentAnalyticsService':
        """
        Remove outlier rows from dataset.
        
        WARNING: This reduces sample size. Use cap_outliers() if you want to preserve all records.
        
        Args:
            column: Column name to filter outliers
            multiplier: IQR multiplier (1.5 = standard, 3.0 = relaxed)
        
        Returns:
            self for method chaining
        """
        logger.info(f"Removing outliers in '{column}' using IQR method (multiplier={multiplier})")
        
        # Calculate IQR bounds
        Q1 = self.df[column].quantile(0.25)
        Q3 = self.df[column].quantile(0.75)
        IQR = Q3 - Q1
        
        lower_bound = Q1 - multiplier * IQR
        upper_bound = Q3 + multiplier * IQR
        
        # Count rows before removal
        original_size = len(self.df)
        
        # Filter out outliers
        self.df = self.df[(self.df[column] >= lower_bound) & (self.df[column] <= upper_bound)]
        
        removed = original_size - len(self.df)
        logger.info(f"Removed {removed} outlier rows from '{column}'. "
                   f"Dataset size: {original_size} → {len(self.df)}")
        
        return self
    
    def get_summary_by_major(self) -> pd.DataFrame:
        """
        Generate summary statistics grouped by major.
        
        Returns:
            DataFrame with aggregated statistics
        """
        logger.info("Generating summary statistics by major")
        
        summary = self.df.groupby('major').agg({
            'student_id': 'count',
            'gpa': 'mean',
            'credits': 'mean',
            'bmi': 'mean' if 'bmi' in self.df.columns else 'count'
        }).round(2)
        
        summary.columns = ['n_students', 'gpa_mean', 'credits_mean', 'bmi_mean']
        summary = summary.reset_index()
        
        logger.info(f"Summary generated for {len(summary)} majors")
        
        return summary
    
    def top_k_per_major(self, k: int = 3) -> pd.DataFrame:
        """
        Get top K students per major sorted by GPA and Credits.
        
        Args:
            k: Number of top students per major
        
        Returns:
            DataFrame with top K students per major
        """
        logger.info(f"Getting top {k} students per major")
        
        # Sort by GPA (descending), then Credits (descending)
        sorted_df = self.df.sort_values(['gpa', 'credits'], ascending=[False, False])
        
        # Get top K per major
        top_students = sorted_df.groupby('major').head(k)
        
        logger.info(f"Retrieved {len(top_students)} top students across majors")
        
        return top_students
    
    def get_processed_dataframe(self) -> pd.DataFrame:
        """
        Get the current processed DataFrame.
        
        Returns:
            Copy of processed DataFrame
        """
        return self.df.copy()
