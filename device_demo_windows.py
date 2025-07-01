#!/usr/bin/env python3
"""
Device Tracking Integration Demo - Windows Compatible Version
This demonstrates how to integrate device tracking into the ticket creation process
No Unicode characters, fully Windows terminal compatible
"""

import sys
import os
import json
from datetime import datetime

def extract_device_info_from_request_demo():
    """Demo of extracting device information from Flask request"""
    print("Extracting device info from request headers and JSON payload...")
    
    # Simulate client-side device info sent with the ticket
    sample_client_data = {
        'deviceType': 'mobile',
        'browser': {
            'name': 'Chrome',
            'version': '91.0.4472.124'
        },
        'os': {
            'name': 'Android',
            'version': '11'
        },
        'screenWidth': 412,
        'screenHeight': 915,
        'viewportWidth': 412,
        'viewportHeight': 734,
        'sessionId': 'sess_12345678',
        'language': 'en-US',
        'timezone': 'America/New_York'
    }
    
    # Simulate server-side parsing from User-Agent
    sample_server_data = {
        'user_agent': 'Mozilla/5.0 (Linux; Android 11; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Mobile Safari/537.36',
        'ip_address': '192.168.1.100',
        'device_type': 'mobile',
        'is_mobile': True,
        'is_tablet': False,
        'is_bot': False
    }
    
    # Merge client and server data
    complete_info = dict(sample_server_data)
    complete_info.update({
        'client_device_type': sample_client_data['deviceType'],
        'client_browser': sample_client_data['browser'],
        'client_os': sample_client_data['os'],
        'screen_resolution': f"{sample_client_data['screenWidth']}x{sample_client_data['screenHeight']}",
        'viewport': f"{sample_client_data['viewportWidth']}x{sample_client_data['viewportHeight']}",
        'session_id': sample_client_data['sessionId'],
        'language': sample_client_data['language'],
        'timezone': sample_client_data['timezone']
    })
    
    return complete_info

def update_user_with_device_info(user_data, device_info):
    """Update user model with device information"""
    try:
        user_data['LastDeviceType'] = device_info.get('device_type')
        user_data['LastBrowser'] = device_info.get('client_browser', {}).get('name')
        user_data['LastOS'] = device_info.get('client_os', {}).get('name')
        user_data['LastIPAddress'] = device_info.get('ip_address')
        user_data['IsMobileUser'] = device_info.get('is_mobile', False)
        user_data['LastLogin'] = datetime.utcnow().isoformat()
        print(f"[OK] Updated user {user_data['UserID']} with device info")
        return user_data
    except Exception as e:
        print(f"[ERROR] Error updating user with device info: {e}")
        return user_data

def update_ticket_with_device_info(ticket_data, device_info):
    """Update ticket model with device information"""
    try:
        browser_info = device_info.get('client_browser', {})
        os_info = device_info.get('client_os', {})
        
        ticket_data['CreatedFromDevice'] = device_info.get('device_type', 'unknown')
        ticket_data['CreatedFromBrowser'] = f"{browser_info.get('name', 'Unknown')} {browser_info.get('version', '')}"
        ticket_data['CreatedFromOS'] = f"{os_info.get('name', 'Unknown')} {os_info.get('version', '')}"
        ticket_data['CreatedFromIP'] = device_info.get('ip_address')
        ticket_data['UserAgent'] = device_info.get('user_agent', 'Unknown')
        
        print(f"[OK] Updated ticket {ticket_data['TicketID']} with device info")
        return ticket_data
    except Exception as e:
        print(f"[ERROR] Error updating ticket with device info: {e}")
        return ticket_data

def get_device_info_display(ticket_data):
    """Get formatted device info for display in admin UI"""
    try:
        device_type = ticket_data.get('CreatedFromDevice', 'Unknown')
        browser = ticket_data.get('CreatedFromBrowser', 'Unknown')
        os = ticket_data.get('CreatedFromOS', 'Unknown')
        ip = ticket_data.get('CreatedFromIP', 'Unknown')
        
        # Determine device icon (text-based for Windows compatibility)
        device_icons = {
            'mobile': '[M]',
            'tablet': '[T]',
            'desktop': '[D]',
            'bot': '[B]',
            'unknown': '[?]'
        }
        device_icon = device_icons.get(device_type, '[?]')
        
        # Determine risk level based on device type and IP
        risk_level = 'normal'
        risk_color = 'green'
        warning_flags = []
        
        if device_type == 'bot':
            risk_level = 'high'
            risk_color = 'red'
            warning_flags.append('Bot detected')
        elif ip and (ip.startswith('10.') or ip.startswith('192.168.') or ip.startswith('172.')):
            risk_level = 'low'
            risk_color = 'blue'
            warning_flags.append('Internal network')
        
        if 'Unknown' in browser or 'Unknown' in os:
            warning_flags.append('Limited device info')
        
        return {
            'device_type': device_type,
            'browser': browser,
            'os': os,
            'ip_address': ip,
            'device_icon': device_icon,
            'risk_level': risk_level,
            'risk_color': risk_color,
            'warning_flags': warning_flags,
            'display_text': f"{device_icon} {device_type.title()} | {browser} | {os}",
            'admin_summary': f"Device: {device_type.title()}, Browser: {browser}, OS: {os}, IP: {ip}"
        }
    except Exception as e:
        print(f"[ERROR] Error formatting device info display: {e}")
        return {
            'device_type': 'Unknown',
            'browser': 'Unknown',
            'os': 'Unknown',
            'ip_address': 'Unknown',
            'device_icon': '[?]',
            'risk_level': 'unknown',
            'risk_color': 'gray',
            'warning_flags': ['Error getting device info'],
            'display_text': '[?] Unknown Device',
            'admin_summary': 'Device information unavailable'
        }

def create_ticket_with_device_tracking_demo():
    """Demo function showing complete device tracking integration"""
    print("Device Tracking Integration Demo")
    print("=" * 50)
    print()
    
    # Step 1: Extract device info from request
    print("Step 1: Extract device information from request")
    device_info = extract_device_info_from_request_demo()
    print(f"   Device Type: {device_info['device_type']}")
    print(f"   Browser: {device_info['client_browser']['name']} {device_info['client_browser']['version']}")
    print(f"   OS: {device_info['client_os']['name']} {device_info['client_os']['version']}")
    print(f"   Screen: {device_info['screen_resolution']}")
    print(f"   IP: {device_info['ip_address']}")
    print(f"   Session: {device_info['session_id']}")
    print()
    
    # Step 2: Create/Update user with device info
    print("Step 2: Update user with device information")
    user_data = {
        'UserID': 123,
        'Name': 'John Doe',
        'Email': 'john@example.com',
        'OrganizationName': 'Tech Corp'
    }
    user_data = update_user_with_device_info(user_data, device_info)
    print(f"   User: {user_data['Name']} ({user_data['Email']})")
    print(f"   Last Device: {user_data['LastDeviceType']}")
    print(f"   Last Browser: {user_data['LastBrowser']}")
    print(f"   Is Mobile User: {user_data['IsMobileUser']}")
    print()
    
    # Step 3: Create ticket with device info
    print("Step 3: Create ticket with device information")
    ticket_data = {
        'TicketID': 456,
        'Subject': 'Login Issues on Mobile App',
        'Priority': 'high',
        'Status': 'open',
        'UserID': user_data['UserID'],
        'CreatedAt': datetime.utcnow().isoformat()
    }
    ticket_data = update_ticket_with_device_info(ticket_data, device_info)
    print(f"   Ticket: #{ticket_data['TicketID']} - {ticket_data['Subject']}")
    print(f"   Created From Device: {ticket_data['CreatedFromDevice']}")
    print(f"   Created From Browser: {ticket_data['CreatedFromBrowser']}")
    print(f"   Created From OS: {ticket_data['CreatedFromOS']}")
    print(f"   IP Address: {ticket_data['CreatedFromIP']}")
    print()
    
    # Step 4: Format for admin display
    print("Step 4: Format device info for admin/super-admin view")
    display_info = get_device_info_display(ticket_data)
    print(f"   Display Text: {display_info['display_text']}")
    print(f"   Admin Summary: {display_info['admin_summary']}")
    print(f"   Risk Level: {display_info['risk_level']} ({display_info['risk_color']})")
    if display_info['warning_flags']:
        print(f"   [!] Warnings: {', '.join(display_info['warning_flags'])}")
    print()
    
    # Step 5: Show admin dashboard view
    print("Step 5: Admin Dashboard View Example")
    print("-" * 40)
    print(f"Ticket #{ticket_data['TicketID']}")
    print(f"Subject: {ticket_data['Subject']}")
    print(f"User: {user_data['Name']} ({user_data['Email']})")
    print(f"Priority: {ticket_data['Priority'].upper()}")
    print(f"Device Info: {display_info['display_text']}")
    print(f"Risk Assessment: {display_info['risk_level'].upper()}")
    if display_info['warning_flags']:
        print(f"[!] Alerts: {', '.join(display_info['warning_flags'])}")
    print("-" * 40)
    print()
    
    print("[OK] Device Tracking Integration Complete!")
    print()
    print("Next Steps for Full Integration:")
    print("1. Run the device tracking migration to add database fields")
    print("2. Add device extraction to ticket creation endpoint in app.py")
    print("3. Update admin ticket templates to display device info")
    print("4. Add device tracking to chat widget initialization")
    print("5. Test end-to-end device tracking flow")
    
    return {
        'user_data': user_data,
        'ticket_data': ticket_data,
        'device_info': device_info,
        'display_info': display_info
    }

def main():
    """Main function"""
    try:
        result = create_ticket_with_device_tracking_demo()
        
        # Save demo results for reference
        demo_file = 'device_tracking_demo_results.json'
        try:
            with open(demo_file, 'w') as f:
                json.dump(result, f, indent=2, default=str)
            print(f"\n[OK] Demo results saved to {demo_file}")
        except Exception as e:
            print(f"\n[ERROR] Could not save demo results: {e}")
            
        return True
        
    except Exception as e:
        print(f"\n[ERROR] Demo failed: {e}")
        return False

if __name__ == "__main__":
    if main():
        print("\n[SUCCESS] Device tracking demo completed successfully!")
        sys.exit(0)
    else:
        print("\n[FAILURE] Device tracking demo failed!")
        sys.exit(1)
