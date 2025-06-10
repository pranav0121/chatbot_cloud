#!/usr/bin/env python3
"""
Simple data creation script that works with existing data
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db, User, Ticket, Category, Message
from datetime import datetime, timedelta
import logging
from werkzeug.security import generate_password_hash
import random

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_test_data():
    """Create test data without clearing existing data"""
    with app.app_context():
        try:
            logger.info("Creating test data...")
            
            # Create all tables
            db.create_all()
            logger.info("Database tables created/verified")
            
            # Create categories if they don't exist
            categories_data = [
                {'name': 'Technical Support', 'description': 'Technical issues and troubleshooting'},
                {'name': 'Account Management', 'description': 'Account-related requests and changes'},
                {'name': 'Billing & Payment', 'description': 'Billing inquiries and payment issues'}
            ]
            
            for cat_data in categories_data:
                existing = Category.query.filter_by(Name=cat_data['name']).first()
                if not existing:
                    category = Category(
                        Name=cat_data['name'],
                        Description=cat_data['description'],
                        CreatedAt=datetime.utcnow()
                    )
                    db.session.add(category)
                    logger.info(f"Created category: {cat_data['name']}")
            
            db.session.commit()
            
            # Create admin user if doesn't exist
            admin_user = User.query.filter_by(Email='admin@supportcenter.com').first()
            if not admin_user:
                admin_user = User(
                    Name='System Administrator',
                    Email='admin@supportcenter.com',
                    PasswordHash=generate_password_hash('admin123'),
                    OrganizationName='Support Center',
                    Position='Administrator',
                    PriorityLevel='critical',
                    IsActive=True,
                    IsAdmin=True,
                    CreatedAt=datetime.utcnow()
                )
                db.session.add(admin_user)
                db.session.commit()
                logger.info("Created admin user")
            
            # Create some test users if they don't exist
            test_users = [
                {
                    'name': 'John Doe',
                    'email': 'john.doe@techcorp.com',
                    'organization': 'TechCorp Inc',
                    'priority': 'high'
                },
                {
                    'name': 'Jane Smith',
                    'email': 'jane.smith@abccompany.com',
                    'organization': 'ABC Company Ltd',
                    'priority': 'medium'
                }
            ]
            
            for user_data in test_users:
                existing = User.query.filter_by(Email=user_data['email']).first()
                if not existing:
                    user = User(
                        Name=user_data['name'],
                        Email=user_data['email'],
                        PasswordHash=generate_password_hash('password123'),
                        OrganizationName=user_data['organization'],
                        Position='Test User',
                        PriorityLevel=user_data['priority'],
                        IsActive=True,
                        IsAdmin=False,
                        CreatedAt=datetime.utcnow()
                    )
                    db.session.add(user)
                    logger.info(f"Created user: {user_data['name']}")
            
            db.session.commit()
            
            # Create some test tickets
            tech_support = Category.query.filter_by(Name='Technical Support').first()
            if tech_support:
                test_tickets = [
                    {
                        'subject': 'Critical System Outage',
                        'priority': 'critical',
                        'status': 'open',
                        'organization': 'TechCorp Inc',
                        'created_by': 'John Doe'
                    },
                    {
                        'subject': 'Password Reset Request',
                        'priority': 'medium',
                        'status': 'in_progress',
                        'organization': 'ABC Company Ltd',
                        'created_by': 'Jane Smith'
                    },
                    {
                        'subject': 'Software Installation Help',
                        'priority': 'low',
                        'status': 'resolved',
                        'organization': 'TechCorp Inc',
                        'created_by': 'John Doe'
                    }
                ]
                
                for ticket_data in test_tickets:
                    existing = Ticket.query.filter_by(Subject=ticket_data['subject']).first()
                    if not existing:
                        user = User.query.filter_by(Name=ticket_data['created_by']).first()
                        ticket = Ticket(
                            UserID=user.UserID if user else None,
                            CategoryID=tech_support.CategoryID,
                            Subject=ticket_data['subject'],
                            Priority=ticket_data['priority'],
                            Status=ticket_data['status'],
                            OrganizationName=ticket_data['organization'],
                            CreatedBy=ticket_data['created_by'],
                            CreatedAt=datetime.utcnow() - timedelta(days=random.randint(0, 7)),
                            UpdatedAt=datetime.utcnow()
                        )
                        db.session.add(ticket)
                        logger.info(f"Created ticket: {ticket_data['subject']}")
                
                db.session.commit()
            
            # Print summary
            total_users = User.query.count()
            total_tickets = Ticket.query.count()
            total_categories = Category.query.count()
            pending_tickets = Ticket.query.filter(Ticket.Status.in_(['open', 'in_progress'])).count()
            resolved_tickets = Ticket.query.filter_by(Status='resolved').count()
            
            logger.info("=== DATA CREATION COMPLETE ===")
            logger.info(f"Total Users: {total_users}")
            logger.info(f"Total Tickets: {total_tickets}")
            logger.info(f"Total Categories: {total_categories}")
            logger.info(f"Pending Tickets: {pending_tickets}")
            logger.info(f"Resolved Tickets: {resolved_tickets}")
            logger.info("")
            logger.info("Admin Login:")
            logger.info("  Email: admin@supportcenter.com")
            logger.info("  Password: admin123")
            logger.info("")
            logger.info("System ready for testing!")
            
        except Exception as e:
            logger.error(f"Error creating test data: {e}")
            db.session.rollback()

if __name__ == '__main__':
    create_test_data()
