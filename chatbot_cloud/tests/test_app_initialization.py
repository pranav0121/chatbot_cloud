class TestAppInitialization:
    def test_application_initialization(self):
        from config_fixed import Config
        assert Config.DB_SERVER is not None
        assert Config.DB_DATABASE is not None
        assert isinstance(Config.SQLALCHEMY_DATABASE_URI, str)