#!/usr/bin/env python3
"""
Clean up old test users, keeping only the new admin user
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db, User
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def cleanup_old_users():
    """Remove old test users, keep only the new admin"""
    with app.app_context():
        try:
            logger.info("Cleaning up old users...")
            
            # List of old emails to remove
            old_emails = [
                'admin@example.com',
                'test@example.com', 
                'john@example.com',
                'jane@example.com'
            ]
            
            for email in old_emails:
                user = User.query.filter_by(Email=email).first()
                if user:
                    db.session.delete(user)
                    logger.info(f"Deleted old user: {email}")
                else:
                    logger.info(f"User not found: {email}")
            
            # Commit changes
            db.session.commit()
            logger.info("Cleanup completed successfully!")
            
            # Show remaining users
            remaining_users = User.query.all()
            print("\n" + "="*50)
            print("REMAINING USERS:")
            print("="*50)
            for user in remaining_users:
                print(f"Name: {user.Name}")
                print(f"Email: {user.Email}")
                print("-" * 30)
            print("="*50)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to cleanup users: {e}")
            db.session.rollback()
            return False

if __name__ == "__main__":
    success = cleanup_old_users()
    if success:
        print("User cleanup completed successfully!")
    else:
        print("User cleanup failed!")
        exit(1)
