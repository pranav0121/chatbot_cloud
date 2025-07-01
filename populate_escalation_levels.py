#!/usr/bin/env python3
"""
Populate escalation levels for existing tickets
- normal: Regular tickets (low, medium priority)
- supervisor: High priority tickets  
- admin: Critical priority or escalated status tickets
"""

from app import app, db, Ticket
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def populate_escalation_levels():
    """Populate escalation levels for existing tickets"""
    logger.info("🔼 POPULATING ESCALATION LEVELS FOR EXISTING TICKETS")
    logger.info("=" * 60)
    
    with app.app_context():
        try:
            # Get all tickets
            tickets = Ticket.query.all()
            logger.info(f"📊 Found {len(tickets)} tickets to process")
            
            escalation_counts = {'normal': 0, 'supervisor': 0, 'admin': 0}
            updated_count = 0
            
            for ticket in tickets:
                # Determine escalation level based on priority and status
                if ticket.Priority == 'critical' or ticket.Status == 'escalated':
                    escalation_level = 'admin'
                elif ticket.Priority == 'high':
                    escalation_level = 'supervisor'
                else:
                    escalation_level = 'normal'
                
                # Update if needed
                if ticket.EscalationLevel != escalation_level:
                    old_level = ticket.EscalationLevel
                    ticket.EscalationLevel = escalation_level
                    updated_count += 1
                    
                    if updated_count <= 10:  # Show first 10 for logging
                        logger.info(f"   ✅ Ticket #{ticket.TicketID}: {ticket.Priority} priority, {ticket.Status} status → {escalation_level}")
                
                escalation_counts[escalation_level] += 1
            
            # Commit changes
            db.session.commit()
            logger.info(f"💾 Updated {updated_count} tickets with escalation levels")
            
            # Show distribution
            logger.info("\n📊 Final Escalation Level Distribution:")
            total = sum(escalation_counts.values())
            for level, count in escalation_counts.items():
                percentage = (count / total * 100) if total > 0 else 0
                logger.info(f"   {level.upper()}: {count} tickets ({percentage:.1f}%)")
            
            # Show sample tickets by escalation level
            logger.info("\n🎫 Sample Tickets by Escalation Level:")
            for level in ['normal', 'supervisor', 'admin']:
                sample_tickets = Ticket.query.filter(Ticket.EscalationLevel == level).limit(3).all()
                if sample_tickets:
                    logger.info(f"   📌 {level.upper()}:")
                    for ticket in sample_tickets:
                        logger.info(f"      #{ticket.TicketID}: {ticket.Subject[:40]}... (Priority: {ticket.Priority}, Status: {ticket.Status})")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error populating escalation levels: {e}")
            db.session.rollback()
            return False

if __name__ == "__main__":
    success = populate_escalation_levels()
    
    if success:
        logger.info("\n🎉 ESCALATION LEVELS POPULATED SUCCESSFULLY!")
        logger.info("✅ All tickets now have appropriate escalation levels")
        logger.info("✅ Distribution: normal, supervisor, admin levels assigned")
    else:
        logger.error("\n❌ ESCALATION LEVEL POPULATION FAILED")
