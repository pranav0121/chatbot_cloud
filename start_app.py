#!/usr/bin/env python3
"""
Start Flask Application with Error Handling
"""

import os
import sys
from datetime import datetime

def start_flask_app():
    """Start Flask application with comprehensive error handling"""
    try:
        print(f"Starting Flask application at {datetime.now()}")
        print("=" * 50)
        
        # Set environment
        os.environ['FLASK_APP'] = 'app.py'
        os.environ['FLASK_ENV'] = 'development'
        
        # Import and run app
        from app import app, socketio
        
        print("✅ App imported successfully")
        print(f"✅ Database configured: {app.config.get('SQLALCHEMY_DATABASE_URI', 'Not set')[:80]}...")
        
        # Start the application
        print("\n🚀 Starting Flask server on http://localhost:5000")
        print("📧 Admin Login: admin@youcloudtech.com / admin123")
        print("🌐 Admin URL: http://localhost:5000/auth/admin/login")
        print("=" * 50)
        
        # Use socketio.run for full functionality
        socketio.run(
            app,
            host='0.0.0.0',
            port=5000,
            debug=True,
            allow_unsafe_werkzeug=True
        )
        
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"\n❌ Error starting Flask app: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = start_flask_app()
    if not success:
        sys.exit(1)
