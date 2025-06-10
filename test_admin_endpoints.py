#!/usr/bin/env python3
"""
Simple admin panel diagnostic
"""

import requests
import json
import sys

def test_admin_endpoints():
    base_url = "http://127.0.0.1:5001"
    
    endpoints = [
        "/api/admin/dashboard-stats",
        "/api/admin/tickets",
        "/api/admin/recent-activity"
    ]
    
    print("=== Admin Panel Diagnostic ===")
    print(f"Testing endpoints on {base_url}")
    print()
    
    for endpoint in endpoints:
        url = f"{base_url}{endpoint}"
        print(f"Testing {endpoint}...")
        
        try:
            response = requests.get(url, timeout=10)
            print(f"  Status: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    if isinstance(data, dict) and 'error' in data:
                        print(f"  Error: {data['error']}")
                    else:
                        print(f"  Success: {len(data) if isinstance(data, list) else 'object'} items")
                except json.JSONDecodeError:
                    print(f"  Invalid JSON response")
            else:
                print(f"  Error response: {response.text[:200]}")
        except requests.exceptions.ConnectionError:
            print(f"  Connection failed - server not running?")
        except requests.exceptions.Timeout:
            print(f"  Request timed out")
        except Exception as e:
            print(f"  Unexpected error: {e}")
        
        print()

if __name__ == "__main__":
    test_admin_endpoints()
