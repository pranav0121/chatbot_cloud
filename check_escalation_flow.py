#!/usr/bin/env python3
"""
Check existing partners and escalation assignments
"""

def check_escalation_flow():
    """Check current partners and escalation assignments"""
    
    try:
        # Import here to avoid circular imports
        from app import app, db, Ticket, User, Category
        from models import Partner, SLALog
        
        with app.app_context():
            print("=== ESCALATION FLOW ANALYSIS ===\n")
            
            # Check existing partners
            print("1. EXISTING PARTNERS:")
            partners = Partner.query.all()
            
            if partners:
                for partner in partners:
                    print(f"   • {partner.name}")
                    print(f"     Type: {partner.partner_type}")
                    print(f"     Email: {partner.email}")
                    print(f"     Status: {partner.status}")
                    print(f"     Contact: {partner.contact_person or 'Not specified'}")
                    print(f"     Phone: {partner.phone or 'Not specified'}")
                    print(f"     Webhook URL: {partner.webhook_url or 'Not configured'}")
                    print(f"     Tickets Handled: {partner.total_tickets_handled}")
                    print(f"     Avg Resolution Time: {partner.avg_resolution_time:.1f} hours")
                    print(f"     Rating: {partner.satisfaction_rating:.1f}/5.0")
                    print()
            else:
                print("   No partners found in database")
                print("   → Escalated tickets won't be automatically assigned")
                print()
            
            # Check recent escalations
            print("2. RECENT ESCALATIONS:")
            recent_escalations = SLALog.query.filter(
                SLALog.escalated_at.isnot(None)
            ).order_by(SLALog.escalated_at.desc()).limit(10).all()
            
            if recent_escalations:
                for sla_log in recent_escalations:
                    ticket = Ticket.query.get(sla_log.ticket_id)
                    partner_assignment = f" → Assigned to Partner ID {ticket.partner_id}" if hasattr(ticket, 'partner_id') and ticket.partner_id else " → No partner assigned"
                    
                    print(f"   • Ticket #{sla_log.ticket_id}: {ticket.Subject if ticket else 'Unknown'}")
                    print(f"     Escalated to: {sla_log.level_name} (Level {sla_log.escalation_level})")
                    print(f"     Escalated at: {sla_log.escalated_at}")
                    print(f"     SLA Target: {sla_log.sla_target_hours} hours")
                    print(f"     Assignment: {partner_assignment}")
                    print()
            else:
                print("   No escalations found")
                print()
            
            # Check tickets with partner assignments
            print("3. TICKETS WITH PARTNER ASSIGNMENTS:")
            # This may not work if partner_id column doesn't exist
            try:
                assigned_tickets = Ticket.query.filter(
                    Ticket.partner_id.isnot(None)
                ).all()
                
                if assigned_tickets:
                    for ticket in assigned_tickets:
                        partner = Partner.query.get(ticket.partner_id)
                        print(f"   • Ticket #{ticket.TicketID}: {ticket.Subject}")
                        print(f"     Assigned to: {partner.name if partner else 'Unknown Partner'}")
                        print(f"     Partner Type: {partner.partner_type if partner else 'Unknown'}")
                        print()
                else:
                    print("   No tickets currently assigned to partners")
                    print()
            except Exception as e:
                print(f"   Could not check partner assignments: {e}")
                print("   (partner_id column may not exist in Tickets table)")
                print()
            
            # Summary
            print("4. ESCALATION FLOW SUMMARY:")
            print("   Level 0 (Bot): Automated response, 0 hour SLA")
            print("   Level 1 (ICP): Implementation and Customization Partners, 4 hour SLA")
            print("   Level 2 (YouCloud): YouCloud Technical Team, 24 hour SLA")
            print()
            print("   When escalated:")
            print("   • Creates SLA log entry with target times")
            print("   • Updates ticket status to 'escalated'")
            print("   • Attempts to assign to available partner")
            print("   • Sends webhook notification to partner (if configured)")
            print("   • Logs admin action for audit trail")
            print()
            
            if not partners:
                print("⚠ WARNING: No partners configured!")
                print("   Escalated tickets will not be automatically assigned.")
                print("   They will remain in 'escalated' status waiting for manual assignment.")
                print()
            
    except Exception as e:
        print(f"Error checking escalation flow: {e}")

if __name__ == "__main__":
    check_escalation_flow()
