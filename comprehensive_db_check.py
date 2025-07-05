#!/usr/bin/env python3
"""
Comprehensive Database Health Check and Issue Detection
"""

import sys
import os
import traceback
from datetime import datetime
from sqlalchemy import text, inspect, create_engine
from sqlalchemy.exc import SQLAlchemyError

# Add current directory to path
sys.path.append('.')


def test_database_connection():
    """Test database connection and basic functionality"""
    print("=== COMPREHENSIVE DATABASE HEALTH CHECK ===")
    print(f"Timestamp: {datetime.now()}")
    print()

    try:
        from config import Config
        from database import db, init_app
        from flask import Flask

        config = Config()
        print(f"DB_SERVER: {config.DB_SERVER}")
        print(f"DB_DATABASE: {config.DB_DATABASE}")
        print(f"DB_USERNAME: {config.DB_USERNAME}")
        print(f"DB_USE_WINDOWS_AUTH: {config.DB_USE_WINDOWS_AUTH}")
        print(f"Connection URI: {config.SQLALCHEMY_DATABASE_URI}")
        print()

        # Create Flask app and initialize database
        app = Flask(__name__)
        app.config.from_object(Config)

        # Configure SQLAlchemy
        app.config['SQLALCHEMY_DATABASE_URI'] = config.SQLALCHEMY_DATABASE_URI
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        app.config['SQLALCHEMY_ENGINE_OPTIONS'] = config.SQLALCHEMY_ENGINE_OPTIONS

        init_app(app)

        issues_found = []

        with app.app_context():
            # Test 1: Basic Connection
            print("1. Testing basic database connection...")
            try:
                result = db.session.execute(text('SELECT 1 as test'))
                row = result.fetchone()
                if row and row[0] == 1:
                    print("   ✓ Basic connection successful")
                else:
                    issues_found.append("Basic connection test failed")
                    print("   ✗ Basic connection test failed")
            except Exception as e:
                issues_found.append(f"Database connection failed: {str(e)}")
                print(f"   ✗ Connection failed: {str(e)}")
                return issues_found

            # Test 2: Check Tables Exist
            print("\n2. Checking required tables exist...")
            required_tables = [
                'Users', 'Tickets', 'Categories', 'Messages', 'Feedback',
                'Attachments', 'CommonQueries', 'Organizations', 'FAQ'
            ]

            try:
                tables_query = text("""
                    SELECT TABLE_NAME 
                    FROM INFORMATION_SCHEMA.TABLES 
                    WHERE TABLE_TYPE = 'BASE TABLE'
                    ORDER BY TABLE_NAME
                """)
                existing_tables = [
                    row[0] for row in db.session.execute(tables_query).fetchall()]
                print(
                    f"   Found {len(existing_tables)} tables: {existing_tables}")

                missing_tables = []
                for table in required_tables:
                    if table not in existing_tables:
                        missing_tables.append(table)

                if missing_tables:
                    issues_found.append(
                        f"Missing required tables: {missing_tables}")
                    print(f"   ✗ Missing tables: {missing_tables}")
                else:
                    print("   ✓ All required tables exist")

            except Exception as e:
                issues_found.append(f"Failed to check tables: {str(e)}")
                print(f"   ✗ Failed to check tables: {str(e)}")

            # Test 3: Check Table Schemas
            print("\n3. Checking table schemas...")
            try:
                from database import User, Ticket, Category, Message

                # Check Users table
                users_query = text("SELECT TOP 1 * FROM Users")
                try:
                    db.session.execute(users_query)
                    print("   ✓ Users table accessible")
                except Exception as e:
                    issues_found.append(f"Users table issue: {str(e)}")
                    print(f"   ✗ Users table issue: {str(e)}")

                # Check Tickets table
                tickets_query = text("SELECT TOP 1 * FROM Tickets")
                try:
                    db.session.execute(tickets_query)
                    print("   ✓ Tickets table accessible")
                except Exception as e:
                    issues_found.append(f"Tickets table issue: {str(e)}")
                    print(f"   ✗ Tickets table issue: {str(e)}")

                # Check Categories table
                categories_query = text("SELECT TOP 1 * FROM Categories")
                try:
                    db.session.execute(categories_query)
                    print("   ✓ Categories table accessible")
                except Exception as e:
                    issues_found.append(f"Categories table issue: {str(e)}")
                    print(f"   ✗ Categories table issue: {str(e)}")

            except Exception as e:
                issues_found.append(f"Schema check failed: {str(e)}")
                print(f"   ✗ Schema check failed: {str(e)}")

            # Test 4: Check Critical Columns
            print("\n4. Checking critical table columns...")
            try:
                # Check Users table columns
                users_columns_query = text("""
                    SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE
                    FROM INFORMATION_SCHEMA.COLUMNS 
                    WHERE TABLE_NAME = 'Users'
                    ORDER BY COLUMN_NAME
                """)
                users_columns = db.session.execute(
                    users_columns_query).fetchall()
                user_column_names = [col[0] for col in users_columns]
                print(f"   Users columns: {user_column_names}")

                # Note: Email is capitalized
                required_user_columns = ['UserID', 'username', 'Email']
                missing_user_cols = [
                    col for col in required_user_columns if col not in user_column_names]
                if missing_user_cols:
                    issues_found.append(
                        f"Missing Users columns: {missing_user_cols}")
                    print(f"   ✗ Missing Users columns: {missing_user_cols}")
                else:
                    print("   ✓ Users table has required columns")

                # Check Tickets table columns
                tickets_columns_query = text("""
                    SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE
                    FROM INFORMATION_SCHEMA.COLUMNS 
                    WHERE TABLE_NAME = 'Tickets'
                    ORDER BY COLUMN_NAME
                """)
                tickets_columns = db.session.execute(
                    tickets_columns_query).fetchall()
                ticket_column_names = [col[0] for col in tickets_columns]
                print(f"   Tickets columns: {ticket_column_names}")

                required_ticket_columns = [
                    'TicketID', 'UserID', 'Subject', 'Status', 'CreatedAt']
                missing_ticket_cols = [
                    col for col in required_ticket_columns if col not in ticket_column_names]
                if missing_ticket_cols:
                    issues_found.append(
                        f"Missing Tickets columns: {missing_ticket_cols}")
                    print(
                        f"   ✗ Missing Tickets columns: {missing_ticket_cols}")
                else:
                    print("   ✓ Tickets table has required columns")

            except Exception as e:
                issues_found.append(f"Column check failed: {str(e)}")
                print(f"   ✗ Column check failed: {str(e)}")

            # Test 5: Check Data Integrity
            print("\n5. Checking data integrity...")
            try:
                # Count records
                user_count = db.session.execute(
                    text("SELECT COUNT(*) FROM Users")).fetchone()[0]
                ticket_count = db.session.execute(
                    text("SELECT COUNT(*) FROM Tickets")).fetchone()[0]
                category_count = db.session.execute(
                    text("SELECT COUNT(*) FROM Categories")).fetchone()[0]

                print(f"   Users: {user_count} records")
                print(f"   Tickets: {ticket_count} records")
                print(f"   Categories: {category_count} records")

                if category_count == 0:
                    issues_found.append(
                        "No categories found - may cause ticket creation issues")
                    print("   ⚠ Warning: No categories found")

                # Check for orphaned tickets
                orphaned_tickets = db.session.execute(text("""
                    SELECT COUNT(*) FROM Tickets t 
                    LEFT JOIN Users u ON t.UserID = u.UserID 
                    WHERE u.UserID IS NULL AND t.UserID IS NOT NULL
                """)).fetchone()[0]

                if orphaned_tickets > 0:
                    issues_found.append(
                        f"Found {orphaned_tickets} orphaned tickets")
                    print(f"   ✗ Found {orphaned_tickets} orphaned tickets")
                else:
                    print("   ✓ No orphaned tickets found")

            except Exception as e:
                issues_found.append(f"Data integrity check failed: {str(e)}")
                print(f"   ✗ Data integrity check failed: {str(e)}")

            # Test 6: Check Foreign Key Constraints
            print("\n6. Checking foreign key constraints...")
            try:
                fk_query = text("""
                    SELECT 
                        fk.name as constraint_name,
                        tp.name as parent_table,
                        cp.name as parent_column,
                        tr.name as referenced_table,
                        cr.name as referenced_column
                    FROM sys.foreign_keys fk
                    INNER JOIN sys.tables tp ON fk.parent_object_id = tp.object_id
                    INNER JOIN sys.tables tr ON fk.referenced_object_id = tr.object_id
                    INNER JOIN sys.foreign_key_columns fkc ON fk.object_id = fkc.constraint_object_id
                    INNER JOIN sys.columns cp ON fkc.parent_column_id = cp.column_id AND fkc.parent_object_id = cp.object_id
                    INNER JOIN sys.columns cr ON fkc.referenced_column_id = cr.column_id AND fkc.referenced_object_id = cr.object_id
                    ORDER BY tp.name, cp.name
                """)
                fk_constraints = db.session.execute(fk_query).fetchall()
                print(
                    f"   Found {len(fk_constraints)} foreign key constraints")

                for fk in fk_constraints:
                    print(f"   FK: {fk[1]}.{fk[2]} -> {fk[3]}.{fk[4]}")

            except Exception as e:
                print(f"   ⚠ Could not check foreign keys: {str(e)}")

            # Test 7: Performance Check
            print("\n7. Checking database performance...")
            try:
                import time
                start_time = time.time()
                db.session.execute(text("SELECT COUNT(*) FROM Tickets"))
                query_time = time.time() - start_time

                if query_time > 5.0:
                    issues_found.append(
                        f"Slow query performance: {query_time:.2f}s")
                    print(f"   ⚠ Slow query performance: {query_time:.2f}s")
                else:
                    print(f"   ✓ Good query performance: {query_time:.3f}s")

            except Exception as e:
                print(f"   ⚠ Could not check performance: {str(e)}")

            # Test 8: Check Connection Pool
            print("\n8. Checking connection pool configuration...")
            try:
                engine = db.get_engine()
                pool = engine.pool
                print(f"   Pool size: {pool.size()}")
                print(f"   Pool timeout: {getattr(pool, '_timeout', 'N/A')}")
                print(
                    f"   Max overflow: {getattr(pool, '_max_overflow', 'N/A')}")
                print("   ✓ Connection pool configured")

            except Exception as e:
                print(f"   ⚠ Could not check connection pool: {str(e)}")

        print("\n=== SUMMARY ===")
        if issues_found:
            print(f"❌ Found {len(issues_found)} database issues:")
            for i, issue in enumerate(issues_found, 1):
                print(f"   {i}. {issue}")
        else:
            print("✅ No database issues found! Database is healthy.")

        return issues_found

    except Exception as e:
        print(f"❌ Critical error during database check: {str(e)}")
        print("Traceback:", traceback.format_exc())
        return [f"Critical error: {str(e)}"]


if __name__ == "__main__":
    issues = test_database_connection()
    if issues:
        print(f"\n🚨 Database requires attention: {len(issues)} issues found")
        sys.exit(1)
    else:
        print("\n✅ Database is production ready!")
        sys.exit(0)
