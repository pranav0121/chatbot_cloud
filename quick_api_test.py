#!/usr/bin/env python3
"""
Quick API Test
Test the ticket creation API to see what it returns
"""

import requests
import json

BASE_URL = "http://127.0.0.1:5000"

test_data = {
    "message": "Quick API test - no user creation needed",
    "subject": "API Test Ticket",
    "priority": "medium"
    # Removing name, email, organization to avoid user creation
}

headers = {
    'Content-Type': 'application/json',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

try:
    response = requests.post(f"{BASE_URL}/api/tickets", json=test_data, headers=headers)
    print(f"Status Code: {response.status_code}")
    print(f"Response Text: {response.text}")
    print(f"Response Headers: {dict(response.headers)}")
    
    if response.status_code == 200:
        try:
            json_data = response.json()
            print(f"JSON Data: {json_data}")
            print(f"Type: {type(json_data)}")
        except:
            print("Response is not valid JSON")
    
except Exception as e:
    print(f"Error: {e}")
