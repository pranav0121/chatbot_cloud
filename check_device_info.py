#!/usr/bin/env python3
"""
Quick Device Info Checker - Command Line Tool
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from device_tracker_core import DeviceInfo, DeviceAnalytics

def check_my_device():
    """Check device info for common user agents"""
    print("🔍 DEVICE INFORMATION CHECKER")
    print("=" * 50)
    
    print("\nChoose an option:")
    print("1. Check Windows Chrome Desktop")
    print("2. Check iPhone Safari Mobile")
    print("3. Check Android Chrome Mobile")
    print("4. Check iPad Safari Tablet")
    print("5. Check Windows Firefox")
    print("6. Check Internet Explorer (legacy)")
    print("7. Enter custom User Agent")
    
    choice = input("\nEnter your choice (1-7): ").strip()
    
    user_agents = {
        '1': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        '2': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1',
        '3': 'Mozilla/5.0 (Linux; Android 10; SM-G973F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.120 Mobile Safari/537.36',
        '4': 'Mozilla/5.0 (iPad; CPU OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1',
        '5': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
        '6': 'Mozilla/5.0 (compatible; MSIE 11.0; Windows NT 10.0; WOW64; Trident/7.0)'
    }
    
    if choice == '7':
        user_agent = input("Enter User Agent string: ").strip()
    elif choice in user_agents:
        user_agent = user_agents[choice]
    else:
        print("Invalid choice. Using default Chrome.")
        user_agent = user_agents['1']
    
    # Analyze device
    device_info = DeviceInfo(user_agent, "192.168.1.100")
    device_data = device_info.get_complete_info()
    
    print(f"\n" + "=" * 50)
    print(f"📱 DEVICE ANALYSIS RESULTS")
    print(f"=" * 50)
    
    print(f"\n🖥️  DEVICE INFORMATION:")
    print(f"   Type: {device_data['device_type'].upper()}")
    print(f"   Mobile: {'Yes' if device_data['is_mobile'] else 'No'}")
    print(f"   Tablet: {'Yes' if device_data['is_tablet'] else 'No'}")
    print(f"   Desktop: {'Yes' if device_data['is_pc'] else 'No'}")
    print(f"   Bot: {'Yes' if device_data['is_bot'] else 'No'}")
    
    print(f"\n🌐  BROWSER INFORMATION:")
    print(f"   Name: {device_data['browser']['family']}")
    print(f"   Version: {device_data['browser']['version_string']}")
    
    print(f"\n💻  OPERATING SYSTEM:")
    print(f"   Name: {device_data['os']['family']}")
    print(f"   Version: {device_data['os']['version_string']}")
    
    print(f"\n🌍  NETWORK:")
    print(f"   IP Address: {device_data['ip_address']}")
    print(f"   User Agent: {device_data['user_agent'][:100]}{'...' if len(device_data['user_agent']) > 100 else ''}")
    
    # Check compatibility
    compatibility = DeviceAnalytics.get_compatibility_info(device_info)
    
    print(f"\n⚡  COMPATIBILITY:")
    print(f"   WebSocket Support: {'Yes' if compatibility['websocket_support'] else 'No'}")
    print(f"   File Upload Support: {'Yes' if compatibility['file_upload_support'] else 'No'}")
    print(f"   Notifications Support: {'Yes' if compatibility['notifications_support'] else 'No'}")
    
    if compatibility['issues']:
        print(f"\n⚠️   COMPATIBILITY WARNINGS:")
        for issue in compatibility['issues']:
            print(f"      • {issue}")
    else:
        print(f"\n✅  No compatibility issues detected!")
    
    # Support recommendations
    print(f"\n🎯  SUPPORT RECOMMENDATIONS:")
    if 'Internet Explorer' in device_data['browser']['family']:
        print(f"   📞 Priority: HIGH")
        print(f"   🔧 Action: Browser upgrade assistance needed")
        print(f"   ⏰ Est. Time: 2-4 hours (includes upgrade)")
    elif device_data['device_type'] == 'mobile' and 'Safari' in device_data['browser']['family']:
        print(f"   📞 Priority: MEDIUM")
        print(f"   🔧 Action: Mobile-specific troubleshooting")
        print(f"   ⏰ Est. Time: 1-2 hours")
    else:
        print(f"   📞 Priority: NORMAL")
        print(f"   🔧 Action: Standard support procedures")
        print(f"   ⏰ Est. Time: 30 minutes - 2 hours")
    
    print(f"\n" + "=" * 50)
    print(f"✅ Analysis Complete!")
    print(f"=" * 50)
    
    # Ask if they want to check another
    again = input("\nCheck another device? (y/n): ").strip().lower()
    if again == 'y':
        print("\n" + "=" * 50)
        check_my_device()

if __name__ == "__main__":
    check_my_device()
