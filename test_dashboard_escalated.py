#!/usr/bin/env python3
"""
Test escalation dashboard to see if it shows the escalated ticket correctly
"""

import requests
import json

def test_escalation_dashboard():
    print("=== TESTING ESCALATION DASHBOARD ===")
    
    base_url = "http://127.0.0.1:5000"
    creds = {'email': 'admin@youcloudtech.com', 'password': 'admin123'}
    
    session = requests.Session()
    login_response = session.post(f"{base_url}/auth/admin/login", data=creds, allow_redirects=True)
    print(f"Login status: {login_response.status_code}")
    
    # Get escalation dashboard
    dashboard_response = session.get(f"{base_url}/super-admin/api/escalation/dashboard")
    print(f"Dashboard API status: {dashboard_response.status_code}")
    
    if dashboard_response.status_code == 200:
        dashboard_data = dashboard_response.json()
        print(f"Found {len(dashboard_data.get('tickets', []))} tickets")
        
        # Look specifically for ticket 53 (our freshly escalated ticket)
        ticket_53_found = False
        for ticket in dashboard_data.get('tickets', []):
            if ticket.get('ticket_id') == 53:
                ticket_53_found = True
                print(f"\nTicket 53 (freshly escalated):")
                print(f"  Subject: {ticket.get('subject', 'N/A')}")
                print(f"  Status: {ticket.get('status', 'N/A')}")
                print(f"  Escalation Level: {ticket.get('escalation_level', 'N/A')}")
                print(f"  Level Name: {ticket.get('level_name', 'N/A')}")
                print(f"  Organization: {ticket.get('organization', 'N/A')}")
                print(f"  SLA Status: {ticket.get('sla_status', 'N/A')}")
                
                # Check if escalation is reflected correctly
                if ticket.get('escalation_level') == 1:
                    print("✓ Dashboard shows correct escalation level")
                else:
                    print(f"✗ Dashboard shows wrong escalation level (expected 1, got {ticket.get('escalation_level')})")
                
                if ticket.get('level_name') == 'ICP':
                    print("✓ Dashboard shows correct level name")
                else:
                    print(f"✗ Dashboard shows wrong level name (expected 'ICP', got '{ticket.get('level_name')}')")
                
                if ticket.get('status') == 'escalated':
                    print("✓ Dashboard shows correct status")
                else:
                    print(f"✗ Dashboard shows wrong status (expected 'escalated', got '{ticket.get('status')}')")
                break
        
        if not ticket_53_found:
            print("✗ Ticket 53 not found in dashboard")
        
        # Look for tickets with escalation level > 0
        escalated_tickets = [t for t in dashboard_data.get('tickets', []) if t.get('escalation_level', 0) > 0]
        print(f"\nTotal escalated tickets in dashboard: {len(escalated_tickets)}")
        
        for ticket in escalated_tickets[:5]:  # Show first 5 escalated tickets
            print(f"  Ticket {ticket.get('ticket_id')}: Level {ticket.get('escalation_level')} ({ticket.get('level_name')})")
    
    else:
        print(f"Dashboard API failed: {dashboard_response.text}")

if __name__ == "__main__":
    test_escalation_dashboard()
