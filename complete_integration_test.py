"""
Complete Odoo Integration Setup and Verification Script
This script will:
1. Verify Flask app is running
2. Test Odoo connection
3. Create test customer and ticket
4. Verify data flow
5. Provide next steps
"""

import requests
import json
import time
import subprocess
import os
from datetime import datetime

def check_flask_running():
    """Check if Flask app is running"""
    print("🔍 Checking if Flask app is running...")
    try:
        response = requests.get("http://localhost:5000/health", timeout=5)
        print("✅ Flask app is running on port 5000")
        return True
    except:
        try:
            response = requests.get("http://localhost:5000/", timeout=5)
            print("✅ Flask app is running on port 5000")
            return True
        except:
            print("❌ Flask app is not running")
            return False

def start_flask_if_needed():
    """Start Flask app if not running"""
    if not check_flask_running():
        print("🚀 Starting Flask application...")
        print("   Command: python app.py")
        print("   Please run this in a separate terminal and press Enter when ready...")
        input("   Press Enter to continue...")
        
        # Wait and check again
        time.sleep(3)
        if check_flask_running():
            print("✅ Flask app is now running!")
            return True
        else:
            print("❌ Flask app is still not running. Please start it manually.")
            return False
    return True

def test_odoo_connection():
    """Test Odoo API connection"""
    print("\n🔗 Testing Odoo connection...")
    try:
        response = requests.get("http://localhost:5000/api/odoo/test-connection", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print("✅ Odoo connection successful!")
            print(f"   Server: {data.get('server_info', {}).get('server_serie', 'Unknown')}")
            print(f"   User: {data.get('user_info', {}).get('name', 'Unknown')}")
            return True
        else:
            print(f"❌ Odoo connection failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Odoo connection error: {str(e)}")
        return False

def create_test_customer():
    """Create a test customer"""
    print("\n👤 Creating test customer...")
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    customer_data = {
        "name": f"API Test Customer {timestamp}",
        "email": f"testcustomer_{timestamp}@example.com",
        "phone": "+1-555-0123",
        "company": "ChatBot Integration Test Co."
    }
    
    try:
        response = requests.post(
            "http://localhost:5000/api/odoo/customers",
            json=customer_data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                customer_id = result.get('data', {}).get('id')
                print(f"✅ Customer created successfully!")
                print(f"   Customer ID: {customer_id}")
                print(f"   Name: {customer_data['name']}")
                print(f"   Email: {customer_data['email']}")
                return customer_id
            else:
                print(f"❌ Customer creation failed: {result.get('message')}")
                return None
        else:
            print(f"❌ Customer creation failed: HTTP {response.status_code}")
            print(f"   Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Customer creation error: {str(e)}")
        return None

def create_test_ticket(customer_id):
    """Create a test ticket"""
    if not customer_id:
        print("⏭️ Skipping ticket creation (no customer ID)")
        return None
    
    print("\n🎫 Creating test ticket...")
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    ticket_data = {
        "name": f"API Test Ticket {timestamp}",
        "description": f"This is a test ticket created via ChatBot API integration on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}.\n\nThis ticket demonstrates the successful integration between:\n- ChatBot System\n- Flask API\n- Odoo Online\n\nCustomer ID: {customer_id}",
        "customer_id": customer_id,
        "priority": "1",  # Normal priority
        "tag_ids": ["api-integration", "chatbot-test"]
    }
    
    try:
        response = requests.post(
            "http://localhost:5000/api/odoo/tickets",
            json=ticket_data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                ticket_id = result.get('data', {}).get('id')
                print(f"✅ Ticket created successfully!")
                print(f"   Ticket ID: {ticket_id}")
                print(f"   Title: {ticket_data['name']}")
                print(f"   Customer ID: {customer_id}")
                return ticket_id
            else:
                print(f"❌ Ticket creation failed: {result.get('message')}")
                return None
        else:
            print(f"❌ Ticket creation failed: HTTP {response.status_code}")
            print(f"   Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Ticket creation error: {str(e)}")
        return None

def verify_data_in_odoo(customer_id, ticket_id):
    """Verify data was created in Odoo"""
    print("\n🔍 Verifying data in Odoo...")
    
    success_count = 0
    
    # Check customer
    if customer_id:
        try:
            response = requests.get(f"http://localhost:5000/api/odoo/customers/{customer_id}")
            if response.status_code == 200:
                print(f"✅ Customer {customer_id} verified in Odoo")
                success_count += 1
            else:
                print(f"❌ Customer {customer_id} not found in Odoo")
        except Exception as e:
            print(f"❌ Error verifying customer: {str(e)}")
    
    # Check ticket
    if ticket_id:
        try:
            response = requests.get(f"http://localhost:5000/api/odoo/tickets/{ticket_id}")
            if response.status_code == 200:
                print(f"✅ Ticket {ticket_id} verified in Odoo")
                success_count += 1
            else:
                print(f"❌ Ticket {ticket_id} not found in Odoo")
        except Exception as e:
            print(f"❌ Error verifying ticket: {str(e)}")
    
    return success_count

def print_verification_links(customer_id, ticket_id):
    """Print links to verify data in Odoo Online"""
    print("\n🌐 Verification Links (Open in browser):")
    print("=" * 50)
    
    if customer_id:
        print(f"📱 View Customer {customer_id}:")
        print(f"   https://youcloudpay.odoo.com/web#id={customer_id}&action=base.action_partner_form&model=res.partner&view_type=form")
    
    if ticket_id:
        print(f"🎫 View Ticket {ticket_id}:")
        print(f"   https://youcloudpay.odoo.com/web#id={ticket_id}&action=helpdesk.helpdesk_ticket_action_main_tree&model=helpdesk.ticket&view_type=form")
    
    print("\n📋 All Records:")
    print("   • All Customers: https://youcloudpay.odoo.com/web#action=base.action_partner_form")
    print("   • All Tickets: https://youcloudpay.odoo.com/web#action=helpdesk.helpdesk_ticket_action_main_tree")

def main():
    print("🚀 COMPLETE ODOO INTEGRATION SETUP & TEST")
    print("=" * 60)
    print(f"   Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Step 1: Ensure Flask is running
    if not start_flask_if_needed():
        print("\n❌ Cannot proceed without Flask app running.")
        print("   Please run: python app.py")
        return
    
    # Step 2: Test Odoo connection
    if not test_odoo_connection():
        print("\n❌ Odoo connection failed. Check your .env configuration:")
        print("   ODOO_URL=https://youcloudpay.odoo.com")
        print("   ODOO_DB=youcloudpay")
        print("   ODOO_USERNAME=your-email")
        print("   ODOO_PASSWORD=your-password")
        return
    
    # Step 3: Create test data
    customer_id = create_test_customer()
    ticket_id = create_test_ticket(customer_id)
    
    # Step 4: Verify data
    verified_count = verify_data_in_odoo(customer_id, ticket_id)
    
    # Step 5: Results
    print("\n" + "=" * 60)
    print("🎯 INTEGRATION TEST RESULTS")
    print("=" * 60)
    
    if customer_id and ticket_id and verified_count >= 2:
        print("🎉 SUCCESS! Complete integration is working!")
        print(f"   ✅ Customer created: ID {customer_id}")
        print(f"   ✅ Ticket created: ID {ticket_id}")
        print(f"   ✅ Data verified in Odoo")
        print("\n🔄 Data Flow Confirmed:")
        print("   ChatBot → Flask API → Odoo Online ✅")
        
        print_verification_links(customer_id, ticket_id)
        
        print("\n🚀 Next Steps:")
        print("   1. Your chatbot can now create customers and tickets in Odoo!")
        print("   2. Configure your chatbot to use these API endpoints:")
        print("      • POST /api/odoo/customers - Create customer")
        print("      • POST /api/odoo/tickets - Create ticket")
        print("      • GET /api/odoo/customers - List customers")
        print("      • GET /api/odoo/tickets - List tickets")
        print("   3. Integration is COMPLETE and READY for production! 🎊")
        
    else:
        print("⚠️ Partial success or issues detected:")
        if customer_id:
            print(f"   ✅ Customer created: ID {customer_id}")
        else:
            print("   ❌ Customer creation failed")
        
        if ticket_id:
            print(f"   ✅ Ticket created: ID {ticket_id}")
        else:
            print("   ❌ Ticket creation failed")
        
        print("\n🔧 Troubleshooting:")
        print("   1. Check Flask app logs for errors")
        print("   2. Verify Odoo credentials in .env file")
        print("   3. Ensure Odoo apps are installed (Helpdesk, CRM, etc.)")
        print("   4. Check network connectivity to Odoo Online")

if __name__ == "__main__":
    main()
