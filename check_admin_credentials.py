#!/usr/bin/env python3
"""
Check what admin users actually exist in the database
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db, User
from werkzeug.security import check_password_hash

def check_admin_users():
    with app.app_context():
        print("=== CHECKING ADMIN USERS IN DATABASE ===")
        
        # Get all users with admin role
        admin_users = User.query.filter_by(IsAdmin=True).all()
        
        print(f"Found {len(admin_users)} admin users:")
        
        for user in admin_users:
            print(f"\nUser ID: {user.UserID}")
            print(f"Name: {user.Name}")
            print(f"Email: {user.Email}")
            print(f"IsAdmin: {user.IsAdmin}")
            print(f"IsActive: {user.IsActive}")
            print(f"Created: {user.CreatedAt}")
            print(f"Last Login: {user.LastLogin}")
            
            # Test common passwords
            test_passwords = [
                'SuperSecure2024!',
                'AdminYCT2024!',
                'admin123',
                'password',
                'Admin123!',
                'SuperAdmin2024!'
            ]
            
            print("Testing passwords:")
            for pwd in test_passwords:
                if check_password_hash(user.PasswordHash, pwd):
                    print(f"  ✓ WORKING PASSWORD: {pwd}")
                else:
                    print(f"  ✗ {pwd}")
        
        # Check all users to see full picture
        print("\n=== ALL USERS SUMMARY ===")
        all_users = User.query.all()
        print(f"Total users in database: {len(all_users)}")
        
        for user in all_users:
            print(f"  {user.Email} - IsAdmin: {user.IsAdmin} - Active: {user.IsActive}")

if __name__ == "__main__":
    check_admin_users()
