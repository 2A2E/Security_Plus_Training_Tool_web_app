"""
Database connection module for Supabase (PostgreSQL) operations
"""
import os
import sys
import logging
from typing import Optional

# Add parent directory to path to import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from supabase import create_client, Client
    from config import Config
except ImportError as e:
    logging.error(f"Failed to import required modules: {e}")
    logging.error("Please install required dependencies: pip install supabase psycopg2-binary")
    raise

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseManager:
    """Supabase database manager for Security Plus Training Tool"""
    
    def __init__(self, supabase_url: str = None, supabase_key: str = None):
        """
        Initialize Supabase connection
        
        Args:
            supabase_url: Supabase project URL
            supabase_key: Supabase API key
        """
        # Use config values as defaults
        config = Config()
        self.supabase_url = supabase_url or os.environ.get('SUPABASE_URL', config.SUPABASE_URL)
        self.supabase_key = supabase_key or os.environ.get('SUPABASE_KEY', config.SUPABASE_KEY)
        self.database_name = os.environ.get('DATABASE_NAME', config.DATABASE_NAME)
        self.client: Optional[Client] = None
        self._connect()
    
    def _connect(self):
        """Establish connection to Supabase"""
        try:
            if not self.supabase_url or not self.supabase_key:
                raise ValueError("Supabase URL and API key are required")
            
            self.client = create_client(self.supabase_url, self.supabase_key)
            
            # Test the connection by making a simple query
            result = self.client.table('questions').select('id').limit(1).execute()
            logger.info(f"Successfully connected to Supabase database: {self.database_name}")
            
        except Exception as e:
            logger.error(f"Failed to connect to Supabase: {e}")
            logger.info("Note: The 'questions' table may not exist yet. This is normal for first-time setup.")
            # Don't raise the error, just log it - the table might not exist yet
            self.client = create_client(self.supabase_url, self.supabase_key)
            logger.info("Supabase client created (table may need to be created)")
    
    def get_client(self) -> Client:
        """Get the Supabase client"""
        if not self.client:
            self._connect()
        return self.client
    
    def get_table(self, table_name: str):
        """Get a table reference from Supabase"""
        if not self.client:
            self._connect()
        return self.client.table(table_name)
    
    def close_connection(self):
        """Close the database connection (Supabase handles this automatically)"""
        logger.info("Supabase connection closed (handled automatically)")

# Global database manager instance
db_manager = DatabaseManager()