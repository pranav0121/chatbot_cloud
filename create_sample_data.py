#!/usr/bin/env python3
"""
Create sample data for testing the chatbot application
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db, User, Category
from werkzeug.security import generate_password_hash
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_sample_data():
    """Create sample users and categories for testing"""
    with app.app_context():
        try:
            logger.info("Creating sample data...")
              # Create admin user
            users_data = [
                {'name': 'Admin User', 'email': 'admin@youcloudtech.com', 'password': 'admin123'}
            ]
            
            for user_data in users_data:
                # Check if user already exists
                existing_user = User.query.filter_by(Email=user_data['email']).first()
                if not existing_user:
                    user = User(
                        Name=user_data['name'],
                        Email=user_data['email'],
                        PasswordHash=generate_password_hash(user_data['password'])
                    )
                    db.session.add(user)
                    logger.info(f"Created user: {user_data['name']} ({user_data['email']})")
                else:
                    logger.info(f"User already exists: {user_data['email']}")
            
            # Create categories if they don't exist
            categories_data = [
                {'name': 'General Support', 'team': 'General'},
                {'name': 'Technical Issues', 'team': 'Tech'},
                {'name': 'Billing Questions', 'team': 'Billing'},
                {'name': 'Product Issues', 'team': 'Product'}
            ]
            
            for cat_data in categories_data:
                existing_category = Category.query.filter_by(Name=cat_data['name']).first()
                if not existing_category:
                    category = Category(
                        Name=cat_data['name'],
                        Team=cat_data['team']
                    )
                    db.session.add(category)
                    logger.info(f"Created category: {cat_data['name']}")
                else:
                    logger.info(f"Category already exists: {cat_data['name']}")
            
            # Commit all changes
            db.session.commit()
            logger.info("Sample data created successfully!")
            
            # Print login credentials
            print("\n" + "="*60)
            print("SAMPLE LOGIN CREDENTIALS:")
            print("="*60)
            for user_data in users_data:
                print(f"Email: {user_data['email']}")
                print(f"Password: {user_data['password']}")
                print("-" * 40)
            print("="*60)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to create sample data: {e}")
            db.session.rollback()
            return False

if __name__ == "__main__":
    success = create_sample_data()
    if success:
        print("Sample data creation completed successfully!")
    else:
        print("Sample data creation failed!")
        exit(1)
