#!/usr/bin/env python3
"""
Test Device Tracking Logic Standalone
Test the exact logic we're using in app.py
"""

from device_tracker_core import DeviceInfo

def test_device_logic():
    """Test the device tracking logic we're using in the app"""
    
    print("🔍 Testing Device Tracking Logic")
    print("=" * 40)
    
    # Simulate the exact data we would get from Flask request
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    ip_address = '192.168.1.100'
    
    try:
        # Create DeviceInfo instance with extracted data (same as in app.py)
        device_info = DeviceInfo(user_agent_string=user_agent, ip_address=ip_address)
        device_data = device_info.get_complete_info()
        
        print("✅ DeviceInfo created and get_complete_info() called")
        print(f"Device data type: {type(device_data)}")
        print(f"Device data: {device_data}")
        
        if device_data:
            browser_info = device_data.get('browser', {})
            os_info = device_data.get('os', {})
            
            print(f"\n📊 Parsed Information:")
            print(f"   device_type: {device_data.get('device_type')}")
            print(f"   browser_info: {browser_info}")
            print(f"   os_info: {os_info}")
            print(f"   user_agent: {device_data.get('user_agent')}")
            print(f"   ip_address: {device_data.get('ip_address')}")
            
            # Test the exact mapping we use in app.py
            device_type = device_data.get('device_type')
            operating_system = os_info.get('family') if os_info else None
            browser = browser_info.get('family') if browser_info else None
            browser_version = browser_info.get('version_string') if browser_info else None
            os_version = os_info.get('version_string') if os_info else None
            user_agent_stored = device_data.get('user_agent')
            ip_address_stored = device_data.get('ip_address')
            
            print(f"\n📱 Values that would be stored in database:")
            print(f"   device_type: {device_type}")
            print(f"   operating_system: {operating_system}")
            print(f"   browser: {browser}")
            print(f"   browser_version: {browser_version}")
            print(f"   os_version: {os_version}")
            print(f"   user_agent: {user_agent_stored}")
            print(f"   ip_address: {ip_address_stored}")
            
            if any([device_type, operating_system, browser, user_agent_stored, ip_address_stored]):
                print("\n✅ Device tracking would capture data!")
            else:
                print("\n❌ No data would be captured")
        else:
            print("❌ No device data returned")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_device_logic()
