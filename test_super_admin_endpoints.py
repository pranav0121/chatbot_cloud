#!/usr/bin/env python3
"""
Test Super Admin API endpoints to verify dashboard functionality
"""

import requests
import json
import time
import sys

BASE_URL = "http://127.0.0.1:5000"

def wait_for_server(max_wait=10):
    """Wait for the server to be ready"""
    print("Waiting for server to be ready...")
    for i in range(max_wait):
        try:
            response = requests.get(f"{BASE_URL}/", timeout=2)
            if response.status_code in [200, 404, 302, 500]:  # Server is responding
                print("Server is ready!")
                return True
        except requests.exceptions.RequestException:
            time.sleep(1)
    print("Server did not start within the expected time")
    return False

def test_super_admin_endpoints():
    """Test super admin API endpoints"""
    
    if not wait_for_server():
        print("Cannot proceed without server running")
        return
    
    print("\n=== TESTING SUPER ADMIN API ENDPOINTS ===\n")
    
    # Session for maintaining cookies
    session = requests.Session()
    
    # Test endpoints that don't require authentication first
    endpoints_to_test = [
        ("/super-admin/api/dashboard/metrics", "Dashboard Metrics"),
        ("/super-admin/api/escalation/dashboard", "Escalation Dashboard"),
        ("/super-admin/api/critical-alerts", "Critical Alerts"),
        ("/super-admin/api/partners", "Partners List"),
        ("/super-admin/api/audit-logs", "Audit Logs"),
        ("/super-admin/api/workflow-logs", "Workflow Logs"),
    ]
    
    for endpoint, description in endpoints_to_test:
        print(f"Testing {description}: {endpoint}")
        try:
            response = session.get(f"{BASE_URL}{endpoint}", timeout=10)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 401:
                print(f"   Result: Authentication required (expected)")
            elif response.status_code == 200:
                try:
                    data = response.json()
                    print(f"   Result: Success - JSON response received")
                    # Print a summary of the response
                    if isinstance(data, dict):
                        if 'success' in data:
                            print(f"   Success: {data.get('success')}")
                        if 'error' in data:
                            print(f"   Error: {data.get('error')}")
                        print(f"   Keys: {list(data.keys())}")
                    else:
                        print(f"   Response type: {type(data)}")
                except json.JSONDecodeError:
                    print(f"   Result: Success - Non-JSON response")
                    print(f"   Content preview: {response.text[:100]}...")
            else:
                print(f"   Result: HTTP {response.status_code}")
                print(f"   Content preview: {response.text[:200]}...")
        except requests.exceptions.RequestException as e:
            print(f"   Exception: {e}")
        print()
    
    # Test main pages (these might redirect to login)
    pages_to_test = [
        ("/super-admin/", "Super Admin Dashboard"),
        ("/super-admin/dashboard", "Dashboard Page"),
        ("/super-admin/escalation", "Escalation Page"),
        ("/super-admin/partners", "Partners Page"),
        ("/super-admin/logs", "Logs Page"),
        ("/super-admin/audit", "Audit Page"),
    ]
    
    print("\n=== TESTING SUPER ADMIN PAGES ===\n")
    
    for endpoint, description in pages_to_test:
        print(f"Testing {description}: {endpoint}")
        try:
            response = session.get(f"{BASE_URL}{endpoint}", timeout=10)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 302:
                print(f"   Result: Redirect (likely to login)")
                if 'Location' in response.headers:
                    print(f"   Redirect to: {response.headers['Location']}")
            elif response.status_code == 200:
                print(f"   Result: Success - Page loaded")
                if 'text/html' in response.headers.get('content-type', ''):
                    print(f"   Content: HTML page")
                else:
                    print(f"   Content: {response.headers.get('content-type', 'Unknown')}")
            else:
                print(f"   Result: HTTP {response.status_code}")
                print(f"   Content preview: {response.text[:200]}...")
        except requests.exceptions.RequestException as e:
            print(f"   Exception: {e}")
        print()

def test_authentication_flow():
    """Test the authentication flow"""
    print("\n=== TESTING AUTHENTICATION FLOW ===\n")
    
    session = requests.Session()
    
    # Try to access login page
    print("Testing admin login page: /auth/admin/login")
    try:
        response = session.get(f"{BASE_URL}/auth/admin/login", timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   Result: Login page accessible")
        else:
            print(f"   Content preview: {response.text[:200]}...")
    except requests.exceptions.RequestException as e:
        print(f"   Exception: {e}")
    print()

if __name__ == "__main__":
    test_super_admin_endpoints()
    test_authentication_flow()
    print("\n=== TEST COMPLETE ===")
