import os
from dotenv import load_dotenv
from urllib.parse import quote_plus

# Load environment variables
load_dotenv()

class Config:
    # Database configuration
    DB_SERVER = os.getenv('DB_SERVER', 'localhost')
    DB_DATABASE = os.getenv('DB_DATABASE', 'SupportChatbot')
    DB_USERNAME = os.getenv('DB_USERNAME', 'sa')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '')
    DB_USE_WINDOWS_AUTH = os.getenv('DB_USE_WINDOWS_AUTH', 'True').lower() in ('true', '1', 't')
    
    # SQL Server connection string with fallback drivers
    @property
    def SQLALCHEMY_DATABASE_URI(self):
        if self.DB_USE_WINDOWS_AUTH:
            # Use Windows Authentication
            driver = quote_plus('ODBC Driver 17 for SQL Server')
            return f'mssql+pyodbc://{self.DB_SERVER}/{self.DB_DATABASE}?driver={driver}&trusted_connection=yes'
        else:
            # Use SQL Server Authentication
            driver = quote_plus('ODBC Driver 17 for SQL Server')
            password = quote_plus(self.DB_PASSWORD) if self.DB_PASSWORD else ''
            return f'mssql+pyodbc://{self.DB_USERNAME}:{password}@{self.DB_SERVER}/{self.DB_DATABASE}?driver={driver}'    
    # Fallback to SQLite if SQL Server fails
    SQLALCHEMY_DATABASE_URI_FALLBACK = 'sqlite:///chatbot.db'
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False  # Disable SQL query logging to reduce noise
    
    # Connection pool configuration to prevent timeouts
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 20,
        'pool_timeout': 120,
        'pool_recycle': 3600,
        'max_overflow': 50,
        'pool_pre_ping': True
    }
    
    # Flask configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-here')
    
    # Session configuration
    SESSION_TYPE = 'filesystem'
    
    # Application configuration
    DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() in ('true', '1', 't')
    
    # API configuration
    API_TITLE = 'Support Chatbot API'
    API_VERSION = 'v1'
