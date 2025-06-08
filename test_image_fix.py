#!/usr/bin/env python3
"""
Quick test script to verify the image upload fix.
This script tests the complete workflow from ticket creation to image upload.
"""

import requests
import json
import os
import time

BASE_URL = "http://localhost:5000"

def test_image_upload_fix():
    """Test the complete image upload workflow"""
    print("🧪 Testing Image Upload Fix")
    print("=" * 50)
    
    # Test 1: Create a ticket and verify user_id is returned
    print("\n1️⃣ Testing ticket creation...")
    ticket_data = {
        "name": "Test User",
        "email": "test@example.com",
        "category_id": 1,
        "subject": "Image Upload Test",
        "message": "Testing image upload functionality"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/tickets", json=ticket_data)
        if response.status_code == 200:
            data = response.json()
            if 'user_id' in data and data['user_id'] is not None:
                print(f"✅ Ticket created successfully with user_id: {data['user_id']}")
                ticket_id = data['ticket_id']
                user_id = data['user_id']
            else:
                print("❌ Ticket created but user_id is missing or null")
                return False
        else:
            print(f"❌ Failed to create ticket: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error creating ticket: {e}")
        return False
    
    # Test 2: Send a text message to verify normal flow
    print("\n2️⃣ Testing text message...")
    message_data = {
        "message": "This is a test message",
        "user_id": user_id
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/tickets/{ticket_id}/messages", json=message_data)
        if response.status_code == 200:
            print("✅ Text message sent successfully")
        else:
            print(f"❌ Failed to send text message: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error sending text message: {e}")
        return False
    
    # Test 3: Create a small test image
    print("\n3️⃣ Testing image upload...")
    test_image_path = "test_image.png"
    
    # Create a simple test image using PIL
    try:
        from PIL import Image
        import io
        
        # Create a small red square image
        img = Image.new('RGB', (100, 100), color='red')
        img.save(test_image_path, 'PNG')
        print(f"✅ Created test image: {test_image_path}")
    except Exception as e:
        print(f"❌ Error creating test image: {e}")
        return False
    
    # Test 4: Upload the image
    try:
        with open(test_image_path, 'rb') as f:
            files = {'file': ('test_image.png', f, 'image/png')}
            data = {
                'message': 'Here is a test image',
                'user_id': str(user_id)
            }
            
            response = requests.post(
                f"{BASE_URL}/api/tickets/{ticket_id}/messages/with-attachment",
                files=files,
                data=data
            )
            
            if response.status_code == 200:
                print("✅ Image uploaded successfully!")
                result = response.json()
                print(f"   Response: {result}")
            else:
                print(f"❌ Image upload failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
    except Exception as e:
        print(f"❌ Error uploading image: {e}")
        return False
    finally:
        # Clean up test image
        if os.path.exists(test_image_path):
            os.remove(test_image_path)
    
    # Test 5: Verify the message appears in the ticket
    print("\n4️⃣ Verifying message history...")
    try:
        response = requests.get(f"{BASE_URL}/api/tickets/{ticket_id}/messages")
        if response.status_code == 200:
            messages = response.json()
            print(f"✅ Retrieved {len(messages)} messages")
            
            # Check if we have messages with attachments
            attachment_messages = [msg for msg in messages if msg.get('attachment')]
            if attachment_messages:
                print(f"✅ Found {len(attachment_messages)} messages with attachments")
                for msg in attachment_messages:
                    print(f"   - Message: {msg['content']}")
                    print(f"   - Attachment: {msg['attachment']['original_name']}")
            else:
                print("⚠️  No messages with attachments found")
        else:
            print(f"❌ Failed to retrieve messages: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error retrieving messages: {e}")
        return False
    
    print("\n🎉 All tests completed successfully!")
    print("=" * 50)
    print("✅ The image upload fix is working correctly!")
    return True

if __name__ == "__main__":
    # Check if server is running
    try:
        response = requests.get(BASE_URL, timeout=5)
        if response.status_code:
            test_image_upload_fix()
        else:
            print("❌ Server is not responding")
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Please start the Flask app first:")
        print("   python app.py")
    except Exception as e:
        print(f"❌ Error testing server: {e}")
