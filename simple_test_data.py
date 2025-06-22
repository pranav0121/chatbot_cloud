#!/usr/bin/env python3
"""
Simple test data creation for admin panel
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db, User, Category, Ticket, Message
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash
import random

def create_simple_test_data():
    """Create simple test data for admin panel testing"""
    with app.app_context():
        print("🚀 Creating simple test data...")
        
        try:
            # Create tables
            db.create_all()
            print("✅ Database tables created")
            
            # Create admin user
            admin_email = "admin@chatbot.com"
            admin_user = User.query.filter_by(Email=admin_email).first()
            if not admin_user:
                admin_user = User(
                    Name="Admin User",
                    Email=admin_email,
                    PasswordHash=generate_password_hash('admin123'),
                    OrganizationName="ChatBot Admin",
                    Position="Administrator",
                    PriorityLevel="critical",
                    IsActive=True,
                    IsAdmin=True,
                    CreatedAt=datetime.utcnow()
                )
                db.session.add(admin_user)
                print("✅ Created admin user")
            
            # Create a simple category
            category = Category.query.filter_by(Name='Technical Support').first()
            if not category:
                category = Category(Name='Technical Support', Description='Technical issues')
                db.session.add(category)
                print("✅ Created category")
            
            # Create a test user
            test_user = User.query.filter_by(Email='test@example.com').first()
            if not test_user:
                test_user = User(
                    Name="Test User",
                    Email="test@example.com",
                    PasswordHash=generate_password_hash('test123'),
                    OrganizationName="Test Company",
                    Position="Tester",
                    PriorityLevel="medium",
                    IsActive=True,
                    CreatedAt=datetime.utcnow()
                )
                db.session.add(test_user)
                print("✅ Created test user")
            
            db.session.commit()
            
            # Create a few test tickets
            ticket_subjects = [
                "Login Issue - Cannot Access Dashboard",
                "Payment Processing Error",
                "Feature Request - Dark Mode",
                "Bug Report - Mobile App Crash"
            ]
            
            for i, subject in enumerate(ticket_subjects):
                existing_ticket = Ticket.query.filter_by(Subject=subject).first()
                if not existing_ticket:
                    statuses = ['open', 'in_progress', 'resolved', 'closed']
                    priorities = ['low', 'medium', 'high', 'critical']
                    
                    ticket = Ticket(
                        Subject=subject,
                        Description=f"Description for {subject}",
                        UserID=test_user.UserID,
                        CategoryID=category.CategoryID,
                        Priority=random.choice(priorities),
                        Status=random.choice(statuses),
                        CreatedBy=test_user.Email,
                        OrganizationName=test_user.OrganizationName,
                        CreatedAt=datetime.utcnow() - timedelta(days=i),
                        UpdatedAt=datetime.utcnow() - timedelta(hours=i*2)
                    )
                    db.session.add(ticket)
                    print(f"✅ Created ticket: {subject}")
            
            db.session.commit()
            
            # Add some messages to tickets
            tickets = Ticket.query.all()
            for ticket in tickets:
                # Add initial user message
                user_msg = Message(
                    TicketID=ticket.TicketID,
                    SenderID=ticket.UserID,
                    Content=f"Initial message for ticket: {ticket.Subject}",
                    IsAdminReply=False,
                    CreatedAt=ticket.CreatedAt
                )
                db.session.add(user_msg)
                
                # Add admin reply
                admin_msg = Message(
                    TicketID=ticket.TicketID,
                    SenderID=admin_user.UserID,
                    Content="Thank you for contacting support. We're looking into your issue.",
                    IsAdminReply=True,
                    CreatedAt=ticket.CreatedAt + timedelta(minutes=30)
                )
                db.session.add(admin_msg)
            
            db.session.commit()
            print("✅ Created test messages")
            
            # Print summary
            print(f"\n📊 Test Data Summary:")
            print(f"   Users: {User.query.count()}")
            print(f"   Categories: {Category.query.count()}")
            print(f"   Tickets: {Ticket.query.count()}")
            print(f"   Messages: {Message.query.count()}")
            
            print(f"\n🔐 Admin Login:")
            print(f"   URL: http://127.0.0.1:5000/auth/admin_login")
            print(f"   Email: admin@chatbot.com")
            print(f"   Password: admin123")
            
        except Exception as e:
            print(f"❌ Error: {e}")
            db.session.rollback()
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    create_simple_test_data()
