class Config:
    DB_SERVER = 'your_db_server'
    DB_DATABASE = 'your_db_database'
    driver = 'ODBC Driver 17 for SQL Server'
    SQLALCHEMY_DATABASE_URI = f'mssql+pyodbc://{DB_SERVER}/{DB_DATABASE}?driver={driver}&trusted_connection=yes'