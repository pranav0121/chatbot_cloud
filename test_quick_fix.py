#!/usr/bin/env python3
"""
Quick test of fixed Super Admin APIs
"""
import requests
import time

def test_fixed_apis():
    print("🔧 Testing Fixed Super Admin APIs")
    print("=" * 50)
    
    # Wait for Flask to fully start
    print("⏳ Waiting for Flask to start...")
    time.sleep(3)
    
    # Login first
    print("🔐 Logging in...")
    session = requests.Session()
    
    login_data = {
        'email': 'superadmin@youcloudtech.com',
        'password': 'superadmin123'
    }
    
    login_response = session.post('http://localhost:5000/auth/admin/login', data=login_data)
    if login_response.status_code == 200:
        print("✅ Login successful")
    else:
        print("❌ Login failed")
        return
    
    # Test APIs
    tests = [
        ('http://localhost:5000/super-admin/api/dashboard-metrics', 'Dashboard Metrics (Original)'),
        ('http://localhost:5000/super-admin/api/dashboard/metrics', 'Dashboard Metrics (Alt)'),
        ('http://localhost:5000/super-admin/api/critical-alerts', 'Critical Alerts (Original)'),
        ('http://localhost:5000/super-admin/api/alerts/critical', 'Critical Alerts (Alt)'),
        ('http://localhost:5000/super-admin/api/sla/overview', 'SLA Overview'),
    ]
    
    for url, name in tests:
        try:
            response = session.get(url, timeout=10)
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"✅ {name}: Working (Status: {response.status_code})")
                except:
                    print(f"⚠️  {name}: Returns data but not JSON (Status: {response.status_code})")
            else:
                print(f"❌ {name}: HTTP {response.status_code}")
        except Exception as e:
            print(f"❌ {name}: Error - {str(e)[:50]}...")
    
    print("\n🎉 Test completed!")

if __name__ == "__main__":
    test_fixed_apis()
