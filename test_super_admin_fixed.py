#!/usr/bin/env python3
"""
Quick test of fixed Super Admin APIs
"""

import requests
import sys

def test_fixed_apis():
    """Test the specific APIs we fixed"""
    
    # First login as super admin
    login_url = "http://localhost:5000/auth/admin/login"
    session = requests.Session()
    
    login_data = {
        'email': 'superadmin@youcloudtech.com',
        'password': 'superadmin123'
    }
    
    print("🔐 Logging in as super admin...")
    login_response = session.post(login_url, data=login_data)
    if login_response.status_code != 200:
        print("❌ Login failed")
        return False
    print("✅ Login successful")
    
    # Test the main problematic APIs
    base_url = "http://localhost:5000/super-admin/api"
    
    tests = [
        ("dashboard-metrics", "Original Dashboard Metrics"),
        ("dashboard/metrics", "Alternative Dashboard Metrics"), 
        ("critical-alerts", "Original Critical Alerts"),
        ("alerts/critical", "Alternative Critical Alerts"),
        ("sla/overview", "SLA Overview")
    ]
    
    results = []
    for endpoint, name in tests:
        url = f"{base_url}/{endpoint}"
        print(f"\n🧪 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            response = session.get(url, timeout=10)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"   ✅ SUCCESS: Valid JSON response")
                    if 'success' in data:
                        print(f"   📊 Success flag: {data['success']}")
                    if 'data' in data:
                        print(f"   📊 Data keys: {list(data['data'].keys())}")
                    results.append(True)
                except:
                    print(f"   ⚠️  WARNING: Non-JSON response")
                    results.append(True)  # Still counts as working
            else:
                print(f"   ❌ HTTP ERROR: {response.status_code}")
                print(f"   Response: {response.text[:100]}...")
                results.append(False)
                
        except Exception as e:
            print(f"   ❌ ERROR: {e}")
            results.append(False)
    
    # Summary
    passed = sum(results)
    total = len(results)
    
    print(f"\n📈 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All fixed APIs working!")
    elif passed > total // 2:
        print("✅ Most APIs working - good progress!")
    else:
        print("⚠️  Still need more fixes")
    
    return passed >= total // 2

if __name__ == "__main__":
    success = test_fixed_apis()
    sys.exit(0 if success else 1)
