#!/usr/bin/env python3
"""
Quick test to verify tag handling fix in Odoo integration
"""
import os
import sys
from dotenv import load_dotenv
from odoo_service import OdooService
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_tag_fix():
    """Test the tag handling fix"""
    try:
        # Load environment variables
        load_dotenv()
          # Initialize Odoo service
        logger.info("🔄 Initializing Odoo service...")
        
        # Get Odoo credentials from environment
        odoo_url = os.getenv('ODOO_URL')
        odoo_db = os.getenv('ODOO_DB')
        odoo_username = os.getenv('ODOO_USERNAME')
        odoo_password = os.getenv('ODOO_PASSWORD')
        
        if not all([odoo_url, odoo_db, odoo_username, odoo_password]):
            logger.error("❌ Missing Odoo credentials in .env file")
            return False
            
        odoo_service = OdooService(odoo_url, odoo_db, odoo_username, odoo_password)
        
        # Test tag creation/lookup
        logger.info("📋 Testing tag creation/lookup...")
        tag_id = odoo_service.get_or_create_tag("test-tag-from-chatbot")
        if tag_id:
            logger.info(f"✅ Tag handling works! Tag ID: {tag_id}")
        else:
            logger.error("❌ Tag handling failed!")
            return False
            
        # Test ticket creation with tags
        logger.info("🎫 Testing ticket creation with tags...")
        
        # Create a test ticket with tags
        ticket_id = odoo_service.create_ticket(
            name="Test Ticket - Tag Fix Verification",
            description="This is a test ticket to verify tag handling is working correctly.",
            priority='1',
            tag_ids=['test-tag-from-chatbot', 'automated-test']
        )
        
        if ticket_id:
            logger.info(f"✅ Ticket created successfully with ID: {ticket_id}")
            logger.info("🎉 Tag fix is working! Tickets can now sync to Odoo with tags.")
            return True
        else:
            logger.error("❌ Ticket creation failed!")
            return False
            
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    logger.info("="*60)
    logger.info("🧪 TESTING TAG FIX FOR ODOO INTEGRATION")
    logger.info("="*60)
    
    success = test_tag_fix()
    
    logger.info("="*60)
    if success:
        logger.info("✅ TAG FIX TEST PASSED!")
        logger.info("✅ You can now run manual_sync_tickets.py successfully")
    else:
        logger.info("❌ TAG FIX TEST FAILED!")
        logger.info("❌ Please check the error messages above")
    logger.info("="*60)
