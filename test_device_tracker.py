#!/usr/bin/env python3
"""
Simple test for device tracker functionality
"""

import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import just the device tracking classes without Flask app
from device_tracker_core import DeviceInfo, SimpleUserAgentParser, DeviceAnalytics

def test_device_tracker():
    """Test device tracking functionality"""
    
    print("=== Testing Device Tracker ===")
    
    # Test with various user agents
    test_user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1",
        "Mozilla/5.0 (iPad; CPU OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    ]
    
    for i, ua in enumerate(test_user_agents, 1):
        print(f"\n--- Test {i} ---")
        print(f"User Agent: {ua[:60]}...")
        
        try:
            # Test SimpleUserAgentParser
            parser = SimpleUserAgentParser(ua)
            browser_info = parser.get_browser_info()
            os_info = parser.get_os_info()
            
            print(f"Browser: {browser_info['family']} {browser_info['version_string']}")
            print(f"OS: {os_info['family']} {os_info['version_string']}")
            print(f"Mobile: {parser.is_mobile}")
            print(f"Tablet: {parser.is_tablet}")
            print(f"PC: {parser.is_pc}")
            print(f"Bot: {parser.is_bot}")
            
            # Test DeviceInfo
            device_info = DeviceInfo(ua, "192.168.1.100")
            device_type = device_info.get_device_type()
            print(f"Device Type: {device_type}")
            
            # Get complete info
            complete_info = device_info.get_complete_info()
            print(f"Complete Device Info: {complete_info['device_type']}, {complete_info['browser']['family']}, {complete_info['os']['family']}")
            
            # Test compatibility checking
            compatibility = DeviceAnalytics.get_compatibility_info(device_info)
            print(f"WebSocket Support: {compatibility['websocket_support']}")
            print(f"File Upload Support: {compatibility['file_upload_support']}")
            if compatibility['issues']:
                print(f"Issues: {', '.join(compatibility['issues'])}")
            else:
                print("No compatibility issues found")
    
        except Exception as e:
            print(f"Error testing user agent: {e}")
    
    # Test analytics
    print(f"\n--- Analytics Test ---")
    stats = DeviceAnalytics.get_device_stats()
    print(f"Device Type Stats: {stats['device_types']}")
    print(f"Browser Stats: {stats['browsers']}")
    print(f"OS Stats: {stats['operating_systems']}")
    
    print("\n=== Device Tracker Test Completed ===")

if __name__ == "__main__":
    test_device_tracker()
