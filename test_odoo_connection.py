#!/usr/bin/env python3
"""
Test Odoo Online API Connection
Tests basic connectivity and authentication with your Odoo instance
"""

import os
import xmlrpc.client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_odoo_connection():
    """Test connection to Odoo Online"""
    
    # Get credentials from environment
    url = os.getenv('ODOO_URL')
    db = os.getenv('ODOO_DB')
    username = os.getenv('ODOO_USERNAME')
    password = os.getenv('ODOO_PASSWORD')
    
    print(f"🔗 Testing connection to: {url}")
    print(f"📊 Database: {db}")
    print(f"👤 Username: {username}")
    print("-" * 50)
    
    try:
        # Test basic connectivity
        print("1️⃣ Testing basic connectivity...")
        common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
        version_info = common.version()
        print(f"✅ Connected! Odoo version: {version_info.get('server_version', 'Unknown')}")
        
        # Test authentication
        print("\n2️⃣ Testing authentication...")
        uid = common.authenticate(db, username, password, {})
        if uid:
            print(f"✅ Authentication successful! User ID: {uid}")
        else:
            print("❌ Authentication failed!")
            return False
            
        # Test object access
        print("\n3️⃣ Testing object access...")
        models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')
        
        # Test reading user info
        user_info = models.execute_kw(db, uid, password, 'res.users', 'read', [uid], {'fields': ['name', 'email', 'company_id']})
        print(f"✅ User info retrieved: {user_info[0]['name']} ({user_info[0]['email']})")
        
        # Test installed apps
        print("\n4️⃣ Testing installed apps...")
        installed_modules = models.execute_kw(db, uid, password, 'ir.module.module', 'search_read', 
                                            [['state', '=', 'installed']], {'fields': ['name', 'shortdesc']})
        
        key_apps = ['helpdesk', 'crm', 'website', 'calendar', 'account', 'contacts', 'project', 'sale']
        found_apps = []
        
        for module in installed_modules:
            if module['name'] in key_apps:
                found_apps.append(f"  ✅ {module['name']}: {module['shortdesc']}")
        
        print("📦 Key installed apps:")
        for app in found_apps:
            print(app)
            
        # Test creating a test contact
        print("\n5️⃣ Testing contact creation...")
        test_contact_data = {
            'name': 'Chatbot Test Contact',
            'email': 'chatbot-test@example.com',
            'phone': '+1-555-TEST',
            'is_company': False,
            'comment': 'Test contact created by chatbot integration'
        }
        
        contact_id = models.execute_kw(db, uid, password, 'res.partner', 'create', [test_contact_data])
        print(f"✅ Test contact created with ID: {contact_id}")
        
        # Clean up - delete test contact
        models.execute_kw(db, uid, password, 'res.partner', 'unlink', [contact_id])
        print(f"🧹 Test contact deleted (cleanup)")
        
        print("\n" + "=" * 50)
        print("🎉 ALL TESTS PASSED! Odoo integration is ready!")
        print("=" * 50)
        return True
        
    except Exception as e:
        print(f"❌ Connection test failed: {str(e)}")
        print("\n🔧 Troubleshooting tips:")
        print("1. Check your internet connection")
        print("2. Verify Odoo URL is correct")
        print("3. Ensure username/password are correct")
        print("4. Check if Odoo instance is accessible")
        return False

if __name__ == "__main__":
    test_odoo_connection()
