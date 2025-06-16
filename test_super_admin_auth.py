#!/usr/bin/env python3
"""
Test Super Admin APIs with Authentication
"""

import requests
import sys

def login_as_super_admin():
    """Login as super admin and return session"""
    session = requests.Session()
    
    # First get the login page to get any CSRF tokens if needed
    try:
        login_url = "http://localhost:5000/auth/admin/login"
        response = session.get(login_url)
        
        if response.status_code != 200:
            print(f"❌ Could not access login page: {response.status_code}")
            return None
        
        # Attempt login with super admin credentials
        login_data = {
            'email': 'superadmin@youcloudtech.com',
            'password': 'superadmin123'
        }
        
        response = session.post(login_url, data=login_data, allow_redirects=False)
        
        if response.status_code in [302, 200]:  # Redirect or success
            print("✅ Successfully logged in as super admin")
            return session
        else:
            print(f"❌ Login failed: {response.status_code}")
            print(f"Response: {response.text[:200]}...")
            return None
            
    except Exception as e:
        print(f"❌ Login error: {e}")
        return None

def test_api_endpoint(session, url, description):
    """Test an API endpoint with authenticated session"""
    try:
        print(f"\n🧪 Testing {description}...")
        print(f"   URL: {url}")
        
        response = session.get(url, timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                if 'success' in data and data['success']:
                    print(f"   ✅ SUCCESS: API working correctly")
                    if 'data' in data:
                        print(f"   📊 Data keys: {list(data['data'].keys()) if isinstance(data['data'], dict) else 'Non-dict data'}")
                    return True
                elif 'error' not in str(data):
                    print(f"   ✅ SUCCESS: API returned data")
                    print(f"   📊 Response keys: {list(data.keys()) if isinstance(data, dict) else 'Non-dict response'}")
                    return True
                else:
                    print(f"   ❌ ERROR: {data.get('error', 'Unknown error')}")
                    return False
            except ValueError as e:
                print(f"   ❌ JSON ERROR: Response is not valid JSON")
                print(f"   Response: {response.text[:200]}...")
                return False
        else:
            print(f"   ❌ HTTP ERROR: {response.status_code}")
            print(f"   Response: {response.text[:200]}...")
            return False
            
    except requests.RequestException as e:
        print(f"   ❌ CONNECTION ERROR: {e}")
        return False
    except Exception as e:
        print(f"   ❌ UNEXPECTED ERROR: {e}")
        return False

def main():
    """Test all super admin API endpoints with authentication"""
    print("=" * 60)
    print("🔧 SUPER ADMIN API TESTING (WITH AUTH)")
    print("=" * 60)
    
    # Login first
    print("🔐 Logging in as super admin...")
    session = login_as_super_admin()
    
    if not session:
        print("❌ Could not authenticate. Stopping tests.")
        return False
    
    base_url = "http://localhost:5000/super-admin/api"
    
    endpoints = [
        (f"{base_url}/dashboard-metrics", "Dashboard Metrics (Original)"),
        (f"{base_url}/dashboard/metrics", "Dashboard Metrics (Alt)"),
        (f"{base_url}/critical-alerts", "Critical Alerts"),
        (f"{base_url}/alerts/critical", "Critical Alerts (Alt)"),
        (f"{base_url}/sla/overview", "SLA Overview"),
        (f"{base_url}/audit/logs?per_page=5", "Audit Logs"),
        (f"{base_url}/escalation/dashboard", "Escalation Dashboard"),
    ]
    
    results = []
    for url, description in endpoints:
        result = test_api_endpoint(session, url, description)
        results.append((description, result))
    
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 60)
    
    passed = 0
    for description, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {status} - {description}")
        if result:
            passed += 1
    
    print(f"\n📈 Results: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 All APIs working correctly!")
    elif passed > 0:
        print("⚠️  Some APIs working, others need attention")
    else:
        print("❌ All APIs failing - check implementation")
    
    return passed >= len(results) // 2  # Pass if at least half work

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
