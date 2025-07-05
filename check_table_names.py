#!/usr/bin/env python3
"""
Check the actual table names in the database to fix foreign key references.
"""
import os
import pyodbc
from dotenv import load_dotenv


def check_table_names():
    """Check actual table names in the database."""
    load_dotenv()

    server = os.getenv('DB_SERVER', 'PRANAV\\SQLEXPRESS')
    database = os.getenv('DB_DATABASE', 'SupportChatbot')
    use_windows_auth = os.getenv(
        'DB_USE_WINDOWS_AUTH', 'True').lower() == 'true'
    username = os.getenv('DB_USERNAME', '')
    password = os.getenv('DB_PASSWORD', '')

    driver = "ODBC Driver 17 for SQL Server"

    try:
        if use_windows_auth:
            conn_str = f"DRIVER={{{driver}}};SERVER={server};DATABASE={database};Trusted_Connection=yes;"
        else:
            conn_str = f"DRIVER={{{driver}}};SERVER={server};DATABASE={database};UID={username};PWD={password};"

        with pyodbc.connect(conn_str) as conn:
            cursor = conn.cursor()

            print("=== Checking Table Names for Foreign Key References ===\n")

            # Check for partner-related tables
            cursor.execute("""
                SELECT TABLE_NAME 
                FROM INFORMATION_SCHEMA.TABLES 
                WHERE TABLE_NAME LIKE '%partner%' OR TABLE_NAME LIKE '%Partner%'
                ORDER BY TABLE_NAME
            """)
            partner_tables = cursor.fetchall()
            print("Partner-related tables:")
            for table in partner_tables:
                print(f"  - {table[0]}")

            print()

            # Check for all tables that might be referenced by foreign keys
            cursor.execute("""
                SELECT TABLE_NAME 
                FROM INFORMATION_SCHEMA.TABLES 
                WHERE TABLE_TYPE = 'BASE TABLE'
                ORDER BY TABLE_NAME
            """)
            all_tables = cursor.fetchall()
            print("All tables in database:")
            for table in all_tables:
                print(f"  - {table[0]}")

            print()

            # Check the columns in the partners table if it exists
            for partner_table_name in ['partners', 'Partners']:
                try:
                    cursor.execute(f"""
                        SELECT COLUMN_NAME, DATA_TYPE 
                        FROM INFORMATION_SCHEMA.COLUMNS 
                        WHERE TABLE_NAME = '{partner_table_name}'
                        ORDER BY ORDINAL_POSITION
                    """)
                    columns = cursor.fetchall()
                    if columns:
                        print(f"Columns in '{partner_table_name}' table:")
                        for col in columns:
                            print(f"  - {col[0]} ({col[1]})")
                        print()
                        break
                except Exception as e:
                    continue

            # Check foreign key constraints in sla_logs
            cursor.execute("""
                SELECT 
                    fk.CONSTRAINT_NAME,
                    fk.TABLE_NAME,
                    fk.COLUMN_NAME,
                    pk.TABLE_NAME AS REFERENCED_TABLE,
                    pk.COLUMN_NAME AS REFERENCED_COLUMN
                FROM INFORMATION_SCHEMA.REFERENTIAL_CONSTRAINTS rc
                JOIN INFORMATION_SCHEMA.KEY_COLUMN_USAGE fk 
                    ON rc.CONSTRAINT_NAME = fk.CONSTRAINT_NAME
                JOIN INFORMATION_SCHEMA.KEY_COLUMN_USAGE pk 
                    ON rc.UNIQUE_CONSTRAINT_NAME = pk.CONSTRAINT_NAME
                WHERE fk.TABLE_NAME = 'sla_logs'
            """)
            foreign_keys = cursor.fetchall()
            print("Foreign keys in sla_logs table:")
            if foreign_keys:
                for fk in foreign_keys:
                    print(f"  - {fk[1]}.{fk[2]} -> {fk[3]}.{fk[4]} ({fk[0]})")
            else:
                print("  No foreign keys found")

    except Exception as e:
        print(f"ERROR: Failed to check database schema")
        print(f"Error: {e}")
        return False


if __name__ == "__main__":
    check_table_names()
