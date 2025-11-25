"""
Student Management System - Main Entry Point

This script demonstrates the complete pipeline for student data analysis.
"""
import logging
import sys
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent))

from src.config.database import DatabaseConfig
from src.repositories.mysql_client import MySQLClient
from src.repositories.student_repository import StudentRepository
from src.reports.report_generator import StudentReportGenerator


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('student_analysis.log', encoding='utf-8')
    ]
)

logger = logging.getLogger(__name__)


def main():
    """Main execution function."""
    try:
        logger.info("=" * 80)
        logger.info("STUDENT MANAGEMENT SYSTEM - ANALYSIS PIPELINE")
        logger.info("=" * 80)
        
        # Step 1: Load database configuration
        logger.info("\n[1/5] Loading database configuration...")
        db_config = DatabaseConfig.from_env()
        logger.info(f"Database config loaded: {db_config}")
        
        # Step 2: Initialize MySQL client
        logger.info("\n[2/5] Initializing MySQL client...")
        mysql_client = MySQLClient(db_config)
        
        # Test connection
        if not mysql_client.test_connection():
            logger.error("Database connection failed!")
            return
        
        logger.info("Database connection successful!")
        
        # Step 3: Initialize repository
        logger.info("\n[3/5] Initializing student repository...")
        repository = StudentRepository(mysql_client)
        
        # Display table info
        table_info = repository.get_table_info()
        logger.info(f"\nTable structure:\n{table_info.to_string()}")
        
        # Count students
        total_students = repository.count_students()
        logger.info(f"\nTotal students in database: {total_students}")
        
        # Get unique majors
        majors = repository.get_unique_majors()
        logger.info(f"Available majors: {', '.join(majors)}")
        
        # Step 4: Generate full report
        logger.info("\n[4/5] Generating comprehensive report...")
        report_generator = StudentReportGenerator(repository)
        
        processed_df = report_generator.generate_full_report(
            output_file='student_report.csv',
            detect_outliers=True,
            top_k=3
        )
        
        # Step 5: Display final statistics
        logger.info("\n[5/5] Final statistics...")
        logger.info(f"Total records processed: {len(processed_df)}")
        logger.info(f"Total columns: {len(processed_df.columns)}")
        logger.info(f"Columns: {list(processed_df.columns)}")
        
        # Display summary by major
        summary = report_generator.get_summary_by_major()
        logger.info(f"\nSummary by major:\n{summary.to_string()}")
        
        logger.info("\n" + "=" * 80)
        logger.info("ANALYSIS COMPLETE!")
        logger.info("=" * 80)
        logger.info(f"Report saved to: student_report.csv")
        logger.info(f"Log saved to: student_analysis.log")
        
    except Exception as e:
        logger.error(f"Error in main execution: {e}", exc_info=True)
        raise
    finally:
        # Cleanup
        if 'mysql_client' in locals():
            mysql_client.close()
            logger.info("Database connection closed")


if __name__ == "__main__":
    main()
