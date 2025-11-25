"""MySQL client for database operations."""
import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from typing import Optional
import logging

from ..config.database import DatabaseConfig


logger = logging.getLogger(__name__)


class MySQLClient:
    """
    MySQL client for executing queries and returning DataFrames.
    
    This class handles database connections and query execution using SQLAlchemy.
    """
    
    def __init__(self, config: DatabaseConfig):
        """
        Initialize MySQL client with database configuration.
        
        Args:
            config: DatabaseConfig instance with connection details
        """
        self.config = config
        self._engine: Optional[Engine] = None
    
    @property
    def engine(self) -> Engine:
        """
        Get or create SQLAlchemy engine.
        
        Returns:
            SQLAlchemy Engine instance
        """
        if self._engine is None:
            connection_string = self.config.get_connection_string()
            self._engine = create_engine(
                connection_string,
                pool_pre_ping=True,  # Verify connections before using
                pool_recycle=3600,   # Recycle connections after 1 hour
                echo=False           # Set to True for SQL debugging
            )
            logger.info(f"Created database engine: {self.config.host}:{self.config.port}/{self.config.database}")
        return self._engine
    
    def execute_query(self, query: str, params: dict = None) -> pd.DataFrame:
        """
        Execute SQL query and return results as pandas DataFrame.
        
        Args:
            query: SQL query string
            params: Optional dictionary of query parameters
            
        Returns:
            pandas DataFrame with query results
            
        Raises:
            Exception: If query execution fails
        """
        try:
            logger.debug(f"Executing query: {query[:100]}...")
            
            if params:
                df = pd.read_sql(text(query), self.engine, params=params)
            else:
                df = pd.read_sql(query, self.engine)
            
            logger.info(f"Query returned {len(df)} rows")
            return df
            
        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            raise
    
    def test_connection(self) -> bool:
        """
        Test database connection.
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text("SELECT 1"))
                result.fetchone()
            logger.info("Database connection test successful")
            return True
        except Exception as e:
            logger.error(f"Database connection test failed: {e}")
            return False
    
    def get_table_info(self, table_name: str) -> pd.DataFrame:
        """
        Get information about table structure.
        
        Args:
            table_name: Name of the table
            
        Returns:
            DataFrame with table column information
        """
        query = f"DESCRIBE {table_name}"
        return self.execute_query(query)
    
    def close(self):
        """Close database connection and dispose of engine."""
        if self._engine:
            self._engine.dispose()
            logger.info("Database engine disposed")
            self._engine = None
