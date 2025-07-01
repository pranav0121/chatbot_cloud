#!/usr/bin/env python3
"""
Immediate database check after escalation
"""

import requests
import json
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db, Ticket
from models import SLALog, TicketStatusLog

def escalate_and_check_immediately():
    print("=== ESCALATE AND CHECK IMMEDIATELY ===")
    
    # Test escalation via API
    base_url = "http://127.0.0.1:5000"
    creds = {'email': 'admin@youcloudtech.com', 'password': 'admin123'}
    
    session = requests.Session()
    login_response = session.post(f"{base_url}/auth/admin/login", data=creds, allow_redirects=True)
    print(f"Login status: {login_response.status_code}")
    
    ticket_id = 51
    
    # Get ticket state before escalation
    with app.app_context():
        ticket_before = Ticket.query.get(ticket_id)
        print(f"\nBEFORE API CALL:")
        print(f"  Status: {ticket_before.Status}")
        print(f"  Escalation Level: {ticket_before.escalation_level}")
        print(f"  Partner ID: {ticket_before.partner_id}")
        
        # Count existing logs
        sla_logs_before = SLALog.query.filter_by(ticket_id=ticket_id).count()
        status_logs_before = TicketStatusLog.query.filter_by(ticket_id=ticket_id).count()
        print(f"  SLA Logs: {sla_logs_before}")
        print(f"  Status Logs: {status_logs_before}")
    
    # Make escalation API call
    print(f"\nMAKING API CALL...")
    escalation_data = {'level': 1, 'comment': 'Immediate check test'}
    escalation_response = session.post(
        f"{base_url}/super-admin/api/escalation/force/{ticket_id}",
        json=escalation_data,
        headers={'Content-Type': 'application/json'}
    )
    
    print(f"API Response: {escalation_response.status_code}")
    try:
        response_data = escalation_response.json()
        print(f"Response data: {json.dumps(response_data, indent=2)}")
    except:
        print(f"Response text: {escalation_response.text}")
    
    # Immediately check database after API call
    with app.app_context():
        ticket_after = Ticket.query.get(ticket_id)
        print(f"\nAFTER API CALL:")
        print(f"  Status: {ticket_after.Status}")
        print(f"  Escalation Level: {ticket_after.escalation_level}")
        print(f"  Partner ID: {ticket_after.partner_id}")
        
        # Count logs after
        sla_logs_after = SLALog.query.filter_by(ticket_id=ticket_id).count()
        status_logs_after = TicketStatusLog.query.filter_by(ticket_id=ticket_id).count()
        print(f"  SLA Logs: {sla_logs_after} (was {sla_logs_before})")
        print(f"  Status Logs: {status_logs_after} (was {status_logs_before})")
        
        # Check the latest logs
        latest_sla = SLALog.query.filter_by(ticket_id=ticket_id).order_by(SLALog.escalated_at.desc()).first()
        latest_status = TicketStatusLog.query.filter_by(ticket_id=ticket_id).order_by(TicketStatusLog.changed_at.desc()).first()
        
        if latest_sla:
            print(f"\nLatest SLA Log:")
            print(f"  Level: {latest_sla.escalation_level}")
            print(f"  Partner ID: {latest_sla.assigned_partner_id}")
            print(f"  Created: {latest_sla.escalated_at}")
        
        if latest_status:
            print(f"\nLatest Status Log:")
            print(f"  Old Status: {latest_status.old_status}")
            print(f"  New Status: {latest_status.new_status}")
            print(f"  Level: {latest_status.escalation_level}")
            print(f"  Created: {latest_status.changed_at}")
        
        # Analysis
        logs_created = (sla_logs_after > sla_logs_before) or (status_logs_after > status_logs_before)
        ticket_updated = (
            ticket_after.Status != ticket_before.Status or 
            ticket_after.escalation_level != ticket_before.escalation_level or 
            ticket_after.partner_id != ticket_before.partner_id
        )
        
        print(f"\nANALYSIS:")
        print(f"  Logs were created: {logs_created}")
        print(f"  Ticket was updated: {ticket_updated}")
        
        if logs_created and not ticket_updated:
            print("  ISSUE: Function is being called and logs created, but ticket not updated!")
        elif not logs_created and not ticket_updated:
            print("  ISSUE: Function may not be called at all!")
        elif logs_created and ticket_updated:
            print("  SUCCESS: Everything working correctly!")

if __name__ == "__main__":
    escalate_and_check_immediately()
