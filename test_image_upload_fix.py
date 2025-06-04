#!/usr/bin/env python3
"""
Test script to verify the image upload fix.
This script will test the ticket creation and message sending workflow.
"""

import requests
import json
import os
import sys
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:5000"
TEST_IMAGE_PATH = "static/uploads/test_image.png"  # We'll create a dummy file

def log(message):
    """Log with timestamp"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {message}")

def test_ticket_creation():
    """Test ticket creation and verify user_id is returned"""
    log("🎫 Testing ticket creation...")
    
    ticket_data = {
        "name": "Test User",
        "email": "test@example.com",
        "category_id": 1,
        "subject": "Image Upload Test",
        "message": "Testing the image upload functionality"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/tickets", json=ticket_data)
        
        if response.status_code == 200:
            data = response.json()
            log(f"✅ Ticket created successfully")
            log(f"   Ticket ID: {data.get('ticket_id')}")
            log(f"   User ID: {data.get('user_id')}")
            log(f"   Status: {data.get('status')}")
            
            if data.get('user_id'):
                log("✅ User ID is now included in ticket creation response!")
                return data['ticket_id'], data['user_id']
            else:
                log("❌ User ID is missing from response")
                return None, None
        else:
            log(f"❌ Failed to create ticket: {response.status_code}")
            log(f"   Response: {response.text}")
            return None, None
            
    except Exception as e:
        log(f"❌ Error creating ticket: {e}")
        return None, None

def test_message_with_user_id(ticket_id, user_id):
    """Test sending a message with the user_id"""
    log("💬 Testing message sending with user_id...")
    
    message_data = {
        "content": "This is a test message to verify user_id is working",
        "user_id": user_id
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/tickets/{ticket_id}/messages",
            json=message_data
        )
        
        if response.status_code == 200:
            data = response.json()
            log(f"✅ Message sent successfully")
            log(f"   Status: {data.get('status')}")
            return True
        else:
            log(f"❌ Failed to send message: {response.status_code}")
            log(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        log(f"❌ Error sending message: {e}")
        return False

def test_image_upload_endpoint(ticket_id, user_id):
    """Test the image upload endpoint specifically"""
    log("🖼️ Testing image upload endpoint...")
    
    # Create a dummy image file for testing
    dummy_image_content = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\tpHYs\x00\x00\x0b\x13\x00\x00\x0b\x13\x01\x00\x9a\x9c\x18\x00\x00\x00\nIDATx\x9cc\xf8\x00\x00\x00\x01\x00\x01\x7f\x18\xddD\x00\x00\x00\x00IEND\xaeB`\x82'
    
    try:
        files = {'file': ('test.png', dummy_image_content, 'image/png')}
        data = {
            'content': 'Test image upload',
            'user_id': str(user_id),
            'is_admin': 'false'
        }
        
        response = requests.post(
            f"{BASE_URL}/api/tickets/{ticket_id}/messages/with-attachment",
            files=files,
            data=data
        )
        
        if response.status_code == 200:
            result = response.json()
            log(f"✅ Image upload successful")
            log(f"   Status: {result.get('status')}")
            return True
        else:
            log(f"❌ Image upload failed: {response.status_code}")
            log(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        log(f"❌ Error uploading image: {e}")
        return False

def check_server_status():
    """Check if the server is running"""
    log("🔍 Checking server status...")
    
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        if response.status_code == 200:
            log("✅ Server is running")
            return True
        else:
            log(f"❌ Server returned status: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        log("❌ Server is not running")
        return False
    except Exception as e:
        log(f"❌ Error checking server: {e}")
        return False

def main():
    """Main test function"""
    log("🚀 Starting image upload fix verification...")
    
    # Check if server is running
    if not check_server_status():
        log("❌ Please start the Flask server first: python app.py")
        return False
    
    # Test ticket creation
    ticket_id, user_id = test_ticket_creation()
    if not ticket_id or not user_id:
        log("❌ Ticket creation failed - cannot proceed with further tests")
        return False
    
    # Test message sending
    message_success = test_message_with_user_id(ticket_id, user_id)
    if not message_success:
        log("❌ Message sending failed")
        return False
    
    # Test image upload
    upload_success = test_image_upload_endpoint(ticket_id, user_id)
    if not upload_success:
        log("❌ Image upload failed")
        return False
    
    log("🎉 All tests passed! Image upload fix appears to be working correctly!")
    log(f"   Test ticket ID: {ticket_id}")
    log(f"   Test user ID: {user_id}")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
