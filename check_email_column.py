#!/usr/bin/env python3
"""
Check email column status
"""

from sqlalchemy import create_engine, text
from config import Config

config = Config()
engine = create_engine(config.SQLALCHEMY_DATABASE_URI)

with engine.connect() as conn:
    # Check if email column exists
    result = conn.execute(text(
        "SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'Users' AND COLUMN_NAME = 'email'"))
    email_cols = result.fetchall()
    print(f"Email column check: {email_cols}")

    # Check Email column (capital E)
    result = conn.execute(text(
        "SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'Users' AND COLUMN_NAME = 'Email'"))
    Email_cols = result.fetchall()
    print(f"Email (capital) column check: {Email_cols}")

    # Add email column if missing
    if not email_cols:
        print("Adding email column...")
        try:
            conn.execute(text("ALTER TABLE Users ADD email NVARCHAR(120)"))
            print("Email column added successfully")

            # Populate it from Email column
            conn.execute(
                text("UPDATE Users SET email = Email WHERE email IS NULL"))
            print("Email data populated from Email column")
        except Exception as e:
            print(f"Error: {e}")
    else:
        print("email column already exists")

    # Show sample data
    try:
        result = conn.execute(
            text("SELECT TOP 3 UserID, Email, email, username FROM Users"))
        rows = result.fetchall()
        print("\nSample user data:")
        for row in rows:
            print(
                f"  UserID: {row[0]}, Email: {row[1]}, email: {row[2]}, username: {row[3]}")
    except Exception as e:
        print(f"Error getting sample data: {e}")
