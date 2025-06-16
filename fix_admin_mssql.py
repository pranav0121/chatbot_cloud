#!/usr/bin/env python3
"""
MSSQL Admin User Fix - Comprehensive Solution
Ensures MSSQL connection and creates/fixes admin user
"""

import pyodbc
import logging
import sys
import os
from werkzeug.security import generate_password_hash
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_odbc_drivers():
    """Check available ODBC drivers for SQL Server"""
    try:
        drivers = pyodbc.drivers()
        sql_drivers = [d for d in drivers if 'SQL Server' in d]
        logger.info("Available SQL Server ODBC drivers:")
        for driver in sql_drivers:
            logger.info(f"  - {driver}")
        return sql_drivers
    except Exception as e:
        logger.error(f"Error checking ODBC drivers: {e}")
        return []

def get_mssql_connection():
    """Get MSSQL connection using best available driver"""
    # Server configuration
    server = os.getenv('DB_SERVER', 'PRANAV\\SQLEXPRESS')
    database = os.getenv('DB_DATABASE', 'SupportChatbot')
    
    # Try different driver options
    drivers_to_try = [
        'ODBC Driver 17 for SQL Server',
        'ODBC Driver 13 for SQL Server', 
        'ODBC Driver 11 for SQL Server',
        'SQL Server Native Client 11.0',
        'SQL Server'
    ]
    
    available_drivers = check_odbc_drivers()
    
    # Find the best available driver
    driver_to_use = None
    for driver in drivers_to_try:
        if driver in available_drivers:
            driver_to_use = driver
            break
    
    if not driver_to_use:
        logger.error("❌ No suitable SQL Server ODBC driver found!")
        return None
    
    logger.info(f"Using driver: {driver_to_use}")
    
    # Build connection string with Windows Authentication
    conn_string = f"DRIVER={{{driver_to_use}}};SERVER={server};DATABASE={database};Trusted_Connection=yes;"
    
    try:
        logger.info(f"Connecting to MSSQL: {server}/{database}")
        conn = pyodbc.connect(conn_string, timeout=30)
        logger.info("✅ MSSQL connection successful!")
        return conn
    except Exception as e:
        logger.error(f"❌ MSSQL connection failed: {e}")
        return None

def ensure_database_exists():
    """Ensure the SupportChatbot database exists"""
    try:
        server = os.getenv('DB_SERVER', 'PRANAV\\SQLEXPRESS')
        database = 'SupportChatbot'
        
        # Get available drivers
        available_drivers = check_odbc_drivers()
        if not available_drivers:
            logger.error("❌ No SQL Server ODBC drivers available")
            return False
        
        driver_to_use = available_drivers[0]  # Use first available driver
        
        # Connect to master database first
        master_conn_string = f"DRIVER={{{driver_to_use}}};SERVER={server};DATABASE=master;Trusted_Connection=yes;"
        
        logger.info("Checking if SupportChatbot database exists...")
        conn = pyodbc.connect(master_conn_string, timeout=30)
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Check if database exists
        cursor.execute("""
            SELECT COUNT(*) 
            FROM sys.databases 
            WHERE name = ?
        """, database)
        
        db_exists = cursor.fetchone()[0] > 0
        
        if not db_exists:
            logger.info(f"Creating database '{database}'...")
            cursor.execute(f"CREATE DATABASE [{database}]")
            logger.info(f"✅ Database '{database}' created successfully!")
        else:
            logger.info(f"✅ Database '{database}' already exists")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        logger.error(f"❌ Error with database setup: {e}")
        return False

def ensure_users_table():
    """Ensure Users table exists with correct schema"""
    conn = get_mssql_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        
        logger.info("Ensuring Users table exists...")
        
        # Create Users table if it doesn't exist
        cursor.execute("""
            IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Users' AND type='U')
            CREATE TABLE Users (
                UserID int IDENTITY(1,1) PRIMARY KEY,
                Name nvarchar(100) NOT NULL,
                Email nvarchar(255) NOT NULL UNIQUE,
                PasswordHash nvarchar(255) NOT NULL,
                OrganizationName nvarchar(200),
                Position nvarchar(100),
                PriorityLevel nvarchar(20) DEFAULT 'medium',
                Phone nvarchar(20),
                Department nvarchar(100),
                PreferredLanguage nvarchar(10) DEFAULT 'en',
                IsActive bit DEFAULT 1,
                IsAdmin bit DEFAULT 0,
                LastLogin datetime2,
                CreatedAt datetime2 DEFAULT GETDATE()
            )
        """)
        
        conn.commit()
        logger.info("✅ Users table verified/created")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        logger.error(f"❌ Error creating Users table: {e}")
        return False

def fix_admin_user_mssql():
    """Fix admin user in MSSQL database"""
    conn = get_mssql_connection()
    if not conn:
        logger.error("❌ Cannot connect to MSSQL")
        return False
    
    try:
        cursor = conn.cursor()
        
        # Standard admin credentials
        admin_email = 'admin@youcloudtech.com'
        admin_password = 'admin123'
        admin_name = 'System Administrator'
        
        # Generate password hash
        password_hash = generate_password_hash(admin_password)
        
        logger.info(f"Checking for existing admin user: {admin_email}")
        
        # Check if admin user exists
        cursor.execute("SELECT UserID, IsActive, IsAdmin FROM Users WHERE Email = ?", admin_email)
        existing_admin = cursor.fetchone()
        
        if existing_admin:
            user_id, is_active, is_admin = existing_admin
            logger.info(f"Found existing admin user (ID: {user_id}, Active: {is_active}, Admin: {is_admin})")
            
            # Update existing admin user
            cursor.execute("""
                UPDATE Users 
                SET PasswordHash = ?, 
                    IsActive = 1, 
                    IsAdmin = 1,
                    Name = ?,
                    OrganizationName = 'YouCloudTech',
                    Position = 'Administrator',
                    PriorityLevel = 'critical',
                    LastLogin = GETDATE()
                WHERE Email = ?
            """, password_hash, admin_name, admin_email)
            
            logger.info("✅ Updated existing admin user")
            
        else:
            # Create new admin user
            logger.info("Creating new admin user...")
            cursor.execute("""
                INSERT INTO Users (
                    Name, Email, PasswordHash, OrganizationName, Position, 
                    PriorityLevel, Department, Phone, IsActive, IsAdmin, 
                    LastLogin, CreatedAt
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1, 1, GETDATE(), GETDATE())
            """, admin_name, admin_email, password_hash, 'YouCloudTech', 
                'Administrator', 'critical', 'IT', '+1-555-ADMIN')
            
            logger.info("✅ Created new admin user")
        
        # Commit changes
        conn.commit()
        
        # Verify the admin user
        cursor.execute("""
            SELECT UserID, Name, Email, IsActive, IsAdmin, OrganizationName 
            FROM Users 
            WHERE Email = ?
        """, admin_email)
        
        admin_info = cursor.fetchone()
        if admin_info:
            user_id, name, email, is_active, is_admin, org = admin_info
            logger.info(f"\n🎯 ADMIN USER VERIFIED:")
            logger.info(f"   UserID: {user_id}")
            logger.info(f"   Name: {name}")
            logger.info(f"   Email: {email}")
            logger.info(f"   Organization: {org}")
            logger.info(f"   IsActive: {bool(is_active)}")
            logger.info(f"   IsAdmin: {bool(is_admin)}")
        
        cursor.close()
        conn.close()
        
        print(f"\n✅ ADMIN USER SUCCESSFULLY CONFIGURED IN MSSQL")
        print(f"📧 Email: {admin_email}")
        print(f"🔑 Password: {admin_password}")
        print(f"🎯 You can now login to the admin panel!")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error fixing admin user: {e}")
        return False

def main():
    """Main function to fix admin user in MSSQL"""
    print("=== MSSQL ADMIN USER FIX ===")
    
    # Step 1: Check ODBC drivers
    print("\n1. Checking ODBC drivers...")
    drivers = check_odbc_drivers()
    if not drivers:
        print("❌ No SQL Server ODBC drivers found!")
        print("Please install SQL Server ODBC Driver 17 or later")
        return False
    
    # Step 2: Ensure database exists
    print("\n2. Ensuring database exists...")
    if not ensure_database_exists():
        print("❌ Database setup failed")
        return False
    
    # Step 3: Ensure Users table exists
    print("\n3. Ensuring Users table exists...")
    if not ensure_users_table():
        print("❌ Users table setup failed")
        return False
    
    # Step 4: Fix admin user
    print("\n4. Fixing admin user...")
    if not fix_admin_user_mssql():
        print("❌ Admin user fix failed")
        return False
    
    print(f"\n🚀 SUCCESS! Next steps:")
    print(f"1. Go to http://localhost:5000/auth/admin/login")
    print(f"2. Login with: admin@youcloudtech.com / admin123")
    print(f"3. Access the Super Admin Portal!")
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)
