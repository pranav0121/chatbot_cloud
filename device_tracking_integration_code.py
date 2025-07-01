#!/usr/bin/env python3
"""
Device Tracking Integration Code for app.py
These are the code snippets to integrate into your main Flask application
"""

# =============================================================================
# PART 1: IMPORTS TO ADD AT THE TOP OF app.py
# =============================================================================

# Add these imports after your existing imports
from device_tracker_core import DeviceInfo, DeviceAnalytics
from device_tracker import DeviceTracker

# =============================================================================
# PART 2: HELPER FUNCTIONS TO ADD TO app.py
# =============================================================================

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
        logger.error(f"Error extracting device info: {e}")
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
        if hasattr(user, 'LastDeviceType'):
            user.LastDeviceType = device_info.get('device_type')
            user.LastBrowser = device_info.get('browser', {}).get('family')
            user.LastOS = device_info.get('os', {}).get('family')
            user.LastIPAddress = device_info.get('ip_address')
            user.IsMobileUser = device_info.get('is_mobile', False)
            user.LastLogin = datetime.utcnow()
            logger.info(f"Updated user {user.UserID} with device info: {device_info.get('device_type')}")
    except Exception as e:
        logger.error(f"Error updating user with device info: {e}")

def update_ticket_with_device_info(ticket, device_info):
    """Update ticket model with device information"""
    try:
        if hasattr(ticket, 'CreatedFromDevice'):
            browser_info = device_info.get('browser', {})
            os_info = device_info.get('os', {})
            
            ticket.CreatedFromDevice = device_info.get('device_type', 'unknown')
            ticket.CreatedFromBrowser = f"{browser_info.get('family', 'Unknown')} {browser_info.get('version_string', '')}"
            ticket.CreatedFromOS = f"{os_info.get('family', 'Unknown')} {os_info.get('version_string', '')}"
            ticket.CreatedFromIP = device_info.get('ip_address')
            ticket.UserAgent = device_info.get('user_agent', 'Unknown')
            
            logger.info(f"Updated ticket {ticket.TicketID} with device info: {device_info.get('device_type')}")
    except Exception as e:
        logger.error(f"Error updating ticket with device info: {e}")

def get_device_info_display_for_admin(ticket):
    """Get formatted device info for display in admin UI"""
    try:
        device_type = getattr(ticket, 'CreatedFromDevice', 'Unknown')
        browser = getattr(ticket, 'CreatedFromBrowser', 'Unknown')
        os = getattr(ticket, 'CreatedFromOS', 'Unknown')
        ip = getattr(ticket, 'CreatedFromIP', 'Unknown')
        
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
        warnings = []
        
        if device_type == 'bot':
            risk_level = 'high'
            risk_color = 'red'
            warnings.append('Bot detected')
        elif ip and (ip.startswith('10.') or ip.startswith('192.168.') or ip.startswith('172.')):
            risk_level = 'low'
            risk_color = 'blue'
            warnings.append('Internal network')
        
        if 'Unknown' in browser or 'Unknown' in os:
            warnings.append('Limited device info')
        
        return {
            'device_type': device_type,
            'browser': browser,
            'os': os,
            'ip_address': ip,
            'device_icon': device_icon,
            'risk_level': risk_level,
            'risk_color': risk_color,
            'warnings': warnings,
            'display_text': f"{device_icon} {device_type.title()} | {browser} | {os}",
            'admin_summary': f"Device: {device_type.title()}, Browser: {browser}, OS: {os}, IP: {ip}"
        }
    except Exception as e:
        logger.error(f"Error formatting device info display: {e}")
        return {
            'device_type': 'Unknown',
            'browser': 'Unknown',
            'os': 'Unknown',
            'ip_address': 'Unknown',
            'device_icon': '❓',
            'risk_level': 'unknown',
            'risk_color': 'gray',
            'warnings': ['Error getting device info'],
            'display_text': '❓ Unknown Device',
            'admin_summary': 'Device information unavailable'
        }

# =============================================================================
# PART 3: MODIFICATIONS TO EXISTING create_ticket() FUNCTION
# =============================================================================

"""
In your existing create_ticket() function around line 942, add this code after:
    logger.info("Creating new ticket...")
    data = request.json
    logger.info(f"Received data: {data}")

ADD THIS:
    # Extract device information from request
    device_info = extract_device_info_from_request()
    logger.info(f"Device info: {device_info.get('device_type')} - {device_info.get('browser', {}).get('family')}")

Then, after creating the user (around the line where you do db.session.flush() for user):
ADD THIS:
    # Update user with device information
    if user:
        update_user_with_device_info(user, device_info)

And after creating the ticket (around the line where you do db.session.flush() for ticket):
ADD THIS:
    # Update ticket with device information
    update_ticket_with_device_info(ticket, device_info)
"""

# =============================================================================
# PART 4: MODIFICATIONS FOR ADMIN TICKET DETAIL VIEW
# =============================================================================

"""
In your get_admin_ticket_details() function, add device info to the returned data.
Around where you build the 'result' dictionary, add:

    # Add device tracking information for admin view
    device_display = get_device_info_display_for_admin(ticket_obj)
    
And then add to the result dictionary:
    'device_info': device_display,
"""

# =============================================================================
# PART 5: NEW ROUTE FOR DEVICE INFO API
# =============================================================================

device_info_route_code = '''
@app.route('/api/device-info', methods=['POST'])
def log_device_info():
    """API endpoint to log device information from client-side"""
    try:
        data = request.json
        if not data:
            return jsonify({'status': 'error', 'message': 'No data provided'}), 400
        
        device_info = extract_device_info_from_request()
        
        # Initialize device tracker
        device_tracker = DeviceTracker(app)
        
        # Log the device information
        device_tracker.log_device_info(
            session_id=data.get('sessionId'),
            user_id=current_user.UserID if current_user.is_authenticated else None,
            event_type=data.get('eventType', 'page_view'),
            page_url=data.get('pageUrl'),
            additional_data=device_info
        )
        
        return jsonify({
            'status': 'success',
            'message': 'Device info logged',
            'device_type': device_info.get('device_type'),
            'session_id': data.get('sessionId')
        })
        
    except Exception as e:
        logger.error(f"Error logging device info: {e}")
        return jsonify({'status': 'error', 'message': 'Failed to log device info'}), 500
'''

print("Device tracking integration code prepared!")
print("\nTo integrate:")
print("1. Add the imports to the top of app.py")
print("2. Add the helper functions to app.py") 
print("3. Modify the create_ticket() function as indicated")
print("4. Modify the get_admin_ticket_details() function as indicated")
print("5. Add the new device info API route")
print("6. Run the device tracking migration to add database fields")
print("7. Update admin templates to display device information")
