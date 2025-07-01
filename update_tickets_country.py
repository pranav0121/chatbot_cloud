#!/usr/bin/env python3
"""
Update existing tickets with detected country information
"""

from app import app, db, Ticket
from location_service import location_service
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def update_existing_tickets_country():
    """Update existing tickets with detected country information"""
    logger.info("🎫 UPDATING EXISTING TICKETS WITH COUNTRY INFORMATION")
    logger.info("=" * 60)
    
    with app.app_context():
        try:
            # Get current location (India)
            location_info = location_service.get_current_location()
            if not location_info:
                logger.error("❌ Could not detect location")
                return False
            
            detected_country = location_info['country']
            logger.info(f"🎯 Detected country: {detected_country}")
            logger.info(f"   City: {location_info['city']}")
            logger.info(f"   Region: {location_info['region']}")
            
            # Get tickets with Unknown or NULL country
            tickets_to_update = Ticket.query.filter(
                db.or_(
                    Ticket.Country == None,
                    Ticket.Country == 'Unknown',
                    Ticket.Country == ''
                )
            ).all()
            
            logger.info(f"📊 Found {len(tickets_to_update)} tickets to update")
            
            if len(tickets_to_update) == 0:
                logger.info("ℹ️  No tickets need country updates")
                return True
            
            # Update tickets
            updated_count = 0
            for ticket in tickets_to_update:
                try:
                    old_country = ticket.Country
                    ticket.Country = detected_country
                    
                    logger.info(f"   ✅ Ticket #{ticket.TicketID} ({ticket.Subject[:30]}...): {old_country} → {detected_country}")
                    updated_count += 1
                    
                except Exception as e:
                    logger.error(f"   ❌ Failed to update Ticket #{ticket.TicketID}: {e}")
            
            # Commit changes
            db.session.commit()
            logger.info(f"💾 Database updated: {updated_count} tickets saved")
            
            # Verify updates
            logger.info("\n📋 Verification:")
            tickets_with_country = Ticket.query.filter(Ticket.Country == detected_country).count()
            total_tickets = Ticket.query.count()
            coverage = (tickets_with_country / total_tickets * 100) if total_tickets > 0 else 0
            
            logger.info(f"   Tickets with {detected_country}: {tickets_with_country}/{total_tickets}")
            logger.info(f"   Coverage: {coverage:.1f}%")
            
            # Show sample updated tickets by status
            logger.info("\n🎫 Sample Updated Tickets by Status:")
            statuses = ['open', 'in_progress', 'resolved', 'closed', 'escalated']
            
            for status in statuses:
                tickets = Ticket.query.filter(
                    Ticket.Status == status,
                    Ticket.Country == detected_country
                ).limit(2).all()
                
                if tickets:
                    logger.info(f"   📌 {status.upper()} tickets:")
                    for ticket in tickets:
                        logger.info(f"      Ticket #{ticket.TicketID}: {ticket.Subject[:40]}... - {ticket.Country}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error updating tickets: {e}")
            db.session.rollback()
            return False

if __name__ == "__main__":
    success = update_existing_tickets_country()
    
    if success:
        logger.info("\n🎉 TICKETS COUNTRY UPDATE COMPLETE!")
        logger.info("✅ All existing tickets now have country information")
    else:
        logger.error("\n❌ TICKETS COUNTRY UPDATE FAILED")
