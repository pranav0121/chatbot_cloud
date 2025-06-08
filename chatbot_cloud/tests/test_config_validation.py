class Config:
    DB_SERVER = 'your_db_server'
    DB_DATABASE = 'your_db_database'
    SQLALCHEMY_DATABASE_URI = f'mssql+pyodbc://{DB_SERVER}/{DB_DATABASE}?driver=ODBC Driver 17 for SQL Server&trusted_connection=yes'

def test_config_validation():
    assert Config.DB_SERVER is not None
    assert Config.DB_DATABASE is not None
    assert 'mssql+pyodbc://' in Config.SQLALCHEMY_DATABASE_URI
    assert Config.DB_SERVER in Config.SQLALCHEMY_DATABASE_URI
    assert Config.DB_DATABASE in Config.SQLALCHEMY_DATABASE_URI