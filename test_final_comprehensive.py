#!/usr/bin/env python3
"""
Final comprehensive test after server restart
"""

import requests
import json
import time

BASE_URL = "http://127.0.0.1:5000"

def test_all_fixed_endpoints():
    session = requests.Session()
    
    print("=== COMPREHENSIVE SUPER ADMIN TEST ===\n")
    
    # Login
    print("1. Logging in...")
    login_data = {
        'email': 'admin@youcloudtech.com', 
        'password': 'admin123'
    }
    
    login_response = session.post(f"{BASE_URL}/auth/admin/login", data=login_data, allow_redirects=False)
    print(f"   Login status: {login_response.status_code}")
    
    if login_response.status_code != 302:
        print("   ❌ Login failed!")
        return
    
    print("   ✅ Login successful!")
    
    # Test endpoints
    endpoints = [
        ("/super-admin/api/dashboard/metrics", "Dashboard Metrics"),
        ("/super-admin/api/escalation/dashboard", "Escalation Dashboard"),
        ("/super-admin/api/critical-alerts", "Critical Alerts"),
        ("/super-admin/api/debug/database", "Database Debug"),
    ]
    
    for endpoint, name in endpoints:
        print(f"\n2. Testing {name}: {endpoint}")
        try:
            response = session.get(f"{BASE_URL}{endpoint}")
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Success!")
                
                # Show key metrics
                if 'activeTickets' in data:
                    print(f"   📊 Active Tickets: {data.get('activeTickets', 'N/A')}")
                    print(f"   📊 Total Tickets: {data.get('totalTickets', 'N/A')}")
                    print(f"   📊 SLA Breaches: {data.get('slaBreaches', 'N/A')}")
                    print(f"   📊 Bot Interactions: {data.get('botInteractions', 'N/A')}")
                elif 'within_sla' in data:
                    print(f"   📊 Within SLA: {data.get('within_sla', 'N/A')}")
                    print(f"   📊 SLA Warning: {data.get('sla_warning', 'N/A')}")
                    print(f"   📊 SLA Breached: {data.get('sla_breached', 'N/A')}")
                elif 'alerts' in data:
                    alerts = data.get('alerts', [])
                    print(f"   📊 Alerts count: {len(alerts)}")
                elif 'results' in data:
                    results = data['results']
                    print(f"   📊 Total Tickets: {results.get('total_tickets', 'N/A')}")
                    print(f"   📊 Active Tickets: {results.get('active_tickets', 'N/A')}")
                    print(f"   📊 Status Distribution: {results.get('status_distribution', {})}")
            else:
                print(f"   ❌ Failed with status {response.status_code}")
                if response.status_code == 404:
                    print("   ⚠️  Endpoint not found - server restart needed")
                else:
                    print(f"   Error: {response.text[:100]}...")
        except Exception as e:
            print(f"   ❌ Exception: {e}")
    
    # Test pages
    print(f"\n3. Testing Dashboard Pages...")
    pages = [
        ("/super-admin/dashboard", "Main Dashboard"),
        ("/super-admin/escalation", "Escalation Dashboard"),
        ("/super-admin/logs", "Logs Page"),
        ("/super-admin/audit", "Audit Page"),
    ]
    
    for page, name in pages:
        try:
            response = session.get(f"{BASE_URL}{page}")
            if response.status_code == 200:
                print(f"   ✅ {name}: OK")
            else:
                print(f"   ❌ {name}: Status {response.status_code}")
        except Exception as e:
            print(f"   ❌ {name}: Exception {e}")
    
    print(f"\n=== TEST COMPLETE ===")

if __name__ == "__main__":
    test_all_fixed_endpoints()
