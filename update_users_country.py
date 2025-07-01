#!/usr/bin/env python3
"""
Update existing users with their likely country (India)
"""

from app import app, db, User
from location_service import location_service
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def update_existing_users_country():
    """Update existing users with detected country information"""
    logger.info("🌍 UPDATING EXISTING USERS WITH COUNTRY INFORMATION")
    logger.info("=" * 60)
    
    with app.app_context():
        try:
            # Get current location (India)
            location_info = location_service.get_current_location()
            if not location_info:
                logger.error("❌ Could not detect location")
                return False
            
            detected_country = location_info['country']
            logger.info(f"🎯 Detected country: {detected_country}")
            logger.info(f"   City: {location_info['city']}")
            logger.info(f"   Region: {location_info['region']}")
            
            # Get users with Unknown or NULL country
            users_to_update = User.query.filter(
                db.or_(
                    User.Country == None,
                    User.Country == 'Unknown',
                    User.Country == ''
                )
            ).all()
            
            logger.info(f"📊 Found {len(users_to_update)} users to update")
            
            if len(users_to_update) == 0:
                logger.info("ℹ️  No users need country updates")
                return True
            
            # Update users
            updated_count = 0
            for user in users_to_update:
                try:
                    old_country = user.Country
                    user.Country = detected_country
                    
                    logger.info(f"   ✅ User #{user.UserID} ({user.Name}): {old_country} → {detected_country}")
                    updated_count += 1
                    
                except Exception as e:
                    logger.error(f"   ❌ Failed to update User #{user.UserID}: {e}")
            
            # Commit changes
            db.session.commit()
            logger.info(f"💾 Database updated: {updated_count} users saved")
            
            # Verify updates
            logger.info("\n📋 Verification:")
            users_with_country = User.query.filter(User.Country == detected_country).count()
            total_users = User.query.count()
            coverage = (users_with_country / total_users * 100) if total_users > 0 else 0
            
            logger.info(f"   Users with {detected_country}: {users_with_country}/{total_users}")
            logger.info(f"   Coverage: {coverage:.1f}%")
            
            # Show sample updated users
            logger.info("\n👥 Sample Updated Users:")
            sample_users = User.query.filter(User.Country == detected_country).limit(5).all()
            for user in sample_users:
                logger.info(f"   User #{user.UserID}: {user.Name} ({user.Email}) - {user.Country}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error updating users: {e}")
            db.session.rollback()
            return False

if __name__ == "__main__":
    success = update_existing_users_country()
    
    if success:
        logger.info("\n🎉 USERS COUNTRY UPDATE COMPLETE!")
        logger.info("✅ All existing users now have country information")
    else:
        logger.error("\n❌ USERS COUNTRY UPDATE FAILED")
