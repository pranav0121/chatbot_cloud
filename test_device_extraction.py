#!/usr/bin/env python3
"""
Test Device Tracking Function
Test the DeviceInfo.extract_from_request() function directly
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from device_tracker_core import DeviceInfo
from flask import Flask, request
import json

app = Flask(__name__)

def test_device_extraction():
    """Test device info extraction with simulated request"""
    
    print("🔍 Testing Device Info Extraction")
    print("=" * 40)
    
    # Create a mock request environment
    with app.test_request_context(
        '/',
        headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json',
            'Accept-Language': 'en-US,en;q=0.9',
            'X-Forwarded-For': '192.168.1.100'
        },
        environ_base={'REMOTE_ADDR': '127.0.0.1'}
    ):
        try:
            device_info = DeviceInfo()
            print("✅ DeviceInfo instance created")
            
            device_data = device_info.extract_from_request(request)
            print("✅ extract_from_request() executed")
            
            print(f"\n📊 Device Data Result:")
            print(f"Type: {type(device_data)}")
            print(f"Data: {device_data}")
            
            if device_data:
                print(f"\n📱 Extracted Device Information:")
                for key, value in device_data.items():
                    print(f"   {key}: {value}")
            else:
                print(f"\n❌ No device data returned")
                
        except Exception as e:
            print(f"❌ Error testing device extraction: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    test_device_extraction()
