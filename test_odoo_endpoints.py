#!/usr/bin/env python3
"""
Test script for Odoo API endpoints integration
"""
import requests
import json
import time

# Flask app base URL
BASE_URL = "http://localhost:5000"

def test_endpoint(method, endpoint, data=None, description=""):
    """Test a Flask endpoint"""
    print(f"\n🧪 Testing: {description}")
    print(f"📡 {method} {endpoint}")
    
    try:
        if method == "GET":
            response = requests.get(f"{BASE_URL}{endpoint}")
        elif method == "POST":
            response = requests.post(f"{BASE_URL}{endpoint}", json=data)
        elif method == "PUT":
            response = requests.put(f"{BASE_URL}{endpoint}", json=data)
        
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Success: {json.dumps(result, indent=2)}")
            return result
        else:
            print(f"❌ Error: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return None

def main():
    print("🚀 Testing Odoo API Integration Endpoints")
    print("=" * 50)
    
    # Wait for Flask to start
    print("⏳ Waiting for Flask app to start...")
    time.sleep(3)
    
    # Test 1: Create a customer in Odoo
    customer_data = {
        "name": "Test Customer API",
        "email": "testcustomer@example.com",
        "phone": "+1234567890",
        "company": "Test Company API"
    }
    
    customer_result = test_endpoint(
        "POST", 
        "/api/odoo/customers", 
        customer_data,
        "Create Customer in Odoo"
    )
    
    # Test 2: Create a ticket in Odoo
    if customer_result and customer_result.get('success'):
        customer_id = customer_result.get('data', {}).get('id')
        
        ticket_data = {
            "name": "Test API Ticket",
            "description": "This is a test ticket created via API integration",
            "customer_id": customer_id,
            "priority": "1",  # Normal priority
            "tag_ids": ["api-test"]
        }
        
        ticket_result = test_endpoint(
            "POST", 
            "/api/odoo/tickets", 
            ticket_data,
            "Create Ticket in Odoo"
        )
        
        # Test 3: Get customer details
        if customer_id:
            test_endpoint(
                "GET", 
                f"/api/odoo/customers/{customer_id}",
                description="Get Customer Details"
            )
        
        # Test 4: Get ticket details
        if ticket_result and ticket_result.get('success'):
            ticket_id = ticket_result.get('data', {}).get('id')
            if ticket_id:
                test_endpoint(
                    "GET", 
                    f"/api/odoo/tickets/{ticket_id}",
                    description="Get Ticket Details"
                )
    
    # Test 5: List customers
    test_endpoint(
        "GET", 
        "/api/odoo/customers?limit=5",
        description="List Recent Customers"
    )
    
    # Test 6: List tickets
    test_endpoint(
        "GET", 
        "/api/odoo/tickets?limit=5",
        description="List Recent Tickets"
    )
    
    # Test 7: Test connection endpoint
    test_endpoint(
        "GET", 
        "/api/odoo/test-connection",
        description="Test Odoo Connection"
    )
    
    print("\n" + "=" * 50)
    print("🎯 API Testing Complete!")
    print("\n📋 Next steps:")
    print("1. Check your Odoo Online instance for new customer and ticket")
    print("2. Go to: https://youcloudpay.odoo.com/web#action=base.action_partner_form")
    print("3. Go to: https://youcloudpay.odoo.com/web#action=helpdesk.helpdesk_ticket_action_main_tree")

if __name__ == "__main__":
    main()
