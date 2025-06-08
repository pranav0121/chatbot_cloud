#!/usr/bin/env python
"""
System Verification Script
Checks that all components of the Customer Support System are properly configured
"""

import os
import sys
from pathlib import Path

def check_files():
    """Check that all required files exist"""
    print("🔍 Checking File Structure...")
    
    required_files = {
        'Core Files': [
            'app.py',
            'config.py',
            'requirements.txt',
            '.env'
        ],
        'Templates': [
            'templates/index.html',
            'templates/admin.html'
        ],
        'Stylesheets': [
            'static/css/style.css',
            'static/css/admin.css'
        ],
        'JavaScript': [
            'static/js/chat.js',
            'static/js/admin.js'
        ],
        'Database Scripts': [
            'database/chatbot.sql',
            'database/setup_user.sql'
        ]
    }
    
    all_good = True
    
    for category, files in required_files.items():
        print(f"\n📁 {category}:")
        for file_path in files:
            if os.path.exists(file_path):
                size = os.path.getsize(file_path)
                print(f"  ✅ {file_path} ({size:,} bytes)")
            else:
                print(f"  ❌ {file_path} - MISSING")
                all_good = False
    
    return all_good

def check_dependencies():
    """Check Python dependencies"""
    print("\n🐍 Checking Python Dependencies...")
    
    required_packages = [
        'flask',
        'flask_sqlalchemy', 
        'python-dotenv',
        'pyodbc',
        'sqlalchemy'
    ]
    
    all_good = True
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"  ✅ {package}")
        except ImportError:
            print(f"  ❌ {package} - NOT INSTALLED")
            all_good = False
    
    return all_good

def check_config():
    """Check configuration"""
    print("\n⚙️ Checking Configuration...")
    
    # Check .env file
    env_vars = [
        'DB_SERVER',
        'DB_DATABASE', 
        'DB_USERNAME',
        'DB_PASSWORD'
    ]
    
    all_good = True
    
    if os.path.exists('.env'):
        print("  ✅ .env file exists")
        
        with open('.env', 'r') as f:
            env_content = f.read()
            
        for var in env_vars:
            if var in env_content:
                print(f"  ✅ {var} configured")
            else:
                print(f"  ❌ {var} - NOT CONFIGURED")
                all_good = False
    else:
        print("  ❌ .env file missing")
        all_good = False
    
    return all_good

def check_app_import():
    """Test importing the Flask app"""
    print("\n🚀 Testing Application Import...")
    
    try:
        sys.path.insert(0, os.getcwd())
        from app import app, db
        print("  ✅ Flask app imports successfully")
        
        with app.app_context():
            print("  ✅ App context works")
            
            # Check routes
            routes = [rule.endpoint for rule in app.url_map.iter_rules()]
            key_routes = ['index', 'admin_dashboard', 'get_categories', 'create_ticket']
            
            for route in key_routes:
                if route in routes:
                    print(f"  ✅ Route '{route}' registered")
                else:
                    print(f"  ❌ Route '{route}' missing")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Import failed: {e}")
        return False

def main():
    """Run all verification checks"""
    print("=" * 60)
    print("🎯 Customer Support System - Verification Check")
    print("=" * 60)
    
    checks = [
        ("File Structure", check_files),
        ("Dependencies", check_dependencies),
        ("Configuration", check_config),
        ("Application", check_app_import)
    ]
    
    results = []
    
    for check_name, check_func in checks:
        try:
            result = check_func()
            results.append(result)
        except Exception as e:
            print(f"\n❌ Error during {check_name} check: {e}")
            results.append(False)
    
    print("\n" + "=" * 60)
    print("📊 VERIFICATION SUMMARY")
    print("=" * 60)
    
    for i, (check_name, _) in enumerate(checks):
        status = "✅ PASSED" if results[i] else "❌ FAILED"
        print(f"{check_name:.<20} {status}")
    
    all_passed = all(results)
    
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 ALL CHECKS PASSED!")
        print("Your Customer Support System is ready to run!")
        print("\nTo start the application:")
        print("  • Run: python app.py")
        print("  • Or use: start.bat / start.ps1")
        print("\nAccess URLs:")
        print("  • User Interface: http://localhost:5000")
        print("  • Admin Dashboard: http://localhost:5000/admin")
    else:
        print("⚠️  SOME CHECKS FAILED")
        print("Please review the errors above and fix them before running the application.")
        print("\nCommon fixes:")
        print("  • Install dependencies: pip install -r requirements.txt")
        print("  • Check .env configuration")
        print("  • Ensure all files are present")
    
    print("=" * 60)
    
    return all_passed

if __name__ == "__main__":
    success = main()
    input("\nPress Enter to exit...")
    sys.exit(0 if success else 1)
