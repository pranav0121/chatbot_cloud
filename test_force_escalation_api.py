#!/usr/bin/env python3
"""
Test the force escalation API directly to see what happens
"""

import requests
import json

BASE_URL = "http://127.0.0.1:5001"

def test_force_escalation_api():
    """Test the force escalation API endpoint directly"""
    
    print("=== TESTING FORCE ESCALATION API ===\n")
    
    # Create session for admin login
    session = requests.Session()
    
    print("1. Logging in as super admin...")
    try:
        login_data = {
            'email': 'superadmin@youcloudtech.com',
            'password': 'superadmin123'
        }
        
        login_response = session.post(f"{BASE_URL}/auth/admin/login", data=login_data)
        print(f"   Login status: {login_response.status_code}")
        
        if login_response.status_code not in [200, 302]:
            print(f"   ❌ Login failed")
            return
        
        print("   ✅ Login successful")
        
    except Exception as e:
        print(f"   ❌ Login error: {e}")
        return
    
    print("\n2. Getting a test ticket...")
    try:
        # Get tickets from escalation dashboard
        escalation_response = session.get(f"{BASE_URL}/super-admin/api/escalation/dashboard")
        
        if escalation_response.status_code == 200:
            data = escalation_response.json()
            tickets = data.get('tickets', [])
            
            if tickets:
                test_ticket = tickets[0]
                ticket_id = test_ticket['ticket_id']
                print(f"   Using Ticket #{ticket_id}: {test_ticket['subject']}")
                print(f"   Current level: {test_ticket['level_name']}")
                print(f"   Current partner: {test_ticket.get('partner', 'None')}")
            else:
                print("   ❌ No tickets found")
                return
        else:
            print(f"   ❌ Failed to get tickets: {escalation_response.status_code}")
            return
            
    except Exception as e:
        print(f"   ❌ Error getting tickets: {e}")
        return
    
    print(f"\n3. Testing force escalation API for Ticket #{ticket_id}...")
    try:
        escalate_data = {
            'level': 1,
            'comment': 'API test escalation to ICP'
        }
        
        escalate_url = f"{BASE_URL}/super-admin/api/escalation/force/{ticket_id}"
        print(f"   POST URL: {escalate_url}")
        print(f"   Data: {escalate_data}")
        
        escalate_response = session.post(escalate_url, json=escalate_data)
        
        print(f"   Response status: {escalate_response.status_code}")
        print(f"   Response headers: {dict(escalate_response.headers)}")
        
        if escalate_response.status_code == 200:
            result = escalate_response.json()
            print(f"   ✅ Success response: {result}")
            
            # Check the actual message format
            message = result.get('message', '')
            if 'assigned to' in message:
                print(f"   🎯 Partner assignment detected in message!")
            else:
                print(f"   ⚠ No partner assignment mentioned in response")
                
        else:
            print(f"   ❌ Error response: {escalate_response.text}")
            
        # Check if the API endpoint exists at all
        if escalate_response.status_code == 404:
            print("   🔍 API endpoint not found - checking available routes...")
            
            # Try to access the super admin dashboard to see if routes are working
            dashboard_response = session.get(f"{BASE_URL}/super-admin/")
            print(f"   Super admin dashboard status: {dashboard_response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Error during escalation: {e}")
    
    print("\n4. Checking updated ticket status...")
    try:
        # Get updated escalation data
        escalation_response = session.get(f"{BASE_URL}/super-admin/api/escalation/dashboard")
        
        if escalation_response.status_code == 200:
            data = escalation_response.json()
            tickets = data.get('tickets', [])
            
            # Find our test ticket
            updated_ticket = None
            for ticket in tickets:
                if ticket['ticket_id'] == ticket_id:
                    updated_ticket = ticket
                    break
            
            if updated_ticket:
                print(f"   Ticket #{ticket_id} after escalation:")
                print(f"   - Level: {updated_ticket['level_name']}")
                print(f"   - Partner: {updated_ticket.get('partner', 'None')}")
                print(f"   - Status: {updated_ticket.get('status', 'Unknown')}")
            else:
                print(f"   ❌ Could not find Ticket #{ticket_id} in updated data")
                
    except Exception as e:
        print(f"   ❌ Error checking updated status: {e}")
    
    print("\n=== TEST COMPLETE ===")

if __name__ == "__main__":
    test_force_escalation_api()
