import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    # Database configuration    DB_SERVER = os.getenv('DB_SERVER', 'localhost')
    DB_DATABASE = os.getenv('DB_DATABASE', 'SupportChatbot')
    DB_USERNAME = os.getenv('DB_USERNAME', 'sa')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '')
    DB_USE_WINDOWS_AUTH = os.getenv('DB_USE_WINDOWS_AUTH', 'True').lower() in ('true', '1', 't')
    
    # SQL Server connection string with fallback drivers
    if DB_USE_WINDOWS_AUTH:
        # Try different drivers in order of preference
        drivers = [
            'ODBC+Driver+17+for+SQL+Server',
            'ODBC+Driver+13+for+SQL+Server', 
            'SQL+Server+Native+Client+11.0',
            'SQL+Server'
        ]
        # Use the first available driver
        driver = 'ODBC+Driver+17+for+SQL+Server'  # Default
        SQLALCHEMY_DATABASE_URI = f'mssql+pyodbc://{DB_SERVER}/{DB_DATABASE}?driver={driver}&trusted_connection=yes'
    else:
        SQLALCHEMY_DATABASE_URI = f'mssql+pyodbc://{DB_USERNAME}:{DB_PASSWORD}@{DB_SERVER}/{DB_DATABASE}?driver=ODBC+Driver+17+for+SQL+Server'
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
