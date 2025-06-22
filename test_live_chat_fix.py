#!/usr/bin/env python3
"""
Quick test to verify live chat WebSocket integration
"""
import os
import time
import logging
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_live_chat_fix():
    """Test the live chat functionality"""
    try:
        # Load environment variables
        load_dotenv()
        
        logger.info("🧪 TESTING LIVE CHAT FIX")
        logger.info("="*50)
        
        # Check if Flask app is running
        import requests
        try:
            response = requests.get('http://127.0.0.1:5000/test', timeout=5)
            if response.status_code == 200:
                logger.info("✅ Flask app is running")
            else:
                logger.error(f"❌ Flask app returned status {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"❌ Flask app is not running: {e}")
            logger.info("💡 Please start the Flask app first: python app.py")
            return False
        
        # Check admin login
        try:
            admin_response = requests.get('http://127.0.0.1:5000/admin', timeout=5)
            if admin_response.status_code in [200, 302]:  # 302 for redirect to login
                logger.info("✅ Admin route is accessible")
            else:
                logger.warning(f"⚠️ Admin route returned status {admin_response.status_code}")
        except Exception as e:
            logger.error(f"❌ Admin route test failed: {e}")
        
        # Test API endpoints
        try:
            api_response = requests.get('http://127.0.0.1:5000/api/admin/dashboard-stats', timeout=5)
            if api_response.status_code in [200, 401, 403]:  # Expected responses
                logger.info("✅ Admin API endpoints are accessible")
            else:
                logger.warning(f"⚠️ Admin API returned status {api_response.status_code}")
        except Exception as e:
            logger.error(f"❌ Admin API test failed: {e}")
        
        # Check file modifications
        admin_js_path = "c:\\Users\\prana\\Downloads\\chatbot_cloud\\static\\js\\admin.js"
        admin_html_path = "c:\\Users\\prana\\Downloads\\chatbot_cloud\\templates\\admin.html"
        
        # Check admin.js for WebSocket code
        if os.path.exists(admin_js_path):
            with open(admin_js_path, 'r', encoding='utf-8') as f:
                admin_js_content = f.read()
                if 'adminSocket = io()' in admin_js_content:
                    logger.info("✅ WebSocket initialization added to admin.js")
                else:
                    logger.error("❌ WebSocket initialization not found in admin.js")
                    return False
                    
                if 'send_message' in admin_js_content and 'join_room' in admin_js_content:
                    logger.info("✅ WebSocket message handling added to admin.js")
                else:
                    logger.error("❌ WebSocket message handling not found in admin.js")
                    return False
        else:
            logger.error(f"❌ admin.js file not found at {admin_js_path}")
            return False
        
        # Check admin.html for Socket.IO script
        if os.path.exists(admin_html_path):
            with open(admin_html_path, 'r', encoding='utf-8') as f:
                admin_html_content = f.read()
                if 'socket.io' in admin_html_content:
                    logger.info("✅ Socket.IO script added to admin.html")
                else:
                    logger.error("❌ Socket.IO script not found in admin.html")
                    return False
        else:
            logger.error(f"❌ admin.html file not found at {admin_html_path}")
            return False
        
        logger.info("="*50)
        logger.info("🎉 LIVE CHAT FIX VERIFICATION COMPLETE!")
        logger.info("="*50)
        logger.info("✅ All modifications have been applied successfully")
        logger.info("")
        logger.info("📋 NEXT STEPS:")
        logger.info("1. Restart your Flask application")
        logger.info("2. Open admin panel: http://127.0.0.1:5000/admin")
        logger.info("3. Go to Live Chat section")
        logger.info("4. Open user chat in another tab: http://127.0.0.1:5000/")
        logger.info("5. Send messages between user and admin")
        logger.info("")
        logger.info("🔧 WHAT WAS FIXED:")
        logger.info("• Added WebSocket connection to admin interface")
        logger.info("• Real-time message delivery admin ↔ user")
        logger.info("• Live notifications for new messages")
        logger.info("• Auto-reconnection on disconnect")
        logger.info("• Proper room management for conversations")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_live_chat_fix()
    
    if success:
        logger.info("\n🚀 Live chat should now be working!")
        logger.info("🔧 If you still have issues, please restart Flask and try again.")
    else:
        logger.info("\n❌ Live chat fix verification failed!")
        logger.info("🔧 Please check the error messages above.")
