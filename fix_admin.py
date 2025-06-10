#!/usr/bin/env python3
"""
Admin Panel Diagnostic and Fix Script
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db, Ticket, User, Category, Message
from sqlalchemy.sql import text
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_database_connectivity():
    """Test basic database operations"""
    print("=== Testing Database Connectivity ===")
    
    try:
        with app.app_context():
            # Test basic connection
            result = db.session.execute(text('SELECT 1')).scalar()
            print(f"✅ Database connection successful: {result}")
            
            # Test table existence
            tables = ['users', 'tickets', 'categories', 'messages']
            for table in tables:
                try:
                    count = db.session.execute(text(f'SELECT COUNT(*) FROM {table}')).scalar()
                    print(f"✅ Table '{table}': {count} records")
                except Exception as e:
                    print(f"❌ Table '{table}': Error - {e}")
            
            return True
            
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def test_admin_apis():
    """Test admin API endpoints"""
    print("\n=== Testing Admin APIs ===")
    
    try:
        with app.app_context():
            # Test dashboard stats
            try:
                total_tickets = Ticket.query.count()
                pending_tickets = Ticket.query.filter(Ticket.Status.in_(['open', 'in_progress'])).count()
                resolved_tickets = Ticket.query.filter_by(Status='resolved').count()
                active_chats = Ticket.query.filter(Ticket.Status.in_(['open', 'in_progress'])).count()
                
                print(f"✅ Dashboard Stats:")
                print(f"   Total Tickets: {total_tickets}")
                print(f"   Pending: {pending_tickets}")
                print(f"   Resolved: {resolved_tickets}")
                print(f"   Active Chats: {active_chats}")
                
            except Exception as e:
                print(f"❌ Dashboard stats failed: {e}")
            
            # Test tickets query
            try:
                tickets = db.session.query(Ticket, User, Category).join(
                    User, Ticket.UserID == User.UserID, isouter=True
                ).join(
                    Category, Ticket.CategoryID == Category.CategoryID, isouter=True
                ).limit(5).all()
                
                print(f"✅ Tickets query: {len(tickets)} tickets found")
                for ticket, user, category in tickets:
                    print(f"   #{ticket.TicketID}: {ticket.Subject} - {ticket.Status}")
                
            except Exception as e:
                print(f"❌ Tickets query failed: {e}")
                
            return True
            
    except Exception as e:
        print(f"❌ Admin API test failed: {e}")
        return False

def create_test_data_if_needed():
    """Create test data if database is empty"""
    print("\n=== Checking/Creating Test Data ===")
    
    try:
        with app.app_context():
            # Check if we have categories
            category_count = Category.query.count()
            if category_count == 0:
                print("Creating default categories...")
                categories = [
                    Category(Name='Technical Support', Description='Technical issues and problems'),
                    Category(Name='Billing', Description='Billing and payment questions'),
                    Category(Name='General', Description='General inquiries'),
                ]
                for cat in categories:
                    db.session.add(cat)
                db.session.commit()
                print(f"✅ Created {len(categories)} categories")
            else:
                print(f"✅ Found {category_count} categories")
            
            # Check if we have admin user
            admin_user = User.query.filter_by(Email='admin@supportcenter.com').first()
            if not admin_user:
                print("Creating admin user...")
                from werkzeug.security import generate_password_hash
                admin_user = User(
                    Name='System Administrator',
                    Email='admin@supportcenter.com',
                    Password=generate_password_hash('admin123'),
                    OrganizationName='Support Center',
                    Position='Administrator',
                    PriorityLevel='high',
                    IsAdmin=True,
                    IsActive=True
                )
                db.session.add(admin_user)
                db.session.commit()
                print("✅ Created admin user")
            else:
                print("✅ Admin user exists")
            
            # Check if we have test tickets
            ticket_count = Ticket.query.count()
            if ticket_count == 0:
                print("Creating test tickets...")
                test_tickets = [
                    Ticket(
                        UserID=admin_user.UserID,
                        CategoryID=1,
                        Subject='Test High Priority Issue',
                        Priority='high',
                        Status='open',
                        OrganizationName='Test Organization',
                        CreatedBy='Test User'
                    ),
                    Ticket(
                        UserID=admin_user.UserID,
                        CategoryID=2,
                        Subject='Test Medium Priority Issue',
                        Priority='medium',
                        Status='in_progress',
                        OrganizationName='Another Organization',
                        CreatedBy='Another User'
                    ),
                ]
                for ticket in test_tickets:
                    db.session.add(ticket)
                db.session.commit()
                print(f"✅ Created {len(test_tickets)} test tickets")
            else:
                print(f"✅ Found {ticket_count} tickets")
                
            return True
            
    except Exception as e:
        print(f"❌ Test data creation failed: {e}")
        return False

def main():
    """Main diagnostic function"""
    print("=== Admin Panel Diagnostic Tool ===")
    print("This tool will test and fix common admin panel issues.")
    print()
    
    # Test database connectivity
    if not test_database_connectivity():
        print("❌ Database connectivity test failed. Check your database connection.")
        return False
    
    # Create test data if needed
    if not create_test_data_if_needed():
        print("❌ Test data creation failed.")
        return False
    
    # Test admin APIs
    if not test_admin_apis():
        print("❌ Admin API test failed.")
        return False
    
    print("\n=== Diagnostic Complete ===")
    print("✅ All tests passed! Your admin panel should be working.")
    print()
    print("Admin Panel URL: http://127.0.0.1:5001/admin")
    print("Admin Login: admin@supportcenter.com / admin123")
    print()
    print("If you're still having issues:")
    print("1. Check the browser console for JavaScript errors")
    print("2. Ensure your Flask app is running on port 5001")
    print("3. Try refreshing the admin panel page")
    
    return True

if __name__ == '__main__':
    main()
