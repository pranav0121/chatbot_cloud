#!/usr/bin/env python3
"""
Test admin login functionality
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db, User
from werkzeug.security import generate_password_hash

def create_admin_user():
    """Create admin user if it doesn't exist"""
    with app.app_context():
        try:
            # Check if admin exists
            admin_email = "admin@chatbot.com"
            admin_user = User.query.filter_by(Email=admin_email).first()
            
            if admin_user:
                print(f"✅ Admin user already exists: {admin_email}")
                print(f"   IsAdmin: {admin_user.IsAdmin}")
                print(f"   IsActive: {admin_user.IsActive}")
            else:
                # Create admin user
                admin_user = User(
                    Name="System Administrator",
                    Email=admin_email,
                    PasswordHash=generate_password_hash('admin123'),
                    OrganizationName="ChatBot Support",
                    Position="Administrator",
                    PriorityLevel="critical",
                    IsActive=True,
                    IsAdmin=True
                )
                db.session.add(admin_user)
                db.session.commit()
                print(f"✅ Created admin user: {admin_email}")
                print(f"   Password: admin123")
            
            # Test admin login URL
            print(f"\n🔗 Admin Login URL: http://127.0.0.1:5000/auth/admin_login")
            print(f"   Email: {admin_email}")
            print(f"   Password: admin123")
            
        except Exception as e:
            print(f"❌ Error: {e}")
            db.session.rollback()

if __name__ == "__main__":
    create_admin_user()
