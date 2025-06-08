import pytest
import tempfile
import os
from app import create_app, db
from config import TestingConfig

@pytest.fixture(scope='session')
def app():
    """Create application for testing"""
    # Create temporary database file
    db_fd, db_path = tempfile.mkstemp()
    
    # Override config for testing
    class TestConfig(TestingConfig):
        DATABASE_URL = f'sqlite:///{db_path}'
        WTF_CSRF_ENABLED = False  # Disable CSRF for testing
    
    app = create_app()
    app.config.from_object(TestConfig)
    
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()
    
    os.close(db_fd)
    os.unlink(db_path)

@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()

@pytest.fixture
def runner(app):
    """Create test CLI runner"""
    return app.test_cli_runner()

@pytest.fixture
def auth_client(client):
    """Create authenticated test client"""
    from app.models.user import User
    from app import db
    
    # Create test user
    user = User(
        name='Test User',
        email='test@example.com',
        role='user',
        language='en'
    )
    user.set_password('testpass')
    db.session.add(user)
    db.session.commit()
    
    # Login
    client.post('/auth/login', data={
        'email': 'test@example.com',
        'password': 'testpass'
    })
    
    return client

@pytest.fixture
def admin_client(client):
    """Create admin authenticated test client"""
    from app.models.user import User
    from app import db
    
    # Create admin user
    admin = User(
        name='Admin User',
        email='admin@example.com',
        role='admin',
        language='en'
    )
    admin.set_password('adminpass')
    db.session.add(admin)
    db.session.commit()
    
    # Login
    client.post('/auth/login', data={
        'email': 'admin@example.com',
        'password': 'adminpass'
    })
    
    return client
