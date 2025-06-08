class Config:
    DB_SERVER = 'your_database_server'
    DB_DATABASE = 'your_database_name'
    SQLALCHEMY_DATABASE_URI = f'mssql+pyodbc://{DB_SERVER}/{DB_DATABASE}?driver=your_driver&trusted_connection=yes'

def test_config():
    assert Config.DB_SERVER == 'your_database_server'
    assert Config.DB_DATABASE == 'your_database_name'
    assert Config.SQLALCHEMY_DATABASE_URI == f'mssql+pyodbc://{Config.DB_SERVER}/{Config.DB_DATABASE}?driver=your_driver&trusted_connection=yes'