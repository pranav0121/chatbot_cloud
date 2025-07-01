#!/usr/bin/env python3
"""
Simple App Syntax Checker
Check if the main syntax error has been resolved
"""

import ast
import sys

def check_app_syntax():
    try:
        with open('app.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Try to parse the AST
        ast.parse(content)
        print("✅ app.py syntax is valid!")
        return True
        
    except SyntaxError as e:
        print(f"❌ Syntax error in app.py:")
        print(f"   Line {e.lineno}: {e.text}")
        print(f"   Error: {e.msg}")
        return False
    except UnicodeDecodeError as e:
        print(f"❌ Unicode encoding error in app.py: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    if check_app_syntax():
        print("Ready to proceed with device tracking integration!")
    else:
        print("Please fix syntax errors before proceeding.")
        sys.exit(1)
