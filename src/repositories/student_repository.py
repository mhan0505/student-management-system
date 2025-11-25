"""Repository for student data access."""
import pandas as pd
from typing import Optional, List
import logging

from .mysql_client import MySQLClient


logger = logging.getLogger(__name__)


class StudentRepository:
    """
    Repository for accessing student data from MySQL database.
    
    This class provides methods to query student data without containing
    any business logic. All methods return pandas DataFrames.
    """
    
    def __init__(self, mysql_client: MySQLClient):
        """
        Initialize repository with MySQL client.
        
        Args:
            mysql_client: MySQLClient instance for database operations
        """
        self.client = mysql_client
        self.table_name = "students"
    
    def fetch_all(self) -> pd.DataFrame:
        """
        Fetch all student records.
        
        Returns:
            DataFrame containing all student records
        """
        query = f"SELECT * FROM {self.table_name}"
        logger.info("Fetching all students")
        return self.client.execute_query(query)
    
    def fetch_by_id(self, student_id: int) -> Optional[pd.DataFrame]:
        """
        Fetch student by ID.
        
        Args:
            student_id: Student ID to search for
            
        Returns:
            DataFrame with single student record or empty DataFrame
        """
        query = f"SELECT * FROM {self.table_name} WHERE student_id = :id"
        logger.info(f"Fetching student with ID: {student_id}")
        return self.client.execute_query(query, {'id': student_id})
    
    def fetch_by_major(self, major: str) -> pd.DataFrame:
        """
        Fetch all students in a specific major.
        
        Args:
            major: Major/program name to filter by
            
        Returns:
            DataFrame containing students in the specified major
        """
        query = f"SELECT * FROM {self.table_name} WHERE major = :major"
        logger.info(f"Fetching students in major: {major}")
        return self.client.execute_query(query, {'major': major})
    
    def fetch_by_gpa_range(self, min_gpa: float, max_gpa: float) -> pd.DataFrame:
        """
        Fetch students within a GPA range.
        
        Args:
            min_gpa: Minimum GPA (inclusive)
            max_gpa: Maximum GPA (inclusive)
            
        Returns:
            DataFrame containing students within GPA range
        """
        query = f"""
            SELECT * FROM {self.table_name} 
            WHERE gpa >= :min_gpa AND gpa <= :max_gpa
            ORDER BY gpa DESC
        """
        logger.info(f"Fetching students with GPA between {min_gpa} and {max_gpa}")
        return self.client.execute_query(query, {'min_gpa': min_gpa, 'max_gpa': max_gpa})
    
    def search_by_name(self, keyword: str) -> pd.DataFrame:
        """
        Search students by name using LIKE query.
        
        Args:
            keyword: Keyword to search for in student names
            
        Returns:
            DataFrame containing matching students
        """
        query = f"""
            SELECT * FROM {self.table_name} 
            WHERE full_name LIKE :keyword
            ORDER BY full_name
        """
        search_pattern = f"%{keyword}%"
        logger.info(f"Searching students with name containing: {keyword}")
        return self.client.execute_query(query, {'keyword': search_pattern})
    
    def fetch_by_gender(self, gender: str) -> pd.DataFrame:
        """
        Fetch students by gender.
        
        Args:
            gender: Gender ('M' or 'F')
            
        Returns:
            DataFrame containing students of specified gender
        """
        query = f"SELECT * FROM {self.table_name} WHERE gender = :gender"
        logger.info(f"Fetching students with gender: {gender}")
        return self.client.execute_query(query, {'gender': gender})
    
    def fetch_by_province(self, province: str) -> pd.DataFrame:
        """
        Fetch students from a specific province.
        
        Args:
            province: Province name
            
        Returns:
            DataFrame containing students from specified province
        """
        query = f"SELECT * FROM {self.table_name} WHERE province = :province"
        logger.info(f"Fetching students from province: {province}")
        return self.client.execute_query(query, {'province': province})
    
    def get_unique_majors(self) -> List[str]:
        """
        Get list of unique majors.
        
        Returns:
            List of unique major names
        """
        query = f"SELECT DISTINCT major FROM {self.table_name} ORDER BY major"
        df = self.client.execute_query(query)
        return df['major'].tolist()
    
    def count_students(self) -> int:
        """
        Count total number of students.
        
        Returns:
            Total student count
        """
        query = f"SELECT COUNT(*) as total FROM {self.table_name}"
        df = self.client.execute_query(query)
        return int(df['total'].iloc[0])
    
    def get_table_info(self) -> pd.DataFrame:
        """
        Get information about the students table structure.
        
        Returns:
            DataFrame with table column information
        """
        return self.client.get_table_info(self.table_name)
    
    # ========== CRUD OPERATIONS ==========
    
    def insert_student(self, student_data: dict) -> bool:
        """
        Insert a new student record.
        
        Args:
            student_data: Dictionary with student fields
            
        Returns:
            True if successful, False otherwise
        """
        try:
            from sqlalchemy import text
            columns = ', '.join(student_data.keys())
            placeholders = ', '.join([f":{k}" for k in student_data.keys()])
            query = f"INSERT INTO {self.table_name} ({columns}) VALUES ({placeholders})"
            
            with self.client.engine.connect() as conn:
                conn.execute(text(query), student_data)
                conn.commit()
                logger.info(f"Inserted student: {student_data.get('student_id', 'N/A')}")
                return True
        except Exception as e:
            logger.error(f"Failed to insert student: {e}")
            return False
    
    def update_student(self, student_id: str, update_data: dict) -> bool:
        """
        Update an existing student record.
        
        Args:
            student_id: Student ID to update
            update_data: Dictionary with fields to update
            
        Returns:
            True if successful, False otherwise
        """
        try:
            from sqlalchemy import text
            set_clause = ', '.join([f"{k} = :{k}" for k in update_data.keys()])
            query = f"UPDATE {self.table_name} SET {set_clause} WHERE student_id = :student_id"
            
            params = {**update_data, 'student_id': student_id}
            
            with self.client.engine.connect() as conn:
                result = conn.execute(text(query), params)
                conn.commit()
                affected_rows = result.rowcount
                logger.info(f"Updated student {student_id}: {affected_rows} rows affected")
                return affected_rows > 0
        except Exception as e:
            logger.error(f"Failed to update student {student_id}: {e}")
            return False
    
    def delete_student(self, student_id: str) -> bool:
        """
        Delete a student record.
        
        Args:
            student_id: Student ID to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            from sqlalchemy import text
            query = f"DELETE FROM {self.table_name} WHERE student_id = :student_id"
            
            with self.client.engine.connect() as conn:
                result = conn.execute(text(query), {"student_id": student_id})
                conn.commit()
                affected_rows = result.rowcount
                logger.info(f"Deleted student {student_id}: {affected_rows} rows affected")
                return affected_rows > 0
        except Exception as e:
            logger.error(f"Failed to delete student {student_id}: {e}")
            return False
    
    def get_students_by_gpa(self, min_gpa: float) -> pd.DataFrame:
        """
        Get students with GPA greater than threshold.
        
        Args:
            min_gpa: Minimum GPA threshold
            
        Returns:
            DataFrame with filtered students
        """
        query = f"SELECT * FROM {self.table_name} WHERE gpa > {min_gpa} ORDER BY gpa DESC"
        return self.client.execute_query(query)
