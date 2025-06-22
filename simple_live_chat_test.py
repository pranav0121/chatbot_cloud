#!/usr/bin/env python3
"""
Simple Live Chat Test - Quick WebSocket Testing
"""

import requests
import time
import json

BASE_URL = "http://localhost:5000"

def test_basic_connectivity():
    """Test basic server connectivity"""
    print("=== Testing Basic Connectivity ===")
    
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        print(f"✅ Server responded with status: {response.status_code}")
        return True
    except Exception as e:
        print(f"❌ Server not responding: {e}")
        return False

def test_api_endpoints():
    """Test API endpoints"""
    print("\n=== Testing API Endpoints ===")
    
    endpoints = [
        "/api/admin/dashboard-stats",
        "/api/admin/tickets",
        "/categories"
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{BASE_URL}{endpoint}", timeout=5)
            status = "✅ PASS" if response.status_code == 200 else "❌ FAIL"
            print(f"{status} {endpoint}: Status {response.status_code}")
        except Exception as e:
            print(f"❌ FAIL {endpoint}: {e}")

def create_test_ticket():
    """Create a test ticket"""
    print("\n=== Creating Test Ticket ===")
    
    ticket_data = {
        'name': 'Live Chat Test User',
        'email': 'testuser@example.com',
        'category': 'Technical Support',
        'subject': 'Live Chat Test Ticket',
        'description': 'This is a test ticket for live chat functionality'
    }
    
    try:
        response = requests.post(f"{BASE_URL}/submit-ticket", json=ticket_data, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            ticket_id = data.get('ticket_id')
            print(f"✅ Test ticket created with ID: {ticket_id}")
            return ticket_id
        else:
            print(f"❌ Failed to create ticket. Status: {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error creating ticket: {e}")
        return None

def test_socket_io_endpoint():
    """Test if Socket.IO endpoint is available"""
    print("\n=== Testing Socket.IO Endpoint ===")
    
    try:
        # Test Socket.IO endpoint
        response = requests.get(f"{BASE_URL}/socket.io/", timeout=5)
        print(f"Socket.IO endpoint status: {response.status_code}")
        
        if response.status_code == 400:  # Expected for Socket.IO handshake
            print("✅ Socket.IO endpoint is available")
            return True
        else:
            print("❌ Socket.IO endpoint may not be working properly")
            return False
            
    except Exception as e:
        print(f"❌ Socket.IO endpoint test failed: {e}")
        return False

def test_message_api(ticket_id):
    """Test message API"""
    if not ticket_id:
        print("❌ No ticket ID provided for message API test")
        return False
        
    print(f"\n=== Testing Messages API for Ticket {ticket_id} ===")
    
    try:
        # Test getting messages
        response = requests.get(f"{BASE_URL}/api/admin/tickets/{ticket_id}/messages", timeout=5)
        print(f"Get messages API status: {response.status_code}")
        
        if response.status_code == 200:
            messages = response.json()
            print(f"✅ Found {len(messages)} messages for ticket {ticket_id}")
            return True
        else:
            print(f"❌ Failed to get messages. Status: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing messages API: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting Simple Live Chat Test")
    print("=" * 50)
    
    # Test 1: Basic connectivity
    if not test_basic_connectivity():
        print("❌ Server is not running. Please start the Flask app first.")
        return
    
    # Test 2: API endpoints
    test_api_endpoints()
    
    # Test 3: Socket.IO endpoint
    socket_available = test_socket_io_endpoint()
    
    # Test 4: Create test ticket
    ticket_id = create_test_ticket()
    
    # Test 5: Message API
    if ticket_id:
        test_message_api(ticket_id)
    
    # Summary
    print("\n" + "=" * 50)
    print("🏁 Test Summary")
    print("=" * 50)
    print(f"Server Status: {'✅ Running' if True else '❌ Down'}")
    print(f"Socket.IO: {'✅ Available' if socket_available else '❌ Not Available'}")
    print(f"Test Ticket: {'✅ Created' if ticket_id else '❌ Failed'}")
    
    if ticket_id:
        print(f"\n🎯 Test Ticket ID: {ticket_id}")
        print("📝 You can use this ticket ID to test live chat manually")
        print(f"👤 User: Go to {BASE_URL} and open ticket #{ticket_id}")
        print(f"👨‍💼 Admin: Go to {BASE_URL}/admin and view ticket #{ticket_id}")

if __name__ == "__main__":
    main()
