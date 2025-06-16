#!/usr/bin/env python3
"""
Test Super Admin APIs
"""

import requests
import sys

def test_api_endpoint(url, description):
    """Test an API endpoint"""
    try:
        print(f"\n🧪 Testing {description}...")
        print(f"   URL: {url}")
        
        response = requests.get(url, timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if 'success' in data and data['success']:
                print(f"   ✅ SUCCESS: API working correctly")
                return True
            elif 'error' not in data:
                print(f"   ✅ SUCCESS: API returned data")
                return True
            else:
                print(f"   ❌ ERROR: {data.get('error', 'Unknown error')}")
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
    """Test all super admin API endpoints"""
    print("=" * 60)
    print("🔧 SUPER ADMIN API TESTING")
    print("=" * 60)
    
    base_url = "http://localhost:5000/super-admin/api"
    
    endpoints = [
        (f"{base_url}/dashboard/metrics", "Dashboard Metrics"),
        (f"{base_url}/alerts/critical", "Critical Alerts"),
        (f"{base_url}/critical-alerts", "Critical Alerts (Alt)"),
        (f"{base_url}/sla/overview", "SLA Overview"),
        (f"{base_url}/audit/logs?per_page=5", "Audit Logs"),
        (f"{base_url}/escalation/dashboard", "Escalation Dashboard"),
    ]
    
    results = []
    for url, description in endpoints:
        result = test_api_endpoint(url, description)
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
    else:
        print("⚠️  Some APIs need attention")
    
    return passed == len(results)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
