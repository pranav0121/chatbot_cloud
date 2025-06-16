#!/usr/bin/env python3
"""
Simple MSSQL Admin Fix - Direct Connection
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from app import app, db, User
    from werkzeug.security import generate_password_hash
    from datetime import datetime
    
    def fix_admin_user():
        print("=== MSSQL ADMIN USER FIX ===")
        
        with app.app_context():
            try:
                # Print database URI to verify MSSQL usage
                print(f"Database URI: {app.config['SQLALCHEMY_DATABASE_URI']}")
                
                if 'mssql' not in app.config['SQLALCHEMY_DATABASE_URI'].lower():
                    print("❌ ERROR: Not using MSSQL database!")
                    print("Current URI suggests SQLite or other database")
                    return False
                
                print("✅ Confirmed using MSSQL database")
                
                # Try to create tables if they don't exist
                print("Creating database tables if needed...")
                db.create_all()
                print("✅ Database tables verified")
                
                # Admin credentials
                admin_email = 'admin@youcloudtech.com'
                admin_password = 'admin123'
                
                print(f"Checking for admin user: {admin_email}")
                
                # Check for existing admin
                admin_user = User.query.filter_by(Email=admin_email).first()
                
                if admin_user:
                    print(f"Found existing admin user: {admin_user.Name}")
                    print(f"Current IsActive: {admin_user.IsActive}")
                    print(f"Current IsAdmin: {admin_user.IsAdmin}")
                    
                    # Update existing admin
                    admin_user.IsActive = True
                    admin_user.IsAdmin = True
                    admin_user.PasswordHash = generate_password_hash(admin_password)
                    admin_user.Name = 'System Administrator'
                    admin_user.OrganizationName = 'YouCloudTech'
                    admin_user.Position = 'Administrator'
                    admin_user.PriorityLevel = 'critical'
                    admin_user.LastLogin = datetime.utcnow()
                    
                    print("✅ Updated existing admin user")
                    
                else:
                    print("No admin user found, creating new one...")
                    
                    # Create new admin user
                    admin_user = User(
                        Name='System Administrator',
                        Email=admin_email,
                        PasswordHash=generate_password_hash(admin_password),
                        OrganizationName='YouCloudTech',
                        Position='Administrator',
                        PriorityLevel='critical',
                        Department='IT',
                        Phone='+1-555-ADMIN',
                        IsActive=True,
                        IsAdmin=True,
                        CreatedAt=datetime.utcnow(),
                        LastLogin=datetime.utcnow()
                    )
                    
                    db.session.add(admin_user)
                    print("✅ Created new admin user")
                
                # Commit changes
                db.session.commit()
                
                # Verify the admin user
                verification = User.query.filter_by(Email=admin_email, IsAdmin=True, IsActive=True).first()
                
                if verification:
                    print(f"\n🎯 ADMIN USER VERIFIED:")
                    print(f"   ID: {verification.UserID}")
                    print(f"   Name: {verification.Name}")
                    print(f"   Email: {verification.Email}")
                    print(f"   Organization: {verification.OrganizationName}")
                    print(f"   IsActive: {verification.IsActive}")
                    print(f"   IsAdmin: {verification.IsAdmin}")
                    
                    print(f"\n✅ SUCCESS!")
                    print(f"📧 Email: {admin_email}")
                    print(f"🔑 Password: {admin_password}")
                    print(f"🎯 Admin panel: http://localhost:5000/auth/admin/login")
                    
                    return True
                else:
                    print("❌ Admin user verification failed")
                    return False
                    
            except Exception as e:
                print(f"❌ Error: {e}")
                import traceback
                traceback.print_exc()
                return False
    
    if __name__ == "__main__":
        success = fix_admin_user()
        if success:
            print("\n🚀 Ready to test admin login!")
        else:
            print("\n❌ Admin fix failed")
            
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Please ensure all dependencies are installed")
except Exception as e:
    print(f"❌ Unexpected error: {e}")
    import traceback
    traceback.print_exc()
