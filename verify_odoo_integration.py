#!/usr/bin/env python3
"""
Simple Odoo Integration Verification Script
Run this after starting Flask app to verify everything works
"""
import requests
import json
import time

def test_integration():
    print("🚀 ODOO INTEGRATION VERIFICATION")
    print("=" * 50)
    
    base_url = "http://localhost:5000"
    
    # Test 1: Connection
    print("\n1️⃣ Testing Odoo Connection...")
    try:
        response = requests.get(f"{base_url}/api/odoo/test-connection", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Connected to Odoo: {data['url']}")
            print(f"✅ User: {data['user']['name']} ({data['user']['email']})")
            print(f"✅ Version: {data['version']['server_version']}")
        else:
            print(f"❌ Connection failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return False
    
    # Test 2: Create Customer
    print("\n2️⃣ Creating Test Customer...")
    customer_data = {
        "name": f"Verification Customer {int(time.time())}",
        "email": f"verify{int(time.time())}@example.com",
        "phone": "+1-555-0123",
        "comment": "Company: Verification Test Co."
    }
    
    try:
        response = requests.post(f"{base_url}/api/odoo/customers", json=customer_data, timeout=10)
        if response.status_code == 200:
            customer = response.json()
            print(f"✅ Customer created: ID {customer['data']['id']}")
            print(f"✅ Name: {customer['data']['name']}")
            customer_id = customer['data']['id']
        else:
            print(f"❌ Customer creation failed: {response.status_code}")
            print(f"Error: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Customer creation error: {e}")
        return False
    
    # Test 3: Create Ticket
    print("\n3️⃣ Creating Test Ticket...")
    ticket_data = {
        "name": f"Verification Ticket {int(time.time())}",
        "description": "This is a test ticket created during Odoo integration verification.",
        "customer_id": customer_id,
        "priority": "1"
    }
    
    try:
        response = requests.post(f"{base_url}/api/odoo/tickets", json=ticket_data, timeout=10)
        if response.status_code == 200:
            ticket = response.json()
            print(f"✅ Ticket created: ID {ticket['data']['id']}")
            print(f"✅ Name: {ticket['data']['name']}")
        else:
            print(f"❌ Ticket creation failed: {response.status_code}")
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"❌ Ticket creation error: {e}")
    
    # Test 4: List Recent Records
    print("\n4️⃣ Listing Recent Records...")
    try:
        customers_response = requests.get(f"{base_url}/api/odoo/customers?limit=3", timeout=10)
        tickets_response = requests.get(f"{base_url}/api/odoo/tickets?limit=3", timeout=10)
        
        if customers_response.status_code == 200:
            customers = customers_response.json()
            print(f"✅ Found {len(customers['data'])} recent customers")
            
        if tickets_response.status_code == 200:
            tickets = tickets_response.json()
            print(f"✅ Found {len(tickets['data'])} recent tickets")
            
    except Exception as e:
        print(f"❌ Listing error: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 VERIFICATION COMPLETE!")
    print("\n📋 Next Steps:")
    print("1. Check your Odoo Online instance:")
    print("   • Customers: https://youcloudpay.odoo.com/web#action=base.action_partner_form")
    print("   • Tickets: https://youcloudpay.odoo.com/web#action=helpdesk.helpdesk_ticket_action_main_tree")
    print("2. Look for the test records created above")
    print("3. Integration is WORKING if you see the new records! ✅")
    
    return True

if __name__ == "__main__":
    test_integration()
