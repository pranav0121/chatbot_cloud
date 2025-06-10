#!/usr/bin/env python3
"""
Initialize database with proper tables and sample data
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db, User, Ticket, Category
from datetime import datetime
import logging
from werkzeug.security import generate_password_hash

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def initialize_system():
    """Initialize the system with proper database structure and sample data"""
    try:
        with app.app_context():
            logger.info("Starting system initialization...")
            
            # Create all tables
            db.create_all()
            logger.info("Database tables created/verified")
            
            # Create default category if none exists
            category = Category.query.first()
            if not category:
                logger.info("Creating default category...")
                category = Category(
                    Name='Technical Support',
                    Description='General technical support requests',
                    CreatedAt=datetime.utcnow()
                )
                db.session.add(category)
                db.session.commit()
                logger.info("Default category created")
            else:
                logger.info(f"Found existing category: {category.Name}")
            
            # Check for admin user
            admin_user = User.query.filter_by(IsAdmin=True).first()
            if not admin_user:
                logger.info("Creating admin user...")
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
                logger.info("Admin user created: admin@supportcenter.com / admin123")
            else:
                logger.info(f"Found existing admin user: {admin_user.Email}")
            
            # Create sample tickets
            ticket_count = Ticket.query.count()
            if ticket_count == 0:
                logger.info("Creating sample tickets...")
                
                sample_tickets = [
                    {
                        'subject': 'Critical System Outage - Production Down',
                        'priority': 'critical',
                        'organization': 'TechCorp Inc',
                        'created_by': 'John Doe',
                        'status': 'open'
                    },
                    {
                        'subject': 'Password Reset Request for Multiple Users',
                        'priority': 'high',
                        'organization': 'ABC Company Ltd',
                        'created_by': 'Jane Smith',
                        'status': 'in_progress'
                    },
                    {
                        'subject': 'Software Installation Assistance Needed',
                        'priority': 'medium',
                        'organization': 'XYZ Solutions',
                        'created_by': 'Bob Johnson',
                        'status': 'open'
                    },
                    {
                        'subject': 'General Question About Features',
                        'priority': 'low',
                        'organization': 'Small Business LLC',
                        'created_by': 'Alice Brown',
                        'status': 'resolved'
                    },
                    {
                        'subject': 'Database Performance Issues',
                        'priority': 'high',
                        'organization': 'DataCorp',
                        'created_by': 'Mike Wilson',
                        'status': 'open'
                    }
                ]
                
                for ticket_data in sample_tickets:
                    ticket = Ticket(
                        UserID=admin_user.UserID,
                        CategoryID=category.CategoryID,
                        Subject=ticket_data['subject'],
                        Priority=ticket_data['priority'],
                        Status=ticket_data['status'],
                        OrganizationName=ticket_data['organization'],
                        CreatedBy=ticket_data['created_by'],
                        CreatedAt=datetime.utcnow(),
                        UpdatedAt=datetime.utcnow()
                    )
                    db.session.add(ticket)
                
                db.session.commit()
                logger.info(f"Created {len(sample_tickets)} sample tickets")
            else:
                logger.info(f"Found {ticket_count} existing tickets")
            
            # Verify everything was created
            total_users = User.query.count()
            total_tickets = Ticket.query.count()
            total_categories = Category.query.count()
            
            logger.info("System initialization completed!")
            logger.info(f"  Users: {total_users}")
            logger.info(f"  Tickets: {total_tickets}")
            logger.info(f"  Categories: {total_categories}")
            logger.info("")
            logger.info("Admin Login:")
            logger.info("  Email: admin@supportcenter.com")
            logger.info("  Password: admin123")
            logger.info("")
            logger.info("You can now start the application with: python app.py")
            
    except Exception as e:
        logger.error(f"System initialization failed: {e}")
        db.session.rollback()

if __name__ == '__main__':
    initialize_system()
