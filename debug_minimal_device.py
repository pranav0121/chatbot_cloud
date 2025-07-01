#!/usr/bin/env python3
"""
Debug Device Tracking - Minimal Test
Test device tracking without user creation
"""

import requests
import json

BASE_URL = "http://127.0.0.1:5000"

def test_minimal_device_capture():
    """Test device tracking with minimal data"""
    
    print("🔍 Testing Minimal Device Tracking")
    print("=" * 40)
    
    # Minimal test data (no user creation)
    test_data = {
        "message": "Device tracking test - minimal data",
        "subject": "Device Debug",
        "priority": "medium"
    }
    
    # Realistic browser headers for device detection
    headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/json',
        'X-Forwarded-For': '192.168.1.100'
    }
    
    try:
        print("📤 Creating ticket without user data...")
        response = requests.post(f"{BASE_URL}/api/tickets", json=test_data, headers=headers)
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            ticket_id = result.get('ticket_id')
            print(f"✅ Ticket created successfully: {ticket_id}")
            print(f"   Priority: {result.get('priority')}")
            print(f"   Organization: {result.get('organization')}")
            
            # Now check if device info was captured by looking at database
            print(f"\n🔍 Checking if device info was captured for ticket {ticket_id}...")
            return ticket_id
        else:
            print(f"❌ Failed: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

if __name__ == "__main__":
    test_minimal_device_capture()
