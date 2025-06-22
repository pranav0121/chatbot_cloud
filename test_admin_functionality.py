#!/usr/bin/env python3
"""
Comprehensive admin panel functionality test
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, socketio, db, User, Ticket, Message, Category
from flask import session
from datetime import datetime
import json

def test_admin_endpoints():
    """Test all admin panel endpoints"""
    with app.test_client() as client:
        with app.app_context():
            print("🧪 Testing Admin Panel Functionality")
            print("=" * 50)
            
            # Test admin login page
            print("1. Testing admin login page...")
            response = client.get('/auth/admin_login')
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                print("   ✅ Admin login page loads")
            else:
                print("   ❌ Admin login page failed")
            
            # Test admin login
            print("\n2. Testing admin login...")
            login_data = {
                'email': 'admin@chatbot.com',
                'password': 'admin123'
            }
            response = client.post('/auth/admin_login', data=login_data, follow_redirects=True)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                print("   ✅ Admin login successful")
                
                # Test admin dashboard
                print("\n3. Testing admin dashboard...")
                response = client.get('/admin')
                print(f"   Status: {response.status_code}")
                if response.status_code == 200:
                    print("   ✅ Admin dashboard loads")
                else:
                    print("   ❌ Admin dashboard failed")
                
                # Test dashboard stats API
                print("\n4. Testing dashboard stats API...")
                response = client.get('/api/admin/dashboard-stats')
                print(f"   Status: {response.status_code}")
                if response.status_code == 200:
                    data = response.get_json()
                    print(f"   ✅ Dashboard stats: {data}")
                else:
                    print("   ❌ Dashboard stats API failed")
                
                # Test tickets API
                print("\n5. Testing tickets API...")
                response = client.get('/api/admin/tickets')
                print(f"   Status: {response.status_code}")
                if response.status_code == 200:
                    tickets = response.get_json()
                    print(f"   ✅ Found {len(tickets)} tickets")
                    if tickets:
                        print(f"   Sample ticket: {tickets[0]['subject']}")
                else:
                    print("   ❌ Tickets API failed")
                
                # Test active conversations API
                print("\n6. Testing active conversations API...")
                response = client.get('/api/admin/active-conversations')
                print(f"   Status: {response.status_code}")
                if response.status_code == 200:
                    conversations = response.get_json()
                    print(f"   ✅ Found {len(conversations)} active conversations")
                else:
                    print("   ❌ Active conversations API failed")
                
                # Test categories API
                print("\n7. Testing categories API...")
                response = client.get('/api/categories')
                print(f"   Status: {response.status_code}")
                if response.status_code == 200:
                    categories = response.get_json()
                    print(f"   ✅ Found {len(categories)} categories")
                else:
                    print("   ❌ Categories API failed")
                
            else:
                print("   ❌ Admin login failed")
            
            # Test database content
            print("\n8. Testing database content...")
            total_users = User.query.count()
            total_tickets = Ticket.query.count()
            total_messages = Message.query.count()
            total_categories = Category.query.count()
            
            print(f"   Users: {total_users}")
            print(f"   Tickets: {total_tickets}")
            print(f"   Messages: {total_messages}")
            print(f"   Categories: {total_categories}")
            
            if total_tickets > 0:
                print("   ✅ Database has content")
                
                # Show ticket statuses
                from sqlalchemy import func
                statuses = db.session.query(Ticket.Status, func.count(Ticket.TicketID)).group_by(Ticket.Status).all()
                print("   Ticket statuses:")
                for status, count in statuses:
                    print(f"     {status}: {count}")
            else:
                print("   ⚠️  No tickets in database")
            
            print("\n" + "=" * 50)
            print("🎯 Test Summary:")
            print("   - Admin panel should be accessible at: http://127.0.0.1:5000/auth/admin_login")
            print("   - Login: admin@chatbot.com / admin123")
            print("   - Dashboard should show ticket statistics")
            print("   - Live chat should work in the Live Chat section")
            print("   - File sharing should work with the paperclip button")

def test_socket_functionality():
    """Test WebSocket functionality"""
    print("\n🔌 Testing WebSocket Setup...")
    
    # Check if socketio is properly configured
    if socketio:
        print("   ✅ SocketIO initialized")
        print(f"   Async mode: {socketio.async_mode}")
        print("   ✅ WebSocket ready for live chat")
    else:
        print("   ❌ SocketIO not initialized")

if __name__ == "__main__":
    test_admin_endpoints()
    test_socket_functionality()
