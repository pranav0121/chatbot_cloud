#!/usr/bin/env python3
"""
Simple test to check if Flask server is responding
"""

import requests
import json

def test_server():
    try:
        # Test basic connectivity
        print("Testing basic connectivity...")
        response = requests.get("http://127.0.0.1:5001/", timeout=5)
        print(f"Main page status: {response.status_code}")
        
        # Test admin page
        print("Testing admin page...")
        response = requests.get("http://127.0.0.1:5001/admin", timeout=5)
        print(f"Admin page status: {response.status_code}")
        
        # Test dashboard stats API
        print("Testing dashboard stats API...")
        response = requests.get("http://127.0.0.1:5001/api/admin/dashboard-stats", timeout=5)
        print(f"Dashboard API status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Dashboard data: {data}")
        else:
            print(f"Dashboard API error: {response.text}")
            
        # Test tickets API
        print("Testing tickets API...")
        response = requests.get("http://127.0.0.1:5001/api/admin/tickets", timeout=5)
        print(f"Tickets API status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Found {len(data)} tickets")
            if data:
                print(f"First ticket: {data[0]}")
        else:
            print(f"Tickets API error: {response.text}")
            
    except Exception as e:
        print(f"Error testing server: {e}")

if __name__ == '__main__':
    test_server()
