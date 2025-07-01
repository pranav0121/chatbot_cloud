#!/usr/bin/env python3
"""
Device Tracking Flask Integration
Add these routes and modifications to your main app.py file
"""

from flask import request, jsonify
from datetime import datetime
from device_tracker_core import DeviceInfo, DeviceAnalytics
import json

# Add this function to your app.py
def extract_device_info_from_request():
    """Extract device information from Flask request"""
    try:
        # Get device info from request headers
        user_agent = request.headers.get('User-Agent', 'Unknown')
        ip_address = request.remote_addr
        
        # Check if device info was sent in request body
        device_data = None
        if request.is_json and 'device_info' in request.json:
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

# MODIFY YOUR EXISTING TICKET CREATION ROUTE TO INCLUDE THIS:
"""
@app.route('/api/tickets', methods=['POST'])
def create_ticket():
    try:
        data = request.get_json()
        
        # Extract device information
        device_info = extract_device_info_from_request()
        
        # Create user if not exists
        user_email = data.get('email', '').strip()
        user_name = data.get('name', '').strip()
        
        if user_email:
            user = User.query.filter_by(Email=user_email).first()
            if not user:
                user = User(
                    Name=user_name or 'Anonymous',
                    Email=user_email,
                    OrganizationName='Customer',
                    # Add device info to user
                    LastDeviceType=device_info.get('device_type'),
                    LastBrowser=device_info.get('browser', {}).get('family'),
                    LastOS=device_info.get('os', {}).get('family'),
                    LastIPAddress=device_info.get('ip_address'),
                    IsMobileUser=device_info.get('is_mobile', False)
                )
                db.session.add(user)
                db.session.flush()  # To get the user ID
            else:
                # Update user's device info
                user.LastDeviceType = device_info.get('device_type')
                user.LastBrowser = device_info.get('browser', {}).get('family')
                user.LastOS = device_info.get('os', {}).get('family') 
                user.LastIPAddress = device_info.get('ip_address')
                user.IsMobileUser = device_info.get('is_mobile', False)
                user.LastLogin = datetime.utcnow()
        else:
            # Create anonymous user
            user = User(
                Name=user_name or 'Anonymous',
                Email=f'anonymous_{int(time.time())}@temp.com',
                OrganizationName='Anonymous',
                LastDeviceType=device_info.get('device_type'),
                LastBrowser=device_info.get('browser', {}).get('family'),
                LastOS=device_info.get('os', {}).get('family'),
                LastIPAddress=device_info.get('ip_address'),
                IsMobileUser=device_info.get('is_mobile', False)
            )
            db.session.add(user)
            db.session.flush()
        
        # Create ticket with device information
        ticket = Ticket(
            UserID=user.UserID,
            CategoryID=data.get('category_id', 1),
            Subject=data.get('subject', 'Support Request'),
            Priority='medium',
            Status='open',
            OrganizationName=user.OrganizationName,
            CreatedBy=user.Name,
            # Add device tracking fields
            CreatedFromDevice=device_info.get('device_type'),
            CreatedFromBrowser=device_info.get('browser', {}).get('family'),
            CreatedFromOS=device_info.get('os', {}).get('family'),
            CreatedFromIP=device_info.get('ip_address'),
            UserAgent=device_info.get('user_agent'),
            Country=device_info.get('country')  # if you have geo-location
        )
        
        # Set priority based on device compatibility
        compatibility = DeviceAnalytics.get_compatibility_info(DeviceInfo(device_info.get('user_agent')))
        if compatibility.get('issues'):
            if 'Internet Explorer' in device_info.get('browser', {}).get('family', ''):
                ticket.Priority = 'high'
                ticket.EscalationReason = 'Browser compatibility issues detected'
            elif device_info.get('device_type') == 'mobile':
                ticket.Priority = 'medium'
        
        db.session.add(ticket)
        db.session.flush()
        
        # Create initial message
        message = Message(
            TicketID=ticket.TicketID,
            Content=data.get('message', ''),
            IsAdminReply=False
        )
        db.session.add(message)
        
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'ticket_id': ticket.TicketID,
            'user_id': user.UserID,
            'device_info': device_info,
            'compatibility_warnings': compatibility.get('issues', [])
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500
"""

# ADD THIS NEW ROUTE FOR DEVICE TRACKING API
"""
@app.route('/api/device-tracking', methods=['POST'])
def track_device_event():
    try:
        data = request.get_json()
        
        # Extract device info
        device_info = extract_device_info_from_request()
        
        # Create device tracking log entry
        from device_tracker import log_device_event
        
        event_id = log_device_event(
            event_type=data.get('eventType', 'unknown'),
            ticket_id=data.get('data', {}).get('ticketId'),
            user_id=data.get('data', {}).get('userId')
        )
        
        return jsonify({
            'status': 'success',
            'event_id': event_id,
            'device_info': device_info
        })
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
"""

# ADD HELPER FUNCTION FOR ADMIN VIEWS
def get_device_display_info(ticket):
    """Get formatted device information for admin display"""
    device_info = {
        'device_type': ticket.CreatedFromDevice or 'Unknown',
        'browser': ticket.CreatedFromBrowser or 'Unknown',
        'os': ticket.CreatedFromOS or 'Unknown',
        'ip': ticket.CreatedFromIP or 'Unknown',
        'user_agent': ticket.UserAgent or 'Unknown'
    }
    
    # Determine device icon and styling
    device_type = device_info['device_type'].lower()
    if device_type == 'mobile':
        device_info['icon'] = 'fa-mobile-alt'
        device_info['color'] = 'text-info'
    elif device_type == 'tablet':
        device_info['icon'] = 'fa-tablet-alt' 
        device_info['color'] = 'text-primary'
    elif device_type == 'desktop':
        device_info['icon'] = 'fa-desktop'
        device_info['color'] = 'text-success'
    else:
        device_info['icon'] = 'fa-question-circle'
        device_info['color'] = 'text-muted'
    
    # Check for compatibility issues
    browser = device_info['browser'].lower()
    if 'internet explorer' in browser:
        device_info['warning'] = 'Browser compatibility issues'
        device_info['warning_level'] = 'danger'
    elif 'safari' in browser and device_type == 'mobile':
        device_info['warning'] = 'Limited mobile Safari support'
        device_info['warning_level'] = 'warning'
    else:
        device_info['warning'] = None
        device_info['warning_level'] = None
    
    # Format for display
    device_info['display_text'] = f"{device_info['device_type'].title()} • {device_info['browser']} • {device_info['os']}"
    
    return device_info

# SAMPLE TEMPLATE HELPER FUNCTIONS TO ADD TO YOUR APP
"""
@app.template_filter('device_icon')
def device_icon_filter(device_type):
    icons = {
        'mobile': 'fa-mobile-alt',
        'tablet': 'fa-tablet-alt',
        'desktop': 'fa-desktop'
    }
    return icons.get(device_type.lower(), 'fa-question-circle')

@app.template_filter('device_color')
def device_color_filter(device_type):
    colors = {
        'mobile': 'text-info',
        'tablet': 'text-primary', 
        'desktop': 'text-success'
    }
    return colors.get(device_type.lower(), 'text-muted')
"""

print("Device tracking Flask integration code ready!")
print("Copy the route modifications into your app.py file")
print("Make sure to import: from device_tracker_core import DeviceInfo, DeviceAnalytics")
