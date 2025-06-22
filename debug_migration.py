#!/usr/bin/env python3
"""
Debug Migration Script - Check what's failing
"""

import sys
import traceback
from config import Config
from odoo_service import OdooService

def debug_connections():
    """Debug connection issues"""
    print("🔍 Debugging Migration Issues...")
    
    try:
        print("1. Testing Config loading...")
        config = Config()
        print(f"   ✅ Config loaded")
        print(f"   - ODOO_URL: {config.ODOO_URL}")
        print(f"   - ODOO_DB: {config.ODOO_DB}")
        print(f"   - ODOO_USERNAME: {config.ODOO_USERNAME}")
        print(f"   - Has password: {'Yes' if hasattr(config, 'ODOO_PASSWORD') and config.ODOO_PASSWORD else 'No'}")
        
        print("\\n2. Testing Odoo connection...")
        odoo_service = OdooService(
            url=config.ODOO_URL,
            db=config.ODOO_DB,
            username=config.ODOO_USERNAME,
            password=config.ODOO_PASSWORD
        )
        print("   ✅ Odoo connection successful")
        
        print("\\n3. Testing customer creation...")
        try:
            customer_id = odoo_service.create_customer(
                name="Debug Test Customer",
                email="debug@test.com",
                comment="Debug test customer"
            )
            print(f"   ✅ Customer created with ID: {customer_id}")
        except Exception as e:
            print(f"   ❌ Customer creation failed: {e}")
            traceback.print_exc()
        
        print("\\n4. Testing ticket creation...")
        try:
            ticket_id = odoo_service.create_ticket(
                name="Debug Test Ticket",
                description="This is a debug test ticket",
                partner_id=customer_id if 'customer_id' in locals() else None,
                priority="1"
            )
            print(f"   ✅ Ticket created with ID: {ticket_id}")
        except Exception as e:
            print(f"   ❌ Ticket creation failed: {e}")
            traceback.print_exc()
        
        print("\\n5. Testing database connection...")
        try:
            import pyodbc
            
            if config.DB_USE_WINDOWS_AUTH:
                conn_str = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={config.DB_SERVER};DATABASE={config.DB_DATABASE};Trusted_Connection=yes;"
            else:
                conn_str = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={config.DB_SERVER};DATABASE={config.DB_DATABASE};UID={config.DB_USERNAME};PWD={config.DB_PASSWORD};"
            
            conn = pyodbc.connect(conn_str)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM Users")
            user_count = cursor.fetchone()[0]
            print(f"   ✅ MSSQL connection successful - Found {user_count} users")
            conn.close()
            
        except Exception as e:
            print(f"   ❌ MSSQL connection failed: {e}")
            traceback.print_exc()
        
        print("\\n✅ All debugging completed!")
        
    except Exception as e:
        print(f"❌ Debug failed: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    debug_connections()
