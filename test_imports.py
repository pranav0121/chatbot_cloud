#!/usr/bin/env python3
"""
Test script to verify all imports work without circular import issues
"""

import sys
import os

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test all critical imports"""
    try:
        print("Testing app.py imports...")
        import app
        print("✅ app.py imported successfully")
        
        print("Testing super_admin.py imports...")
        from super_admin import super_admin_bp
        print("✅ super_admin_bp imported successfully")
        
        print("Testing models imports...")
        from models import Partner, SLALog, TicketStatusLog, AuditLog
        print("✅ Extended models imported successfully")
        
        print("Testing Flask app initialization...")
        flask_app = app.app
        print(f"✅ Flask app initialized: {flask_app}")
        
        print("Testing database connection...")
        with flask_app.app_context():
            from app import db
            db.create_all()
            print("✅ Database connection and table creation successful")
        
        print("\n🎉 ALL IMPORTS AND INITIALIZATION SUCCESSFUL!")
        print("The application should start without errors.")
        return True
        
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        return False
    except Exception as e:
        print(f"❌ General Error: {e}")
        return False

if __name__ == "__main__":
    success = test_imports()
    sys.exit(0 if success else 1)
