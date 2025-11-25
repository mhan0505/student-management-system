"""
Student Report Generator

Orchestrates the complete data pipeline.
UI-friendly wrapper around Analytics Service.
"""
import pandas as pd
import logging
from pathlib import Path
from datetime import datetime

from src.repositories.student_repository import StudentRepository
from src.services.analytics_service import StudentAnalyticsService

logger = logging.getLogger(__name__)


class StudentReportGenerator:
    """
    High-level report generation orchestrator.
    
    Design Pattern: Facade Pattern
    - Simplifies complex analytics workflow
    - Provides easy-to-use interface for UI layer
    """
    
    def __init__(self, repository: StudentRepository):
        """
        Initialize report generator.
        
        Args:
            repository: Student data repository
        """
        self.repository = repository
        self.analytics_service = None
        logger.info("Report generator initialized")
    
    def generate_full_report(self, output_file: str = None, detect_outliers: bool = True, 
                            top_k: int = 3, iqr_multiplier: float = 1.5) -> pd.DataFrame:
        """
        Generate complete analysis report.
        
        Pipeline:
        1. Fetch data from repository
        2. Impute missing values
        3. Calculate BMI
        4. Calculate age
        5. Calculate z-scores
        6. Detect outliers (optional)
        7. Export to CSV (optional)
        
        Args:
            output_file: CSV file path (optional)
            detect_outliers: Whether to detect and log outliers
            top_k: Number of top students per major to show
            iqr_multiplier: IQR multiplier for outlier detection
        
        Returns:
            Processed DataFrame
        """
        logger.info("=" * 60)
        logger.info("Starting full report generation pipeline")
        logger.info("=" * 60)
        
        # Step 1: Fetch data
        logger.info("\nStep 1/7: Fetching student data from database")
        df_raw = self.repository.fetch_all()
        logger.info(f"Fetched {len(df_raw)} student records")
        logger.info(f"Columns: {list(df_raw.columns)}")
        logger.info(f"Missing values:\n{df_raw.isnull().sum()}")
        
        # Step 2: Initialize analytics service
        logger.info("\nStep 2/7: Initializing analytics service")
        self.analytics_service = StudentAnalyticsService(df_raw)
        
        # Step 3: Impute missing values
        logger.info("\nStep 3/7: Imputing missing values")
        self.analytics_service.impute_missing()
        
        # Step 4: Calculate BMI
        logger.info("\nStep 4/7: Calculating BMI")
        self.analytics_service.add_bmi()
        
        # Step 5: Calculate age
        logger.info("\nStep 5/7: Calculating age")
        self.analytics_service.add_age()
        
        # Step 6: Calculate z-scores
        logger.info("\nStep 6/7: Calculating z-scores")
        self.analytics_service.add_zscores()
        
        # Step 7: Finalize
        logger.info("\nStep 7/7: Finalizing processed data")
        df_processed = self.analytics_service.get_data()
        
        # Outlier detection (if requested)
        if detect_outliers:
            logger.info("\n" + "=" * 60)
            logger.info("OUTLIER DETECTION")
            logger.info("=" * 60)
            
            bmi_outliers = self.analytics_service.detect_outliers_iqr('bmi', multiplier=iqr_multiplier)
            logger.info(f"\nOutliers detected in 'bmi':")
            if not bmi_outliers.empty:
                logger.info(f"\n{bmi_outliers[['student_id', 'full_name', 'bmi']].to_string()}")
            
            gpa_outliers = self.analytics_service.detect_outliers_iqr('gpa', multiplier=iqr_multiplier)
            if not gpa_outliers.empty:
                logger.info(f"\nOutliers detected in 'gpa':")
                logger.info(f"\n{gpa_outliers[['student_id', 'full_name', 'gpa']].to_string()}")
        
        # Summary statistics
        logger.info("\n" + "=" * 60)
        logger.info("SUMMARY STATISTICS BY MAJOR")
        logger.info("=" * 60)
        summary = self.analytics_service.get_summary_by_major()
        logger.info(f"\n{summary.to_string()}")
        
        # Top students per major
        logger.info("\n" + "=" * 60)
        logger.info(f"TOP {top_k} STUDENTS PER MAJOR")
        logger.info("=" * 60)
        top_students = self.get_top_students_per_major(top_k)
        logger.info(f"\n{top_students[['major', 'full_name', 'gpa', 'credits']].to_string()}")
        
        # Export to CSV
        if output_file:
            logger.info("\n" + "=" * 60)
            logger.info("EXPORTING REPORT")
            logger.info("=" * 60)
            
            output_path = Path(output_file)
            df_processed.to_csv(output_path, index=False, encoding='utf-8-sig')
            
            logger.info(f"Report exported to: {output_path.absolute()}")
            logger.info(f"Total rows: {len(df_processed)}, Total columns: {len(df_processed.columns)}")
        
        logger.info("\n" + "=" * 60)
        logger.info("Report generation complete!")
        logger.info("=" * 60)
        
        return df_processed
    
    def get_summary_by_major(self) -> pd.DataFrame:
        """Get summary statistics by major"""
        if self.analytics_service is None:
            raise RuntimeError("Analytics service not initialized. Run generate_full_report first.")
        return self.analytics_service.get_summary_by_major()
    
    def get_top_students_per_major(self, k: int = 3) -> pd.DataFrame:
        """
        Get top K students per major by GPA.
        
        Args:
            k: Number of top students per major
        
        Returns:
            DataFrame with top students
        """
        if self.analytics_service is None:
            raise RuntimeError("Analytics service not initialized. Run generate_full_report first.")
        
        df = self.analytics_service.get_data()
        
        logger.info(f"Finding top {k} students per major")
        
        top_students = df.groupby('major', group_keys=False).apply(
            lambda x: x.nlargest(k, 'gpa')
        )
        
        logger.info(f"Selected {len(top_students)} top students across all majors")
        
        return top_students
