import pytest
from app import create_app, db
from app.models.user import User
from app.models.complaint import Complaint
from app.models.faq import FAQ

@pytest.fixture
def app():
    """Create application for testing"""
    app = create_app('testing')
    
    with app.app_context():
        db.create_all()
        
        # Create test admin user
        admin = User(
            name='Test Admin',
            email='admin@test.com',
            role='admin',
            language='en'
        )
        admin.set_password('testpass')
        db.session.add(admin)
        
        # Create test regular user
        user = User(
            name='Test User',
            email='user@test.com',
            role='user',
            language='en'
        )
        user.set_password('testpass')
        db.session.add(user)
        
        # Create test FAQ
        faq = FAQ(
            question='How to reset password?',
            answer='Click forgot password link',
            category='account',
            language='en'
        )
        db.session.add(faq)
        
        db.session.commit()
        
        yield app
        
        db.drop_all()

@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()

@pytest.fixture
def runner(app):
    """Create test CLI runner"""
    return app.test_cli_runner()

class TestAuth:
    """Test authentication functionality"""
    
    def test_register_get(self, client):
        """Test register page loads"""
        response = client.get('/auth/register')
        assert response.status_code == 200
        assert b'Create Account' in response.data
    
    def test_register_post_valid(self, client):
        """Test valid user registration"""
        response = client.post('/auth/register', data={
            'name': 'New User',
            'email': 'newuser@test.com',
            'password': 'testpass123',
            'confirm_password': 'testpass123'
        })
        assert response.status_code == 302  # Redirect after success
    
    def test_register_post_invalid(self, client):
        """Test invalid user registration"""
        response = client.post('/auth/register', data={
            'name': 'Short',
            'email': 'invalid-email',
            'password': '123',
            'confirm_password': 'different'
        })
        assert response.status_code == 200
        assert b'error' in response.data.lower()
    
    def test_login_get(self, client):
        """Test login page loads"""
        response = client.get('/auth/login')
        assert response.status_code == 200
        assert b'Sign In' in response.data
    
    def test_login_valid(self, client):
        """Test valid user login"""
        response = client.post('/auth/login', data={
            'email': 'user@test.com',
            'password': 'testpass'
        })
        assert response.status_code == 302  # Redirect after success
    
    def test_login_invalid(self, client):
        """Test invalid user login"""
        response = client.post('/auth/login', data={
            'email': 'user@test.com',
            'password': 'wrongpass'
        })
        assert response.status_code == 200
        assert b'Invalid' in response.data

class TestChat:
    """Test chat functionality"""
    
    def test_chat_page_unauthorized(self, client):
        """Test chat page requires login"""
        response = client.get('/chat')
        assert response.status_code == 302  # Redirect to login
    
    def test_chat_page_authorized(self, client):
        """Test chat page with login"""
        # Login first
        client.post('/auth/login', data={
            'email': 'user@test.com',
            'password': 'testpass'
        })
        
        response = client.get('/chat')
        assert response.status_code == 200
        assert b'Chat Support' in response.data

class TestAdmin:
    """Test admin functionality"""
    
    def test_admin_unauthorized(self, client):
        """Test admin page requires admin login"""
        response = client.get('/admin/dashboard')
        assert response.status_code == 302  # Redirect to login
    
    def test_admin_user_access_denied(self, client):
        """Test regular user cannot access admin"""
        # Login as regular user
        client.post('/auth/login', data={
            'email': 'user@test.com',
            'password': 'testpass'
        })
        
        response = client.get('/admin/dashboard')
        assert response.status_code == 302  # Redirect
    
    def test_admin_authorized(self, client):
        """Test admin page with admin login"""
        # Login as admin
        client.post('/auth/login', data={
            'email': 'admin@test.com',
            'password': 'testpass'
        })
        
        response = client.get('/admin/dashboard')
        assert response.status_code == 200
        assert b'Admin Dashboard' in response.data

class TestAPI:
    """Test API functionality"""
    
    def test_health_check(self, client):
        """Test health check endpoint"""
        response = client.get('/health')
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'healthy'
        assert 'database' in data
    
    def test_faq_search(self, client):
        """Test FAQ search API"""
        response = client.get('/api/faq/search?q=password')
        assert response.status_code == 200
        data = response.get_json()
        assert 'results' in data

class TestModels:
    """Test database models"""
    
    def test_user_model(self, app):
        """Test User model"""
        with app.app_context():
            user = User(
                name='Test User',
                email='test@example.com',
                role='user',
                language='en'
            )
            user.set_password('testpass')
            
            assert user.check_password('testpass')
            assert not user.check_password('wrongpass')
            assert user.get_full_name() == 'Test User'
            assert not user.is_admin()
    
    def test_faq_model(self, app):
        """Test FAQ model"""
        with app.app_context():
            faq = FAQ(
                question='Test question?',
                answer='Test answer',
                category='general',
                language='en'
            )
            
            assert faq.get_category_display() == 'General'
            assert faq.get_helpfulness_ratio() == 0.5
