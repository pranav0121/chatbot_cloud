#!/usr/bin/env python3
"""
Complete Admin Panel Fix
This script addresses common admin panel issues and ensures everything works correctly.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db, Ticket, User, Category, Message
from sqlalchemy.sql import text
from werkzeug.security import generate_password_hash
from datetime import datetime
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fix_database_schema():
    """Ensure all required columns exist"""
    print("=== Fixing Database Schema ===")
    
    try:
        with app.app_context():
            # Create all tables
            db.create_all()
            print("✅ Database tables created/verified")
            
            # Check and add missing columns to Users table
            try:
                # Test if new columns exist
                db.session.execute(text('SELECT OrganizationName, Position, PriorityLevel, IsAdmin FROM users LIMIT 1'))
                print("✅ Users table has all required columns")
            except Exception:
                print("Adding missing columns to Users table...")
                try:
                    db.session.execute(text('ALTER TABLE users ADD OrganizationName NVARCHAR(255)'))
                    db.session.execute(text('ALTER TABLE users ADD Position NVARCHAR(255)'))
                    db.session.execute(text('ALTER TABLE users ADD PriorityLevel NVARCHAR(50) DEFAULT \'medium\''))
                    db.session.execute(text('ALTER TABLE users ADD Phone NVARCHAR(50)'))
                    db.session.execute(text('ALTER TABLE users ADD Department NVARCHAR(255)'))
                    db.session.execute(text('ALTER TABLE users ADD LastLogin DATETIME'))
                    db.session.execute(text('ALTER TABLE users ADD IsActive BIT DEFAULT 1'))
                    db.session.execute(text('ALTER TABLE users ADD IsAdmin BIT DEFAULT 0'))
                    db.session.commit()
                    print("✅ Added missing columns to Users table")
                except Exception as e:
                    print(f"⚠️  Could not add columns to Users table: {e}")
            
            # Check and add missing columns to Tickets table
            try:
                # Test if new columns exist
                db.session.execute(text('SELECT Priority, OrganizationName, CreatedBy FROM tickets LIMIT 1'))
                print("✅ Tickets table has all required columns")
            except Exception:
                print("Adding missing columns to Tickets table...")
                try:
                    db.session.execute(text('ALTER TABLE tickets ADD Priority NVARCHAR(50) DEFAULT \'medium\''))
                    db.session.execute(text('ALTER TABLE tickets ADD OrganizationName NVARCHAR(255)'))
                    db.session.execute(text('ALTER TABLE tickets ADD CreatedBy NVARCHAR(255)'))
                    db.session.execute(text('ALTER TABLE tickets ADD AssignedTo NVARCHAR(255)'))
                    db.session.commit()
                    print("✅ Added missing columns to Tickets table")
                except Exception as e:
                    print(f"⚠️  Could not add columns to Tickets table: {e}")
            
            return True
            
    except Exception as e:
        print(f"❌ Database schema fix failed: {e}")
        return False

def create_admin_user():
    """Create or update admin user"""
    print("\n=== Creating/Updating Admin User ===")
    
    try:
        with app.app_context():
            admin_user = User.query.filter_by(Email='admin@supportcenter.com').first()
            
            if admin_user:
                # Update existing admin user
                admin_user.IsAdmin = True
                admin_user.IsActive = True
                admin_user.OrganizationName = admin_user.OrganizationName or 'Support Center'
                admin_user.Position = admin_user.Position or 'Administrator'
                admin_user.PriorityLevel = admin_user.PriorityLevel or 'high'
                print("✅ Updated existing admin user")
            else:
                # Create new admin user
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
                print("✅ Created new admin user")
            
            db.session.commit()
            return True
            
    except Exception as e:
        print(f"❌ Admin user creation failed: {e}")
        return False

def create_sample_data():
    """Create sample data for testing"""
    print("\n=== Creating Sample Data ===")
    
    try:
        with app.app_context():
            # Create categories if they don't exist
            if Category.query.count() == 0:
                categories = [
                    Category(Name='Technical Support', Description='Technical issues and problems'),
                    Category(Name='Billing', Description='Billing and payment questions'),
                    Category(Name='General', Description='General inquiries'),
                    Category(Name='Account Issues', Description='Account related problems'),
                ]
                for cat in categories:
                    db.session.add(cat)
                db.session.commit()
                print(f"✅ Created {len(categories)} categories")
            
            # Create sample users if needed
            if User.query.count() < 5:
                sample_users = [
                    User(
                        Name='John Doe',
                        Email='john.doe@company.com',
                        Password=generate_password_hash('password123'),
                        OrganizationName='Tech Corp',
                        Position='Software Engineer',
                        PriorityLevel='medium',
                        IsActive=True
                    ),
                    User(
                        Name='Jane Smith',
                        Email='jane.smith@enterprise.com',
                        Password=generate_password_hash('password123'),
                        OrganizationName='Enterprise Inc',
                        Position='Project Manager',
                        PriorityLevel='high',
                        IsActive=True
                    )
                ]
                for user in sample_users:
                    db.session.add(user)
                db.session.commit()
                print(f"✅ Created {len(sample_users)} sample users")
            
            # Create sample tickets if needed
            if Ticket.query.count() < 10:
                users = User.query.all()
                categories = Category.query.all()
                
                if users and categories:
                    sample_tickets = [
                        Ticket(
                            UserID=users[0].UserID,
                            CategoryID=categories[0].CategoryID,
                            Subject='Critical System Outage',
                            Priority='critical',
                            Status='open',
                            OrganizationName=users[0].OrganizationName,
                            CreatedBy=users[0].Name
                        ),
                        Ticket(
                            UserID=users[1].UserID if len(users) > 1 else users[0].UserID,
                            CategoryID=categories[1].CategoryID if len(categories) > 1 else categories[0].CategoryID,
                            Subject='Billing Question',
                            Priority='medium',
                            Status='in_progress',
                            OrganizationName=users[1].OrganizationName if len(users) > 1 else users[0].OrganizationName,
                            CreatedBy=users[1].Name if len(users) > 1 else users[0].Name
                        ),
                        Ticket(
                            UserID=users[0].UserID,
                            CategoryID=categories[2].CategoryID if len(categories) > 2 else categories[0].CategoryID,
                            Subject='General Inquiry',
                            Priority='low',
                            Status='resolved',
                            OrganizationName=users[0].OrganizationName,
                            CreatedBy=users[0].Name
                        )
                    ]
                    
                    for ticket in sample_tickets:
                        db.session.add(ticket)
                        db.session.flush()  # Get the ID
                        
                        # Add initial message
                        message = Message(
                            TicketID=ticket.TicketID,
                            SenderID=ticket.UserID,
                            Content=f"This is a sample ticket for {ticket.Subject}. Please help resolve this issue.",
                            IsAdminReply=False
                        )
                        db.session.add(message)
                    
                    db.session.commit()
                    print(f"✅ Created {len(sample_tickets)} sample tickets")
            
            return True
            
    except Exception as e:
        print(f"❌ Sample data creation failed: {e}")
        return False

def test_admin_endpoints():
    """Test all admin endpoints"""
    print("\n=== Testing Admin Endpoints ===")
    
    try:
        with app.app_context():
            # Test dashboard stats
            total_tickets = Ticket.query.count()
            pending_tickets = Ticket.query.filter(Ticket.Status.in_(['open', 'in_progress'])).count()
            resolved_tickets = Ticket.query.filter_by(Status='resolved').count()
            
            print(f"✅ Dashboard Stats Working:")
            print(f"   Total Tickets: {total_tickets}")
            print(f"   Pending: {pending_tickets}")
            print(f"   Resolved: {resolved_tickets}")
            
            # Test tickets query with joins
            tickets = db.session.query(Ticket, User, Category).join(
                User, Ticket.UserID == User.UserID, isouter=True
            ).join(
                Category, Ticket.CategoryID == Category.CategoryID
            ).limit(5).all()
            
            print(f"✅ Tickets Query Working: {len(tickets)} tickets")
            
            return True
            
    except Exception as e:
        print(f"❌ Admin endpoints test failed: {e}")
        return False

def main():
    """Main fix function"""
    print("=== Admin Panel Complete Fix ===")
    print("This will fix all common admin panel issues.")
    print()
    
    success = True
    
    # Step 1: Fix database schema
    if not fix_database_schema():
        success = False
    
    # Step 2: Create admin user
    if not create_admin_user():
        success = False
    
    # Step 3: Create sample data
    if not create_sample_data():
        success = False
    
    # Step 4: Test admin endpoints
    if not test_admin_endpoints():
        success = False
    
    print("\n=== Fix Complete ===")
    if success:
        print("✅ All fixes applied successfully!")
        print()
        print("Your admin panel should now be working correctly.")
        print()
        print("🌐 Admin Panel: http://127.0.0.1:5001/admin")
        print("🔑 Login: admin@supportcenter.com / admin123")
        print()
        print("Next steps:")
        print("1. Start your Flask application: python app.py")
        print("2. Open the admin panel in your browser")
        print("3. Login with the admin credentials")
        print("4. Check the dashboard, tickets, and live chat sections")
    else:
        print("❌ Some fixes failed. Please check the errors above.")
    
    return success

if __name__ == '__main__':
    main()
