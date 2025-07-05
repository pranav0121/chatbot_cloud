#!/usr/bin/env python3
"""
Check SLA monitoring specific database schema and tables.
"""
import os
import pyodbc
from dotenv import load_dotenv


def check_sla_schema():
    """Check SLA monitoring specific database schema."""
    load_dotenv()

    server = os.getenv('DB_SERVER', 'PRANAV\\SQLEXPRESS')
    database = os.getenv('DB_DATABASE', 'SupportChatbot')
    use_windows_auth = os.getenv(
        'DB_USE_WINDOWS_AUTH', 'True').lower() == 'true'
    username = os.getenv('DB_USERNAME', '')
    password = os.getenv('DB_PASSWORD', '')

    # Use the most recent driver
    driver = "ODBC Driver 17 for SQL Server"

    try:
        if use_windows_auth:
            conn_str = f"DRIVER={{{driver}}};SERVER={server};DATABASE={database};Trusted_Connection=yes;"
        else:
            conn_str = f"DRIVER={{{driver}}};SERVER={server};DATABASE={database};UID={username};PWD={password};"

        with pyodbc.connect(conn_str) as conn:
            cursor = conn.cursor()

            print("=== SLA Monitoring Database Schema Check ===\n")

            # Check for sla_logs table
            cursor.execute("""
                SELECT TABLE_NAME 
                FROM INFORMATION_SCHEMA.TABLES 
                WHERE TABLE_NAME = 'sla_logs'
            """)
            sla_table = cursor.fetchone()
            print(f"sla_logs table exists: {bool(sla_table)}")

            if sla_table:
                # Check sla_logs columns
                cursor.execute("""
                    SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE
                    FROM INFORMATION_SCHEMA.COLUMNS 
                    WHERE TABLE_NAME = 'sla_logs'
                    ORDER BY ORDINAL_POSITION
                """)
                sla_columns = cursor.fetchall()
                print("sla_logs columns:")
                for col in sla_columns:
                    print(f"  - {col[0]} ({col[1]}, nullable: {col[2]})")

            print()

            # Check for Tickets table SLA columns
            cursor.execute("""
                SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_NAME = 'Tickets' AND COLUMN_NAME IN ('escalation_level', 'current_sla_target')
                ORDER BY COLUMN_NAME
            """)
            ticket_sla_columns = cursor.fetchall()
            print("Tickets SLA columns:")
            if ticket_sla_columns:
                for col in ticket_sla_columns:
                    print(f"  - {col[0]} ({col[1]}, nullable: {col[2]})")
            else:
                print("  No SLA columns found in Tickets table")

            print()

            # Check for all relevant tables
            tables_to_check = ['partners',
                               'bot_configurations', 'escalation_rules']
            cursor.execute("""
                SELECT TABLE_NAME 
                FROM INFORMATION_SCHEMA.TABLES 
                WHERE TABLE_NAME IN ('partners', 'bot_configurations', 'escalation_rules')
            """)
            existing_tables = [row[0] for row in cursor.fetchall()]
            print("Required tables for SLA monitoring:")
            for table in tables_to_check:
                exists = table in existing_tables
                print(f"  - {table}: {'✓' if exists else '✗'}")

            print()

            # Count records in key tables
            if sla_table:
                cursor.execute("SELECT COUNT(*) FROM sla_logs")
                sla_count = cursor.fetchone()[0]
                print(f"sla_logs records: {sla_count}")

            cursor.execute("SELECT COUNT(*) FROM Tickets")
            ticket_count = cursor.fetchone()[0]
            print(f"Tickets records: {ticket_count}")

            print()
            print("=== Schema Check Complete ===")

            # Overall assessment
            required_checks = [
                sla_table is not None,
                len(ticket_sla_columns) >= 2,
                'partners' in existing_tables,
                'bot_configurations' in existing_tables
            ]

            if all(required_checks):
                print("✅ All required tables and columns for SLA monitoring exist!")
                return True
            else:
                print("❌ Some required schema elements are missing for SLA monitoring")
                return False

    except Exception as e:
        print(f"ERROR: Failed to check database schema")
        print(f"Error: {e}")
        return False


if __name__ == "__main__":
    check_sla_schema()
