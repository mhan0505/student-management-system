"""Database configuration management."""
import os
from dataclasses import dataclass
from typing import Optional
from dotenv import load_dotenv


@dataclass
class DatabaseConfig:
    """
    Database configuration data class.
    
    Attributes:
        host: MySQL server host
        port: MySQL server port
        username: Database username
        password: Database password
        database: Database name
        charset: Character set (default: utf8mb4)
    """
    host: str
    port: int
    username: str
    password: str
    database: str
    charset: str = 'utf8mb4'
    
    @classmethod
    def from_env(cls, env_file: str = '.env') -> 'DatabaseConfig':
        """
        Load database configuration from environment variables.
        
        Args:
            env_file: Path to .env file (default: '.env')
            
        Returns:
            DatabaseConfig instance
            
        Raises:
            ValueError: If required environment variables are missing
        """
        load_dotenv(env_file)
        
        # Get required fields
        username = os.getenv('MYSQL_USER')
        host = os.getenv('MYSQL_HOST', 'localhost')
        port = int(os.getenv('MYSQL_PORT', '3306'))
        database = os.getenv('MYSQL_DB')
        password = os.getenv('MYSQL_PASSWORD', '')
        
        # Validate required fields
        if not username:
            raise ValueError("MYSQL_USER environment variable is required")
        if not database:
            raise ValueError("MYSQL_DB environment variable is required")
        
        return cls(
            host=host,
            port=port,
            username=username,
            password=password,
            database=database
        )
    
    def get_connection_string(self) -> str:
        """
        Generate SQLAlchemy connection string.
        
        Returns:
            MySQL connection string in format: mysql+pymysql://user:pass@host:port/db
        """
        return f"mysql+pymysql://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}?charset={self.charset}"
    
    def validate(self) -> bool:
        """
        Validate configuration fields.
        
        Returns:
            True if all required fields are present
        """
        required_fields = [self.host, self.username, self.database]
        return all(field for field in required_fields)
    
    def __repr__(self) -> str:
        """String representation (hides password)."""
        return (f"DatabaseConfig(host='{self.host}', port={self.port}, "
                f"username='{self.username}', database='{self.database}')")
