#!/usr/bin/env python3
"""
Check actual Tickets table columns in the database.
"""
import os
import pyodbc
from dotenv import load_dotenv


def check_tickets_columns():
    """Check actual columns in the Tickets table."""
    load_dotenv()

    server = os.getenv('DB_SERVER', 'PRANAV\\SQLEXPRESS')
    database = os.getenv('DB_DATABASE', 'SupportChatbot')

    driver = "ODBC Driver 17 for SQL Server"
    conn_str = f"DRIVER={{{driver}}};SERVER={server};DATABASE={database};Trusted_Connection=yes;"

    try:
        with pyodbc.connect(conn_str) as conn:
            cursor = conn.cursor()

            print("=== Actual Tickets Table Schema ===\n")

            # Get all columns with their data types
            cursor.execute("""
                SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE, COLUMN_DEFAULT
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_NAME = 'Tickets'
                ORDER BY ORDINAL_POSITION
            """)

            columns = cursor.fetchall()
            print("Actual Tickets table columns:")
            for col in columns:
                nullable = "nullable" if col[2] == "YES" else "not null"
                default = f"default: {col[3]}" if col[3] else "no default"
                print(f"  - {col[0]} ({col[1]}, {nullable}, {default})")

            print(f"\nTotal columns: {len(columns)}")

            # Get a sample record to see actual data
            cursor.execute("SELECT TOP 1 * FROM Tickets")
            sample = cursor.fetchone()

            if sample:
                print("\nSample record values:")
                for i, col in enumerate(columns):
                    value = sample[i] if i < len(sample) else "N/A"
                    print(f"  {col[0]}: {value}")

            return [col[0] for col in columns]

    except Exception as e:
        print(f"ERROR: Failed to check database schema")
        print(f"Error: {e}")
        return []


if __name__ == "__main__":
    check_tickets_columns()
