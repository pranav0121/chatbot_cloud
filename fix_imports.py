#!/usr/bin/env python3
"""
Fix App.py Imports
Remove problematic device_tracker imports
"""

import re

def fix_app_imports():
    """Remove problematic device_tracker imports from app.py"""
    try:
        with open('app.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Remove the problematic import lines
        content = re.sub(r'from device_tracker import DeviceTracker\n', '', content)
        content = re.sub(r'from device_tracker import device_tracker\n', '', content)
        
        with open('app.py', 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ Fixed app.py imports")
        return True
        
    except Exception as e:
        print(f"❌ Error fixing imports: {e}")
        return False

if __name__ == "__main__":
    fix_app_imports()
