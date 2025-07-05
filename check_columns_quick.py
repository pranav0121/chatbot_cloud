#!/usr/bin/env python3
"""Check actual Tickets table column names."""
import os
import pyodbc
from dotenv import load_dotenv

load_dotenv()

server = os.getenv('DB_SERVER', 'PRANAV\\SQLEXPRESS')
database = os.getenv('DB_DATABASE', 'SupportChatbot')

conn_str = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};Trusted_Connection=yes;"

with pyodbc.connect(conn_str) as conn:
    cursor = conn.cursor()
    cursor.execute(
        "SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'Tickets' ORDER BY ORDINAL_POSITION")
    columns = [row[0] for row in cursor.fetchall()]
    print('Actual Tickets table columns:')
    for col in columns:
        print(f'  - {col}')
