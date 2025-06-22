#!/usr/bin/env python3
"""
Live Chat Debug Test - Comprehensive WebSocket and Socket.IO Testing
This script will test the live chat functionality between user and admin
"""

import requests
import time
import json
import threading
from datetime import datetime
import socketio

# Test configuration
BASE_URL = "http://localhost:5000"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

# Global variables
test_results = []
user_messages = []
admin_messages = []

def log_result(test_name, success, message=""):
    """Log test results"""
    result = {
        'test': test_name,
        'success': success,
        'message': message,
        'timestamp': datetime.now().isoformat()
    }
    test_results.append(result)
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"{status} {test_name}: {message}")

def test_api_endpoints():
    """Test basic API endpoints"""
    print("\n=== Testing API Endpoints ===")
    
    try:
        # Test dashboard stats
        response = requests.get(f"{BASE_URL}/api/admin/dashboard-stats")
        log_result("Dashboard Stats API", response.status_code == 200, f"Status: {response.status_code}")
        
        # Test tickets endpoint
        response = requests.get(f"{BASE_URL}/api/admin/tickets")
        log_result("Tickets API", response.status_code == 200, f"Status: {response.status_code}")
        
        # Test categories endpoint
        response = requests.get(f"{BASE_URL}/categories")
        log_result("Categories API", response.status_code == 200, f"Status: {response.status_code}")
        
    except Exception as e:
        log_result("API Endpoints", False, f"Error: {str(e)}")

def create_test_ticket():
    """Create a test ticket for live chat testing"""
    print("\n=== Creating Test Ticket ===")
    
    try:
        ticket_data = {
            'name': 'Live Chat Test User',
            'email': 'testuser@example.com',
            'category': 'Technical Support',
            'subject': 'Live Chat Test Ticket',
            'description': 'This is a test ticket for live chat functionality'
        }
        
        response = requests.post(f"{BASE_URL}/submit-ticket", json=ticket_data)
        
        if response.status_code == 200:
            data = response.json()
            ticket_id = data.get('ticket_id')
            log_result("Create Test Ticket", True, f"Ticket ID: {ticket_id}")
            return ticket_id
        else:
            log_result("Create Test Ticket", False, f"Status: {response.status_code}")
            return None
            
    except Exception as e:
        log_result("Create Test Ticket", False, f"Error: {str(e)}")
        return None

def test_socket_connection():
    """Test Socket.IO connection"""
    print("\n=== Testing Socket.IO Connection ===")
    
    try:
        # Create user socket connection
        user_sio = socketio.Client()
        
        # Connection event handlers
        @user_sio.event
        def connect():
            log_result("User Socket Connection", True, "Connected successfully")
        
        @user_sio.event
        def disconnect():
            print("User socket disconnected")
        
        @user_sio.event
        def connect_error(data):
            log_result("User Socket Connection", False, f"Connection error: {data}")
        
        # Connect to server
        user_sio.connect(BASE_URL)
        time.sleep(2)  # Give it time to connect
        
        # Test if connected
        if user_sio.connected:
            log_result("User Socket Status", True, "Socket.IO connection established")
        else:
            log_result("User Socket Status", False, "Socket.IO connection failed")
        
        user_sio.disconnect()
        return True
        
    except Exception as e:
        log_result("Socket.IO Connection", False, f"Error: {str(e)}")
        return False

def test_room_join_leave(ticket_id):
    """Test joining and leaving rooms"""
    print(f"\n=== Testing Room Management for Ticket {ticket_id} ===")
    
    try:
        user_sio = socketio.Client()
        room_joined = False
        
        @user_sio.event
        def connect():
            print("User connected for room test")
        
        @user_sio.event
        def room_joined(data):
            nonlocal room_joined
            room_joined = True
            log_result("Room Join", True, f"Joined room for ticket {data.get('ticket_id')}")
        
        user_sio.connect(BASE_URL)
        time.sleep(1)
        
        # Join room
        user_sio.emit('join_room', {'ticket_id': ticket_id})
        time.sleep(2)
        
        if room_joined:
            log_result("Room Management", True, "Successfully joined room")
        else:
            log_result("Room Management", False, "Failed to join room")
        
        # Leave room
        user_sio.emit('leave_room', {'ticket_id': ticket_id})
        time.sleep(1)
        
        user_sio.disconnect()
        return room_joined
        
    except Exception as e:
        log_result("Room Management", False, f"Error: {str(e)}")
        return False

def test_message_exchange(ticket_id):
    """Test bidirectional message exchange"""
    print(f"\n=== Testing Message Exchange for Ticket {ticket_id} ===")
    
    try:
        user_sio = socketio.Client()
        admin_sio = socketio.Client()
        
        user_received_admin_message = False
        admin_received_user_message = False
        
        # User socket events
        @user_sio.event
        def connect():
            print("User connected for message test")
            user_sio.emit('join_room', {'ticket_id': ticket_id})
        
        @user_sio.event
        def new_message(data):
            nonlocal user_received_admin_message
            print(f"User received message: {data}")
            if data.get('is_admin'):
                user_received_admin_message = True
                log_result("User Receives Admin Message", True, "User received admin message")
        
        # Admin socket events
        @admin_sio.event
        def connect():
            print("Admin connected for message test")
            admin_sio.emit('join_room', {'ticket_id': ticket_id})
        
        @admin_sio.event
        def new_message(data):
            nonlocal admin_received_user_message
            print(f"Admin received message: {data}")
            if not data.get('is_admin'):
                admin_received_user_message = True
                log_result("Admin Receives User Message", True, "Admin received user message")
        
        # Connect both sockets
        user_sio.connect(BASE_URL)
        admin_sio.connect(BASE_URL)
        time.sleep(2)
        
        # Send user message
        user_message = {
            'ticket_id': ticket_id,
            'content': 'Hello from user - this is a test message',
            'is_admin': False
        }
        user_sio.emit('send_message', user_message)
        time.sleep(2)
        
        # Send admin message
        admin_message = {
            'ticket_id': ticket_id,
            'content': 'Hello from admin - this is a test reply',
            'is_admin': True
        }
        admin_sio.emit('send_message', admin_message)
        time.sleep(2)
        
        # Check results
        if admin_received_user_message:
            log_result("Bidirectional Messaging", True, "Admin received user message")
        else:
            log_result("Bidirectional Messaging", False, "Admin did not receive user message")
        
        if user_received_admin_message:
            log_result("Bidirectional Messaging", True, "User received admin message")
        else:
            log_result("Bidirectional Messaging", False, "User did not receive admin message")
        
        # Cleanup
        user_sio.disconnect()
        admin_sio.disconnect()
        
        return admin_received_user_message and user_received_admin_message
        
    except Exception as e:
        log_result("Message Exchange", False, f"Error: {str(e)}")
        return False

def test_message_persistence(ticket_id):
    """Test if messages are properly saved to database"""
    print(f"\n=== Testing Message Persistence for Ticket {ticket_id} ===")
    
    try:
        # Get messages via API
        response = requests.get(f"{BASE_URL}/api/admin/tickets/{ticket_id}/messages")
        
        if response.status_code == 200:
            messages = response.json()
            message_count = len(messages)
            log_result("Message Persistence", message_count > 0, f"Found {message_count} messages")
            
            # Check if we have both user and admin messages
            user_messages = [msg for msg in messages if not msg.get('is_admin')]
            admin_messages = [msg for msg in messages if msg.get('is_admin')]
            
            log_result("User Messages Saved", len(user_messages) > 0, f"Found {len(user_messages)} user messages")
            log_result("Admin Messages Saved", len(admin_messages) > 0, f"Found {len(admin_messages)} admin messages")
            
            return message_count > 0
        else:
            log_result("Message Persistence", False, f"API error: {response.status_code}")
            return False
            
    except Exception as e:
        log_result("Message Persistence", False, f"Error: {str(e)}")
        return False

def run_comprehensive_test():
    """Run all live chat tests"""
    print("🚀 Starting Comprehensive Live Chat Test")
    print("=" * 50)
    
    # Test 1: Basic API endpoints
    test_api_endpoints()
    
    # Test 2: Socket.IO connection
    socket_works = test_socket_connection()
    
    if not socket_works:
        print("❌ Socket.IO connection failed - skipping further tests")
        return
    
    # Test 3: Create test ticket
    ticket_id = create_test_ticket()
    
    if not ticket_id:
        print("❌ Failed to create test ticket - skipping further tests")
        return
    
    # Test 4: Room management
    room_works = test_room_join_leave(ticket_id)
    
    # Test 5: Message exchange
    message_works = test_message_exchange(ticket_id)
    
    # Test 6: Message persistence
    persistence_works = test_message_persistence(ticket_id)
    
    # Summary
    print("\n" + "=" * 50)
    print("🏁 TEST SUMMARY")
    print("=" * 50)
    
    passed = sum(1 for result in test_results if result['success'])
    total = len(test_results)
    
    print(f"Total Tests: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {total - passed}")
    print(f"Success Rate: {(passed/total)*100:.1f}%")
    
    print("\nDetailed Results:")
    for result in test_results:
        status = "✅" if result['success'] else "❌"
        print(f"{status} {result['test']}: {result['message']}")
    
    # Save results to file
    with open('live_chat_test_results.json', 'w') as f:
        json.dump(test_results, f, indent=2)
    
    print(f"\n📊 Results saved to live_chat_test_results.json")
    print(f"🎯 Test ticket ID: {ticket_id}")

if __name__ == "__main__":
    try:
        run_comprehensive_test()
    except KeyboardInterrupt:
        print("\n⏹️ Test interrupted by user")
    except Exception as e:
        print(f"\n💥 Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
