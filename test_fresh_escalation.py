#!/usr/bin/env python3
"""
Find a non-escalated ticket and test escalation on it
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db, Ticket
import requests
import json

def test_fresh_ticket_escalation():
    print("=== TESTING ESCALATION ON FRESH TICKET ===")
    
    with app.app_context():
        # Find a ticket that's not escalated yet
        fresh_ticket = Ticket.query.filter_by(Status='open', escalation_level=0).first()
        
        if not fresh_ticket:
            print("No fresh tickets found. Creating one...")
            # We'll use an existing ticket but reset it first
            fresh_ticket = Ticket.query.filter_by(TicketID=51).first()
            if fresh_ticket:
                fresh_ticket.Status = 'open'
                fresh_ticket.escalation_level = 0
                fresh_ticket.partner_id = None
                db.session.commit()
                print(f"Reset ticket {fresh_ticket.TicketID} to fresh state")
            else:
                print("No tickets available for testing")
                return
        
        ticket_id = fresh_ticket.TicketID
        print(f"\nUsing ticket {ticket_id}")
        print(f"  Subject: {fresh_ticket.Subject}")
        print(f"  Status: {fresh_ticket.Status}")
        print(f"  Escalation Level: {fresh_ticket.escalation_level}")
        print(f"  Partner ID: {fresh_ticket.partner_id}")
    
    # Now test escalation via API
    base_url = "http://127.0.0.1:5000"
    creds = {'email': 'admin@youcloudtech.com', 'password': 'admin123'}
    
    session = requests.Session()
    login_response = session.post(f"{base_url}/auth/admin/login", data=creds, allow_redirects=True)
    
    # Make escalation API call
    print(f"\nEscalating ticket {ticket_id} from fresh state...")
    escalation_data = {'level': 1, 'comment': 'Fresh ticket escalation test'}
    escalation_response = session.post(
        f"{base_url}/super-admin/api/escalation/force/{ticket_id}",
        json=escalation_data,
        headers={'Content-Type': 'application/json'}
    )
    
    print(f"API Response: {escalation_response.status_code}")
    try:
        response_data = escalation_response.json()
        print(f"Response: {json.dumps(response_data, indent=2)}")
    except:
        print(f"Response text: {escalation_response.text}")
    
    # Check database immediately after
    with app.app_context():
        updated_ticket = Ticket.query.get(ticket_id)
        print(f"\nAfter escalation:")
        print(f"  Status: {updated_ticket.Status}")
        print(f"  Escalation Level: {updated_ticket.escalation_level}")
        print(f"  Partner ID: {updated_ticket.partner_id}")
        
        # Verify changes
        if updated_ticket.Status == 'escalated':
            print("✓ Status updated correctly")
        else:
            print(f"✗ Status not updated (expected 'escalated', got '{updated_ticket.Status}')")
            
        if updated_ticket.escalation_level == 1:
            print("✓ Escalation level updated correctly")
        else:
            print(f"✗ Escalation level not updated (expected 1, got {updated_ticket.escalation_level})")
            
        if updated_ticket.partner_id == 1:
            print("✓ Partner assigned correctly")
        else:
            print(f"✗ Partner not assigned (expected 1, got {updated_ticket.partner_id})")

if __name__ == "__main__":
    test_fresh_ticket_escalation()
