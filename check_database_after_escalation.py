#!/usr/bin/env python3
"""
Check the database directly for SLA logs and ticket status after escalation
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db, Ticket
from database import SLALog, TicketStatusLog, Partner

def check_database_after_escalation():
    with app.app_context():
        print("=== CHECKING DATABASE AFTER ESCALATION ===")
        
        # Check specific ticket 51
        ticket_id = 51
        ticket = Ticket.query.get(ticket_id)
        
        if ticket:
            print(f"\nTicket {ticket_id} in database:")
            print(f"  Subject: {ticket.Subject}")
            print(f"  Status: {ticket.Status}")
            print(f"  Escalation Level: {getattr(ticket, 'escalation_level', 'No column')}")
            print(f"  Updated At: {ticket.UpdatedAt}")
            print(f"  Partner ID: {getattr(ticket, 'partner_id', 'No column')}")
        else:
            print(f"Ticket {ticket_id} not found")
        
        # Check SLA logs for this ticket
        print(f"\nSLA Logs for ticket {ticket_id}:")
        sla_logs = SLALog.query.filter_by(ticket_id=ticket_id).order_by(SLALog.escalated_at.desc()).all()
        
        if sla_logs:
            for i, log in enumerate(sla_logs):
                print(f"  Log {i+1}:")
                print(f"    Escalation Level: {log.escalation_level}")
                print(f"    Level Name: {log.level_name}")
                print(f"    Escalated At: {log.escalated_at}")
                print(f"    Assigned Partner ID: {log.assigned_partner_id}")
                print(f"    Status: {log.status}")
        else:
            print("  No SLA logs found")
        
        # Check ticket status logs
        print(f"\nTicket Status Logs for ticket {ticket_id}:")
        status_logs = TicketStatusLog.query.filter_by(ticket_id=ticket_id).order_by(TicketStatusLog.changed_at.desc()).all()
        
        if status_logs:
            for i, log in enumerate(status_logs[:5]):  # Show last 5
                print(f"  Log {i+1}:")
                print(f"    Old Status: {log.old_status}")
                print(f"    New Status: {log.new_status}")
                print(f"    Changed At: {log.changed_at}")
                print(f"    Changed By: {log.changed_by_type} (ID: {log.changed_by_id})")
                print(f"    Escalation Level: {log.escalation_level}")
                print(f"    Comment: {log.comment}")
        else:
            print("  No status logs found")
        
        # Check available partners
        print(f"\nAvailable Partners:")
        icp_partners = Partner.query.filter_by(partner_type='ICP', status='active').all()
        ycp_partners = Partner.query.filter_by(partner_type='YCP', status='active').all()
        
        print(f"  ICP Partners: {len(icp_partners)}")
        for partner in icp_partners:
            print(f"    - {partner.name} (ID: {partner.id})")
        
        print(f"  YCP Partners: {len(ycp_partners)}")
        for partner in ycp_partners:
            print(f"    - {partner.name} (ID: {partner.id})")
        
        # Check if ticket table has the escalation_level column
        print(f"\nChecking ticket table structure...")
        try:
            result = db.session.execute("SELECT TOP 1 escalation_level FROM Tickets WHERE TicketID = :ticket_id", {"ticket_id": ticket_id})
            escalation_level = result.scalar()
            print(f"  escalation_level column exists, value for ticket {ticket_id}: {escalation_level}")
        except Exception as e:
            print(f"  escalation_level column may not exist: {e}")
        
        try:
            result = db.session.execute("SELECT TOP 1 partner_id FROM Tickets WHERE TicketID = :ticket_id", {"ticket_id": ticket_id})
            partner_id = result.scalar()
            print(f"  partner_id column exists, value for ticket {ticket_id}: {partner_id}")
        except Exception as e:
            print(f"  partner_id column may not exist: {e}")

if __name__ == "__main__":
    check_database_after_escalation()
