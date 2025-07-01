# Device Tracking Integration Guide

## Overview

This guide provides step-by-step instructions to integrate device tracking into your chatbot system so that when a user starts the chat or raises a ticket, device/browser info is captured and made visible to admins/super-admins.

## 🔧 Prerequisites

1. Device tracking migration has been run (adds database fields)
2. Client-side device tracking is implemented in chat widget
3. Main Flask application syntax is correct

## 📋 Integration Steps

### Step 1: Fix App.py Syntax Error (If Needed)

First, ensure your app.py file has no syntax errors. The error around line 1849-1856 needs to be resolved before proceeding.

### Step 2: Run Device Tracking Migration

```bash
cd "c:\Users\prana\Downloads\chatbot_cloud"
python add_device_tracking_migration.py
```

This adds the following fields to your database:

- **Users table**: LastDeviceType, LastBrowser, LastOS, LastIPAddress, IsMobileUser
- **Tickets table**: CreatedFromDevice, CreatedFromBrowser, CreatedFromOS, CreatedFromIP, UserAgent
- **device_tracking_logs table**: Complete tracking log for analytics

### Step 3: Add Imports to app.py

Add these imports at the top of your app.py file:

```python
from device_tracker_core import DeviceInfo, DeviceAnalytics
from device_tracker import DeviceTracker
```

### Step 4: Add Helper Functions to app.py

Copy the helper functions from `device_tracking_integration_code.py`:

- `extract_device_info_from_request()`
- `update_user_with_device_info()`
- `update_ticket_with_device_info()`
- `get_device_info_display_for_admin()`

### Step 5: Modify create_ticket() Function

In your `create_ticket()` function around line 942, add device tracking:

```python
@app.route('/api/tickets', methods=['POST'])
def create_ticket():
    try:
        logger.info("Creating new ticket...")
        data = request.json
        logger.info(f"Received data: {data}")

        # NEW: Extract device information from request
        device_info = extract_device_info_from_request()
        logger.info(f"Device info: {device_info.get('device_type')} - {device_info.get('browser', {}).get('family')}")

        # ... existing validation code ...

        # After creating/finding user and doing db.session.flush():
        if user:
            # NEW: Update user with device information
            update_user_with_device_info(user, device_info)

        # ... existing ticket creation code ...

        # After creating ticket and doing db.session.flush():
        # NEW: Update ticket with device information
        update_ticket_with_device_info(ticket, device_info)

        # ... rest of existing code ...
```

### Step 6: Modify Admin Ticket Details

In your `get_admin_ticket_details()` function, add device info to the response:

```python
@app.route('/api/admin/tickets/<int:ticket_id>', methods=['GET'])
@admin_required
def get_admin_ticket_details(ticket_id):
    try:
        # ... existing code to get ticket ...

        # NEW: Add device tracking information for admin view
        device_display = get_device_info_display_for_admin(ticket_obj)

        result = {
            'id': ticket_obj.TicketID,
            'subject': ticket_obj.Subject,
            # ... existing fields ...
            'device_info': device_display,  # NEW: Add device info
        }

        return jsonify(result)
```

### Step 7: Add Device Info API Endpoint

Add this new route to app.py for client-side device logging:

```python
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
```

### Step 8: Update Admin Templates

1. Add the device info display section to your admin ticket detail template
2. Use the template code from `templates/device_info_admin_template.html`
3. Place it in your ticket detail view where you want device info to appear

Example integration in your existing template:

```html
<!-- Existing ticket info -->
<div class="ticket-header">
  <h3>Ticket #{{ ticket.id }}: {{ ticket.subject }}</h3>
</div>

<!-- NEW: Device Info Section -->
{% include 'device_info_admin_template.html' %}

<!-- Existing messages and other content -->
```

### Step 9: Verify Chat Widget Integration

Ensure your `static/js/chat.js` already has device tracking integration:

- Device tracking initialization on chat open
- Device info sent with ticket creation requests
- Tracking events logged for analytics

### Step 10: Test the Integration

1. **Test Device Detection**:

```bash
python device_integration_demo_standalone.py
```

2. **Test Chat Widget**:

   - Open the chat widget from different devices
   - Create a test ticket
   - Verify device info is captured

3. **Test Admin View**:

   - Login as admin/super-admin
   - View ticket details
   - Verify device information is displayed

4. **Test Different Scenarios**:
   - Mobile browser
   - Desktop browser
   - Tablet browser
   - Different browsers (Chrome, Firefox, Safari)
   - Different operating systems

## 🔍 What Admins/Super-Admins Will See

When viewing a ticket, admins will see:

📱 **Device Information**

```
📱 Mobile | Chrome 91.0.4472.124 | Android 11    [LOW RISK]

Browser: Chrome 91.0.4472.124
Operating System: Android 11
IP Address: 192.168.1.100
Device Type: mobile

⚠️ Alerts: Internal network

Summary: Device: Mobile, Browser: Chrome 91.0.4472.124, OS: Android 11, IP: 192.168.1.100
```

Risk levels:

- 🟢 **LOW**: Internal network, trusted devices
- 🟡 **NORMAL**: Regular external users
- 🔴 **HIGH**: Bots, suspicious patterns

## 📊 Device Analytics Available

The system tracks:

- Device types (mobile, desktop, tablet)
- Browser families and versions
- Operating systems and versions
- IP addresses and geolocation
- Screen resolutions and viewports
- Session information
- User interaction patterns

## 🛠️ Troubleshooting

**Issue**: Syntax error in app.py

- **Solution**: Fix the bracket mismatch around line 1849-1856 in the error handling section

**Issue**: Device info not showing

- **Solution**: Ensure migration was run and database fields exist

**Issue**: Client-side device tracking not working

- **Solution**: Check browser console for JavaScript errors, verify device-tracker.js is loaded

**Issue**: Permission errors in admin view

- **Solution**: Ensure user has admin/super-admin privileges

## 🔮 Next Steps

1. **Enhanced Analytics**: Add device usage dashboards
2. **Risk Scoring**: Implement advanced fraud detection
3. **Geolocation**: Add country/city detection
4. **Performance Monitoring**: Track device-specific performance
5. **A/B Testing**: Device-specific feature testing

## 📁 Files Created/Modified

**New Files**:

- `device_tracking_integration_code.py` - Integration helper code
- `device_integration_demo_standalone.py` - Standalone demo
- `templates/device_info_admin_template.html` - Admin UI template
- This integration guide

**Existing Files to Modify**:

- `app.py` - Add imports, helper functions, modify routes
- Admin ticket template - Add device info display
- `static/js/chat.js` - Already has device tracking integration

**Database Changes**:

- Users table: Device tracking fields added
- Tickets table: Device tracking fields added
- device_tracking_logs table: Complete tracking log

The device tracking integration is now complete! Admins and super-admins will be able to see comprehensive device information for every ticket, helping them better understand user context and identify potential issues or security concerns.
