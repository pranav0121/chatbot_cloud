#!/usr/bin/env python3
"""
Check all admin users in the system
"""

from app import app, db, User
from werkzeug.security import generate_password_hash
from datetime import datetime

def check_admin_users():
    with app.app_context():
        try:
            print("=== CHECKING ALL ADMIN USERS ===")
            
            # Find all admin users
            all_admins = User.query.filter_by(IsAdmin=True).all()
            
            print(f"Found {len(all_admins)} admin user(s):")
            for admin in all_admins:
                print(f"  - Email: {admin.Email}")
                print(f"    Name: {admin.Name}")
                print(f"    IsActive: {admin.IsActive}")
                print(f"    IsAdmin: {admin.IsAdmin}")
                print()
            
            # Also check for potential admin emails
            potential_emails = [
                'admin@youcloudtech.com',
                'admin@supportcenter.com',
                'admin@support.com'
            ]
            
            print("=== CHECKING POTENTIAL ADMIN EMAILS ===")
            for email in potential_emails:
                user = User.query.filter_by(Email=email).first()
                if user:
                    print(f"✓ Found user with email {email}:")
                    print(f"  - Name: {user.Name}")
                    print(f"  - IsActive: {user.IsActive}")
                    print(f"  - IsAdmin: {user.IsAdmin}")
                else:
                    print(f"✗ No user found with email {email}")
                print()
                
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    check_admin_users()
