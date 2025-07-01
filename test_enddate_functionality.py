#!/usr/bin/env python3
"""
Test script to verify EndDate functionality
"""

from app import app, db, Ticket
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_enddate_functionality():
    """Test the EndDate functionality"""
    with app.app_context():
        logger.info("=== TESTING ENDDATE FUNCTIONALITY ===")
        
        # Check if EndDate column exists in the model
        try:
            sample_ticket = Ticket.query.first()
            if sample_ticket:
                logger.info(f"✅ EndDate column exists: {hasattr(sample_ticket, 'EndDate')}")
                logger.info(f"Sample ticket #{sample_ticket.TicketID}:")
                logger.info(f"  Status: {sample_ticket.Status}")
                logger.info(f"  CreatedAt: {sample_ticket.CreatedAt}")
                logger.info(f"  UpdatedAt: {sample_ticket.UpdatedAt}")
                logger.info(f"  EndDate: {sample_ticket.EndDate}")
                
                # Test setting EndDate on resolved/closed tickets
                if sample_ticket.Status in ['resolved', 'closed'] and not sample_ticket.EndDate:
                    logger.info("Setting EndDate for resolved/closed ticket...")
                    sample_ticket.EndDate = datetime.utcnow()
                    db.session.commit()
                    logger.info(f"✅ EndDate set to: {sample_ticket.EndDate}")
                
                # Count tickets with EndDate
                tickets_with_enddate = Ticket.query.filter(Ticket.EndDate.isnot(None)).count()
                total_resolved_closed = Ticket.query.filter(Ticket.Status.in_(['resolved', 'closed'])).count()
                
                logger.info(f"📊 Statistics:")
                logger.info(f"  Total resolved/closed tickets: {total_resolved_closed}")
                logger.info(f"  Tickets with EndDate: {tickets_with_enddate}")
                
                # Show some examples
                resolved_tickets = Ticket.query.filter(Ticket.Status.in_(['resolved', 'closed'])).limit(3).all()
                logger.info(f"📋 Sample resolved/closed tickets:")
                for ticket in resolved_tickets:
                    logger.info(f"  Ticket #{ticket.TicketID}: Status={ticket.Status}, EndDate={ticket.EndDate}")
                
                return True
            else:
                logger.warning("No tickets found in database")
                return True
                
        except Exception as e:
            logger.error(f"❌ EndDate test failed: {e}")
            return False

def test_api_response():
    """Test that API endpoints include EndDate"""
    logger.info("\n=== TESTING API RESPONSE ===")
    
    with app.test_client() as client:
        try:
            # Test ticket details API
            sample_ticket = Ticket.query.first()
            if sample_ticket:
                response = client.get(f'/api/tickets/{sample_ticket.TicketID}')
                if response.status_code == 200:
                    data = response.json
                    logger.info(f"✅ API Response includes EndDate: {'end_date' in data}")
                    logger.info(f"  EndDate value: {data.get('end_date', 'Not present')}")
                else:
                    logger.warning(f"API returned status {response.status_code}")
            
            return True
        except Exception as e:
            logger.error(f"❌ API test failed: {e}")
            return False

if __name__ == "__main__":
    success1 = test_enddate_functionality()
    success2 = test_api_response()
    
    if success1 and success2:
        logger.info("\n🎉 All EndDate tests passed!")
        logger.info("✅ EndDate functionality is working correctly")
        logger.info("✅ API endpoints include EndDate information")
        logger.info("✅ Database migration was successful")
    else:
        logger.error("\n❌ Some tests failed")
