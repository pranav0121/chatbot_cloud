import os
from dotenv import load_dotenv
from flask import Flask
from app.services.translation_service import TranslationService
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

def test_translation_service():
    """Test the translation service with provided API key"""
    # Create a test Flask app context
    app = Flask(__name__)
    app.config['GOOGLE_TRANSLATE_API_KEY'] = os.environ.get('GOOGLE_TRANSLATE_API_KEY')
    
    logger.info(f"API Key configured: {'Yes' if app.config['GOOGLE_TRANSLATE_API_KEY'] else 'No'}")
    
    with app.app_context():
        # Test language detection
        text = "Hello, how are you today?"
        try:
            detected_lang = TranslationService.detect_language(text)
            logger.info(f"Detected language: {detected_lang}")
        except Exception as e:
            logger.error(f"Language detection failed: {e}")
        
        # Test translation
        try:
            translated_text = TranslationService.translate_text(text, 'hi')
            logger.info(f"Original text: {text}")
            logger.info(f"Translated text: {translated_text}")
        except Exception as e:
            logger.error(f"Translation failed: {e}")
    
    return True

if __name__ == '__main__':
    print("Testing translation service...")
    test_translation_service()
    print("Test complete!")
