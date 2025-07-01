#!/usr/bin/env python3
"""
Device Tracking Module for Chatbot Cloud
Tracks user devices, browsers, and session information for analytics and support
"""

import re
import json
from datetime import datetime
from flask import request, session

# Import db dynamically to avoid circular import
db = None

def init_device_tracker(app):
    """Initialize device tracker with Flask app"""
    global db
    from flask_sqlalchemy import SQLAlchemy
    db = app.extensions['sqlalchemy'].db
    return db

# Simple user agent parsing without external dependencies
class SimpleUserAgentParser:
    """Simple user agent parser that doesn't require external libraries"""
    
    def __init__(self, user_agent_string):
        self.user_agent_string = user_agent_string or ""
        self.ua_lower = self.user_agent_string.lower()
    
    def get_browser_info(self):
        """Extract browser information from user agent"""
        browser_patterns = {
            'chrome': r'chrome/([\d.]+)',
            'firefox': r'firefox/([\d.]+)',
            'safari': r'version/([\d.]+).*safari',
            'edge': r'edge/([\d.]+)',
            'opera': r'opera/([\d.]+)',
            'internet explorer': r'msie ([\d.]+)'
        }
        
        for browser, pattern in browser_patterns.items():
            match = re.search(pattern, self.ua_lower)
            if match:
                return {
                    'family': browser.title(),
                    'version_string': match.group(1),
                    'version': [int(x) for x in match.group(1).split('.') if x.isdigit()]
                }
        
        return {
            'family': 'Unknown',
            'version_string': '0.0',
            'version': [0, 0]
        }
    
    def get_os_info(self):
        """Extract OS information from user agent"""
        os_patterns = {
            'windows': r'windows nt ([\d.]+)',
            'macos': r'mac os x ([\d_]+)',
            'ios': r'os ([\d_]+)',
            'android': r'android ([\d.]+)',
            'linux': r'linux'
        }
        
        for os_name, pattern in os_patterns.items():
            match = re.search(pattern, self.ua_lower)
            if match:
                if len(match.groups()) > 0:
                    version = match.group(1).replace('_', '.')
                    return {
                        'family': os_name.title(),
                        'version_string': version,
                        'version': [int(x) for x in version.split('.') if x.isdigit()]
                    }
                else:
                    return {
                        'family': os_name.title(),
                        'version_string': 'Unknown',
                        'version': [0]
                    }
        
        return {
            'family': 'Unknown',
            'version_string': 'Unknown',
            'version': [0]
        }
    
    @property
    def is_mobile(self):
        """Check if device is mobile"""
        mobile_patterns = [
            'mobile', 'android', 'iphone', 'ipod', 'blackberry',
            'windows phone', 'palm', 'symbian'
        ]
        return any(pattern in self.ua_lower for pattern in mobile_patterns)
    
    @property
    def is_tablet(self):
        """Check if device is tablet"""
        tablet_patterns = ['ipad', 'tablet', 'kindle']
        return any(pattern in self.ua_lower for pattern in tablet_patterns)
    
    @property
    def is_pc(self):
        """Check if device is PC/desktop"""
        return not (self.is_mobile or self.is_tablet)
    
    @property
    def is_bot(self):
        """Check if user agent indicates a bot"""
        bot_patterns = [
            'bot', 'crawler', 'spider', 'scraper', 'curl', 'wget',
            'python-requests', 'googlebot', 'bingbot', 'facebookexternalhit'
        ]
        return any(pattern in self.ua_lower for pattern in bot_patterns)

class DeviceInfo:
    """Device information parser and tracker"""
    
    def __init__(self, user_agent_string=None, ip_address=None):
        self.user_agent_string = user_agent_string or self.get_user_agent()
        self.ip_address = ip_address or self.get_ip_address()
        self.parsed_ua = SimpleUserAgentParser(self.user_agent_string)
        
    @staticmethod
    def get_user_agent():
        """Get user agent from current request"""
        return request.headers.get('User-Agent', 'Unknown')
    
    @staticmethod
    def get_ip_address():
        """Get IP address from current request"""
        # Check for forwarded headers (proxy/load balancer)
        if request.headers.get('X-Forwarded-For'):
            return request.headers.get('X-Forwarded-For').split(',')[0].strip()
        elif request.headers.get('X-Real-IP'):
            return request.headers.get('X-Real-IP')
        else:
            return request.remote_addr
    
    def get_device_type(self):
        """Determine device type"""
        if self.parsed_ua.is_mobile:
            return 'mobile'
        elif self.parsed_ua.is_tablet:
            return 'tablet'
        elif self.parsed_ua.is_pc:
            return 'desktop'
        else:
            return 'unknown'
    
    def get_browser_info(self):
        """Get detailed browser information"""
        return self.parsed_ua.get_browser_info()
    
    def get_os_info(self):
        """Get operating system information"""
        return self.parsed_ua.get_os_info()
    
    def is_bot(self):
        """Check if user agent indicates a bot/crawler"""
        return self.parsed_ua.is_bot
    
    def get_complete_info(self):
        """Get complete device information as dictionary"""
        return {
            'user_agent': self.user_agent_string,
            'ip_address': self.ip_address,
            'device_type': self.get_device_type(),
            'is_mobile': self.parsed_ua.is_mobile,
            'is_tablet': self.parsed_ua.is_tablet,
            'is_pc': self.parsed_ua.is_pc,
            'is_bot': self.is_bot(),
            'browser': self.get_browser_info(),
            'os': self.get_os_info(),
            'timestamp': datetime.utcnow().isoformat()
        }

class DeviceSession:
    """Track device sessions and user interactions"""
    
    @staticmethod
    def start_session(user_id=None):
        """Start a new device session"""
        device_info = DeviceInfo()
        session_id = session.get('session_id') or DeviceSession.generate_session_id()
        
        session_data = {
            'session_id': session_id,
            'user_id': user_id,
            'device_info': device_info.get_complete_info(),
            'started_at': datetime.utcnow().isoformat(),
            'page_views': 1,
            'last_activity': datetime.utcnow().isoformat()
        }
        
        # Store in Flask session
        session['device_session'] = session_data
        session['session_id'] = session_id
        
        return session_data
    
    @staticmethod
    def update_session_activity():
        """Update session with new activity"""
        if 'device_session' in session:
            session['device_session']['last_activity'] = datetime.utcnow().isoformat()
            session['device_session']['page_views'] = session['device_session'].get('page_views', 0) + 1
            session.permanent = True
    
    @staticmethod
    def get_session_info():
        """Get current session information"""
        return session.get('device_session', {})
    
    @staticmethod
    def generate_session_id():
        """Generate unique session ID"""
        import uuid
        return str(uuid.uuid4())
    
    @staticmethod
    def end_session():
        """End current session"""
        if 'device_session' in session:
            session['device_session']['ended_at'] = datetime.utcnow().isoformat()

class DeviceTracker:
    """Main device tracking class for integration with tickets and support"""
    
    @staticmethod
    def track_ticket_creation(ticket_id, user_id=None):
        """Track device info when ticket is created"""
        device_info = DeviceInfo()
        session_info = DeviceSession.get_session_info()
        
        tracking_data = {
            'ticket_id': ticket_id,
            'user_id': user_id,
            'device_info': device_info.get_complete_info(),
            'session_info': session_info,
            'event': 'ticket_created',
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Could store in database if needed
        return tracking_data
    
    @staticmethod
    def track_chat_interaction(ticket_id, message_type='user', user_id=None):
        """Track device info during chat interactions"""
        device_info = DeviceInfo()
        
        tracking_data = {
            'ticket_id': ticket_id,
            'user_id': user_id,
            'device_type': device_info.get_device_type(),
            'browser': device_info.get_browser_info()['family'],
            'os': device_info.get_os_info()['family'],
            'is_mobile': device_info.parsed_ua.is_mobile,
            'message_type': message_type,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        return tracking_data
    
    @staticmethod
    def get_device_compatibility_info():
        """Get device compatibility information for support"""
        device_info = DeviceInfo()
        browser = device_info.get_browser_info()
        os = device_info.get_os_info()
        
        # Define compatibility rules
        compatibility = {
            'websocket_support': True,  # Assume modern browsers support WebSocket
            'file_upload_support': True,
            'notifications_support': True,
            'issues': []
        }
        
        # Check for known compatibility issues
        if browser['family'] == 'Internet Explorer':
            compatibility['issues'].append('Internet Explorer is not fully supported. Please use Chrome, Firefox, or Edge.')
            compatibility['websocket_support'] = False
            
        if device_info.get_device_type() == 'mobile' and browser['family'] == 'Safari':
            compatibility['issues'].append('Some features may be limited on mobile Safari.')
            
        return compatibility
    
    @staticmethod
    def get_support_context():
        """Get device context for support agents"""
        device_info = DeviceInfo()
        session_info = DeviceSession.get_session_info()
        compatibility = DeviceTracker.get_device_compatibility_info()
        
        return {
            'device': {
                'type': device_info.get_device_type(),
                'browser': device_info.get_browser_info(),
                'os': device_info.get_os_info(),
                'is_mobile': device_info.parsed_ua.is_mobile,
                'user_agent': device_info.user_agent_string
            },
            'session': session_info,
            'compatibility': compatibility,
            'ip_address': device_info.ip_address
        }

class DeviceAnalytics:
    """Device analytics and reporting"""
    
    @staticmethod
    def get_device_stats():
        """Get device usage statistics"""
        # This would typically query from a database
        # For now, return sample structure
        return {
            'device_types': {
                'desktop': 60,
                'mobile': 35,
                'tablet': 5
            },
            'browsers': {
                'Chrome': 50,
                'Firefox': 20,
                'Safari': 15,
                'Edge': 10,
                'Other': 5
            },
            'operating_systems': {
                'Windows': 45,
                'Android': 25,
                'iOS': 15,
                'macOS': 10,
                'Linux': 3,
                'Other': 2
            }
        }
    
    @staticmethod
    def get_compatibility_issues():
        """Get common compatibility issues reported"""
        return [
            {
                'browser': 'Internet Explorer',
                'issue': 'WebSocket connection failures',
                'count': 12,
                'solution': 'Recommend upgrading to modern browser'
            },
            {
                'browser': 'Safari Mobile',
                'issue': 'File upload issues',
                'count': 8,
                'solution': 'Use native file picker'
            }
        ]

# Utility functions for template use
def get_current_device_info():
    """Template function to get current device info"""
    device_info = DeviceInfo()
    return device_info.get_complete_info()

def is_mobile_device():
    """Template function to check if current device is mobile"""
    device_info = DeviceInfo()
    return device_info.parsed_ua.is_mobile

def get_browser_name():
    """Template function to get browser name"""
    device_info = DeviceInfo()
    return device_info.get_browser_info()['family']

# Flask integration functions
def init_device_tracking(app):
    """Initialize device tracking with Flask app"""
    
    @app.before_request
    def before_request():
        """Track device info before each request"""
        # Skip for static files and API endpoints that don't need tracking
        if request.endpoint and (
            request.endpoint.startswith('static') or 
            request.path.startswith('/static')
        ):
            return
            
        # Start or update session
        if 'device_session' not in session:
            DeviceSession.start_session()
        else:
            DeviceSession.update_session_activity()
    
    # Add template functions
    app.jinja_env.globals['get_current_device_info'] = get_current_device_info
    app.jinja_env.globals['is_mobile_device'] = is_mobile_device
    app.jinja_env.globals['get_browser_name'] = get_browser_name

# Database model for storing device tracking data (if needed)
# Note: Commented out to avoid circular import. Use migration script instead.
# class DeviceTrackingLog(db.Model):
#     """Device tracking log for persistent storage"""
#     __tablename__ = 'device_tracking_logs'
#     
#     id = db.Column(db.Integer, primary_key=True)
#     session_id = db.Column(db.String(255), nullable=False)
#     user_id = db.Column(db.Integer, db.ForeignKey('Users.UserID'), nullable=True)
    ticket_id = db.Column(db.Integer, db.ForeignKey('Tickets.TicketID'), nullable=True)
    
    # Device information
    device_type = db.Column(db.String(20), nullable=True)  # mobile, tablet, desktop
    browser_name = db.Column(db.String(50), nullable=True)
    browser_version = db.Column(db.String(50), nullable=True)
    os_name = db.Column(db.String(50), nullable=True)
    os_version = db.Column(db.String(50), nullable=True)
    user_agent = db.Column(db.Text, nullable=True)
    ip_address = db.Column(db.String(45), nullable=True)
    
    # Session information
    is_mobile = db.Column(db.Boolean, default=False)
    is_tablet = db.Column(db.Boolean, default=False)
    is_bot = db.Column(db.Boolean, default=False)
    
    # Tracking metadata
    event_type = db.Column(db.String(50), nullable=False)  # page_view, ticket_create, chat_message
    page_url = db.Column(db.String(500), nullable=True)
    referrer = db.Column(db.String(500), nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    session_started_at = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    user = db.relationship('User', backref=db.backref('device_logs', lazy=True))
    ticket = db.relationship('Ticket', backref=db.backref('device_logs', lazy=True))

def log_device_event(event_type, ticket_id=None, user_id=None):
    """Log device event to database"""
    try:
        # Note: Device tracking logging disabled to avoid circular import
        # Use device_migration_standalone.py to create tables and log events
        return True
    except Exception as e:
        print(f"Error logging device event: {e}")
        return False

# Export main classes and functions
__all__ = [
    'DeviceInfo',
    'DeviceSession', 
    'DeviceTracker',
    'DeviceAnalytics',
    'init_device_tracking',
    'log_device_event',
    'get_current_device_info',
    'is_mobile_device',
    'get_browser_name'
]
