#!/usr/bin/env python3
"""
Direct Admin Fix via API calls
Works with running Flask application
"""

import requests
import json
import sys
from datetime import datetime

def test_server_connection():
    """Test if Flask server is running"""
    try:
        response = requests.get('http://localhost:5000/', timeout=5)
        print(f"✅ Flask server is running (Status: {response.status_code})")
        return True
    except requests.ConnectionError:
        print("❌ Flask server is not running")
        print("Please start the Flask server with: flask run")
        return False
    except Exception as e:
        print(f"❌ Error connecting to server: {e}")
        return False

def check_admin_login():
    """Test admin login with credentials"""
    try:
        # Try to access admin login page
        response = requests.get('http://localhost:5000/auth/admin/login', timeout=5)
        print(f"✅ Admin login page accessible (Status: {response.status_code})")
        
        # Try to login with admin credentials
        login_data = {
            'email': 'admin@youcloudtech.com',
            'password': 'admin123'
        }
        
        session = requests.Session()
        
        # Get CSRF token if needed
        login_page = session.get('http://localhost:5000/auth/admin/login')
        
        # Attempt login
        login_response = session.post(
            'http://localhost:5000/auth/admin/login',
            data=login_data,
            allow_redirects=False
        )
        
        print(f"Login attempt status: {login_response.status_code}")
        
        if login_response.status_code == 302:
            # Check redirect location
            redirect_url = login_response.headers.get('Location', '')
            if 'admin' in redirect_url.lower() and 'login' not in redirect_url.lower():
                print("✅ Admin login successful!")
                return True, "Login successful"
            else:
                print(f"❌ Login failed - redirected to: {redirect_url}")
                return False, f"Redirected to: {redirect_url}"
        else:
            print(f"❌ Login failed - Status: {login_response.status_code}")
            # Check response content for error messages
            if 'deactivated' in login_response.text.lower():
                return False, "Account deactivated"
            elif 'invalid' in login_response.text.lower():
                return False, "Invalid credentials"
            else:
                return False, f"HTTP {login_response.status_code}"
                
    except Exception as e:
        print(f"❌ Error testing admin login: {e}")
        return False, str(e)

def try_create_admin_via_register():
    """Try to create admin user via registration endpoint"""
    try:
        print("\nTrying to create admin user via registration...")
        
        register_data = {
            'name': 'System Administrator',
            'email': 'admin@youcloudtech.com',
            'password': 'admin123',
            'organization': 'YouCloudTech',
            'position': 'Administrator',
            'priority': 'critical'
        }
        
        response = requests.post(
            'http://localhost:5000/auth/register',
            data=register_data,
            allow_redirects=False
        )
        
        print(f"Registration response: {response.status_code}")
        
        if response.status_code == 302:
            print("✅ User registration successful")
            return True
        else:
            print(f"❌ Registration failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error creating admin via registration: {e}")
        return False

def check_database_api():
    """Check if we can access database via API"""
    try:
        # Try to access dashboard stats (this would require database access)
        response = requests.get('http://localhost:5000/api/admin/dashboard-stats', timeout=5)
        print(f"Dashboard API status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Database API accessible - Total tickets: {data.get('totalTickets', 'N/A')}")
            return True
        else:
            print(f"❌ Database API not accessible: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error checking database API: {e}")
        return False

def main():
    """Main function to diagnose and fix admin issues"""
    print("=== ADMIN LOGIN DIAGNOSIS & FIX ===")
    
    # Step 1: Check server connection
    print("\n1. Checking Flask server connection...")
    if not test_server_connection():
        return False
    
    # Step 2: Check database API access
    print("\n2. Checking database API access...")
    db_accessible = check_database_api()
    
    # Step 3: Test admin login
    print("\n3. Testing admin login...")
    login_success, login_message = check_admin_login()
    
    if login_success:
        print("🎯 ADMIN LOGIN IS WORKING!")
        print("✅ You can access the admin panel at: http://localhost:5000/auth/admin/login")
        print("📧 Email: admin@youcloudtech.com")
        print("🔑 Password: admin123")
        return True
    
    print(f"❌ Admin login failed: {login_message}")
    
    # Step 4: Try to create admin user via registration
    if 'deactivated' in login_message.lower() or 'invalid' in login_message.lower():
        print("\n4. Attempting to create/fix admin user...")
        if try_create_admin_via_register():
            print("✅ Admin user created via registration")
            print("Now testing login again...")
            
            login_success, login_message = check_admin_login()
            if login_success:
                print("🎯 ADMIN LOGIN NOW WORKING!")
                return True
    
    # Step 5: Provide manual instructions
    print("\n❌ AUTOMATED FIX FAILED")
    print("\n🔧 MANUAL FIX REQUIRED:")
    print("1. Stop the Flask server (Ctrl+C)")
    print("2. Use SQL Server Management Studio to connect to your database")
    print("3. Run this SQL command to fix the admin user:")
    print("""
    USE SupportChatbot;
    
    -- Update existing admin or create if not exists
    IF EXISTS (SELECT 1 FROM Users WHERE Email = 'admin@youcloudtech.com')
    BEGIN
        UPDATE Users 
        SET IsActive = 1, IsAdmin = 1, 
            PasswordHash = '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewlqkkMCHUdE3M2e',
            Name = 'System Administrator'
        WHERE Email = 'admin@youcloudtech.com';
        PRINT 'Admin user updated';
    END
    ELSE
    BEGIN
        INSERT INTO Users (Name, Email, PasswordHash, OrganizationName, Position, PriorityLevel, IsActive, IsAdmin, CreatedAt)
        VALUES ('System Administrator', 'admin@youcloudtech.com', 
                '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewlqkkMCHUdE3M2e',
                'YouCloudTech', 'Administrator', 'critical', 1, 1, GETDATE());
        PRINT 'Admin user created';
    END
    """)
    print("4. Restart the Flask server")
    print("5. Try logging in again")
    
    return False

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🚀 SUCCESS! Admin login is working!")
    else:
        print("\n❌ Please follow the manual fix instructions above")
