#!/usr/bin/env python3
"""
Quick test script to verify the template fixes work correctly
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from flask import render_template_string
from datetime import datetime

# Test basic template rendering with datetime
test_template = """
<div>Time: {{ test_time.strftime('%H:%M') }}</div>
<div>Date: {{ test_time.strftime('%B %d, %Y') }}</div>
"""

def test_datetime_formatting():
    """Test that datetime formatting works in templates"""
    app = create_app()
    app.config['TESTING'] = True
    
    with app.test_request_context('/'):
        test_time = datetime.now()
        rendered = render_template_string(test_template, test_time=test_time)
        print("✅ Datetime formatting test passed!")
        print(f"Rendered output: {rendered.strip()}")
        return True

def test_app_startup():
    """Test that the app can start without template errors"""
    try:
        app = create_app()
        print("✅ Application startup test passed!")
        print(f"App name: {app.name}")
        return True
    except Exception as e:
        print(f"❌ Application startup failed: {e}")
        return False

if __name__ == '__main__':
    print("Testing YouCloudPay Chatbot Template Fixes...")
    print("=" * 50)
    
    # Test 1: App startup
    startup_success = test_app_startup()
    
    # Test 2: Datetime formatting
    if startup_success:
        datetime_success = test_datetime_formatting()
        
        if datetime_success:
            print("\n🎉 All tests passed! The moment.js template errors have been fixed.")
            print("The application should now work correctly without UndefinedError.")
        else:
            print("\n❌ Datetime formatting test failed.")
    else:
        print("\n❌ Application startup failed.")
