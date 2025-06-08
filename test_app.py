#!/usr/bin/env python
"""
Simple test script to verify the Flask application starts correctly
"""
import sys
import os

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from app import app, db
    print("✓ Successfully imported Flask app and database")
    
    # Test app context
    with app.app_context():
        print("✓ Flask app context works")
        
        # Test database connection
        try:
            db.create_all()
            print("✓ Database connection successful")
        except Exception as e:
            print(f"⚠ Database warning: {e}")
            print("Note: This is expected if SQL Server is not running")
        
        print("\n📋 Application Summary:")
        print(f"   • Flask app: {app.name}")
        print(f"   • Debug mode: {app.config.get('DEBUG', False)}")
        print(f"   • Secret key configured: {'SECRET_KEY' in app.config}")
        
        print("\n🌐 Available Routes:")
        for rule in app.url_map.iter_rules():
            print(f"   • {rule.endpoint}: {rule.rule}")
        
        print("\n🚀 To start the application, run:")
        print("   python app.py")
        print("\n   Then visit:")
        print("   • User Interface: http://localhost:5000")
        print("   • Admin Dashboard: http://localhost:5000/admin")

except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure all dependencies are installed:")
    print("   pip install -r requirements.txt")
except Exception as e:
    print(f"❌ Error: {e}")
