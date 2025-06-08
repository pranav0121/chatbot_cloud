#!/usr/bin/env python3
"""
Comprehensive test script to verify the image upload fix works end-to-end.
This script tests the complete workflow from ticket creation to image upload.
"""

import requests
import json
import io
import time
from PIL import Image
import os

# Configuration
BASE_URL = "http://localhost:5000"

def create_test_image():
    """Create a small test image for uploading"""
    # Create a simple 100x100 red square image
    img = Image.new('RGB', (100, 100), color='red')
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    return img_bytes

def test_complete_workflow():
    """Test the complete image upload workflow"""
    print("🚀 Testing complete image upload workflow...")
    print()
    
    # Step 1: Create a ticket
    print("Step 1: Creating a ticket...")
    ticket_data = {
        "name": "Test User",
        "email": "test@example.com", 
        "category_id": 1,
        "subject": "Image Upload Test",
        "message": "Testing the image upload functionality"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/tickets", json=ticket_data)
        if response.status_code != 200:
            print(f"❌ Failed to create ticket: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
        ticket_result = response.json()
        ticket_id = ticket_result.get('ticket_id')
        user_id = ticket_result.get('user_id')
        
        print(f"✅ Ticket created successfully")
        print(f"   Ticket ID: {ticket_id}")
        print(f"   User ID: {user_id}")
        
        if not user_id:
            print("❌ User ID is missing from ticket creation response!")
            return False
            
    except Exception as e:
        print(f"❌ Error creating ticket: {e}")
        return False
    
    print()
    
    # Step 2: Send a text message first
    print("Step 2: Sending a text message...")
    message_data = {
        "content": "This is a test message before uploading an image",
        "user_id": user_id
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/tickets/{ticket_id}/messages",
            json=message_data
        )
        
        if response.status_code == 200:
            print("✅ Text message sent successfully")
        else:
            print(f"❌ Failed to send text message: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error sending text message: {e}")
        return False
    
    print()
    
    # Step 3: Upload an image
    print("Step 3: Uploading an image...")
    
    try:
        test_image = create_test_image()
        files = {'file': ('test_image.png', test_image, 'image/png')}
        data = {
            'content': 'Here is a test image attachment',
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
            message_id = result.get('message_id')
            print("✅ Image uploaded successfully")
            print(f"   Message ID: {message_id}")
        else:
            print(f"❌ Failed to upload image: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error uploading image: {e}")
        return False
    
    print()
    
    # Step 4: Verify the message appears in admin view
    print("Step 4: Verifying admin can see the image...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/admin/tickets/{ticket_id}")
        
        if response.status_code == 200:
            admin_data = response.json()
            messages = admin_data.get('messages', [])
            
            # Look for messages with attachments
            image_messages = [msg for msg in messages if msg.get('attachments') and len(msg['attachments']) > 0]
            
            if image_messages:
                print("✅ Admin can see messages with attachments")
                print(f"   Found {len(image_messages)} messages with attachments")
                
                # Check attachment details
                for msg in image_messages:
                    for att in msg['attachments']:
                        print(f"   📎 Attachment: {att.get('original_name')}")
                        print(f"      URL: {att.get('url')}")
                        print(f"      Size: {att.get('file_size')} bytes")
            else:
                print("❌ No messages with attachments found in admin view")
                return False
                
        else:
            print(f"❌ Failed to get admin ticket view: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error checking admin view: {e}")
        return False
    
    print()
    
    # Step 5: Test that we can retrieve messages normally
    print("Step 5: Verifying regular message retrieval...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/tickets/{ticket_id}/messages")
        
        if response.status_code == 200:
            messages = response.json()
            print(f"✅ Retrieved {len(messages)} messages successfully")
            
            # Check if any have attachments in the standard view
            for msg in messages:
                if hasattr(msg, 'attachments') or 'attachment' in str(msg):
                    print("   📎 Found message with attachment reference")
        else:
            print(f"❌ Failed to retrieve messages: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error retrieving messages: {e}")
        return False
    
    print()
    print("🎉 Complete workflow test passed!")
    print(f"   Test Ticket ID: {ticket_id}")
    print(f"   Test User ID: {user_id}")
    
    return True

def check_server():
    """Check if server is running"""
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        return response.status_code == 200
    except:
        return False

def main():
    """Main test function"""
    print("🔧 Image Upload Fix - End-to-End Test")
    print("=" * 50)
    print()
    
    # Check server
    if not check_server():
        print("❌ Server is not running!")
        print("Please start the server first: python app.py")
        return False
    
    print("✅ Server is running")
    print()
    
    # Run the complete workflow test
    success = test_complete_workflow()
    
    print()
    print("=" * 50)
    
    if success:
        print("🎉 SUCCESS: Image upload fix is working correctly!")
        print()
        print("What was fixed:")
        print("• Backend now returns user_id when creating tickets")
        print("• Frontend stores user_id in currentUser object")
        print("• Image uploads now include valid user_id")
        print("• Images appear correctly in admin panel")
    else:
        print("❌ FAILURE: Image upload fix needs more work")
    
    return success

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
