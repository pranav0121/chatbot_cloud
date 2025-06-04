#!/usr/bin/env python3
"""
Database Migration Script - Add Attachment Table
This script adds the Attachments table to support file uploads in the chatbot system.
"""

import os
import sys
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Add the current directory to sys.path so we can import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import Config

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)

# Define the Attachment model for migration
class Attachment(db.Model):
    __tablename__ = 'Attachments'
    AttachmentID = db.Column(db.Integer, primary_key=True)
    MessageID = db.Column(db.Integer, db.ForeignKey('Messages.MessageID'))
    OriginalName = db.Column(db.String(255), nullable=False)
    StoredName = db.Column(db.String(255), nullable=False)
    FileSize = db.Column(db.Integer, nullable=False)
    MimeType = db.Column(db.String(100), nullable=False)
    CreatedAt = db.Column(db.DateTime, default=datetime.utcnow)

def run_migration():
    """Run the database migration"""
    try:
        with app.app_context():
            print("Starting database migration...")
            
            # Check if Attachments table already exists
            inspector = db.inspect(db.engine)
            existing_tables = inspector.get_table_names()
            
            if 'Attachments' in existing_tables:
                print("✓ Attachments table already exists. Migration not needed.")
                return True
            
            # Create the Attachments table
            print("Creating Attachments table...")
            db.create_all()
            
            print("✓ Migration completed successfully!")
            print("✓ Attachments table created with the following structure:")
            print("  - AttachmentID (Primary Key)")
            print("  - MessageID (Foreign Key to Messages.MessageID)")
            print("  - OriginalName (Original filename)")
            print("  - StoredName (Stored filename)")
            print("  - FileSize (File size in bytes)")
            print("  - MimeType (MIME type)")
            print("  - CreatedAt (Creation timestamp)")
            
            return True
            
    except Exception as e:
        print(f"❌ Migration failed: {str(e)}")
        return False

if __name__ == '__main__':
    success = run_migration()
    if success:
        print("\n🎉 Database migration completed successfully!")
        print("The chatbot now supports file attachments.")
    else:
        print("\n💥 Migration failed. Please check the error messages above.")
        sys.exit(1)