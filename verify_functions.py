"""
Quick code verification script to ensure all critical functions are properly defined
"""

import re
import os

def check_function_exists(file_path, function_name):
    """Check if a function exists in a JavaScript file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Look for function definitions
        patterns = [
            f'function {function_name}\\s*\\(',  # function name()
            f'{function_name}\\s*=\\s*function',  # name = function
            f'{function_name}\\s*:\\s*function',  # name: function (object method)
            f'async function {function_name}\\s*\\(',  # async function name()
        ]
        
        for pattern in patterns:
            if re.search(pattern, content):
                return True
        return False
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return False

def verify_fixes():
    """Verify that all critical functions are properly implemented"""
    base_path = "c:\\Users\\prana\\Downloads\\chatbot_cloud\\static\\js"
    
    # Functions to check in chat.js
    chat_functions = [
        'selectCategory',
        'initializePasteHandler', 
        'handlePaste',
        'handlePastedImage',
        'displayInlinePastedImage'
    ]
    
    # Functions to check in admin.js
    admin_functions = [
        'viewTicket',
        'openImageModal',
        'formatFileSize'
    ]
    
    print("🔍 Verifying Critical Functions")
    print("=" * 40)
    
    # Check chat.js functions
    chat_file = os.path.join(base_path, "chat.js")
    print(f"\n📁 Checking {chat_file}")
    
    for func in chat_functions:
        exists = check_function_exists(chat_file, func)
        status = "✅" if exists else "❌"
        print(f"  {status} {func}")
    
    # Check admin.js functions
    admin_file = os.path.join(base_path, "admin.js")
    print(f"\n📁 Checking {admin_file}")
    
    for func in admin_functions:
        exists = check_function_exists(admin_file, func)
        status = "✅" if exists else "❌"
        print(f"  {status} {func}")
    
    print("\n" + "=" * 40)
    print("Verification complete!")

if __name__ == "__main__":
    verify_fixes()
