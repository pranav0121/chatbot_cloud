#!/usr/bin/env python3
"""
Test escalation and partner assignment functionality
"""

import requests
import json

BASE_URL = "http://127.0.0.1:5001"

def test_escalation_with_partners():
    """Test the complete escalation flow with partner assignments"""
    
    print("=== TESTING ESCALATION WITH PARTNER ASSIGNMENT ===\n")
    
    # Create session for admin login
    session = requests.Session()
    
    print("1. Logging in as super admin...")
    try:
        # Login to super admin
        login_data = {
            'email': 'superadmin@youcloudtech.com',
            'password': 'superadmin123'
        }
        
        login_response = session.post(f"{BASE_URL}/auth/admin/login", data=login_data)
        print(f"   Login status: {login_response.status_code}")
        
        if login_response.status_code not in [200, 302]:
            print(f"   ❌ Login failed: {login_response.text}")
            return
        
        print("   ✅ Login successful")
        
    except Exception as e:
        print(f"   ❌ Login error: {e}")
        return
    
    print("\n2. Getting current escalation dashboard...")
    try:
        escalation_response = session.get(f"{BASE_URL}/super-admin/api/escalation/dashboard")
        
        if escalation_response.status_code == 200:
            escalation_data = escalation_response.json()
            tickets = escalation_data.get('tickets', [])
            
            print(f"   ✅ Found {len(tickets)} tickets in escalation dashboard")
            
            # Show tickets with their partner assignments
            for ticket in tickets[:5]:  # Show first 5
                partner_info = "Unassigned"
                if ticket.get('partner'):
                    partner_info = f"{ticket['partner']['name']} ({ticket['partner']['type']})"
                
                print(f"     • Ticket #{ticket['ticket_id']}: {ticket['subject'][:40]}...")
                print(f"       Level: {ticket['level_name']} | Partner: {partner_info}")
            
        else:
            print(f"   ❌ Failed to get escalation data: {escalation_response.status_code}")
            return
            
    except Exception as e:
        print(f"   ❌ Error getting escalation data: {e}")
        return
    
    print("\n3. Testing manual escalation...")
    if tickets:
        # Test escalating the first ticket
        test_ticket = tickets[0]
        ticket_id = test_ticket['ticket_id']
        
        print(f"   Testing escalation of Ticket #{ticket_id}")
        
        # Force escalate to Level 1 (ICP)
        escalate_data = {
            'level': 1,
            'comment': 'Test escalation to ICP partner'
        }
        
        try:
            escalate_response = session.post(
                f"{BASE_URL}/super-admin/api/escalation/force/{ticket_id}",
                json=escalate_data
            )
            
            if escalate_response.status_code == 200:
                result = escalate_response.json()
                print(f"   ✅ Escalation successful: {result.get('message', 'No message')}")
            else:
                print(f"   ❌ Escalation failed: {escalate_response.status_code}")
                print(f"       Response: {escalate_response.text}")
                
        except Exception as e:
            print(f"   ❌ Error during escalation: {e}")
    
    print("\n4. Checking updated escalation dashboard...")
    try:
        # Get updated escalation data
        escalation_response = session.get(f"{BASE_URL}/super-admin/api/escalation/dashboard")
        
        if escalation_response.status_code == 200:
            escalation_data = escalation_response.json()
            tickets = escalation_data.get('tickets', [])
            
            print(f"   ✅ Updated dashboard shows {len(tickets)} tickets")
            
            # Show updated partner assignments
            assigned_count = 0
            for ticket in tickets:
                if ticket.get('partner'):
                    assigned_count += 1
                    print(f"     ✅ Ticket #{ticket['ticket_id']}: Assigned to {ticket['partner']['name']}")
            
            print(f"   Total assigned tickets: {assigned_count}/{len(tickets)}")
            
        else:
            print(f"   ❌ Failed to get updated escalation data: {escalation_response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Error getting updated escalation data: {e}")
    
    print("\n5. Checking partner status...")
    try:
        partners_response = session.get(f"{BASE_URL}/super-admin/api/partners")
        
        if partners_response.status_code == 200:
            partners_data = partners_response.json()
            partners = partners_data.get('partners', [])
            
            print(f"   ✅ Found {len(partners)} partners:")
            for partner in partners:
                tickets_handled = partner.get('total_tickets_handled', 0)
                print(f"     • {partner['name']} ({partner['partner_type']})")
                print(f"       Tickets handled: {tickets_handled}")
                print(f"       Status: {partner['status']}")
                print(f"       Webhook: {'✅' if partner.get('webhook_url') else '❌'}")
        else:
            print(f"   ❌ Failed to get partners: {partners_response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Error getting partners: {e}")
    
    print("\n=== TEST COMPLETE ===")

if __name__ == "__main__":
    test_escalation_with_partners()
