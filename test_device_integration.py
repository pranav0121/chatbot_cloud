#!/usr/bin/env python3
"""
Device Tracking Integration Tester
Quick test to verify all components are working
"""

import os
import json
from datetime import datetime

def test_device_tracker_core():
    """Test core device tracking functionality"""
    print("🧪 Testing device_tracker_core.py...")
    try:
        from device_tracker_core import DeviceInfo, DeviceAnalytics
        
        # Test with sample user agent
        sample_ua = "Mozilla/5.0 (iPhone; CPU iPhone OS 14_7_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Mobile/15E148 Safari/604.1"
        device_info = DeviceInfo(sample_ua, "192.168.1.100")
        info = device_info.get_complete_info()
        
        print(f"   ✅ Device Type: {info['device_type']}")
        print(f"   ✅ Browser: {info['browser']['family']}")
        print(f"   ✅ OS: {info['os']['family']}")
        return True
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_client_side_files():
    """Test if client-side files exist and are accessible"""
    print("\n🧪 Testing client-side files...")
    
    files_to_check = [
        'static/js/device-tracker.js',
        'static/js/chat.js',
        'static/device_tracker_test.html'
    ]
    
    all_exist = True
    for file_path in files_to_check:
        if os.path.exists(file_path):
            size = os.path.getsize(file_path)
            print(f"   ✅ {file_path} ({size:,} bytes)")
        else:
            print(f"   ❌ {file_path} - Missing")
            all_exist = False
    
    return all_exist

def test_database_migration():
    """Test if device tracking tables exist"""
    print("\n🧪 Testing database migration...")
    try:
        import sqlite3
        
        if not os.path.exists("chatbot.db"):
            print("   ⚠️  chatbot.db not found - database not initialized")
            return False
        
        conn = sqlite3.connect("chatbot.db")
        cursor = conn.cursor()
        
        # Check device_tracking_logs table
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='device_tracking_logs'")
        if cursor.fetchone():
            print("   ✅ device_tracking_logs table exists")
            cursor.execute("PRAGMA table_info(device_tracking_logs)")
            columns = cursor.fetchall()
            print(f"      Contains {len(columns)} columns")
        else:
            print("   ❌ device_tracking_logs table missing")
            return False
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"   ❌ Database error: {e}")
        return False

def test_integration_files():
    """Test if integration files are ready"""
    print("\n🧪 Testing integration files...")
    
    integration_files = [
        'device_tracking_integration_code.py',
        'templates/device_info_admin_template.html',
        'DEVICE_TRACKING_INTEGRATION_GUIDE.md',
        'device_demo_windows.py'
    ]
    
    all_exist = True
    for file_path in integration_files:
        if os.path.exists(file_path):
            size = os.path.getsize(file_path)
            print(f"   ✅ {file_path} ({size:,} bytes)")
        else:
            print(f"   ❌ {file_path} - Missing")
            all_exist = False
    
    return all_exist

def test_app_syntax():
    """Test if app.py has valid syntax"""
    print("\n🧪 Testing app.py syntax...")
    try:
        with open('app.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        compile(content, 'app.py', 'exec')
        print("   ✅ app.py syntax is valid")
        return True
        
    except SyntaxError as e:
        print(f"   ❌ Syntax error in app.py: Line {e.lineno}: {e.msg}")
        return False
    except Exception as e:
        print(f"   ❌ Error reading app.py: {e}")
        return False

def run_integration_demo():
    """Run the integration demo"""
    print("\n🧪 Testing integration demo...")
    try:
        import subprocess
        result = subprocess.run(['python', 'device_demo_windows.py'], 
                              capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("   ✅ Integration demo ran successfully")
            return True
        else:
            print(f"   ❌ Demo failed with return code {result.returncode}")
            print(f"      Error: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"   ❌ Demo test error: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Device Tracking Integration Test Suite")
    print("=" * 50)
    
    tests = [
        ("Core Device Tracking", test_device_tracker_core),
        ("Client-side Files", test_client_side_files),
        ("Database Migration", test_database_migration),
        ("Integration Files", test_integration_files),
        ("App.py Syntax", test_app_syntax),
        ("Integration Demo", run_integration_demo),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"   ❌ Test failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n📊 Test Results Summary")
    print("-" * 30)
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("\n🎉 All tests passed! Device tracking integration is ready!")
        print("\n🔧 Final manual steps:")
        print("1. Fix circular import in app.py (remove DeviceTracker import)")
        print("2. Run create_tables.py to create Users/Tickets tables")
        print("3. Run device migration to add device fields")
        print("4. Add device tracking code to create_ticket() function")
        print("5. Add device info display to admin templates")
    else:
        print(f"\n⚠️  {len(tests) - passed} test(s) failed. Check errors above.")
    
    # Save test results
    try:
        test_results = {
            'timestamp': datetime.now().isoformat(),
            'tests_run': len(tests),
            'tests_passed': passed,
            'results': dict(results)
        }
        
        with open('device_tracking_test_results.json', 'w') as f:
            json.dump(test_results, f, indent=2)
        
        print(f"\n💾 Test results saved to device_tracking_test_results.json")
        
    except Exception as e:
        print(f"\n⚠️  Could not save test results: {e}")

if __name__ == "__main__":
    main()
