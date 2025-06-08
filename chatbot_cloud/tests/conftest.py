class Config:
    DB_SERVER = 'your_database_server'
    DB_DATABASE = 'your_database_name'
    SQLALCHEMY_DATABASE_URI = f'mssql+pyodbc://{DB_SERVER}/{DB_DATABASE}?driver={{driver}}&trusted_connection=yes'