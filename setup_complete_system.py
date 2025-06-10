#!/usr/bin/env python3
"""
Comprehensive database setup with full test data for all functionality
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db, User, Ticket, Category, Message
from datetime import datetime, timedelta
import logging
from werkzeug.security import generate_password_hash
from sqlalchemy import text
import random

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_comprehensive_test_data():
    """Create comprehensive test data for all system functionality"""
    with app.app_context():
        try:
            logger.info("Starting comprehensive database setup...")
            
            # Create all tables
            db.create_all()
            logger.info("Database tables created/verified")
              # Clear existing data for fresh start (handle foreign key constraints)
            logger.info("Clearing existing data...")
            
            # Delete in correct order to respect foreign key constraints
            db.session.execute(text('DELETE FROM Messages'))
            db.session.execute(text('DELETE FROM Tickets'))
            db.session.execute(text('DELETE FROM Users'))
            db.session.execute(text('DELETE FROM Categories'))
            db.session.commit()
            
            # Create categories
            logger.info("Creating categories...")
            categories = [
                {'name': 'Technical Support', 'description': 'Technical issues and troubleshooting'},
                {'name': 'Account Management', 'description': 'Account-related requests and changes'},
                {'name': 'Billing & Payment', 'description': 'Billing inquiries and payment issues'},
                {'name': 'Feature Request', 'description': 'New feature requests and suggestions'},
                {'name': 'Bug Report', 'description': 'Software bugs and issues'}
            ]
            
            category_objects = []
            for cat_data in categories:
                category = Category(
                    Name=cat_data['name'],
                    Description=cat_data['description'],
                    CreatedAt=datetime.utcnow()
                )
                db.session.add(category)
                category_objects.append(category)
            
            db.session.commit()
            logger.info(f"Created {len(categories)} categories")
            
            # Create users with different organizations and priority levels
            logger.info("Creating users...")
            users_data = [
                {
                    'name': 'System Administrator',
                    'email': 'admin@supportcenter.com',
                    'password': 'admin123',
                    'organization': 'Support Center',
                    'position': 'Administrator',
                    'priority': 'critical',
                    'department': 'IT',
                    'phone': '+1-555-0001',
                    'is_admin': True
                },
                {
                    'name': 'John Doe',
                    'email': 'john.doe@techcorp.com',
                    'password': 'password123',
                    'organization': 'TechCorp Inc',
                    'position': 'Senior Developer',
                    'priority': 'high',
                    'department': 'Engineering',
                    'phone': '+1-555-0101',
                    'is_admin': False
                },
                {
                    'name': 'Jane Smith',
                    'email': 'jane.smith@abccompany.com',
                    'password': 'password123',
                    'organization': 'ABC Company Ltd',
                    'position': 'Project Manager',
                    'priority': 'medium',
                    'department': 'Operations',
                    'phone': '+1-555-0102',
                    'is_admin': False
                },
                {
                    'name': 'Bob Johnson',
                    'email': 'bob.johnson@xyzsolutions.com',
                    'password': 'password123',
                    'organization': 'XYZ Solutions',
                    'position': 'IT Specialist',
                    'priority': 'medium',
                    'department': 'IT',
                    'phone': '+1-555-0103',
                    'is_admin': False
                },
                {
                    'name': 'Alice Brown',
                    'email': 'alice.brown@smallbiz.com',
                    'password': 'password123',
                    'organization': 'Small Business LLC',
                    'position': 'Office Manager',
                    'priority': 'low',
                    'department': 'Administration',
                    'phone': '+1-555-0104',
                    'is_admin': False
                },
                {
                    'name': 'Mike Wilson',
                    'email': 'mike.wilson@datacorp.com',
                    'password': 'password123',
                    'organization': 'DataCorp',
                    'position': 'Database Administrator',
                    'priority': 'high',
                    'department': 'IT',
                    'phone': '+1-555-0105',
                    'is_admin': False
                }
            ]
            
            user_objects = []
            for user_data in users_data:
                # Set last login to random time in the last 7 days
                last_login = datetime.utcnow() - timedelta(days=random.randint(0, 7), hours=random.randint(0, 23))
                
                user = User(
                    Name=user_data['name'],
                    Email=user_data['email'],
                    PasswordHash=generate_password_hash(user_data['password']),
                    OrganizationName=user_data['organization'],
                    Position=user_data['position'],
                    PriorityLevel=user_data['priority'],
                    Department=user_data['department'],
                    Phone=user_data['phone'],
                    IsActive=True,
                    IsAdmin=user_data['is_admin'],
                    LastLogin=last_login,
                    CreatedAt=datetime.utcnow() - timedelta(days=random.randint(1, 30))
                )
                db.session.add(user)
                user_objects.append(user)
            
            db.session.commit()
            logger.info(f"Created {len(users_data)} users")
            
            # Create tickets with various statuses and priorities
            logger.info("Creating tickets...")
            tickets_data = [
                {
                    'subject': 'Critical System Outage - Production Down',
                    'priority': 'critical',
                    'status': 'open',
                    'user_index': 1,  # John Doe
                    'category_index': 0,  # Technical Support
                    'days_ago': 0
                },
                {
                    'subject': 'Database Performance Issues',
                    'priority': 'high',
                    'status': 'in_progress',
                    'user_index': 5,  # Mike Wilson
                    'category_index': 0,  # Technical Support
                    'days_ago': 1
                },
                {
                    'subject': 'Password Reset Request for Team',
                    'priority': 'high',
                    'status': 'open',
                    'user_index': 2,  # Jane Smith
                    'category_index': 1,  # Account Management
                    'days_ago': 2
                },
                {
                    'subject': 'Billing Discrepancy - Invoice #12345',
                    'priority': 'medium',
                    'status': 'in_progress',
                    'user_index': 3,  # Bob Johnson
                    'category_index': 2,  # Billing & Payment
                    'days_ago': 3
                },
                {
                    'subject': 'Feature Request: Dark Mode Support',
                    'priority': 'low',
                    'status': 'open',
                    'user_index': 4,  # Alice Brown
                    'category_index': 3,  # Feature Request
                    'days_ago': 5
                },
                {
                    'subject': 'Software Installation Error',
                    'priority': 'medium',
                    'status': 'resolved',
                    'user_index': 1,  # John Doe
                    'category_index': 0,  # Technical Support
                    'days_ago': 7
                },
                {
                    'subject': 'Bug: Dashboard Not Loading',
                    'priority': 'high',
                    'status': 'resolved',
                    'user_index': 2,  # Jane Smith
                    'category_index': 4,  # Bug Report
                    'days_ago': 10
                },
                {
                    'subject': 'Account Upgrade Request',
                    'priority': 'medium',
                    'status': 'closed',
                    'user_index': 3,  # Bob Johnson
                    'category_index': 1,  # Account Management
                    'days_ago': 15
                },
                {
                    'subject': 'General Question About Features',
                    'priority': 'low',
                    'status': 'resolved',
                    'user_index': 4,  # Alice Brown
                    'category_index': 0,  # Technical Support
                    'days_ago': 20
                },
                {
                    'subject': 'Security Vulnerability Report',
                    'priority': 'critical',
                    'status': 'resolved',
                    'user_index': 5,  # Mike Wilson
                    'category_index': 4,  # Bug Report
                    'days_ago': 25
                }
            ]
            
            admin_user = user_objects[0]  # First user is admin
            
            for ticket_data in tickets_data:
                user = user_objects[ticket_data['user_index']]
                category = category_objects[ticket_data['category_index']]
                created_date = datetime.utcnow() - timedelta(days=ticket_data['days_ago'])
                
                ticket = Ticket(
                    UserID=user.UserID,
                    CategoryID=category.CategoryID,
                    Subject=ticket_data['subject'],
                    Priority=ticket_data['priority'],
                    Status=ticket_data['status'],
                    OrganizationName=user.OrganizationName,
                    CreatedBy=user.Name,
                    AssignedTo=admin_user.UserID if ticket_data['status'] in ['in_progress', 'resolved'] else None,
                    CreatedAt=created_date,
                    UpdatedAt=created_date + timedelta(hours=random.randint(1, 24))
                )
                db.session.add(ticket)
            
            db.session.commit()
            logger.info(f"Created {len(tickets_data)} tickets")
            
            # Create some messages for tickets
            logger.info("Creating messages...")
            tickets = Ticket.query.all()
            for i, ticket in enumerate(tickets[:5]):  # Add messages to first 5 tickets
                # Initial message from user
                initial_message = Message(
                    TicketID=ticket.TicketID,
                    SenderID=ticket.UserID,
                    Content=f"Initial message for ticket: {ticket.Subject}. This is a detailed description of the issue.",
                    IsAdminReply=False,
                    CreatedAt=ticket.CreatedAt + timedelta(minutes=5)
                )
                db.session.add(initial_message)
                
                # Admin reply if ticket is in progress or resolved
                if ticket.Status in ['in_progress', 'resolved']:
                    admin_reply = Message(
                        TicketID=ticket.TicketID,
                        SenderID=admin_user.UserID,
                        Content=f"Thank you for reporting this issue. We are working on resolving it.",
                        IsAdminReply=True,
                        CreatedAt=ticket.CreatedAt + timedelta(hours=2)
                    )
                    db.session.add(admin_reply)
            
            db.session.commit()
            logger.info("Created messages for tickets")
            
            # Verify data was created
            total_users = User.query.count()
            total_tickets = Ticket.query.count()
            total_categories = Category.query.count()
            total_messages = Message.query.count()
            
            # Get statistics for verification
            pending_tickets = Ticket.query.filter(Ticket.Status.in_(['open', 'in_progress'])).count()
            resolved_tickets = Ticket.query.filter_by(Status='resolved').count()
            critical_tickets = Ticket.query.filter_by(Priority='critical').count()
            
            logger.info("=== DATABASE SETUP COMPLETE ===")
            logger.info(f"Total Users: {total_users}")
            logger.info(f"Total Tickets: {total_tickets}")
            logger.info(f"Total Categories: {total_categories}")
            logger.info(f"Total Messages: {total_messages}")
            logger.info(f"Pending Tickets: {pending_tickets}")
            logger.info(f"Resolved Tickets: {resolved_tickets}")
            logger.info(f"Critical Tickets: {critical_tickets}")
            logger.info("")
            logger.info("=== LOGIN CREDENTIALS ===")
            logger.info("Admin:")
            logger.info("  Email: admin@supportcenter.com")
            logger.info("  Password: admin123")
            logger.info("")
            logger.info("Test Users:")
            for user_data in users_data[1:]:
                logger.info(f"  {user_data['name']}: {user_data['email']} / password123")
            logger.info("")
            logger.info("System is ready for testing!")
            
        except Exception as e:
            logger.error(f"Error creating test data: {e}")
            db.session.rollback()

if __name__ == '__main__':
    create_comprehensive_test_data()
