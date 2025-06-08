"""
Test script to verify the database fix worked
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db, Category, Ticket, User, Message
from config import Config
from sqlalchemy import text

def test_database_connection():
    """Test database connection and basic operations"""
    try:
        with app.app_context():
            print("Testing database connection...")
            
            # Test basic connection
            db.session.execute(text('SELECT 1'))
            print("✓ Database connection successful")
            
            # Test table queries
            categories = Category.query.all()
            print(f"✓ Categories table: {len(categories)} records")
            
            tickets = Ticket.query.all()
            print(f"✓ Tickets table: {len(tickets)} records")
            
            users = User.query.all()
            print(f"✓ Users table: {len(users)} records")
            
            messages = Message.query.all()
            print(f"✓ Messages table: {len(messages)} records")
            
            # Test admin tickets query (the one that was failing)
            admin_tickets = db.session.query(Ticket, User, Category).join(
                User, Ticket.UserID == User.UserID, isouter=True
            ).join(
                Category, Ticket.CategoryID == Category.CategoryID
            ).order_by(Ticket.CreatedAt.desc()).all()
            
            print(f"✓ Admin tickets query: {len(admin_tickets)} records")
            
            print("\n🎉 All database tests passed!")
            print("The admin panel should now work without errors.")
            return True
            
    except Exception as e:
        print(f"✗ Database test failed: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_database_connection()
    if not success:
        sys.exit(1)
