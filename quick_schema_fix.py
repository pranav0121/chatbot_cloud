#!/usr/bin/env python3
"""
Quick Database Schema Fix for metadata_json column
"""

import sys
import os

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def fix_metadata_column():
    """Fix the missing metadata_json column"""
    print("🔧 FIXING METADATA_JSON COLUMN...")
    
    try:
        import app
        from sqlalchemy import text
        
        with app.app.app_context():
            from app import db
            
            print("Adding metadata_json column to ticket_status_logs table...")
            
            # Add the missing column
            db.session.execute(text("""
                ALTER TABLE ticket_status_logs 
                ADD metadata_json NVARCHAR(MAX) NULL
            """))
            
            db.session.commit()
            print("✅ metadata_json column added successfully!")
            
            return True
            
    except Exception as e:
        if "already exists" in str(e).lower() or "duplicate column" in str(e).lower():
            print("✅ metadata_json column already exists!")
            return True
        else:
            print(f"❌ Error: {e}")
            return False

if __name__ == "__main__":
    success = fix_metadata_column()
    print("Schema fix completed!" if success else "Schema fix failed!")
    sys.exit(0 if success else 1)
