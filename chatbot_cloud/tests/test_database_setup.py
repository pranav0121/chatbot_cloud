class TestDatabaseSetup:
    def test_database_connection(self):
        from config_fixed import Config
        assert Config.SQLALCHEMY_DATABASE_URI is not None
        assert "mssql+pyodbc://" in Config.SQLALCHEMY_DATABASE_URI
        assert "trusted_connection=yes" in Config.SQLALCHEMY_DATABASE_URI