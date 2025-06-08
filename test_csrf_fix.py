#!/usr/bin/env python3
"""
Test script to verify the CSRF token fix for the chat interface
"""

import requests
import re
from bs4 import BeautifulSoup

def test_csrf_fix():
    """Test that the CSRF token is included in the page and used in form submission"""
    print("🧪 Testing CSRF token fix...")
    
    # Step 1: Login to the application
    session = requests.Session()
    
    # Get the login page to extract CSRF token
    login_response = session.get("http://localhost:5000/auth/login")
    if login_response.status_code != 200:
        print("❌ Failed to load login page")
        return False
    
    # Extract CSRF token from the login page
    login_soup = BeautifulSoup(login_response.text, 'html.parser')
    csrf_meta = login_soup.find('meta', {'name': 'csrf-token'})
    if not csrf_meta:
        print("❌ CSRF meta tag not found on login page")
        return False
    
    csrf_token = csrf_meta.get('content')
    if not csrf_token:
        print("❌ CSRF token content is missing")
        return False
    
    # Step 2: Verify that the conversation page has the CSRF token
    # Create a new complaint/chat
    new_chat_response = session.get("http://localhost:5000/chat/new")
    if "redirect" in new_chat_response.url:
        print("🔑 Login required. Please run the test when logged in.")
        return False
    
    # Get the complaint ID from the redirect URL
    complaint_id = re.search(r"/chat/(\d+)", new_chat_response.url)
    if not complaint_id:
        print("❌ Failed to create new chat")
        return False
    
    complaint_id = complaint_id.group(1)
    
    # Load the conversation page
    conv_response = session.get(f"http://localhost:5000/chat/{complaint_id}")
    if conv_response.status_code != 200:
        print(f"❌ Failed to load conversation page: {conv_response.status_code}")
        return False
    
    # Extract CSRF token from conversation page
    conv_soup = BeautifulSoup(conv_response.text, 'html.parser')
    csrf_meta = conv_soup.find('meta', {'name': 'csrf-token'})
    
    if not csrf_meta:
        print("❌ CSRF meta tag not found on conversation page")
        return False
    
    csrf_token = csrf_meta.get('content')
    if not csrf_token:
        print("❌ CSRF token content is missing")
        return False
    
    # Step 3: Check if the JavaScript code includes the CSRF token in the request headers
    message_script = conv_soup.find('script', text=re.compile('csrf-token'))
    if not message_script:
        print("❌ CSRF token not found in JavaScript code")
        return False
    
    if "'X-CSRFToken': csrfToken" not in message_script.text:
        print("❌ X-CSRFToken header not properly set in JavaScript code")
        return False
    
    print("✅ CSRF fix verification passed!")
    return True

if __name__ == "__main__":
    test_csrf_fix()
