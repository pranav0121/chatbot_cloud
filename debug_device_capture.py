#!/usr/bin/env python3
"""
Debug Device Tracking in Live System
Check if device info is being captured and stored
"""

import requests
import json

BASE_URL = "http://127.0.0.1:5000"

def test_device_capture():
    """Test if device tracking captures and stores device info"""
    
    print("🔍 Testing Device Tracking Capture")
    print("=" * 50)
    
    # Test data with realistic browser headers
    test_data = {
        "message": "Device tracking debug test - checking capture",
        "subject": "Device Debug Test",
        "priority": "medium",
        "name": "Device Test User",
        "email": "devicetest@debug.com", 
        "organization": "Debug Org"
    }
    
    # Realistic browser headers
    headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Referer': 'http://127.0.0.1:5000/',
        'X-Requested-With': 'XMLHttpRequest',
        'X-Forwarded-For': '192.168.1.100',
        'Remote-Addr': '127.0.0.1'
    }
    
    try:
        print("📤 Sending ticket creation request with device headers...")
        response = requests.post(f"{BASE_URL}/api/tickets", json=test_data, headers=headers)
        
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            ticket_id = result.get('ticket_id')
            print(f"✅ Ticket created: {ticket_id}")
            return ticket_id
        else:
            print(f"❌ Failed to create ticket")
            return None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

if __name__ == "__main__":
    test_device_capture()
