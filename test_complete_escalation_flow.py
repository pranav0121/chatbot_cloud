#!/usr/bin/env python3
"""
Complete test of escalation flow with working credentials
"""

import requests
import json
import sys

def test_complete_escalation_flow():
    base_url = "http://127.0.0.1:5000"
    
    print("=== COMPLETE ESCALATION FLOW TEST ===")
    
    # Use working admin credentials
    creds = {'email': 'admin@youcloudtech.com', 'password': 'admin123'}
    
    session = requests.Session()
    
    # Step 1: Login
    print("\n1. Logging in as admin...")
    login_response = session.post(f"{base_url}/auth/admin/login", data=creds, allow_redirects=True)
    print(f"Login status: {login_response.status_code}")
    
    # Step 2: Get initial escalation dashboard state
    print("\n2. Getting initial escalation dashboard state...")
    dashboard_response = session.get(f"{base_url}/super-admin/api/escalation/dashboard")
    
    if dashboard_response.status_code == 200:
        dashboard_data = dashboard_response.json()
        print(f"Found {len(dashboard_data.get('tickets', []))} tickets")
        
        if dashboard_data.get('tickets'):
            # Use the first ticket for testing
            test_ticket = dashboard_data['tickets'][0]
            ticket_id = test_ticket['ticket_id']
            
            print(f"\nBEFORE ESCALATION:")
            print(f"  Ticket ID: {ticket_id}")
            print(f"  Subject: {test_ticket.get('subject', 'N/A')}")
            print(f"  Status: {test_ticket.get('status', 'N/A')}")
            print(f"  Escalation Level: {test_ticket.get('escalation_level', 'N/A')}")
            print(f"  Level Name: {test_ticket.get('level_name', 'N/A')}")
            print(f"  Organization: {test_ticket.get('organization', 'N/A')}")
            print(f"  SLA Status: {test_ticket.get('sla_status', 'N/A')}")
            print(f"  Time Remaining: {test_ticket.get('time_remaining', 'N/A')}")
        else:
            print("No tickets found in dashboard")
            return
    else:
        print(f"Failed to get dashboard: {dashboard_response.status_code}")
        return
    
    # Step 3: Force escalate the ticket
    print(f"\n3. Force escalating ticket {ticket_id} to level 1...")
    escalation_data = {
        'level': 1,
        'comment': 'Complete flow test escalation'
    }
    
    escalation_response = session.post(
        f"{base_url}/super-admin/api/escalation/force/{ticket_id}",
        json=escalation_data,
        headers={'Content-Type': 'application/json'}
    )
    
    print(f"Escalation response status: {escalation_response.status_code}")
    
    try:
        escalation_result = escalation_response.json()
        print(f"Escalation response: {json.dumps(escalation_result, indent=2)}")
    except:
        print(f"Escalation response text: {escalation_response.text}")
    
    # Step 4: Get updated escalation dashboard state
    print("\n4. Getting updated escalation dashboard state...")
    updated_dashboard_response = session.get(f"{base_url}/super-admin/api/escalation/dashboard")
    
    if updated_dashboard_response.status_code == 200:
        updated_dashboard_data = updated_dashboard_response.json()
        print(f"Found {len(updated_dashboard_data.get('tickets', []))} tickets")
        
        # Find our ticket in the updated data
        for ticket in updated_dashboard_data.get('tickets', []):
            if ticket['ticket_id'] == ticket_id:
                print(f"\nAFTER ESCALATION:")
                print(f"  Ticket ID: {ticket_id}")
                print(f"  Subject: {ticket.get('subject', 'N/A')}")
                print(f"  Status: {ticket.get('status', 'N/A')}")
                print(f"  Escalation Level: {ticket.get('escalation_level', 'N/A')}")
                print(f"  Level Name: {ticket.get('level_name', 'N/A')}")
                print(f"  Organization: {ticket.get('organization', 'N/A')}")
                print(f"  SLA Status: {ticket.get('sla_status', 'N/A')}")
                print(f"  Time Remaining: {ticket.get('time_remaining', 'N/A')}")
                
                # Check if changes were applied
                if ticket.get('escalation_level') == 1:
                    print("\n✓ Escalation level updated correctly!")
                else:
                    print(f"\n✗ Escalation level not updated (expected 1, got {ticket.get('escalation_level')})")
                
                if ticket.get('status') == 'escalated':
                    print("✓ Status updated to escalated!")
                else:
                    print(f"✗ Status not updated (expected 'escalated', got '{ticket.get('status')}')")
                
                if ticket.get('level_name') == 'ICP':
                    print(f"✓ Level name updated: {ticket.get('level_name')}")
                else:
                    print(f"✗ Level name not updated (expected 'ICP', got '{ticket.get('level_name')}')")
                
                break
        else:
            print(f"Ticket {ticket_id} not found in updated dashboard")
    else:
        print(f"Failed to get updated dashboard: {updated_dashboard_response.status_code}")
    
    # Step 5: Test escalating to level 2
    print(f"\n5. Force escalating ticket {ticket_id} to level 2...")
    escalation_data_l2 = {
        'level': 2,
        'comment': 'Test escalation to YouCloud level'
    }
    
    escalation_response_l2 = session.post(
        f"{base_url}/super-admin/api/escalation/force/{ticket_id}",
        json=escalation_data_l2,
        headers={'Content-Type': 'application/json'}
    )
    
    print(f"Level 2 escalation status: {escalation_response_l2.status_code}")
    
    try:
        escalation_result_l2 = escalation_response_l2.json()
        print(f"Level 2 escalation response: {json.dumps(escalation_result_l2, indent=2)}")
    except:
        print(f"Level 2 escalation response text: {escalation_response_l2.text}")
    
    # Step 6: Final dashboard check
    print("\n6. Final dashboard check...")
    final_dashboard_response = session.get(f"{base_url}/super-admin/api/escalation/dashboard")
    
    if final_dashboard_response.status_code == 200:
        final_dashboard_data = final_dashboard_response.json()
        
        for ticket in final_dashboard_data.get('tickets', []):
            if ticket['ticket_id'] == ticket_id:
                print(f"\nFINAL STATE:")
                print(f"  Ticket ID: {ticket_id}")
                print(f"  Subject: {ticket.get('subject', 'N/A')}")
                print(f"  Status: {ticket.get('status', 'N/A')}")
                print(f"  Escalation Level: {ticket.get('escalation_level', 'N/A')}")
                print(f"  Level Name: {ticket.get('level_name', 'N/A')}")
                print(f"  Organization: {ticket.get('organization', 'N/A')}")
                print(f"  SLA Status: {ticket.get('sla_status', 'N/A')}")
                print(f"  Time Remaining: {ticket.get('time_remaining', 'N/A')}")
                break

if __name__ == "__main__":
    test_complete_escalation_flow()
