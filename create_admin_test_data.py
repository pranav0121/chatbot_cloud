#!/usr/bin/env python3
"""
Create test data for admin panel
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db, User, Category, Ticket, Message
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash
import random

def create_test_data():
    """Create comprehensive test data for admin panel"""
    with app.app_context():
        print("🚀 Creating test data for admin panel...")
        
        try:
            # Create tables if they don't exist
            db.create_all()
            print("✅ Database tables created/verified")
            
            # Create categories
            categories = [
                ('Technical Support', 'Technical issues and troubleshooting'),
                ('Billing', 'Billing and payment related inquiries'),
                ('General Inquiry', 'General questions and information'),
                ('Bug Report', 'Software bugs and issues'),
                ('Feature Request', 'New feature suggestions')
            ]
            
            category_objects = []
            for name, desc in categories:
                category = Category.query.filter_by(Name=name).first()
                if not category:
                    category = Category(Name=name, Description=desc)
                    db.session.add(category)
                    print(f"✅ Created category: {name}")
                category_objects.append(category)
            
            db.session.commit()
            
            # Create test users
            users = [
                ('John Smith', 'john.smith@example.com', 'TechCorp Inc', 'Developer', 'high'),
                ('Jane Doe', 'jane.doe@company.com', 'Business Solutions', 'Manager', 'medium'),
                ('Bob Johnson', 'bob.johnson@startup.com', 'Startup XYZ', 'CTO', 'critical'),
                ('Alice Brown', 'alice.brown@enterprise.com', 'Enterprise Corp', 'Admin', 'low'),
                ('Charlie Davis', 'charlie.davis@freelance.com', 'Freelancer', 'Consultant', 'medium')
            ]
            
            user_objects = []
            for name, email, org, position, priority in users:
                user = User.query.filter_by(Email=email).first()
                if not user:
                    user = User(
                        Name=name,
                        Email=email,
                        PasswordHash=generate_password_hash('password123'),
                        OrganizationName=org,
                        Position=position,
                        PriorityLevel=priority,
                        Phone=f"+1-555-{random.randint(1000, 9999)}",
                        Department='Support',
                        IsActive=True,
                        CreatedAt=datetime.utcnow() - timedelta(days=random.randint(1, 30))
                    )
                    db.session.add(user)
                    print(f"✅ Created user: {name} ({email})")
                user_objects.append(user)
            
            db.session.commit()
            
            # Create test tickets with different statuses
            ticket_data = [
                ('Login Issues', 'Cannot log into the system', 'open', 'high'),
                ('Payment Processing Error', 'Credit card payment failing', 'in_progress', 'critical'),
                ('Feature Request - Dark Mode', 'Please add dark mode support', 'open', 'low'),
                ('Bug: Dashboard Not Loading', 'Dashboard shows blank page', 'resolved', 'medium'),
                ('Integration Question', 'How to integrate with our API?', 'in_progress', 'medium'),
                ('Account Suspension', 'My account was suspended unexpectedly', 'open', 'high'),
                ('Export Data Issues', 'Cannot export reports to PDF', 'resolved', 'low'),
                ('Mobile App Crash', 'App crashes on startup', 'in_progress', 'critical')
            ]
            
            ticket_objects = []
            for i, (subject, description, status, priority) in enumerate(ticket_data):
                # Random user and category
                user = random.choice(user_objects)
                category = random.choice(category_objects)
                
                # Check if ticket already exists
                existing_ticket = Ticket.query.filter_by(Subject=subject).first()
                if not existing_ticket:
                    ticket = Ticket(
                        Subject=subject,
                        Description=description,
                        UserID=user.UserID,
                        CategoryID=category.CategoryID,
                        Priority=priority,
                        Status=status,
                        CreatedBy=user.Email,
                        OrganizationName=user.OrganizationName,
                        CreatedAt=datetime.utcnow() - timedelta(hours=random.randint(1, 72)),
                        UpdatedAt=datetime.utcnow() - timedelta(minutes=random.randint(1, 120))
                    )
                    db.session.add(ticket)
                    ticket_objects.append(ticket)
                    print(f"✅ Created ticket: {subject} (Status: {status}, Priority: {priority})")
            
            db.session.commit()
            
            # Create test messages for tickets
            message_templates = [
                "Thank you for contacting support. We're looking into your issue.",
                "I've escalated this to our technical team for further investigation.",
                "Could you please provide more details about when this issue started?",
                "We've identified the root cause and are working on a fix.",
                "This issue has been resolved. Please try again and let us know if you need further assistance.",
                "I understand your frustration. Let me help you resolve this quickly.",
                "We've updated our system. This should fix the issue you reported.",
                "Thank you for your patience. The issue is now completely resolved."
            ]
            
            for ticket in ticket_objects:
                # Add 2-5 messages per ticket
                num_messages = random.randint(2, 5)
                for j in range(num_messages):
                    is_admin = j % 2 == 1  # Alternate between user and admin messages
                    content = random.choice(message_templates)
                    
                    message = Message(
                        TicketID=ticket.TicketID,
                        SenderID=None,  # Could be linked to actual users
                        Content=content,
                        IsAdminReply=is_admin,
                        CreatedAt=ticket.CreatedAt + timedelta(minutes=j * 30)
                    )
                    db.session.add(message)
            
            db.session.commit()
            print("✅ Created test messages for tickets")
            
            # Create an admin user if it doesn't exist
            admin_email = "admin@chatbot.com"
            admin_user = User.query.filter_by(Email=admin_email).first()
            if not admin_user:
                admin_user = User(
                    Name="System Administrator",
                    Email=admin_email,
                    PasswordHash=generate_password_hash('admin123'),
                    OrganizationName="ChatBot Support",
                    Position="Administrator",
                    PriorityLevel="critical",
                    IsActive=True,
                    IsAdmin=True,
                    CreatedAt=datetime.utcnow()
                )
                db.session.add(admin_user)
                db.session.commit()
                print(f"✅ Created admin user: {admin_email} (password: admin123)")
            
            # Print summary
            total_users = User.query.count()
            total_categories = Category.query.count()
            total_tickets = Ticket.query.count()
            total_messages = Message.query.count()
            
            print(f"\n📊 Test Data Summary:")
            print(f"   Users: {total_users}")
            print(f"   Categories: {total_categories}")
            print(f"   Tickets: {total_tickets}")
            print(f"   Messages: {total_messages}")
            
            # Print tickets by status
            statuses = db.session.query(Ticket.Status, db.func.count(Ticket.TicketID)).group_by(Ticket.Status).all()
            print(f"\n🎫 Tickets by Status:")
            for status, count in statuses:
                print(f"   {status}: {count}")
            
            print("\n✅ Test data creation completed successfully!")
            print("🔐 Admin Login: admin@chatbot.com / admin123")
            
        except Exception as e:
            print(f"❌ Error creating test data: {e}")
            db.session.rollback()
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    create_test_data()
