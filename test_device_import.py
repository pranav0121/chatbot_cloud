#!/usr/bin/env python3
"""
Test DeviceInfo Import and Usage
"""

try:
    print("Testing DeviceInfo import...")
    from device_tracker_core import DeviceInfo
    print("✅ DeviceInfo imported successfully")
    
    # Test creating DeviceInfo instance
    test_user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    test_ip = "192.168.1.100"
    
    print(f"Testing DeviceInfo with:")
    print(f"  User-Agent: {test_user_agent}")
    print(f"  IP: {test_ip}")
    
    device_info = DeviceInfo(user_agent_string=test_user_agent, ip_address=test_ip)
    print("✅ DeviceInfo instance created")
    
    device_data = device_info.get_complete_info()
    print("✅ get_complete_info() called")
    
    print(f"Device data: {device_data}")
    
    if device_data:
        browser_info = device_data.get('browser', {})
        os_info = device_data.get('os', {})
        
        print(f"\nParsed info:")
        print(f"  Device Type: {device_data.get('device_type')}")
        print(f"  Browser: {browser_info.get('family') if browser_info else 'Unknown'}")
        print(f"  Browser Version: {browser_info.get('version_string') if browser_info else 'Unknown'}")
        print(f"  OS: {os_info.get('family') if os_info else 'Unknown'}")
        print(f"  OS Version: {os_info.get('version_string') if os_info else 'Unknown'}")
        print(f"  User Agent: {device_data.get('user_agent')}")
        print(f"  IP: {device_data.get('ip_address')}")
        
except ImportError as e:
    print(f"❌ Import error: {e}")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
