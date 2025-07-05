#!/usr/bin/env python3
"""
Test database updates directly without going through the API
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db, Ticket
from database import SLALog, TicketStatusLog, Partner
from datetime import datetime

def test_direct_ticket_update():
    with app.app_context():
        print("=== TESTING DIRECT TICKET UPDATE ===")
        
        # Get ticket 51
        ticket_id = 51
        ticket = Ticket.query.get(ticket_id)
        
        if not ticket:
            print(f"Ticket {ticket_id} not found")
            return
        
        print(f"BEFORE UPDATE:")
        print(f"  Status: {ticket.Status}")
        print(f"  Escalation Level: {ticket.escalation_level}")
        print(f"  Partner ID: {ticket.partner_id}")
        print(f"  Updated At: {ticket.UpdatedAt}")
        
        # Make changes
        old_status = ticket.Status
        old_escalation_level = ticket.escalation_level
        old_partner_id = ticket.partner_id
        
        print(f"\nMAKING CHANGES...")
        ticket.Status = 'escalated'
        ticket.escalation_level = 1
        ticket.partner_id = 1  # Demo ICP Partner
        ticket.UpdatedAt = datetime.utcnow()
        
        print(f"  New Status: {ticket.Status}")
        print(f"  New Escalation Level: {ticket.escalation_level}")
        print(f"  New Partner ID: {ticket.partner_id}")
        print(f"  New Updated At: {ticket.UpdatedAt}")
        
        # Commit changes
        try:
            print(f"\nCOMMITTING CHANGES...")
            db.session.commit()
            print("Commit successful!")
        except Exception as e:
            print(f"Commit failed: {e}")
            db.session.rollback()
            return
        
        # Re-query the ticket to verify changes
        print(f"\nRE-QUERYING TICKET...")
        db.session.refresh(ticket)  # Refresh from database
        
        print(f"AFTER UPDATE (re-queried):")
        print(f"  Status: {ticket.Status}")
        print(f"  Escalation Level: {ticket.escalation_level}")
        print(f"  Partner ID: {ticket.partner_id}")
        print(f"  Updated At: {ticket.UpdatedAt}")
        
        # Verify changes took effect
        if ticket.Status == 'escalated':
            print("✓ Status update successful")
        else:
            print(f"✗ Status update failed (expected 'escalated', got '{ticket.Status}')")
            
        if ticket.escalation_level == 1:
            print("✓ Escalation level update successful")
        else:
            print(f"✗ Escalation level update failed (expected 1, got {ticket.escalation_level})")
            
        if ticket.partner_id == 1:
            print("✓ Partner ID update successful")
        else:
            print(f"✗ Partner ID update failed (expected 1, got {ticket.partner_id})")
        
        # Rollback changes for testing
        print(f"\nROLLING BACK CHANGES FOR NEXT TEST...")
        ticket.Status = old_status
        ticket.escalation_level = old_escalation_level
        ticket.partner_id = old_partner_id
        db.session.commit()
        print("Rollback complete")

if __name__ == "__main__":
    test_direct_ticket_update()
