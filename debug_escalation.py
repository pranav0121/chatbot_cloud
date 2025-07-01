#!/usr/bin/env python3
"""
Debug escalation dashboard directly
"""

from app import app, db, Ticket, Message, User
from datetime import datetime

def debug_escalation_logic():
    with app.app_context():
        print("=== DEBUGGING ESCALATION LOGIC ===\n")
        
        # Get active tickets (same query as API)
        tickets = db.session.query(Ticket).filter(
            Ticket.Status.in_(['open', 'in_progress'])
        ).order_by(Ticket.Priority.desc(), Ticket.CreatedAt.desc()).all()
        
        print(f"Found {len(tickets)} active tickets")
        
        if len(tickets) == 0:
            print("❌ No active tickets found!")
            return
        
        current_time = datetime.utcnow()
        within_sla = 0
        sla_warning = 0
        sla_breached = 0
        
        # Process first few tickets to see what happens
        for i, ticket in enumerate(tickets[:5]):
            print(f"\n--- Ticket {i+1}: ID {ticket.TicketID} ---")
            print(f"Priority: {ticket.Priority}")
            print(f"Status: {ticket.Status}")
            print(f"Created: {ticket.CreatedAt}")
            
            try:
                # Same logic as API
                hours_passed = (current_time - ticket.CreatedAt).total_seconds() / 3600
                print(f"Hours passed: {hours_passed:.2f}")
                
                # SLA targets based on priority (handle None priority)
                sla_targets = {
                    'critical': 2,
                    'high': 4,
                    'medium': 24,
                    'low': 48
                }
                
                # Handle None priority or invalid priority
                priority = ticket.Priority
                if priority is None:
                    priority = 'medium'  # Default priority
                    print(f"Priority was None, using default: {priority}")
                
                target_hours = sla_targets.get(priority.lower(), 24)
                print(f"Target hours for {priority}: {target_hours}")
                
                time_remaining = target_hours - hours_passed
                print(f"Time remaining: {time_remaining:.2f} hours")
                
                # Determine SLA status
                if time_remaining < 0:
                    sla_status = 'red'
                    sla_breached += 1
                    print(f"SLA Status: BREACHED (red)")
                elif time_remaining < target_hours * 0.25:  # 25% of target time left
                    sla_status = 'orange'
                    sla_warning += 1
                    print(f"SLA Status: WARNING (orange)")
                else:
                    sla_status = 'green'
                    within_sla += 1
                    print(f"SLA Status: OK (green)")
                    
            except Exception as e:
                print(f"❌ Error processing ticket: {e}")
        
        print(f"\n=== FINAL COUNTS ===")
        print(f"Within SLA: {within_sla}")
        print(f"SLA Warning: {sla_warning}")
        print(f"SLA Breached: {sla_breached}")
        print(f"Total processed: {within_sla + sla_warning + sla_breached}")

if __name__ == "__main__":
    debug_escalation_logic()
