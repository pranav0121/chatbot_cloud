#!/usr/bin/env python3
"""
Script to fix all imports from 'models' to 'database' in all Python files.
"""
import os
import re
import glob


def fix_imports_in_file(file_path):
    """Fix imports from models to database in a single file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Track if we made any changes
        original_content = content

        # Replace import statements
        patterns = [
            (r'from database import', 'from database import'),
            (r'import database', 'import database'),
        ]

        for pattern, replacement in patterns:
            content = re.sub(pattern, replacement, content)

        # Only write if changes were made
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ Fixed imports in: {file_path}")
            return True
        else:
            return False

    except Exception as e:
        print(f"❌ Error fixing {file_path}: {e}")
        return False


def fix_all_imports():
    """Fix imports in all Python files in the project."""
    print("🔄 Fixing all model imports in the project...\n")

    # Get all Python files
    python_files = glob.glob("*.py") + glob.glob("**/*.py", recursive=True)

    # Filter out virtual environment files
    python_files = [f for f in python_files if not f.startswith('venv')]

    fixed_count = 0
    total_count = 0

    for file_path in python_files:
        if os.path.exists(file_path):
            total_count += 1
            if fix_imports_in_file(file_path):
                fixed_count += 1

    print(f"\n📊 Summary:")
    print(f"   Files processed: {total_count}")
    print(f"   Files fixed: {fixed_count}")
    print(f"   Files unchanged: {total_count - fixed_count}")

    if fixed_count > 0:
        print(f"\n✅ All imports have been fixed!")
    else:
        print(f"\n✨ No files needed fixing!")


if __name__ == "__main__":
    fix_all_imports()
