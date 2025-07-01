#!/usr/bin/env python3
"""
Fix escalation partner assignment issues
"""

import logging
from datetime import datetime

logger = logging.getLogger(__name__)

def fix_escalation_partner_assignment():
    """Fix all escalation and partner assignment issues"""
    
    try:
        from app import app, db, Ticket
        from models import Partner, SLALog
        
        with app.app_context():
            print("=== FIXING ESCALATION PARTNER ASSIGNMENT ===\n")
            
            # 1. Check and create missing YouCloud partners
            print("1. Checking for YouCloud (Level 2) partners...")
            ycp_partners = Partner.query.filter_by(partner_type='YCP', status='active').all()
            
            if not ycp_partners:
                print("   Creating YouCloud technical team partner...")
                
                youcloud_partner = Partner(
                    name='YouCloud Technical Team',
                    partner_type='YCP',
                    email='technical@youcloud.com',
                    contact_person='Technical Support Manager',
                    phone='+1-555-YOUCLOUD',
                    status='active',
                    webhook_url='https://youcloud.com/api/support/webhook',  # placeholder
                    escalation_settings=json.dumps({
                        'sla_hours': 24,
                        'auto_assign': True,
                        'notification_email': 'technical@youcloud.com'
                    }),
                    sla_settings=json.dumps({
                        'response_time': 2,  # 2 hours max response time
                        'resolution_time': 24  # 24 hours max resolution time
                    }),
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                
                db.session.add(youcloud_partner)
                db.session.commit()
                print("   ✅ YouCloud partner created successfully")
            else:
                print(f"   ✅ Found {len(ycp_partners)} YouCloud partners")
            
            # 2. Fix partner type mapping
            print("\n2. Checking partner type mapping...")
            icp_partners = Partner.query.filter_by(partner_type='ICP', status='active').all()
            print(f"   ICP Partners: {len(icp_partners)}")
            ycp_partners = Partner.query.filter_by(partner_type='YCP', status='active').all()
            print(f"   YCP Partners: {len(ycp_partners)}")
            
            if not icp_partners:
                print("   ⚠ Warning: No ICP partners found")
            if not ycp_partners:
                print("   ⚠ Warning: No YCP partners found")
            
            # 3. Update escalated tickets that don't have partner assignments
            print("\n3. Fixing unassigned escalated tickets...")
            
            # Find tickets that are escalated but not assigned to partners
            unassigned_tickets = db.session.query(Ticket).filter(
                Ticket.Status == 'escalated',
                Ticket.partner_id.is_(None)
            ).all()
            
            print(f"   Found {len(unassigned_tickets)} unassigned escalated tickets")
            
            assigned_count = 0
            for ticket in unassigned_tickets:
                try:
                    # Get the latest SLA log for this ticket
                    latest_sla = SLALog.query.filter_by(
                        ticket_id=ticket.TicketID
                    ).order_by(SLALog.escalated_at.desc()).first()
                    
                    if latest_sla:
                        # Assign partner based on escalation level
                        if latest_sla.escalation_level == 1:
                            # Level 1 -> ICP
                            available_partners = Partner.query.filter_by(
                                partner_type='ICP',
                                status='active'
                            ).all()
                        elif latest_sla.escalation_level == 2:
                            # Level 2 -> YouCloud
                            available_partners = Partner.query.filter_by(
                                partner_type='YCP',
                                status='active'
                            ).all()
                        else:
                            available_partners = []
                        
                        if available_partners:
                            # Assign to first available partner (you could implement load balancing here)
                            partner = available_partners[0]
                            ticket.partner_id = partner.id
                            
                            # Update SLA log with partner assignment
                            latest_sla.assigned_partner_id = partner.id
                            latest_sla.status = 'assigned'
                            
                            # Update partner statistics
                            partner.total_tickets_handled = (partner.total_tickets_handled or 0) + 1
                            
                            assigned_count += 1
                            
                            print(f"   ✅ Assigned Ticket #{ticket.TicketID} to {partner.name} ({partner.partner_type})")
                        else:
                            print(f"   ⚠ No available partners for level {latest_sla.escalation_level} (Ticket #{ticket.TicketID})")
                    
                except Exception as e:
                    print(f"   ❌ Error assigning Ticket #{ticket.TicketID}: {e}")
            
            db.session.commit()
            print(f"   ✅ Successfully assigned {assigned_count} tickets to partners")
            
            # 4. Create sample webhook URL for demo partner
            print("\n4. Updating demo partner configuration...")
            demo_partner = Partner.query.filter_by(name='Demo ICP Partner').first()
            if demo_partner:
                if not demo_partner.webhook_url:
                    demo_partner.webhook_url = 'https://demo-icp.example.com/api/support/webhook'
                
                if not demo_partner.escalation_settings:
                    demo_partner.escalation_settings = json.dumps({
                        'sla_hours': 4,
                        'auto_assign': True,
                        'notification_email': demo_partner.email
                    })
                
                if not demo_partner.sla_settings:
                    demo_partner.sla_settings = json.dumps({
                        'response_time': 1,  # 1 hour max response time
                        'resolution_time': 4  # 4 hours max resolution time
                    })
                
                db.session.commit()
                print("   ✅ Demo partner configuration updated")
            
            # 5. Summary
            print("\n=== SUMMARY ===")
            all_partners = Partner.query.filter_by(status='active').all()
            for partner in all_partners:
                assigned_tickets = Ticket.query.filter_by(partner_id=partner.id).count()
                print(f"• {partner.name} ({partner.partner_type})")
                print(f"  - Assigned tickets: {assigned_tickets}")
                print(f"  - Total handled: {partner.total_tickets_handled or 0}")
                print(f"  - Webhook: {'✅' if partner.webhook_url else '❌'}")
                print(f"  - Settings: {'✅' if partner.escalation_settings else '❌'}")
                print()
            
            print("✅ All escalation issues have been fixed!")
            
    except Exception as e:
        print(f"❌ Error fixing escalation issues: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    import json
    fix_escalation_partner_assignment()
