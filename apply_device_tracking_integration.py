#!/usr/bin/env python3
"""
Device Tracking Integration Applier
This script fixes the app.py syntax error and applies device tracking integration
"""

import os
import sys
import re
import shutil
from datetime import datetime

def backup_file(filepath):
    """Create a backup of a file"""
    backup_path = f"{filepath}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.copy2(filepath, backup_path)
    print(f"✅ Created backup: {backup_path}")
    return backup_path

def fix_app_syntax_error():
    """Attempt to fix the syntax error in app.py"""
    app_path = "app.py"
    
    if not os.path.exists(app_path):
        print(f"❌ {app_path} not found")
        return False
    
    # Create backup
    backup_path = backup_file(app_path)
    
    try:
        # Read the file with proper encoding
        with open(app_path, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()
        
        # Look for the problematic pattern and fix it
        # Pattern: return jsonify({ ... 'tickets': [], 'offset': 0, 'has_more': False } })
        # Should be: return jsonify({ ... 'tickets': [], 'pagination': { ... } })
        
        problem_pattern = r"(\s+return jsonify\(\{\s*'success': False,\s*'error': 'Failed to fetch tickets',\s*'tickets': \[\],)\s*'offset': 0,\s*'has_more': False\s*\}\s*\}\)"
        
        fixed_pattern = r"\1\n            'pagination': {\n                'total': 0,\n                'limit': 50,\n                'offset': 0,\n                'has_more': False\n            }\n        })"
        
        # Apply the fix
        new_content = re.sub(problem_pattern, fixed_pattern, content, flags=re.MULTILINE | re.DOTALL)
        
        if new_content != content:
            print("🔧 Found and fixed syntax error pattern")
            
            # Write the corrected content
            with open(app_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            # Test if the syntax is now valid
            try:
                compile(new_content, app_path, 'exec')
                print("✅ Syntax error fixed successfully!")
                return True
            except SyntaxError as e:
                print(f"❌ Syntax error still present: Line {e.lineno}: {e.msg}")
                # Restore backup
                shutil.copy2(backup_path, app_path)
                print("🔄 Restored original file")
                return False
        else:
            print("⚠️  Could not find the expected error pattern")
            return False
            
    except Exception as e:
        print(f"❌ Error fixing syntax: {e}")
        # Restore backup
        if os.path.exists(backup_path):
            shutil.copy2(backup_path, app_path)
            print("🔄 Restored original file")
        return False

def add_device_tracking_imports():
    """Add device tracking imports to app.py"""
    app_path = "app.py"
    
    try:
        with open(app_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if imports already exist
        if 'from device_tracker_core import' in content:
            print("✅ Device tracking imports already present")
            return True
        
        # Find the location to add imports (after existing imports)
        import_pattern = r"(from werkzeug\.datastructures import FileStorage\n)"
        
        new_imports = """from werkzeug.datastructures import FileStorage

# Device Tracking Imports
from device_tracker_core import DeviceInfo, DeviceAnalytics
from device_tracker import DeviceTracker

"""
        
        new_content = re.sub(import_pattern, new_imports, content)
        
        if new_content != content:
            with open(app_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print("✅ Added device tracking imports")
            return True
        else:
            print("⚠️  Could not add imports - pattern not found")
            return False
            
    except Exception as e:
        print(f"❌ Error adding imports: {e}")
        return False

def add_device_helper_functions():
    """Add device tracking helper functions to app.py"""
    app_path = "app.py"
    
    helper_functions = '''
# =============================================================================
# Device Tracking Helper Functions
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

'''
    
    try:
        with open(app_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if functions already exist
        if 'def extract_device_info_from_request():' in content:
            print("✅ Device tracking helper functions already present")
            return True
        
        # Find location to add functions (after config setup, before routes)
        pattern = r"(app\.config\['LANGUAGES'\] = \{[^}]+\}\nbabel = Babel\(app\))"
        
        if re.search(pattern, content):
            new_content = re.sub(pattern, f"\\1{helper_functions}", content)
            
            with open(app_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print("✅ Added device tracking helper functions")
            return True
        else:
            print("⚠️  Could not add helper functions - insertion point not found")
            return False
            
    except Exception as e:
        print(f"❌ Error adding helper functions: {e}")
        return False

def main():
    """Main integration function"""
    print("🚀 Device Tracking Integration Applier")
    print("=" * 50)
    
    # Change to correct directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    steps = [
        ("Fix app.py syntax error", fix_app_syntax_error),
        ("Add device tracking imports", add_device_tracking_imports),
        ("Add device helper functions", add_device_helper_functions),
    ]
    
    success_count = 0
    for step_name, step_func in steps:
        print(f"\n🔄 {step_name}...")
        if step_func():
            success_count += 1
        else:
            print(f"❌ Failed: {step_name}")
    
    print(f"\n📊 Results: {success_count}/{len(steps)} steps completed successfully")
    
    if success_count == len(steps):
        print("\n✅ Device tracking integration applied successfully!")
        print("\n🔧 Next manual steps:")
        print("1. Run: python add_device_tracking_migration.py")
        print("2. Modify create_ticket() function to include device tracking")
        print("3. Modify get_admin_ticket_details() to include device info")
        print("4. Add device info template to admin UI")
        print("5. Test the integration")
    else:
        print("\n⚠️  Some steps failed. Check the output above and apply manually.")
    
    return success_count == len(steps)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Integration cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)
