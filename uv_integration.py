"""
Urban Vyapari Integration Module
Token-based authentication for external API access
"""

import jwt
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify

# Configuration
UV_INTEGRATION_SECRET = "urbanvyapari-chatbot-integration-2024"
UV_API_KEY = "UV_CHATBOT_API_KEY_2024"

def generate_uv_token(admin_info):
    """Generate JWT token for Urban Vyapari admin access"""
    payload = {
        'admin_id': admin_info.get('admin_id'),
        'admin_name': admin_info.get('admin_name'), 
        'admin_email': admin_info.get('admin_email'),
        'source': 'urbanvyapari',
        'permissions': ['read_tickets', 'create_tickets', 'update_tickets', 'read_analytics'],
        'exp': datetime.utcnow() + timedelta(hours=24),  # 24 hours validity
        'iat': datetime.utcnow()
    }
    return jwt.encode(payload, UV_INTEGRATION_SECRET, algorithm='HS256')

def validate_uv_token(token):
    """Validate Urban Vyapari JWT token"""
    try:
        payload = jwt.decode(token, UV_INTEGRATION_SECRET, algorithms=['HS256'])
        
        # Check if token is expired
        if datetime.utcnow().timestamp() > payload.get('exp', 0):
            return None
            
        return payload
    except jwt.InvalidTokenError:
        return None

def uv_auth_required(f):
    """
    Decorator for Urban Vyapari token authentication
    Falls back to regular admin session if no token provided
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check for token in query params or Authorization header
        token = request.args.get('token')
        if not token:
            auth_header = request.headers.get('Authorization', '')
            if auth_header.startswith('Bearer '):
                token = auth_header.replace('Bearer ', '')
        
        if token:
            # Validate Urban Vyapari token
            payload = validate_uv_token(token)
            if payload:
                # Add Urban Vyapari admin info to request
                request.uv_admin = payload
                return f(*args, **kwargs)
            else:
                return jsonify({'error': 'Invalid or expired token'}), 401
        
        # Fall back to regular admin session authentication
        # Import here to avoid circular imports
        from flask import session
        if 'admin_logged_in' not in session:
            return jsonify({'error': 'Authentication required', 'login_url': '/admin/login'}), 401
        
        return f(*args, **kwargs)
    
    return decorated_function

def add_uv_response_metadata(response_data):
    """Add Urban Vyapari source metadata to API responses"""
    if hasattr(request, 'uv_admin'):
        if isinstance(response_data, dict):
            response_data['uv_metadata'] = {
                'accessed_by': request.uv_admin['admin_name'],
                'source': 'urbanvyapari',
                'timestamp': datetime.utcnow().isoformat(),
                'admin_id': request.uv_admin['admin_id']
            }
    return response_data

def validate_uv_api_key(api_key):
    """Validate Urban Vyapari API key"""
    return api_key == UV_API_KEY

def apply_query_filters(query_params):
    """Extract and validate query parameters for filtering"""
    return {
        'status': query_params.get('status', 'all'),
        'priority': query_params.get('priority', 'all'), 
        'category': query_params.get('category', 'all'),
        'organization': query_params.get('organization', 'all'),
        'limit': min(int(query_params.get('limit', 50)), 100),  # Max 100 items
        'offset': int(query_params.get('offset', 0))
    }
