#!/usr/bin/env python3
"""
Debug escalation partner assignment in detail
"""

import requests
import json

def debug_escalation_assignment():
    """Debug the escalation and partner assignment flow"""
    
    try:
        from app import app, db, Ticket
        from database import Partner, SLALog
        
        with app.app_context():
            print("=== DEBUGGING ESCALATION ASSIGNMENT ===\n")
            
            # 1. Check current partners
            print("1. CURRENT PARTNERS:")
            partners = Partner.query.all()
            for partner in partners:
                print(f"   • {partner.name} (ID: {partner.id})")
                print(f"     Type: {partner.partner_type}")
                print(f"     Status: {partner.status}")
                print(f"     Tickets handled: {partner.total_tickets_handled or 0}")
                print()
            
            # 2. Check recently escalated tickets
            print("2. RECENT ESCALATIONS:")
            recent_sla_logs = SLALog.query.filter(
                SLALog.escalated_at.isnot(None)
            ).order_by(SLALog.escalated_at.desc()).limit(5).all()
            
            for sla_log in recent_sla_logs:
                ticket = Ticket.query.get(sla_log.ticket_id)
                print(f"   • Ticket #{sla_log.ticket_id}: {ticket.Subject if ticket else 'Unknown'}")
                print(f"     Escalation Level: {sla_log.escalation_level} ({sla_log.level_name})")
                print(f"     SLA Status: {getattr(sla_log, 'status', 'No status')}")
                print(f"     Assigned Partner ID: {getattr(sla_log, 'assigned_partner_id', 'No partner ID')}")
                print(f"     Ticket Partner ID: {getattr(ticket, 'partner_id', 'No partner ID') if ticket else 'No ticket'}")
                print(f"     Escalated At: {sla_log.escalated_at}")
                print()
            
            # 3. Check tickets that should be assigned but aren't
            print("3. ESCALATED TICKETS WITHOUT PARTNERS:")
            escalated_tickets = Ticket.query.filter_by(Status='escalated').all()
            unassigned_count = 0
            
            for ticket in escalated_tickets:
                if not getattr(ticket, 'partner_id', None):
                    unassigned_count += 1
                    latest_sla = SLALog.query.filter_by(
                        ticket_id=ticket.TicketID
                    ).order_by(SLALog.escalated_at.desc()).first()
                    
                    print(f"   • Ticket #{ticket.TicketID}: {ticket.Subject}")
                    print(f"     Status: {ticket.Status}")
                    print(f"     Escalation Level: {getattr(ticket, 'escalation_level', 'Not set')}")
                    if latest_sla:
                        print(f"     Latest SLA Level: {latest_sla.escalation_level}")
                        print(f"     SLA Partner ID: {getattr(latest_sla, 'assigned_partner_id', 'None')}")
                    print()
            
            print(f"   Total unassigned escalated tickets: {unassigned_count}")
            
            # 4. Manual partner assignment test
            if escalated_tickets:
                print("\n4. TESTING MANUAL PARTNER ASSIGNMENT:")
                test_ticket = escalated_tickets[0]
                print(f"   Testing with Ticket #{test_ticket.TicketID}")
                
                # Get ICP partner
                icp_partner = Partner.query.filter_by(partner_type='ICP', status='active').first()
                if icp_partner:
                    print(f"   Found ICP partner: {icp_partner.name} (ID: {icp_partner.id})")
                    
                    # Assign manually
                    old_partner_id = getattr(test_ticket, 'partner_id', None)
                    test_ticket.partner_id = icp_partner.id
                    
                    # Update partner stats
                    icp_partner.total_tickets_handled = (icp_partner.total_tickets_handled or 0) + 1
                    
                    db.session.commit()
                    
                    print(f"   ✅ Assigned Ticket #{test_ticket.TicketID} to {icp_partner.name}")
                    print(f"   Previous partner ID: {old_partner_id}")
                    print(f"   New partner ID: {test_ticket.partner_id}")
                    print(f"   Partner tickets handled: {icp_partner.total_tickets_handled}")
                else:
                    print("   ❌ No ICP partner found")
            
            # 5. Test the force escalation function directly
            print("\n5. TESTING FORCE ESCALATION FUNCTION:")
            if escalated_tickets and len(escalated_tickets) > 1:
                test_ticket2 = escalated_tickets[1]
                print(f"   Testing force escalation on Ticket #{test_ticket2.TicketID}")
                
                # Simulate the force escalation data
                try:
                    # Find ICP partners
                    available_partners = Partner.query.filter_by(
                        partner_type='ICP',
                        status='active'
                    ).all()
                    
                    print(f"   Available ICP partners: {len(available_partners)}")
                    
                    if available_partners:
                        partner = available_partners[0]
                        print(f"   Would assign to: {partner.name}")
                        
                        # Check if ticket has partner_id attribute
                        if hasattr(test_ticket2, 'partner_id'):
                            print(f"   ✅ Ticket has partner_id attribute: {test_ticket2.partner_id}")
                        else:
                            print(f"   ❌ Ticket missing partner_id attribute")
                    else:
                        print("   ❌ No available ICP partners")
                        
                except Exception as e:
                    print(f"   ❌ Error in force escalation test: {e}")
            
            print("\n=== DEBUG COMPLETE ===")
            
    except Exception as e:
        print(f"❌ Error in debug: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_escalation_assignment()
