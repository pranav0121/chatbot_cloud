#!/usr/bin/env python3
"""
Test Device Tracking Endpoint
Test the new device tracking endpoint we added
"""

import requests
import json

BASE_URL = "http://127.0.0.1:5000"

def test_device_endpoint():
    """Test the device tracking endpoint"""
    
    print("🔍 Testing Device Tracking Endpoint")
    print("=" * 40)
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'X-Forwarded-For': '192.168.1.100'
    }
    
    try:
        response = requests.get(f"{BASE_URL}/test-device-tracking", headers=headers)
        
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Device tracking endpoint is working!")
            
            device_data = data.get('device_data', {})
            print(f"Device Type: {device_data.get('device_type')}")
            print(f"Browser: {device_data.get('browser', {}).get('family')}")
            print(f"OS: {device_data.get('os', {}).get('family')}")
            print(f"User Agent: {data.get('user_agent', '')[:50]}...")
            print(f"IP: {data.get('ip_address')}")
            
        else:
            print(f"❌ Endpoint failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_device_endpoint()
