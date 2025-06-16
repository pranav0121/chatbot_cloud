#!/usr/bin/env python3
"""
Fix Admin User Account
"""

from app import app, db, User
from werkzeug.security import generate_password_hash
from datetime import datetime

def fix_admin_user():
    with app.app_context():
        try:
            print("Checking admin user...")
            
            # Find admin user
            admin = User.query.filter_by(Email='admin@youcloudtech.com').first()
            
            if admin:
                print(f"Admin user found: {admin.Email}")
                print(f"IsAdmin: {admin.IsAdmin}")
                print(f"IsActive: {admin.IsActive}")
                
                # Fix admin user
                admin.IsActive = True
                admin.IsAdmin = True
                admin.PasswordHash = generate_password_hash('admin123')
                db.session.commit()
                
                print("✅ Admin user fixed!")
                print("Email: admin@youcloudtech.com")
                print("Password: admin123")
                
            else:
                print("No admin user found, creating new one...")
                
                new_admin = User(
                    Email='admin@youcloudtech.com',
                    PasswordHash=generate_password_hash('admin123'),
                    IsAdmin=True,
                    IsActive=True,
                    Name='System Administrator',
                    CreatedAt=datetime.utcnow()
                )
                
                db.session.add(new_admin)
                db.session.commit()
                
                print("✅ New admin user created!")
                print("Email: admin@youcloudtech.com")
                print("Password: admin123")
                
        except Exception as e:
            print(f"Error: {e}")
            db.session.rollback()

if __name__ == "__main__":
    fix_admin_user()
