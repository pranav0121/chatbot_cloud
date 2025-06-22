#!/usr/bin/env python3
"""
Debug admin panel - check for issues
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def check_admin_files():
    """Check if all admin files exist and are properly configured"""
    print("🔍 Checking Admin Panel Files...")
    print("=" * 40)
    
    files_to_check = [
        ('templates/admin.html', 'Admin HTML template'),
        ('static/js/admin.js', 'Admin JavaScript'),
        ('static/css/admin.css', 'Admin CSS'),
        ('auth.py', 'Authentication module'),
        ('app.py', 'Main application')
    ]
    
    for file_path, description in files_to_check:
        full_path = os.path.join(os.getcwd(), file_path)
        if os.path.exists(full_path):
            size = os.path.getsize(full_path)
            print(f"✅ {description}: {file_path} ({size} bytes)")
        else:
            print(f"❌ {description}: {file_path} - NOT FOUND")
    
    print("\n🔍 Checking Key Functions in admin.js...")
    
    # Check admin.js for key functions
    admin_js_path = os.path.join(os.getcwd(), 'static/js/admin.js')
    if os.path.exists(admin_js_path):
        with open(admin_js_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        functions_to_check = [
            'loadDashboardData',
            'showSection',
            'refreshData',
            'sendAdminMessage',
            'initializeWebSocket',
            'handleAdminFileSelect',
            'clearAdminFileSelection',
            'loadTickets',
            'loadActiveConversations',
            'viewTicket',
            'deleteTicket'
        ]
        
        for func in functions_to_check:
            if f"function {func}" in content or f"{func} =" in content:
                print(f"✅ Function {func} found")
            else:
                print(f"❌ Function {func} missing")
    
    print("\n🔍 Checking admin.html for proper structure...")
    admin_html_path = os.path.join(os.getcwd(), 'templates/admin.html')
    if os.path.exists(admin_html_path):
        with open(admin_html_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        elements_to_check = [
            ('total-tickets', 'Total tickets counter'),
            ('pending-tickets', 'Pending tickets counter'),
            ('resolved-tickets', 'Resolved tickets counter'),
            ('active-chats', 'Active chats counter'),
            ('admin-chat-messages', 'Chat messages container'),
            ('admin-message-input', 'Message input field'),
            ('admin-file-input', 'File input field'),
            ('conversations-list', 'Conversations list'),
            ('tickets-tbody', 'Tickets table body')
        ]
        
        for element_id, description in elements_to_check:
            if f'id="{element_id}"' in content:
                print(f"✅ Element {description}: #{element_id}")
            else:
                print(f"❌ Element {description}: #{element_id} missing")
    
    print("\n📋 Admin Panel Setup Instructions:")
    print("1. Navigate to: http://127.0.0.1:5000/auth/admin_login")
    print("2. Login with: admin@chatbot.com / admin123")
    print("3. Check Dashboard section for stats")
    print("4. Check Tickets section for ticket list")
    print("5. Check Live Chat section for conversations")
    print("6. Test file sharing with paperclip button")

if __name__ == "__main__":
    check_admin_files()
