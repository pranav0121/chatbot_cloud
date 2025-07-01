#!/usr/bin/env python3
"""
Add EscalationLevel field to Tickets table
- normal: Regular escalation level
- supervisor: Supervisor escalation level  
- admin: Admin escalation level
"""

from app import app, db, Ticket
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def add_escalation_level_field():
    """Add EscalationLevel field to Tickets table"""
    logger.info("🔼 ADDING ESCALATION LEVEL FIELD TO TICKETS")
    logger.info("=" * 50)
    
    with app.app_context():
        try:
            # Check if column already exists
            inspector = db.inspect(db.engine)
            columns = [col['name'] for col in inspector.get_columns('Tickets')]
            
            if 'EscalationLevel' in columns:
                logger.info("✅ EscalationLevel column already exists")
                
                # Count existing tickets
                total_tickets = Ticket.query.count()
                tickets_with_escalation = Ticket.query.filter(Ticket.EscalationLevel.isnot(None)).count()
                logger.info(f"📊 Total tickets: {total_tickets}")
                logger.info(f"📊 Tickets with escalation level: {tickets_with_escalation}")
                
                return True
            
            # Add EscalationLevel column (SQL Server syntax)
            logger.info("📝 Adding EscalationLevel column to Tickets table...")
            with db.engine.connect() as conn:
                trans = conn.begin()
                conn.execute(db.text("ALTER TABLE Tickets ADD EscalationLevel NVARCHAR(20) DEFAULT 'normal'"))
                trans.commit()
            
            logger.info("✅ EscalationLevel column added successfully")
            
            # Set default escalation levels based on ticket status and priority
            logger.info("🔄 Setting default escalation levels for existing tickets...")
            
            tickets = Ticket.query.all()
            updated_count = 0
            
            for ticket in tickets:
                # Determine escalation level based on priority and status
                if ticket.Priority == 'critical' or ticket.Status == 'escalated':
                    escalation_level = 'admin'
                elif ticket.Priority == 'high':
                    escalation_level = 'supervisor'
                else:
                    escalation_level = 'normal'
                
                # Update ticket escalation level
                ticket.EscalationLevel = escalation_level
                updated_count += 1
                
                if updated_count <= 10:  # Show first 10 for logging
                    logger.info(f"   Ticket #{ticket.TicketID}: {ticket.Priority} priority → {escalation_level} escalation")
            
            # Commit changes
            db.session.commit()
            logger.info(f"💾 Updated {updated_count} tickets with escalation levels")
            
            # Verify the updates
            logger.info("\n📊 Escalation Level Distribution:")
            normal_count = Ticket.query.filter(Ticket.EscalationLevel == 'normal').count()
            supervisor_count = Ticket.query.filter(Ticket.EscalationLevel == 'supervisor').count()
            admin_count = Ticket.query.filter(Ticket.EscalationLevel == 'admin').count()
            
            logger.info(f"   Normal: {normal_count} tickets")
            logger.info(f"   Supervisor: {supervisor_count} tickets")
            logger.info(f"   Admin: {admin_count} tickets")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error adding EscalationLevel field: {e}")
            db.session.rollback()
            return False

if __name__ == "__main__":
    success = add_escalation_level_field()
    
    if success:
        logger.info("\n🎉 ESCALATION LEVEL FIELD ADDED SUCCESSFULLY!")
        logger.info("✅ EscalationLevel column added to Tickets table")
        logger.info("✅ Existing tickets assigned appropriate escalation levels")
        logger.info("✅ Ready for escalation level tracking")
    else:
        logger.error("\n❌ ESCALATION LEVEL FIELD ADDITION FAILED")
