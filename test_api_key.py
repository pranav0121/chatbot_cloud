"""
This script tests if the Google Translate API key is being properly loaded
into the application configuration and used correctly.
"""

import os
from dotenv import load_dotenv
from app import create_app
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_api_key_loaded():
    """Test that the API key is loaded properly"""
    # Load environment variables
    load_dotenv()
    
    # Check environment variable
    api_key_env = os.environ.get('GOOGLE_TRANSLATE_API_KEY')
    logger.info(f"API key in environment: {'Yes' if api_key_env else 'No'}")
    
    # Create app and check configuration
    app = create_app('development')
    with app.app_context():
        api_key_config = app.config.get('GOOGLE_TRANSLATE_API_KEY')
        logger.info(f"API key in app config: {'Yes' if api_key_config else 'No'}")
        
        if api_key_config:
            logger.info(f"API key first 5 chars: {api_key_config[:5]}...")
        
        return api_key_config is not None and len(api_key_config) > 0

if __name__ == "__main__":
    result = test_api_key_loaded()
    if result:
        print("SUCCESS: Google Translate API key is properly configured!")
    else:
        print("FAILURE: Google Translate API key is not properly configured!")
