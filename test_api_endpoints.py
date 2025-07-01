#!/usr/bin/env python3
"""
Test API endpoints directly to diagnose issues
"""

import requests
import json
import time

BASE_URL = "http://127.0.0.1:5000"

def test_api_endpoints():
    """Test all the API endpoints that the admin panel uses"""
    
    print("=== TESTING API ENDPOINTS ===\n")
    
    # Test 1: Dashboard Stats
    print("1. Testing /api/admin/dashboard-stats")
    try:
        response = requests.get(f"{BASE_URL}/api/admin/dashboard-stats", timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Data: {json.dumps(data, indent=2)}")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"   Exception: {e}")
    
    print()
    
    # Test 2: Admin Tickets
    print("2. Testing /api/admin/tickets")
    try:
        response = requests.get(f"{BASE_URL}/api/admin/tickets", timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Found {len(data)} tickets")
            if data:
                print(f"   Sample ticket: {json.dumps(data[0], indent=2)}")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"   Exception: {e}")
    
    print()
    
    # Test 3: Recent Activity
    print("3. Testing /api/admin/recent-activity")
    try:
        response = requests.get(f"{BASE_URL}/api/admin/recent-activity", timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Data: {json.dumps(data, indent=2)}")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"   Exception: {e}")
    
    print()
    
    # Test 4: Categories
    print("4. Testing /api/categories")
    try:
        response = requests.get(f"{BASE_URL}/api/categories", timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Found {len(data)} categories")
            for cat in data:
                print(f"     - {cat['name']}")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"   Exception: {e}")
    
    print()
    
    # Test 5: Main admin page
    print("5. Testing /admin page")
    try:
        response = requests.get(f"{BASE_URL}/admin", timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   Admin page accessible")
        else:
            print(f"   Error: {response.status_code}")
    except Exception as e:
        print(f"   Exception: {e}")

if __name__ == '__main__':
    print("Waiting for server to be ready...")
    time.sleep(2)
    test_api_endpoints()
