"""
Simple test to verify database connection and app startup
"""
import os
import sys

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    print("Testing database connection...")
    
    # Import required modules
    from app import app, db, Category
    from sqlalchemy import text
    
    # Test within app context
    with app.app_context():
        # Test basic database connection
        result = db.session.execute(text('SELECT 1'))
        print("✓ Database connection successful!")
        
        # Test table access
        categories = Category.query.all()
        print(f"✓ Found {len(categories)} categories")
        
        # Test if we can access category names
        for cat in categories[:3]:  # Show first 3
            print(f"  - {cat.Name} ({cat.Team})")
        
        print("\n🎉 Database test passed! Admin panel should work now.")
        
except Exception as e:
    print(f"❌ Error: {str(e)}")
    print("Database may need to be recreated.")
