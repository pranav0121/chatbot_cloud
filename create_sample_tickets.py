#!/usr/bin/env python3
"""
Create sample test tickets to verify the system is working properly
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db, User, Ticket, Category
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_sample_tickets():
    """Create sample tickets for testing"""
    with app.app_context():
        try:
            # Create all tables if they don't exist
            db.create_all()
            logger.info("Database tables created/verified")
            
            # First, make sure we have a category
            category = Category.query.first()
            if not category:
                logger.info("Creating sample category...")
                category = Category(
                    Name='Technical Support',
                    Description='General technical support'
                )
                db.session.add(category)
                db.session.commit()
                logger.info("Sample category created")
            
            # Get admin user
            admin_user = User.query.filter_by(IsAdmin=True).first()
            if not admin_user:
                logger.error("No admin user found! Run migrate_database.py first")
                return
            
            # Create test tickets with different priorities
            test_tickets = [
                {
                    'subject': 'Critical System Outage',
                    'priority': 'critical',
                    'organization': 'ABC Corporation',
                    'created_by': 'John Doe'
                },
                {
                    'subject': 'Password Reset Request',
                    'priority': 'medium',
                    'organization': 'XYZ Company',
                    'created_by': 'Jane Smith'
                },
                {
                    'subject': 'Software License Issue',
                    'priority': 'high',
                    'organization': 'Tech Solutions Inc',
                    'created_by': 'Bob Johnson'
                },
                {
                    'subject': 'General Question',
                    'priority': 'low',
                    'organization': 'Small Business LLC',
                    'created_by': 'Alice Brown'
                }
            ]
            
            logger.info("Creating sample tickets...")
            for ticket_data in test_tickets:
                # Check if ticket already exists
                existing = Ticket.query.filter_by(Subject=ticket_data['subject']).first()
                if not existing:
                    ticket = Ticket(
                        UserID=admin_user.UserID,  # Assign to admin for now
                        CategoryID=category.CategoryID,
                        Subject=ticket_data['subject'],
                        Priority=ticket_data['priority'],
                        OrganizationName=ticket_data['organization'],
                        CreatedBy=ticket_data['created_by'],
                        Status='open'
                    )
                    db.session.add(ticket)
                    logger.info(f"Created ticket: {ticket_data['subject']}")
                else:
                    logger.info(f"Ticket already exists: {ticket_data['subject']}")
            
            db.session.commit()
            logger.info("Sample tickets created successfully!")
            
            # Verify tickets were created
            total_tickets = Ticket.query.count()
            logger.info(f"Total tickets in database: {total_tickets}")
            
        except Exception as e:
            logger.error(f"Error creating sample tickets: {e}")
            db.session.rollback()

if __name__ == '__main__':
    create_sample_tickets()
