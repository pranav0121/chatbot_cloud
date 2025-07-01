#!/usr/bin/env python3
"""
Check admin credentials and test login
"""

from app import app, db, User
from werkzeug.security import check_password_hash

def check_admin_credentials():
    with app.app_context():
        print("=== CHECKING ADMIN CREDENTIALS ===\n")
        
        # Check all potential admin emails
        admin_emails = [
            'superadmin@youcloudtech.com',
            'admin@youcloudtech.com', 
            'admin@supportcenter.com',
            'admin@chatbot.com'
        ]
        
        for email in admin_emails:
            user = User.query.filter_by(Email=email).first()
            if user:
                print(f"✓ Found user: {email}")
                print(f"  Name: {user.Name}")
                print(f"  IsAdmin: {user.IsAdmin}")
                print(f"  IsActive: {user.IsActive}")
                print(f"  Has Password Hash: {bool(user.PasswordHash)}")
                
                # Test common passwords
                test_passwords = ['youcloud2024!', 'admin123', 'password', 'admin']
                for pwd in test_passwords:
                    if user.PasswordHash and check_password_hash(user.PasswordHash, pwd):
                        print(f"  ✓ Password '{pwd}' WORKS!")
                        break
                else:
                    print(f"  ✗ None of the test passwords work")
                print()
            else:
                print(f"✗ No user found: {email}\n")

if __name__ == "__main__":
    check_admin_credentials()
