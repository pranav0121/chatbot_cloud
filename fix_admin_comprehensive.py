#!/usr/bin/env python3
"""
Comprehensive Admin User Fix
Resolves inconsistent admin email addresses and ensures admin account is active
"""

from app import app, db, User
from werkzeug.security import generate_password_hash
from datetime import datetime

def fix_admin_credentials():
    """Fix admin user credentials and resolve email inconsistencies"""
    with app.app_context():
        try:
            print("=== COMPREHENSIVE ADMIN USER FIX ===")
            
            # List of potential admin emails to check/clean up
            admin_emails = [
                'admin@youcloudtech.com',
                'admin@supportcenter.com',
                'admin@support.com'
            ]
            
            # Find all existing admin users
            all_admin_users = []
            for email in admin_emails:
                user = User.query.filter_by(Email=email).first()
                if user:
                    all_admin_users.append(user)
                    print(f"Found existing user: {email} - Admin: {user.IsAdmin}, Active: {user.IsActive}")
            
            # Also check for any other admin users
            other_admins = User.query.filter_by(IsAdmin=True).all()
            for admin in other_admins:
                if admin not in all_admin_users:
                    all_admin_users.append(admin)
                    print(f"Found other admin user: {admin.Email} - Active: {admin.IsActive}")
            
            # Standardize to use admin@youcloudtech.com as the primary admin
            primary_admin = None
            
            # Look for existing admin@youcloudtech.com
            for user in all_admin_users:
                if user.Email == 'admin@youcloudtech.com':
                    primary_admin = user
                    break
            
            if primary_admin:
                print(f"\nUpdating primary admin: {primary_admin.Email}")
                # Ensure this admin is properly configured
                primary_admin.IsAdmin = True
                primary_admin.IsActive = True
                primary_admin.PasswordHash = generate_password_hash('admin123')
                primary_admin.Name = primary_admin.Name or 'System Administrator'
                primary_admin.OrganizationName = primary_admin.OrganizationName or 'YouCloudTech'
                primary_admin.Position = primary_admin.Position or 'Administrator'
                primary_admin.PriorityLevel = primary_admin.PriorityLevel or 'critical'
                primary_admin.LastLogin = datetime.utcnow()
                
                # Remove other admin accounts to avoid confusion
                for user in all_admin_users:
                    if user != primary_admin:
                        print(f"Removing duplicate admin account: {user.Email}")
                        db.session.delete(user)
                
            else:
                print("\nNo admin@youcloudtech.com found. Creating new primary admin...")
                
                # Remove all existing admin accounts first
                for user in all_admin_users:
                    print(f"Removing existing admin account: {user.Email}")
                    db.session.delete(user)
                
                # Create new primary admin
                primary_admin = User(
                    Name='System Administrator',
                    Email='admin@youcloudtech.com',
                    PasswordHash=generate_password_hash('admin123'),
                    OrganizationName='YouCloudTech',
                    Position='Administrator',
                    PriorityLevel='critical',
                    Department='IT',
                    Phone='+1-555-ADMIN',
                    IsAdmin=True,
                    IsActive=True,
                    CreatedAt=datetime.utcnow(),
                    LastLogin=datetime.utcnow()
                )
                db.session.add(primary_admin)
            
            # Commit all changes
            db.session.commit()
            
            print(f"\n✅ ADMIN USER SUCCESSFULLY CONFIGURED")
            print(f"📧 Email: admin@youcloudtech.com")
            print(f"🔑 Password: admin123")
            print(f"👤 Name: {primary_admin.Name}")
            print(f"✅ IsAdmin: {primary_admin.IsAdmin}")
            print(f"✅ IsActive: {primary_admin.IsActive}")
            print(f"\n🎯 You can now login to the admin panel with these credentials!")
            
            return True
            
        except Exception as e:
            print(f"❌ Error fixing admin user: {e}")
            db.session.rollback()
            import traceback
            traceback.print_exc()
            return False

if __name__ == "__main__":
    success = fix_admin_credentials()
    if success:
        print(f"\n🚀 NEXT STEPS:")
        print(f"1. Go to http://localhost:5000/auth/admin/login")
        print(f"2. Login with: admin@youcloudtech.com / admin123")
        print(f"3. Access the Super Admin Portal successfully!")
    else:
        print(f"\n❌ Fix failed. Please check the error messages above.")
