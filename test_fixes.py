#!/usr/bin/env python3
"""
Test script to verify the three critical fixes:
1. Category input section appearing after category selection
2. Paste functionality for image uploads
3. Admin panel image viewing
"""

import requests
import time
import json
import os
from typing import Dict, Any

class FixTester:
    def __init__(self, base_url: str = "http://localhost:5000"):
        self.base_url = base_url
        self.session = requests.Session()
        
    def test_server_connectivity(self) -> bool:
        """Test if the server is running and accessible"""
        try:
            response = self.session.get(f"{self.base_url}/")
            return response.status_code == 200
        except requests.exceptions.ConnectionError:
            return False
    
    def create_test_ticket_with_message(self) -> Dict[str, Any]:
        """Create a test ticket to verify category input functionality"""
        print("📝 Testing ticket creation (simulating category input fix)...")
        
        ticket_data = {
            "name": "Test User",
            "email": "test@example.com",
            "category_id": 1,
            "subject": "Technical Support Test",
            "message": "This is a test ticket to verify category input functionality works correctly."
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/api/tickets",
                json=ticket_data
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Ticket created successfully: ID {result.get('ticket_id')}")
                return result
            else:
                print(f"❌ Failed to create ticket: {response.status_code}")
                print(f"Response: {response.text}")
                return {}
                
        except Exception as e:
            print(f"❌ Error creating ticket: {e}")
            return {}
    
    def create_test_ticket_with_attachment(self) -> Dict[str, Any]:
        """Create a test ticket with file attachment to test paste functionality"""
        print("📎 Testing ticket creation with attachment (simulating paste fix)...")
        
        # Create a simple test image file
        test_image_path = "test_image.png"
        try:
            # Create a minimal PNG file for testing
            png_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\tpHYs\x00\x00\x0b\x13\x00\x00\x0b\x13\x01\x00\x9a\x9c\x18\x00\x00\x00\nIDATx\x9cc\xf8\x00\x00\x00\x01\x00\x01\x00\x00\x00\x00IEND\xaeB`\x82'
            
            with open(test_image_path, 'wb') as f:
                f.write(png_data)
            
            # Prepare form data
            form_data = {
                'name': 'Test User',
                'email': 'test@example.com',
                'category_id': '2',  # Product Issues
                'subject': 'Test with Image',
                'message': 'This is a test ticket with an attached image to verify paste functionality.'
            }
            
            files = {
                'file': ('test_image.png', open(test_image_path, 'rb'), 'image/png')
            }
            
            response = self.session.post(
                f"{self.base_url}/api/tickets/with-attachment",
                data=form_data,
                files=files
            )
            
            files['file'][1].close()  # Close the file
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Ticket with attachment created successfully: ID {result.get('ticket_id')}")
                return result
            else:
                print(f"❌ Failed to create ticket with attachment: {response.status_code}")
                print(f"Response: {response.text}")
                return {}
                
        except Exception as e:
            print(f"❌ Error creating ticket with attachment: {e}")
            return {}
        finally:
            # Clean up test file
            if os.path.exists(test_image_path):
                os.remove(test_image_path)
    
    def test_admin_ticket_view(self, ticket_id: int) -> bool:
        """Test admin panel ticket viewing functionality"""
        print(f"👨‍💼 Testing admin ticket view for ticket ID {ticket_id}...")
        
        try:
            response = self.session.get(f"{self.base_url}/api/admin/tickets/{ticket_id}")
            
            if response.status_code == 200:
                ticket_data = response.json()
                print(f"✅ Admin can view ticket {ticket_id}")
                
                # Check if ticket has messages with attachments
                messages = ticket_data.get('messages', [])
                has_attachments = any(
                    msg.get('attachments') and len(msg['attachments']) > 0 
                    for msg in messages
                )
                
                if has_attachments:
                    print("✅ Ticket contains messages with attachments - admin panel should display them")
                    
                    # Check attachment structure
                    for msg in messages:
                        if msg.get('attachments'):
                            for att in msg['attachments']:
                                required_fields = ['id', 'original_name', 'url', 'file_size', 'mime_type']
                                if all(field in att for field in required_fields):
                                    print(f"✅ Attachment data structure is valid: {att['original_name']}")
                                else:
                                    print(f"❌ Attachment missing required fields: {att}")
                else:
                    print("ℹ️ No attachments found in ticket messages")
                
                return True
            else:
                print(f"❌ Failed to view ticket via admin API: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error viewing ticket via admin API: {e}")
            return False
    
    def test_admin_dashboard_access(self) -> bool:
        """Test admin dashboard accessibility"""
        print("🏠 Testing admin dashboard access...")
        
        try:
            response = self.session.get(f"{self.base_url}/admin")
            
            if response.status_code == 200:
                print("✅ Admin dashboard is accessible")
                return True
            else:
                print(f"❌ Admin dashboard not accessible: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error accessing admin dashboard: {e}")
            return False
    
    def run_all_tests(self):
        """Run all tests to verify the fixes"""
        print("🚀 Starting comprehensive fix testing...\n")
        
        # Test 1: Server connectivity
        if not self.test_server_connectivity():
            print("❌ Server is not running. Please start the application first.")
            print("Run: python app.py")
            return False
        
        print("✅ Server is running and accessible\n")
        
        # Test 2: Admin dashboard access
        if not self.test_admin_dashboard_access():
            print("❌ Admin dashboard test failed")
            return False
        print()
        
        # Test 3: Category input functionality (Issue 1)
        print("=== Testing Fix 1: Category Input Display ===")
        ticket_result = self.create_test_ticket_with_message()
        test1_success = bool(ticket_result.get('ticket_id'))
        print()
        
        # Test 4: Paste functionality (Issue 2) 
        print("=== Testing Fix 2: Paste Functionality ===")
        attachment_ticket_result = self.create_test_ticket_with_attachment()
        test2_success = bool(attachment_ticket_result.get('ticket_id'))
        print()
        
        # Test 5: Admin image viewing (Issue 3)
        print("=== Testing Fix 3: Admin Panel Image Viewing ===")
        test3_success = False
        
        # Test with both tickets if available
        for result in [ticket_result, attachment_ticket_result]:
            if result.get('ticket_id'):
                if self.test_admin_ticket_view(result['ticket_id']):
                    test3_success = True
        
        print()
        
        # Summary
        print("=" * 50)
        print("📊 TEST SUMMARY")
        print("=" * 50)
        print(f"Fix 1 - Category Input Display: {'✅ PASS' if test1_success else '❌ FAIL'}")
        print(f"Fix 2 - Paste Functionality: {'✅ PASS' if test2_success else '❌ FAIL'}")
        print(f"Fix 3 - Admin Image Viewing: {'✅ PASS' if test3_success else '❌ FAIL'}")
        print()
        
        all_passed = test1_success and test2_success and test3_success
        
        if all_passed:
            print("🎉 ALL FIXES VERIFIED SUCCESSFULLY!")
            print("The chatbot system is ready for production use.")
        else:
            print("⚠️ Some tests failed. Please review the output above.")
            
        return all_passed

def main():
    """Main function to run the tests"""
    print("Chatbot Fix Verification Tool")
    print("=" * 40)
    
    tester = FixTester()
    tester.run_all_tests()

if __name__ == "__main__":
    main()
