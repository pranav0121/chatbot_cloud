#!/usr/bin/env python3
"""
Fix critical database schema issues
"""

from config import Config
import os
import sys
from datetime import datetime
from sqlalchemy import create_engine, text, Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.exc import SQLAlchemyError

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


def main():
    print("=== FIXING DATABASE SCHEMA ISSUES ===")
    print(f"Timestamp: {datetime.now()}")

    config = Config()
    engine = create_engine(config.SQLALCHEMY_DATABASE_URI,
                           **config.SQLALCHEMY_ENGINE_OPTIONS)

    try:
        with engine.connect() as conn:
            print("\n1. Creating missing Organizations table...")
            try:
                create_organizations_sql = """
                IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Organizations' AND xtype='U')
                CREATE TABLE Organizations (
                    id INT IDENTITY(1,1) PRIMARY KEY,
                    name NVARCHAR(200) NOT NULL,
                    domain NVARCHAR(100),
                    created_at DATETIME2 DEFAULT GETDATE(),
                    created_by INT,
                    is_active BIT DEFAULT 1,
                    FOREIGN KEY (created_by) REFERENCES Users(UserID)
                )
                """
                conn.execute(text(create_organizations_sql))
                print("   ✓ Organizations table created successfully")
            except Exception as e:
                print(f"   ⚠ Organizations table creation issue: {e}")

            print("\n2. Creating missing FAQ table...")
            try:
                create_faq_sql = """
                IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='FAQ' AND xtype='U')
                CREATE TABLE FAQ (
                    id INT IDENTITY(1,1) PRIMARY KEY,
                    question NVARCHAR(500) NOT NULL,
                    answer NTEXT NOT NULL,
                    category NVARCHAR(100),
                    language NVARCHAR(10) DEFAULT 'en',
                    is_active BIT DEFAULT 1,
                    created_at DATETIME2 DEFAULT GETDATE(),
                    updated_at DATETIME2 DEFAULT GETDATE()
                )
                """
                conn.execute(text(create_faq_sql))
                print("   ✓ FAQ table created successfully")
            except Exception as e:
                print(f"   ⚠ FAQ table creation issue: {e}")

            print("\n3. Adding missing columns to Users table...")
            try:
                # Check if username column exists
                check_username_sql = """
                SELECT COUNT(*) as col_count 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_NAME = 'Users' AND COLUMN_NAME = 'username'
                """
                result = conn.execute(text(check_username_sql)).fetchone()
                if result.col_count == 0:
                    add_username_sql = "ALTER TABLE Users ADD username NVARCHAR(80)"
                    conn.execute(text(add_username_sql))
                    print("   ✓ Added username column to Users table")
                else:
                    print("   ✓ username column already exists")

                # Check if email column exists
                check_email_sql = """
                SELECT COUNT(*) as col_count 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_NAME = 'Users' AND COLUMN_NAME = 'email'
                """
                result = conn.execute(text(check_email_sql)).fetchone()
                if result.col_count == 0:
                    add_email_sql = "ALTER TABLE Users ADD email NVARCHAR(120)"
                    conn.execute(text(add_email_sql))
                    print("   ✓ Added email column to Users table")
                else:
                    print("   ✓ email column already exists")

            except Exception as e:
                print(f"   ⚠ Column addition issue: {e}")

            print("\n4. Updating existing user data to populate new columns...")
            try:
                # Populate username from Name or Email
                update_username_sql = """
                UPDATE Users 
                SET username = COALESCE(
                    CASE WHEN Name IS NOT NULL AND Name != '' THEN Name ELSE NULL END,
                    CASE WHEN Email IS NOT NULL AND Email != '' THEN LEFT(Email, CHARINDEX('@', Email + '@') - 1) ELSE NULL END,
                    'user' + CAST(UserID AS NVARCHAR(10))
                )
                WHERE username IS NULL OR username = ''
                """
                conn.execute(text(update_username_sql))

                # Populate email from Email column
                update_email_sql = """
                UPDATE Users 
                SET email = Email
                WHERE email IS NULL OR email = ''
                """
                conn.execute(text(update_email_sql))

                print("   ✓ Updated user data successfully")
            except Exception as e:
                print(f"   ⚠ Data update issue: {e}")

            print("\n5. Adding foreign key constraints if missing...")
            try:
                # Check if organization_id column exists in Users table
                check_org_id_sql = """
                SELECT COUNT(*) as col_count 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_NAME = 'Users' AND COLUMN_NAME = 'organization_id'
                """
                result = conn.execute(text(check_org_id_sql)).fetchone()
                if result.col_count == 0:
                    add_org_id_sql = "ALTER TABLE Users ADD organization_id INT"
                    conn.execute(text(add_org_id_sql))
                    print("   ✓ Added organization_id column to Users table")

                # Add foreign key constraint
                try:
                    add_fk_sql = """
                    IF NOT EXISTS (SELECT * FROM sys.foreign_keys WHERE name = 'FK_Users_Organizations')
                    ALTER TABLE Users ADD CONSTRAINT FK_Users_Organizations 
                    FOREIGN KEY (organization_id) REFERENCES Organizations(id)
                    """
                    conn.execute(text(add_fk_sql))
                    print("   ✓ Added foreign key constraint")
                except Exception as fk_e:
                    print(f"   ⚠ Foreign key constraint issue: {fk_e}")

            except Exception as e:
                print(f"   ⚠ Foreign key setup issue: {e}")

            print("\n6. Creating default data...")
            try:
                # Create default organization
                default_org_sql = """
                IF NOT EXISTS (SELECT * FROM Organizations WHERE name = 'Default Organization')
                INSERT INTO Organizations (name, domain, is_active) 
                VALUES ('Default Organization', 'default.com', 1)
                """
                conn.execute(text(default_org_sql))

                # Create some default FAQ entries
                default_faq_sql = """
                IF NOT EXISTS (SELECT * FROM FAQ WHERE question LIKE 'How to create%')
                INSERT INTO FAQ (question, answer, category, language) VALUES
                ('How to create a support ticket?', 'You can create a support ticket by clicking the "New Ticket" button and filling out the required information.', 'General', 'en'),
                ('How to check ticket status?', 'You can check your ticket status in the dashboard or by using the ticket ID in the search function.', 'General', 'en'),
                ('What are the support hours?', 'Our support team is available 24/7 for critical issues and during business hours for general inquiries.', 'General', 'en')
                """
                conn.execute(text(default_faq_sql))

                print("   ✓ Created default data")
            except Exception as e:
                print(f"   ⚠ Default data creation issue: {e}")

    except SQLAlchemyError as e:
        print(f"❌ Database error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

    print("\n=== SCHEMA FIX COMPLETED ===")
    print("✅ All database schema issues have been addressed")
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
