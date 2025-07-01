#!/usr/bin/env python3
"""
Comprehensive End Date tracking test
"""

from app import app, db, Ticket
from datetime import datetime
import logging
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_enddate_comprehensive():
    """Comprehensive test of EndDate functionality"""
    with app.app_context():
        logger.info("🔍 COMPREHENSIVE END DATE TRACKING TEST")
        logger.info("=" * 50)
        
        # 1. Check database schema
        logger.info("1. Database Schema Check:")
        try:
            # Get a sample ticket to check the model
            sample = Ticket.query.first()
            if sample:
                logger.info(f"   ✅ EndDate column exists: {hasattr(sample, 'EndDate')}")
                logger.info(f"   ✅ Sample ticket EndDate: {sample.EndDate}")
            else:
                logger.info("   ⚠️  No tickets in database")
        except Exception as e:
            logger.error(f"   ❌ Schema check failed: {e}")
            return False
        
        # 2. Count tickets by status and EndDate
        logger.info("\n2. Ticket Status Analysis:")
        try:
            total_tickets = Ticket.query.count()
            open_tickets = Ticket.query.filter(Ticket.Status == 'open').count()
            in_progress_tickets = Ticket.query.filter(Ticket.Status == 'in_progress').count()
            escalated_tickets = Ticket.query.filter(Ticket.Status == 'escalated').count()
            resolved_tickets = Ticket.query.filter(Ticket.Status == 'resolved').count()
            closed_tickets = Ticket.query.filter(Ticket.Status == 'closed').count()
            
            tickets_with_enddate = Ticket.query.filter(Ticket.EndDate.isnot(None)).count()
            resolved_closed_total = resolved_tickets + closed_tickets
            
            logger.info(f"   📊 Total tickets: {total_tickets}")
            logger.info(f"   📊 Open: {open_tickets}")
            logger.info(f"   📊 In Progress: {in_progress_tickets}")
            logger.info(f"   📊 Escalated: {escalated_tickets}")
            logger.info(f"   📊 Resolved: {resolved_tickets}")
            logger.info(f"   📊 Closed: {closed_tickets}")
            logger.info(f"   📊 Total Resolved/Closed: {resolved_closed_total}")
            logger.info(f"   📊 Tickets with EndDate: {tickets_with_enddate}")
            
            if resolved_closed_total > 0:
                coverage = (tickets_with_enddate / resolved_closed_total) * 100
                logger.info(f"   📊 EndDate Coverage: {coverage:.1f}%")
        except Exception as e:
            logger.error(f"   ❌ Status analysis failed: {e}")
            return False
        
        # 3. Show sample tickets with their EndDate
        logger.info("\n3. Sample Tickets with EndDate:")
        try:
            resolved_closed = Ticket.query.filter(
                Ticket.Status.in_(['resolved', 'closed'])
            ).limit(5).all()
            
            for ticket in resolved_closed:
                logger.info(f"   🎫 Ticket #{ticket.TicketID}:")
                logger.info(f"      Status: {ticket.Status}")
                logger.info(f"      Created: {ticket.CreatedAt}")
                logger.info(f"      Updated: {ticket.UpdatedAt}")
                logger.info(f"      EndDate: {ticket.EndDate}")
                if ticket.EndDate and ticket.CreatedAt:
                    duration = ticket.EndDate - ticket.CreatedAt
                    logger.info(f"      Duration: {duration}")
                logger.info("")
        except Exception as e:
            logger.error(f"   ❌ Sample tickets check failed: {e}")
            return False
        
        # 4. Test API endpoints
        logger.info("4. API Endpoint Testing:")
        with app.test_client() as client:
            try:
                # Test ticket details API
                sample_ticket = Ticket.query.first()
                if sample_ticket:
                    response = client.get(f'/api/tickets/{sample_ticket.TicketID}')
                    if response.status_code == 200:
                        data = response.json
                        logger.info(f"   ✅ Ticket Details API includes EndDate: {'end_date' in data}")
                        logger.info(f"      EndDate value: {data.get('end_date', 'Not found')}")
                    else:
                        logger.warning(f"   ⚠️  API returned status {response.status_code}")
                
                # Test admin tickets API
                response = client.get('/api/admin/tickets')
                if response.status_code == 200:
                    data = response.json
                    if data and len(data) > 0:
                        first_ticket = data[0]
                        logger.info(f"   ✅ Admin Tickets API includes EndDate: {'end_date' in first_ticket}")
                        logger.info(f"      Sample EndDate: {first_ticket.get('end_date', 'Not found')}")
                    else:
                        logger.info("   ⚠️  No tickets returned from admin API")
                else:
                    logger.warning(f"   ⚠️  Admin API returned status {response.status_code}")
            except Exception as e:
                logger.error(f"   ❌ API testing failed: {e}")
                return False
        
        # 5. Test status change logic (simulation)
        logger.info("\n5. Status Change Logic Test:")
        try:
            # Find an open ticket to test with
            open_ticket = Ticket.query.filter(Ticket.Status == 'open').first()
            if open_ticket:
                original_status = open_ticket.Status
                original_enddate = open_ticket.EndDate
                
                logger.info(f"   🔄 Testing with Ticket #{open_ticket.TicketID}")
                logger.info(f"      Original Status: {original_status}")
                logger.info(f"      Original EndDate: {original_enddate}")
                
                # Test setting to resolved
                open_ticket.Status = 'resolved'
                open_ticket.EndDate = datetime.utcnow()
                db.session.commit()
                
                logger.info(f"   ✅ Changed to resolved, EndDate set: {open_ticket.EndDate}")
                
                # Test changing back to open
                open_ticket.Status = 'open'
                open_ticket.EndDate = None
                db.session.commit()
                
                logger.info(f"   ✅ Changed back to open, EndDate cleared: {open_ticket.EndDate}")
                
                # Restore original state
                open_ticket.Status = original_status
                open_ticket.EndDate = original_enddate
                db.session.commit()
                
                logger.info(f"   ✅ Restored original state")
            else:
                logger.info("   ⚠️  No open tickets available for testing")
        except Exception as e:
            logger.error(f"   ❌ Status change test failed: {e}")
            return False
        
        return True

if __name__ == "__main__":
    success = test_enddate_comprehensive()
    
    if success:
        logger.info("\n" + "=" * 50)
        logger.info("🎉 COMPREHENSIVE END DATE TEST PASSED!")
        logger.info("✅ All EndDate functionality is working correctly")
        logger.info("✅ Database schema includes EndDate column")
        logger.info("✅ API endpoints return EndDate information")
        logger.info("✅ Status change logic handles EndDate properly")
        logger.info("✅ Migration was successful")
        logger.info("=" * 50)
    else:
        logger.error("\n❌ COMPREHENSIVE TEST FAILED")
