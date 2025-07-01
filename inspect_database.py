#!/usr/bin/env python3
"""
Database Schema Inspector
Check what tables and columns exist in the database
"""

import sqlite3
import os

def inspect_database():
    """Inspect the SQLite database schema"""
    
    db_path = "chatbot.db"
    if not os.path.exists(db_path):
        print(f"❌ Database file {db_path} not found!")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🔍 Database Schema Inspection")
        print("=" * 40)
        
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        print(f"\n📋 Found {len(tables)} tables:")
        for table in tables:
            table_name = table[0]
            print(f"\n📁 Table: {table_name}")
            
            # Get columns for each table
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            
            for col in columns:
                col_id, col_name, col_type, not_null, default_val, pk = col
                pk_marker = " [PK]" if pk else ""
                null_marker = " NOT NULL" if not_null else ""
                default_marker = f" DEFAULT {default_val}" if default_val else ""
                print(f"   - {col_name}: {col_type}{pk_marker}{null_marker}{default_marker}")
        
        # Check for device tracking related columns
        print(f"\n🔍 Device Tracking Status:")
        device_related_tables = []
        
        for table in tables:
            table_name = table[0]
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            
            device_columns = []
            for col in columns:
                col_name = col[1]
                if any(keyword in col_name.lower() for keyword in ['device', 'browser', 'mobile', 'useragent', 'ip']):
                    device_columns.append(col_name)
            
            if device_columns:
                device_related_tables.append((table_name, device_columns))
        
        if device_related_tables:
            print("   Found device-related columns:")
            for table_name, cols in device_related_tables:
                print(f"   📋 {table_name}: {', '.join(cols)}")
        else:
            print("   ❌ No device-related columns found in existing tables")
        
        # Check if device_tracking_logs exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='device_tracking_logs'")
        if cursor.fetchone():
            print("   ✅ device_tracking_logs table exists")
            cursor.execute("SELECT COUNT(*) FROM device_tracking_logs")
            count = cursor.fetchone()[0]
            print(f"      Contains {count} records")
        else:
            print("   ❌ device_tracking_logs table does not exist")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error inspecting database: {e}")

if __name__ == "__main__":
    inspect_database()
