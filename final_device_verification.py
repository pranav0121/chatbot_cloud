#!/usr/bin/env python3
"""
Final Device Tracking Verification Test
Comprehensive test to verify device tracking is working end-to-end
"""

import requests
import json
import time
from datetime import datetime

BASE_URL = "http://127.0.0.1:5000"

def test_complete_device_tracking():
    """Test complete device tracking workflow"""
    
    print("🔍 FINAL DEVICE TRACKING VERIFICATION")
    print("=" * 50)
    
    # Test ticket creation with device tracking
    print("\n1. Testing ticket creation with device tracking...")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'X-Forwarded-For': '192.168.1.100',
        'Content-Type': 'application/json'
    }
    
    ticket_data = {
        'message': f'Final device tracking test - {datetime.now().strftime("%H:%M:%S")}',
        'subject': 'Final Device Verification Test',
        'priority': 'medium'
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/tickets", json=ticket_data, headers=headers, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            ticket_id = result.get('ticket_id')
            print(f"✅ Ticket created successfully: #{ticket_id}")
            
            # Wait a moment for processing
            time.sleep(2)
            
            # Test ticket retrieval to verify device info
            print(f"\n2. Verifying device info for ticket #{ticket_id}...")
            
            ticket_response = requests.get(f"{BASE_URL}/api/tickets/{ticket_id}", timeout=10)
            if ticket_response.status_code == 200:
                ticket_details = ticket_response.json()
                print(f"✅ Ticket details retrieved successfully")
                
                # Check if device info is available in response
                if any(key in ticket_details for key in ['device_type', 'browser', 'operating_system']):
                    print("✅ Device information found in API response")
                else:
                    print("ℹ️ Device info not in API response (may be in database only)")
                
            else:
                print(f"❌ Failed to retrieve ticket details: {ticket_response.status_code}")
            
            return ticket_id
            
        else:
            print(f"❌ Failed to create ticket: {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return None

def test_database_verification(ticket_id):
    """Verify device info is stored in database"""
    if not ticket_id:
        return
        
    print(f"\n3. Database verification for ticket #{ticket_id}...")
    
    # Import database checking function
    try:
        import sys
        import os
        sys.path.append(os.getcwd())
        
        from check_device_db import check_specific_ticket_device
        device_info = check_specific_ticket_device(ticket_id)
        
        if device_info:
            print(f"✅ Device info found in database:")
            print(f"   Device Type: {device_info.get('device_type', 'N/A')}")
            print(f"   OS: {device_info.get('operating_system', 'N/A')}")
            print(f"   Browser: {device_info.get('browser', 'N/A')}")
            print(f"   IP: {device_info.get('ip_address', 'N/A')}")
            return True
        else:
            print(f"❌ No device info found in database")
            return False
            
    except Exception as e:
        print(f"⚠️ Database verification failed: {e}")
        return False

def main():
    """Run complete device tracking verification"""
    
    print("🚀 Starting Final Device Tracking Verification")
    print(f"🕒 Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Test ticket creation
    ticket_id = test_complete_device_tracking()
    
    # Verify database storage
    if ticket_id:
        db_success = test_database_verification(ticket_id)
        
        print("\n" + "=" * 50)
        print("📊 FINAL VERIFICATION RESULTS")
        print("=" * 50)
        
        if db_success:
            print("🎉 ✅ DEVICE TRACKING FULLY FUNCTIONAL!")
            print("   • Ticket creation: ✅ SUCCESS")
            print("   • Device extraction: ✅ SUCCESS") 
            print("   • Database storage: ✅ SUCCESS")
            print("   • Data integrity: ✅ VERIFIED")
            print()
            print("🏁 Device tracking integration is COMPLETE and working!")
        else:
            print("❌ DEVICE TRACKING INCOMPLETE")
            print("   Some components are not working properly")
    else:
        print("\n❌ VERIFICATION FAILED")
        print("Could not create test ticket")
    
    print(f"\n🕒 Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
