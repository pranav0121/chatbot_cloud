#!/usr/bin/env python3
"""
Device Tracking Integration Demo
This demonstrates how to integrate device tracking into the ticket creation process
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, request, jsonify
from datetime import datetime
import json

# Import our device tracking modules
from device_tracker_core import DeviceInfo, DeviceAnalytics
from device_tracker import DeviceTracker

def extract_device_info_from_request():
    """Extract device information from Flask request"""
    try:
        # Get device info from request headers
        user_agent = request.headers.get('User-Agent', 'Unknown')
        ip_address = request.remote_addr
        
        # Check if device info was sent in request body
        device_data = None
        if request.is_json and hasattr(request, 'json') and request.json and 'device_info' in request.json:
            device_data = request.json['device_info']
        
        # Create device info object
        device_info = DeviceInfo(user_agent, ip_address)
        complete_info = device_info.get_complete_info()
        
        # Use client-side data if available, otherwise use server-side parsing
        if device_data:
            # Merge client-side data with server-side analysis
            complete_info.update({
                'client_device_type': device_data.get('deviceType'),
                'client_browser': device_data.get('browser', {}),
                'client_os': device_data.get('os', {}),
                'screen_resolution': f"{device_data.get('screenWidth', 0)}x{device_data.get('screenHeight', 0)}",
                'viewport': f"{device_data.get('viewportWidth', 0)}x{device_data.get('viewportHeight', 0)}",
                'session_id': device_data.get('sessionId'),
                'language': device_data.get('language'),
                'timezone': device_data.get('timezone')
            })
        
        return complete_info
        
    except Exception as e:
        print(f"Error extracting device info: {e}")
        return {
            'user_agent': request.headers.get('User-Agent', 'Unknown'),
            'ip_address': request.remote_addr,
            'device_type': 'unknown',
            'browser': {'family': 'Unknown', 'version_string': '0.0'},
            'os': {'family': 'Unknown', 'version_string': '0.0'},
            'error': str(e)
        }

def update_user_with_device_info(user, device_info):
    """Update user model with device information"""
    try:
        user.LastDeviceType = device_info.get('device_type')
        user.LastBrowser = device_info.get('browser', {}).get('family')
        user.LastOS = device_info.get('os', {}).get('family')
        user.LastIPAddress = device_info.get('ip_address')
        user.IsMobileUser = device_info.get('is_mobile', False)
        user.LastLogin = datetime.utcnow()
        print(f"Updated user {user.UserID} with device info: {device_info.get('device_type')}")
    except Exception as e:
        print(f"Error updating user with device info: {e}")

def update_ticket_with_device_info(ticket, device_info):
    """Update ticket model with device information"""
    try:
        browser_info = device_info.get('browser', {})
        os_info = device_info.get('os', {})
        
        ticket.CreatedFromDevice = device_info.get('device_type', 'unknown')
        ticket.CreatedFromBrowser = f"{browser_info.get('family', 'Unknown')} {browser_info.get('version_string', '')}"
        ticket.CreatedFromOS = f"{os_info.get('family', 'Unknown')} {os_info.get('version_string', '')}"
        ticket.CreatedFromIP = device_info.get('ip_address')
        ticket.UserAgent = device_info.get('user_agent', 'Unknown')
        
        print(f"Updated ticket {ticket.TicketID} with device info: {device_info.get('device_type')}")
    except Exception as e:
        print(f"Error updating ticket with device info: {e}")

def get_device_info_display(ticket):
    """Get formatted device info for display in admin UI"""
    try:
        device_type = ticket.CreatedFromDevice or 'Unknown'
        browser = ticket.CreatedFromBrowser or 'Unknown'
        os = ticket.CreatedFromOS or 'Unknown'
        ip = ticket.CreatedFromIP or 'Unknown'
        
        # Determine device icon
        device_icon = '🖥️'  # Default desktop
        if device_type == 'mobile':
            device_icon = '📱'
        elif device_type == 'tablet':
            device_icon = '📱'
        elif device_type == 'bot':
            device_icon = '🤖'
        
        # Determine risk level
        risk_level = 'normal'
        risk_color = 'green'
        if device_type == 'bot':
            risk_level = 'high'
            risk_color = 'red'
        elif ip.startswith('10.') or ip.startswith('192.168.') or ip.startswith('172.'):
            risk_level = 'low'
            risk_color = 'blue'
        
        return {
            'device_type': device_type,
            'browser': browser,
            'os': os,
            'ip_address': ip,
            'device_icon': device_icon,
            'risk_level': risk_level,
            'risk_color': risk_color,
            'display_text': f"{device_icon} {device_type.title()} | {browser} | {os}"
        }
    except Exception as e:
        print(f"Error formatting device info display: {e}")
        return {
            'device_type': 'Unknown',
            'browser': 'Unknown',
            'os': 'Unknown',
            'ip_address': 'Unknown',
            'device_icon': '❓',
            'risk_level': 'unknown',
            'risk_color': 'gray',
            'display_text': '❓ Unknown Device'
        }

def create_ticket_with_device_tracking_demo():
    """Demo function showing how to integrate device tracking into ticket creation"""
    print("=== Device Tracking Integration Demo ===")
    print()
    
    # Simulate extracting device info from request
    print("1. Extract device information from request:")
    # Note: In real implementation, this would use actual Flask request
    sample_device_info = {
        'device_type': 'mobile',
        'browser': {'family': 'Chrome', 'version_string': '91.0.4472.124'},
        'os': {'family': 'Android', 'version_string': '11'},
        'ip_address': '192.168.1.100',
        'user_agent': 'Mozilla/5.0 (Linux; Android 11; SM-G991B) AppleWebKit/537.36',
        'is_mobile': True,
        'is_tablet': False,
        'is_bot': False
    }
    
    print(f"   Device Type: {sample_device_info['device_type']}")
    print(f"   Browser: {sample_device_info['browser']['family']} {sample_device_info['browser']['version_string']}")
    print(f"   OS: {sample_device_info['os']['family']} {sample_device_info['os']['version_string']}")
    print(f"   IP: {sample_device_info['ip_address']}")
    print()
    
    # Simulate updating user with device info
    print("2. Update user with device information:")
    class MockUser:
        def __init__(self, user_id):
            self.UserID = user_id
            self.Name = "John Doe"
            self.Email = "john@example.com"
    
    mock_user = MockUser(123)
    update_user_with_device_info(mock_user, sample_device_info)
    print(f"   Updated user {mock_user.UserID}")
    print(f"   Last Device: {mock_user.LastDeviceType}")
    print(f"   Last Browser: {mock_user.LastBrowser}")
    print(f"   Is Mobile User: {mock_user.IsMobileUser}")
    print()
    
    # Simulate updating ticket with device info
    print("3. Update ticket with device information:")
    class MockTicket:
        def __init__(self, ticket_id):
            self.TicketID = ticket_id
            self.Subject = "Sample Support Request"
    
    mock_ticket = MockTicket(456)
    update_ticket_with_device_info(mock_ticket, sample_device_info)
    print(f"   Updated ticket {mock_ticket.TicketID}")
    print(f"   Created From Device: {mock_ticket.CreatedFromDevice}")
    print(f"   Created From Browser: {mock_ticket.CreatedFromBrowser}")
    print(f"   Created From OS: {mock_ticket.CreatedFromOS}")
    print()
    
    # Simulate admin view formatting
    print("4. Format device info for admin display:")
    display_info = get_device_info_display(mock_ticket)
    print(f"   Display Text: {display_info['display_text']}")
    print(f"   Risk Level: {display_info['risk_level']} ({display_info['risk_color']})")
    print(f"   Device Icon: {display_info['device_icon']}")
    print()
    
    print("=== Integration Complete ===")
    return display_info

if __name__ == "__main__":
    create_ticket_with_device_tracking_demo()
