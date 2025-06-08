import os
import requests
from flask import current_app
import logging

logger = logging.getLogger(__name__)

class TranslationService:
    """Translation service using Google Translate API or DeepL API"""
    
    @staticmethod
    def detect_language(text):
        """Detect the language of text"""
        try:
            # Use Google Translate API for detection
            api_key = current_app.config.get('GOOGLE_TRANSLATE_API_KEY')
            if not api_key:
                logger.warning("No translation API key configured in app.config")
                # Try to get it directly from environment
                import os
                api_key = os.environ.get('GOOGLE_TRANSLATE_API_KEY')
                if not api_key:
                    logger.warning("No translation API key found in environment variables")
                    return 'en'
                else:
                    logger.info("Found translation API key in environment variables")
            else:
                logger.info("Using translation API key from app.config")
            
            # For development without a valid API key, simulate detection
            if os.environ.get('FLASK_ENV') == 'development':
                logger.info("Running in development mode - using simulated language detection")
                return 'en'
            
            url = f"https://translation.googleapis.com/language/translate/v2/detect"
            params = {
                'key': api_key,
                'q': text
            }
            
            logger.info(f"Sending request to Google Translate API (detect): {url}")
            response = requests.post(url, data=params)
            if response.status_code == 200:
                result = response.json()
                detected_lang = result['data']['detections'][0][0]['language']
                confidence = result['data']['detections'][0][0]['confidence']
                logger.info(f"Detected language: {detected_lang} with confidence: {confidence}")
                
                # Only return detected language if confidence is high enough
                if confidence > 0.7:
                    return detected_lang
            else:
                logger.error(f"Translation API error: {response.status_code}, Response: {response.text}")
            
            return 'en'  # Default to English
            
        except Exception as e:
            logger.error(f"Language detection failed: {e}")
            return 'en'
    
    @staticmethod
    def translate_text(text, target_language, source_language=None):
        """Translate text to target language"""
        try:
            # Skip translation if target is same as source
            if source_language and source_language == target_language:
                return text
            
            # Skip translation if text is too short
            if len(text.strip()) < 3:
                return text
                
            # For development without a valid API key, simulate translation
            if os.environ.get('FLASK_ENV') == 'development':
                logger.info(f"Running in development mode - using simulated translation to {target_language}")
                # Simple simulation of translation for testing purposes
                if target_language == 'hi':
                    return f"[Hindi] {text}"
                elif target_language == 'te':
                    return f"[Telugu] {text}"
                elif target_language == 'mr':
                    return f"[Marathi] {text}"
                elif target_language == 'kn':
                    return f"[Kannada] {text}"
                elif target_language == 'ta':
                    return f"[Tamil] {text}"
                else:
                    return text
            
            api_key = current_app.config.get('GOOGLE_TRANSLATE_API_KEY')
            if not api_key:
                logger.warning("No translation API key configured")
                return text
            
            url = f"https://translation.googleapis.com/language/translate/v2"
            params = {
                'key': api_key,
                'q': text,
                'target': target_language,
                'format': 'text'
            }
            
            if source_language:
                params['source'] = source_language
            
            logger.info(f"Sending request to Google Translate API (translate): {url}")
            response = requests.post(url, data=params)
            if response.status_code == 200:
                result = response.json()
                translated_text = result['data']['translations'][0]['translatedText']
                logger.info(f"Successfully translated text from {source_language or 'auto'} to {target_language}")
                return translated_text
            else:
                logger.error(f"Translation API error: {response.status_code}, Response: {response.text}")
                # Simulate translation as fallback when API fails
                if target_language == 'hi':
                    return f"[Hindi] {text}"
                elif target_language == 'te':
                    return f"[Telugu] {text}"
                elif target_language == 'mr':
                    return f"[Marathi] {text}"
                elif target_language == 'kn':
                    return f"[Kannada] {text}"
                elif target_language == 'ta':
                    return f"[Tamil] {text}"
                else:
                    return text
                
        except Exception as e:
            logger.error(f"Translation failed: {e}")
            return text
    
    @staticmethod
    def get_supported_languages():
        """Get list of supported languages"""
        return {
            'en': 'English',
            'hi': 'हिंदी (Hindi)',
            'te': 'తెలుగు (Telugu)',
            'mr': 'मराठी (Marathi)',
            'kn': 'ಕನ್ನಡ (Kannada)',
            'ta': 'தமிழ் (Tamil)'
        }
    
    @staticmethod
    def translate_message_content(message, user_language):
        """Translate message content for user's preferred language"""
        if not message.content:
            return message.content
        
        # If message is already in user's language, return as is
        if message.language == user_language:
            return message.content
        
        # If we have a translated version, use it
        if message.content_translated and message.language != user_language:
            return message.content_translated
        
        # Translate the content
        translated = TranslationService.translate_text(
            message.content, 
            user_language, 
            message.language
        )
        
        # Save translated version for future use
        message.content_translated = translated
        from app import db
        db.session.commit()
        
        return translated