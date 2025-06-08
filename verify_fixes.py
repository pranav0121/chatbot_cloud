"""
YouCloudPay Fix Verification Script

This script verifies:
1. Categories are properly displayed for all users in chat
2. Translation API key is configured correctly
"""

from flask import Flask
from app import create_app, db
from app.models.user import User
from app.models.complaint import Complaint
from app.models.message import Message
from app.services.chatbot_service import ChatbotService
from app.services.translation_service import TranslationService
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_category_display():
    """Test that categories are displayed correctly"""
    app = create_app('development')
    with app.app_context():
        # Get a test user or create one
        test_user = User.query.filter_by(email='test@example.com').first()
        if not test_user:
            from werkzeug.security import generate_password_hash
            test_user = User(
                name='Test User',
                email='test@example.com',
                password_hash=generate_password_hash('password123'),
                role='user',
                language='en'
            )
            db.session.add(test_user)
            db.session.commit()
            logger.info("Created test user")
        
        # Create a new complaint
        new_complaint = Complaint(
            user_id=test_user.id,
            title='Test Complaint',
            description='',
            category='',
            status='open'
        )
        db.session.add(new_complaint)
        db.session.commit()
        logger.info(f"Created test complaint ID: {new_complaint.id}")
        
        # Test initial greeting
        greeting = ChatbotService.generate_bot_response("hello", test_user, new_complaint)
        logger.info(f"Bot greeting: {greeting}")
        
        # Test category list display
        categories = ChatbotService._initiate_complaint_flow(test_user)
        logger.info(f"Categories display: {categories}")
        
        # Verify vertical formatting (numbered list)
        has_vertical_format = "1. **" in categories
        logger.info(f"Categories are displayed in vertical format: {has_vertical_format}")
        
        # Test invalid category input
        invalid_response = ChatbotService._handle_complaint_flow("invalid_category", new_complaint, test_user)
        logger.info(f"Invalid category response: {invalid_response}")
        
        # Verify consistent vertical formatting
        has_consistent_format = "1. **" in invalid_response
        logger.info(f"Invalid response has consistent vertical format: {has_consistent_format}")
        
        # Clean up
        db.session.delete(new_complaint)
        db.session.commit()
        logger.info("Test complaint deleted")
        
        return has_vertical_format and has_consistent_format and "Please select a valid category" in invalid_response

def test_translation_api():
    """Test that translation API key is configured"""
    app = create_app('development')
    with app.app_context():
        api_key = app.config.get('GOOGLE_TRANSLATE_API_KEY')
        if not api_key:
            logger.error("No translation API key configured")
            return False
        
        logger.info(f"API Key configured: {api_key[:5]}...")
        
        # Test translation
        original_text = "Hello, this is a test."
        try:
            translated = TranslationService.translate_text(original_text, 'hi')
            logger.info(f"Original: {original_text}")
            logger.info(f"Translated: {translated}")
            return translated != original_text
        except Exception as e:
            logger.error(f"Translation test failed: {e}")
            return False

if __name__ == "__main__":
    print("====== YouCloudPay Fixes Verification ======")
    print("\n1. Testing category display in chat...")
    categories_ok = test_category_display()
    print(f"Categories test: {'PASSED' if categories_ok else 'FAILED'}")
    
    print("\n2. Testing translation API key...")
    translation_ok = test_translation_api()
    print(f"Translation API test: {'PASSED' if translation_ok else 'FAILED'}")
    
    print("\n====== Summary ======")
    if categories_ok and translation_ok:
        print("All fixes have been implemented successfully! ✓")
    else:
        print("Some issues remain. Please check the logs.")
