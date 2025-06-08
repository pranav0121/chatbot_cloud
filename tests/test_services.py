import pytest
from app.services.chatbot_service import ChatbotService
from app.services.translation_service import TranslationService
from app.services.file_service import FileService
from app.models.user import User
from app.models.message import Message
from app.models.complaint import Complaint
from app import create_app, db

@pytest.fixture
def app():
    """Create application for testing"""
    app = create_app('testing')
    
    with app.app_context():
        db.create_all()
        
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
        
        yield app
        
        db.drop_all()

class TestChatbotService:
    """Test chatbot service functionality"""
    
    def test_greeting_detection(self):
        """Test greeting message detection"""
        assert ChatbotService._is_greeting("hello")
        assert ChatbotService._is_greeting("hi there")
        assert ChatbotService._is_greeting("good morning")
        assert not ChatbotService._is_greeting("help me")
    
    def test_complaint_detection(self):
        """Test complaint keyword detection"""
        assert ChatbotService._is_complaint_related("I have a problem")
        assert ChatbotService._is_complaint_related("file a complaint")
        assert ChatbotService._is_complaint_related("issue with billing")
        assert not ChatbotService._is_complaint_related("hello there")
    
    def test_category_extraction(self):
        """Test category extraction from message"""
        assert ChatbotService._extract_category("billing issue") == "billing"
        assert ChatbotService._extract_category("technical problem") == "technical"
        assert ChatbotService._extract_category("random message") is None
    
    def test_bot_response_generation(self, app):
        """Test bot response generation"""
        with app.app_context():
            user = User.query.first()
            
            # Test greeting response
            response = ChatbotService.generate_response("hello", user)
            assert "Hello" in response
            assert "YouCloudPay" in response
            
            # Test default response
            response = ChatbotService.generate_response("random message", user)
            assert "not sure" in response.lower()

class TestTranslationService:
    """Test translation service functionality"""
    
    def test_language_detection(self):
        """Test language detection"""
        # Mock the API call since we don't have API keys in testing
        service = TranslationService()
        
        # Test fallback to English
        lang = service.detect_language("Hello world")
        assert lang == 'en'  # Should fallback to English in testing
    
    def test_text_translation(self):
        """Test text translation"""
        service = TranslationService()
        
        # Test same language (should return original)
        result = service.translate_text("Hello", 'en', 'en')
        assert result == "Hello"
        
        # Test translation without API (should return original)
        result = service.translate_text("Hello", 'en', 'es')
        assert result == "Hello"  # Should return original in testing

class TestFileService:
    """Test file service functionality"""
    
    def test_allowed_file_extension(self):
        """Test file extension validation"""
        assert FileService.allowed_file("document.pdf")
        assert FileService.allowed_file("image.jpg")
        assert FileService.allowed_file("text.txt")
        assert not FileService.allowed_file("virus.exe")
        assert not FileService.allowed_file("script.js")
    
    def test_file_type_detection(self):
        """Test file type detection"""
        assert FileService.get_file_type("document.pdf") == "document"
        assert FileService.get_file_type("image.jpg") == "image"
        assert FileService.get_file_type("archive.zip") == "archive"
        assert FileService.get_file_type("unknown.xyz") == "other"
    
    def test_unique_filename_generation(self):
        """Test unique filename generation"""
        filename1 = FileService.generate_unique_filename("test.txt")
        filename2 = FileService.generate_unique_filename("test.txt")
        
        # Should be different due to timestamp
        assert filename1 != filename2
        assert filename1.endswith("_test.txt")
        assert filename2.endswith("_test.txt")
    
    def test_file_size_formatting(self):
        """Test file size formatting"""
        assert FileService.format_file_size(1024) == "1.0 KB"
        assert FileService.format_file_size(1048576) == "1.0 MB"
        assert FileService.format_file_size(1073741824) == "1.0 GB"
        assert FileService.format_file_size(500) == "500.0 B"
