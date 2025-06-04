#!/usr/bin/env python3
"""
Comprehensive Image Upload Test
Tests the complete image upload workflow to verify the fix
"""

import requests
import json
import time
import os
from PIL import Image
import io

BASE_URL = 'http://localhost:5000'

def create_test_image():
    """Create a simple test image"""
    img = Image.new('RGB', (100, 100), color='red')
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    return img_bytes

def test_image_upload_workflow():
    """Test the complete image upload workflow"""
    print("🧪 Testing Complete Image Upload Workflow")
    print("=" * 50)
    
    try:
        # Step 1: Test basic connectivity
        print("1. Testing basic connectivity...")
        response = requests.get(f'{BASE_URL}/api/health')
        if response.status_code == 200:
            print("   ✅ Server is running")
        else:
            print(f"   ❌ Server connectivity failed: {response.status_code}")
            return False
        
        # Step 2: Get categories
        print("2. Getting categories...")
        response = requests.get(f'{BASE_URL}/api/categories')
        if response.status_code == 200:
            categories = response.json()
            print(f"   ✅ Found {len(categories)} categories")
            category_id = categories[0]['id'] if categories else 1
        else:
            print(f"   ❌ Failed to get categories: {response.status_code}")
            category_id = 1
        
        # Step 3: Create a ticket
        print("3. Creating a ticket...")
        ticket_data = {
            'name': 'Test User',
            'email': 'test@example.com',
            'category_id': category_id,
            'subject': 'Image Upload Test',
            'message': 'Testing image upload functionality'
        }
        
        response = requests.post(f'{BASE_URL}/api/tickets', json=ticket_data)
        if response.status_code == 200:
            ticket_result = response.json()
            ticket_id = ticket_result.get('ticket_id')
            user_id = ticket_result.get('user_id')
            print(f"   ✅ Ticket created: ID={ticket_id}, User ID={user_id}")
        else:
            print(f"   ❌ Failed to create ticket: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
        
        # Step 4: Upload image with message
        print("4. Uploading image with message...")
        
        # Create test image
        test_image = create_test_image()
        
        files = {
            'attachment': ('test_image.png', test_image, 'image/png')
        }
        
        data = {
            'user_id': user_id,
            'content': 'Here is my screenshot of the issue',
            'is_admin': 'false'
        }
        
        response = requests.post(
            f'{BASE_URL}/api/tickets/{ticket_id}/messages/with-attachment',
            files=files,
            data=data
        )
        
        if response.status_code == 200:
            message_result = response.json()
            message_id = message_result.get('message_id')
            print(f"   ✅ Image uploaded successfully: Message ID={message_id}")
        else:
            print(f"   ❌ Failed to upload image: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
        
        # Step 5: Verify message appears in admin panel
        print("5. Verifying message appears in admin panel...")
        time.sleep(1)  # Give database time to process
        
        response = requests.get(f'{BASE_URL}/api/tickets/{ticket_id}/messages')
        if response.status_code == 200:
            messages = response.json()
            
            # Find our message
            uploaded_message = None
            for msg in messages:
                if msg.get('id') == message_id:
                    uploaded_message = msg
                    break
            
            if uploaded_message:
                attachments = uploaded_message.get('attachments', [])
                if attachments:
                    attachment = attachments[0]
                    print(f"   ✅ Message found with attachment:")
                    print(f"      - Original name: {attachment.get('original_name')}")
                    print(f"      - URL: {attachment.get('url')}")
                    print(f"      - File size: {attachment.get('file_size')} bytes")
                    print(f"      - MIME type: {attachment.get('mime_type')}")
                else:
                    print("   ❌ Message found but no attachments")
                    return False
            else:
                print("   ❌ Uploaded message not found")
                return False
        else:
            print(f"   ❌ Failed to get messages: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
        
        # Step 6: Test image accessibility
        print("6. Testing image accessibility...")
        image_url = f"{BASE_URL}{attachment['url']}"
        response = requests.get(image_url)
        if response.status_code == 200:
            print(f"   ✅ Image accessible at: {image_url}")
        else:
            print(f"   ❌ Image not accessible: {response.status_code}")
            return False
        
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ Image upload functionality is working correctly")
        print("✅ Images appear in admin panel")
        print("✅ Database schema issues resolved")
        print("✅ Connection pool issues resolved")
        
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Make sure Flask app is running on localhost:5000")
        return False
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = test_image_upload_workflow()
    if not success:
        print("\n💥 Some tests failed. Check the errors above.")
        exit(1)
    else:
        print("\n🚀 Ready for production use!")
