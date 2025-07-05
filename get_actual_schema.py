#!/usr/bin/env python3
"""
Get actual database schema
"""

from sqlalchemy import create_engine, text
from config import Config

config = Config()
engine = create_engine(config.SQLALCHEMY_DATABASE_URI)

with engine.connect() as conn:
    result = conn.execute(text(
        "SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'Users' ORDER BY COLUMN_NAME"))
    actual_columns = [row[0] for row in result.fetchall()]
    print('ACTUAL Users table columns:')
    for col in actual_columns:
        print(f'  {col}')
