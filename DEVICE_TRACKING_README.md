# Device Tracking System - Chatbot Cloud

## Overview

The Device Tracking System provides comprehensive device and browser information collection for better support analytics and user experience optimization in the Chatbot Cloud platform.

## Components

### 1. Python Backend (`device_tracker_core.py`)

**Core Classes:**

- `SimpleUserAgentParser`: Parses user agents without external dependencies
- `DeviceInfo`: Collects and analyzes device information
- `DeviceAnalytics`: Provides analytics and compatibility checking

**Features:**

- Browser detection (Chrome, Firefox, Safari, Edge, Opera, IE)
- OS detection (Windows, macOS, iOS, Android, Linux)
- Device type classification (mobile, tablet, desktop)
- Bot detection
- Compatibility issue identification

### 2. JavaScript Frontend (`device-tracker.js`)

**Main Class: `DeviceTracker`**

**Capabilities:**

- Real-time device information collection
- Browser capability detection
- Screen and viewport information
- Network connection details (when available)
- Session tracking
- Event logging
- Compatibility warnings

### 3. Database Integration (`add_device_tracking_migration.py`)

**Database Tables:**

- `device_tracking_logs`: Stores device tracking events
- Enhanced `Users` table with device fields
- Enhanced `Tickets` table with device fields

## Installation & Setup

### 1. Run Migration

```bash
python add_device_tracking_migration.py
```

### 2. Include JavaScript in Templates

```html
<script src="{{ url_for('static', filename='js/device-tracker.js') }}"></script>
```

### 3. Test Functionality

Open the test page:

```
/static/device_tracker_test.html
```

## Usage

### Basic Device Information

```javascript
// Get current device context
const deviceInfo = deviceTracker.getDeviceContext();
console.log(deviceInfo);

// Output example:
{
    deviceType: "desktop",
    browser: { name: "Chrome", version: "91.0.4472.124" },
    os: { name: "Windows", version: "10.0" },
    capabilities: {
        touchSupport: false,
        webSocket: true,
        localStorage: true,
        // ... more capabilities
    },
    screen: { width: 1920, height: 1080, viewport: "1200x800" }
}
```

### Event Tracking

```javascript
// Track page views
deviceTracker.trackPageView("/chat");

// Track chat events
deviceTracker.trackChatEvent("message_sent", { messageId: 123 });

// Track ticket creation
deviceTracker.trackTicketCreation("ticket-456", "category-1");

// Custom event tracking
deviceTracker.trackEvent("custom_event", { data: "value" });
```

### Compatibility Checking

```javascript
// Get compatibility warnings
const warnings = deviceTracker.getCompatibilityWarnings();

// Example output:
[
  {
    type: "warning",
    message: "Some features may be limited on mobile Safari.",
  },
];
```

### Integration with Forms

The system automatically adds device information to forms with the class `chat-form`:

```html
<form class="chat-form" method="post">
  <!-- Your form fields -->
  <!-- Device fields will be automatically added as hidden inputs -->
</form>
```

## Python Integration

### Using Device Info in Flask Routes

```python
from device_tracker_core import DeviceInfo

@app.route('/api/tickets', methods=['POST'])
def create_ticket():
    # Get device info from request
    device_info = DeviceInfo()
    device_context = device_info.get_complete_info()

    # Store device info with ticket
    ticket = Ticket(
        # ... other fields
        CreatedFromDevice=device_context['device_type'],
        CreatedFromBrowser=device_context['browser']['family'],
        CreatedFromOS=device_context['os']['family'],
        UserAgent=device_context['user_agent']
    )
```

### Analytics and Reporting

```python
from device_tracker_core import DeviceAnalytics

# Get device usage statistics
stats = DeviceAnalytics.get_device_stats()

# Get compatibility information
device_info = DeviceInfo(request.headers.get('User-Agent'))
compatibility = DeviceAnalytics.get_compatibility_info(device_info)
```

## Database Schema

### device_tracking_logs Table

```sql
CREATE TABLE device_tracking_logs (
    id INTEGER PRIMARY KEY,
    session_id VARCHAR(255) NOT NULL,
    user_id INTEGER,
    ticket_id INTEGER,
    device_type VARCHAR(20),
    browser_name VARCHAR(50),
    browser_version VARCHAR(50),
    os_name VARCHAR(50),
    os_version VARCHAR(50),
    user_agent TEXT,
    ip_address VARCHAR(45),
    is_mobile BOOLEAN DEFAULT 0,
    is_tablet BOOLEAN DEFAULT 0,
    is_bot BOOLEAN DEFAULT 0,
    event_type VARCHAR(50) NOT NULL,
    page_url VARCHAR(500),
    referrer VARCHAR(500),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    session_started_at DATETIME
);
```

### Enhanced Users Table

```sql
-- Additional fields added to Users table
ALTER TABLE Users ADD COLUMN LastDeviceType VARCHAR(20);
ALTER TABLE Users ADD COLUMN LastBrowser VARCHAR(50);
ALTER TABLE Users ADD COLUMN LastOS VARCHAR(50);
ALTER TABLE Users ADD COLUMN LastIPAddress VARCHAR(45);
ALTER TABLE Users ADD COLUMN IsMobileUser BOOLEAN DEFAULT 0;
```

### Enhanced Tickets Table

```sql
-- Additional fields added to Tickets table
ALTER TABLE Tickets ADD COLUMN CreatedFromDevice VARCHAR(20);
ALTER TABLE Tickets ADD COLUMN CreatedFromBrowser VARCHAR(50);
ALTER TABLE Tickets ADD COLUMN CreatedFromOS VARCHAR(50);
ALTER TABLE Tickets ADD COLUMN CreatedFromIP VARCHAR(45);
ALTER TABLE Tickets ADD COLUMN UserAgent TEXT;
```

## Testing

### Python Tests

```bash
python test_device_tracker.py
```

### Browser Tests

1. Open `/static/device_tracker_test.html`
2. Check device information display
3. Test event tracking buttons
4. Monitor browser console for logs

### Test Results Example

```
=== Testing Device Tracker ===
--- Test 1 ---
User Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36...
Browser: Chrome 91.0.4472.124
OS: Windows 10.0
Mobile: False
Tablet: False
PC: True
Bot: False
Device Type: desktop
Complete Device Info: desktop, Chrome, Windows
WebSocket Support: True
File Upload Support: True
No compatibility issues found
```

## API Endpoints

### Device Tracking Endpoint

```javascript
POST /api/device-tracking
Content-Type: application/json

{
    "eventType": "page_view",
    "sessionId": "session_123456",
    "deviceContext": { /* device info */ },
    "timestamp": "2024-01-01T12:00:00.000Z",
    "data": { /* event-specific data */ }
}
```

## Browser Support

### Fully Supported

- Chrome 60+
- Firefox 55+
- Safari 11+
- Edge 79+

### Limited Support

- Internet Explorer 11 (with warnings)
- Older mobile browsers

### Detected Capabilities

- WebSocket support
- Local Storage support
- Session Storage support
- File API support
- WebRTC support
- Touch support
- Cookie support

## Compatibility Features

### Automatic Detection

- Browser compatibility issues
- Missing features warnings
- Mobile-specific limitations

### User Notifications

```javascript
// Automatically shows warnings for:
// - Internet Explorer users
// - Mobile Safari limitations
// - Missing browser features
// - Disabled cookies
```

## Privacy Considerations

### Data Collected

- Browser type and version
- Operating system
- Screen resolution
- Device type (mobile/tablet/desktop)
- IP address
- User agent string
- Session information

### Data Protection

- No personal information is collected
- Session IDs are anonymized
- Data is used for support and analytics only
- Local storage is used for temporary caching

## Integration Examples

### Chat Widget Integration

```javascript
// Automatically track when chat is opened
document.addEventListener("chatInitialized", function () {
  deviceTracker.trackChatEvent("initialized");
});

// Track ticket creation
document.addEventListener("ticketCreated", function (event) {
  deviceTracker.trackTicketCreation(
    event.detail.ticketId,
    event.detail.categoryId
  );
});
```

### Admin Dashboard Integration

```python
# In admin views, show device information for tickets
@app.route('/admin/ticket/<int:ticket_id>')
def admin_ticket_view(ticket_id):
    ticket = Ticket.query.get(ticket_id)

    device_info = {
        'type': ticket.CreatedFromDevice,
        'browser': ticket.CreatedFromBrowser,
        'os': ticket.CreatedFromOS,
        'user_agent': ticket.UserAgent
    }

    return render_template('admin/ticket.html',
                         ticket=ticket,
                         device_info=device_info)
```

## Troubleshooting

### Common Issues

1. **Device tracker not initializing**

   - Check browser console for errors
   - Ensure device-tracker.js is loaded
   - Verify script placement after DOM ready

2. **Events not being tracked**

   - Check network requests in browser dev tools
   - Verify API endpoint is accessible
   - Check local storage for cached events

3. **Compatibility warnings not showing**
   - Test on different browsers
   - Check console logs
   - Verify warning detection logic

### Debug Commands

```javascript
// Check device tracker status
window.getDeviceInfo();

// View stored events
JSON.parse(localStorage.getItem("device_tracking_events"));

// Check compatibility
deviceTracker.getCompatibilityWarnings();
```

## Performance Considerations

### Minimal Impact

- Lightweight parsing without external dependencies
- Asynchronous event tracking
- Local storage for offline support
- Efficient regex patterns for UA parsing

### Optimization Features

- Event batching (future enhancement)
- Automatic cleanup of old events
- Minimal DOM manipulation
- Lazy loading support

## Future Enhancements

### Planned Features

- Real-time device analytics dashboard
- Advanced compatibility checking
- Performance monitoring integration
- A/B testing based on device types
- Automated support escalation based on device issues

### API Extensions

- Bulk event processing
- Historical analytics queries
- Device-specific feature flags
- Support team notifications
