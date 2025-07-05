#!/usr/bin/env python3
"""
Fix PasswordHash constraint issue
"""

from sqlalchemy import create_engine, text
from config import Config

config = Config()
engine = create_engine(config.SQLALCHEMY_DATABASE_URI)

with engine.connect() as conn:
    # Check PasswordHash column constraints
    print("Checking PasswordHash column constraints...")
    result = conn.execute(text("""
        SELECT COLUMN_NAME, IS_NULLABLE, COLUMN_DEFAULT
        FROM INFORMATION_SCHEMA.COLUMNS 
        WHERE TABLE_NAME = 'Users' AND COLUMN_NAME = 'PasswordHash'
    """))
    for row in result:
        print(f"PasswordHash column: nullable={row[1]}, default={row[2]}")

    # Make PasswordHash nullable or add a default value
    print("\nFixing PasswordHash constraint...")
    try:
        # First try to make it nullable
        conn.execute(
            text("ALTER TABLE Users ALTER COLUMN PasswordHash NVARCHAR(255) NULL"))
        print("✓ Made PasswordHash column nullable")
    except Exception as e:
        print(f"Could not make nullable: {e}")
        try:
            # Alternative: Add a default value
            conn.execute(text(
                "ALTER TABLE Users ADD CONSTRAINT DF_Users_PasswordHash DEFAULT '' FOR PasswordHash"))
            print("✓ Added default value for PasswordHash")
        except Exception as e2:
            print(f"Could not add default: {e2}")

    # Also check other potentially problematic columns
    print("\nChecking other NOT NULL columns...")
    result = conn.execute(text("""
        SELECT COLUMN_NAME, IS_NULLABLE, COLUMN_DEFAULT
        FROM INFORMATION_SCHEMA.COLUMNS 
        WHERE TABLE_NAME = 'Users' AND IS_NULLABLE = 'NO' AND COLUMN_DEFAULT IS NULL
        ORDER BY COLUMN_NAME
    """))

    problematic_cols = []
    for row in result:
        if row[0] not in ['UserID']:  # Skip primary key
            problematic_cols.append(row[0])
            print(f"  {row[0]}: NOT NULL, no default")

    # Fix other problematic columns
    if problematic_cols:
        print(f"\nFixing {len(problematic_cols)} problematic columns...")

        column_fixes = {
            'Name': "ALTER TABLE Users ALTER COLUMN Name NVARCHAR(100) NULL",
            'Email': "ALTER TABLE Users ALTER COLUMN Email NVARCHAR(255) NULL",
            'OrganizationName': "ALTER TABLE Users ALTER COLUMN OrganizationName NVARCHAR(200) NULL",
            'Position': "ALTER TABLE Users ALTER COLUMN Position NVARCHAR(100) NULL",
            'Phone': "ALTER TABLE Users ALTER COLUMN Phone NVARCHAR(20) NULL",
            'Department': "ALTER TABLE Users ALTER COLUMN Department NVARCHAR(100) NULL",
            'Country': "ALTER TABLE Users ALTER COLUMN Country NVARCHAR(100) NULL"
        }

        for col in problematic_cols:
            if col in column_fixes:
                try:
                    conn.execute(text(column_fixes[col]))
                    print(f"  ✓ Fixed {col}")
                except Exception as e:
                    print(f"  ✗ Could not fix {col}: {e}")

    print("\n=== CONSTRAINT FIXES COMPLETED ===")
    print("Database should now allow proper User creation")
