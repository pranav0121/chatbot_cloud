#!/usr/bin/env python3
"""
Device Tracking Integration Example
Shows how to integrate device tracking with the existing chatbot system
"""

import sys
import os
from datetime import datetime

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from device_tracker_core import DeviceInfo, DeviceAnalytics

def demo_device_tracking():
    """Demonstrate device tracking functionality"""
    
    print("=" * 60)
    print("🚀 DEVICE TRACKING INTEGRATION DEMO")
    print("=" * 60)
    
    # Simulate different user agents from real users
    real_user_agents = [
        {
            'ua': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'ip': '192.168.1.100',
            'scenario': 'Desktop user creating a ticket'
        },
        {
            'ua': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1',
            'ip': '192.168.1.101',
            'scenario': 'Mobile user chatting with support'
        },
        {
            'ua': 'Mozilla/5.0 (iPad; CPU OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1',
            'ip': '192.168.1.102',
            'scenario': 'Tablet user browsing help articles'
        },
        {
            'ua': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
            'ip': '192.168.1.103',
            'scenario': 'Desktop Firefox user with file upload issue'
        },
        {
            'ua': 'Mozilla/5.0 (compatible; MSIE 11.0; Windows NT 10.0; WOW64; Trident/7.0)',
            'ip': '192.168.1.104',
            'scenario': 'Legacy IE user needing browser upgrade'
        }
    ]
    
    print("\n📊 ANALYZING USER DEVICES AND GENERATING SUPPORT INSIGHTS\n")
    
    for i, user in enumerate(real_user_agents, 1):
        print(f"--- User {i}: {user['scenario']} ---")
        
        # Create device info object
        device_info = DeviceInfo(user['ua'], user['ip'])
        device_data = device_info.get_complete_info()
        
        # Display key information
        print(f"🖥️  Device Type: {device_data['device_type'].upper()}")
        print(f"🌐  Browser: {device_data['browser']['family']} {device_data['browser']['version_string']}")
        print(f"💻  OS: {device_data['os']['family']} {device_data['os']['version_string']}")
        print(f"📱  Mobile: {'Yes' if device_data['is_mobile'] else 'No'}")
        print(f"🤖  Bot: {'Yes' if device_data['is_bot'] else 'No'}")
        print(f"🌍  IP: {user['ip']}")
        
        # Check compatibility and provide support recommendations
        compatibility = DeviceAnalytics.get_compatibility_info(device_info)
        
        if compatibility['issues']:
            print(f"⚠️  Issues Detected:")
            for issue in compatibility['issues']:
                print(f"     • {issue}")
                
            # Provide support recommendations
            if 'Internet Explorer' in device_data['browser']['family']:
                print(f"💡  Support Action: Recommend browser upgrade to Chrome/Firefox/Edge")
                print(f"📞  Priority: HIGH - May need phone support for upgrade assistance")
            elif device_data['device_type'] == 'mobile' and 'Safari' in device_data['browser']['family']:
                print(f"💡  Support Action: Provide mobile-specific troubleshooting steps")
                print(f"📞  Priority: MEDIUM - Mobile Safari feature limitations")
        else:
            print(f"✅  No compatibility issues detected")
            print(f"💡  Support Action: Standard support procedures apply")
            print(f"📞  Priority: NORMAL")
        
        # Simulate ticket creation with device tracking
        ticket_data = simulate_ticket_creation(device_info, user['scenario'])
        print(f"🎫  Ticket Created: #{ticket_data['ticket_id']}")
        print(f"📋  Category: {ticket_data['category']}")
        print(f"⏰  Estimated Resolution: {ticket_data['estimated_resolution']}")
        
        print()
    
    # Show analytics summary
    show_analytics_summary()
    
    # Demonstrate support team insights
    show_support_insights()

def simulate_ticket_creation(device_info, scenario):
    """Simulate creating a ticket with device tracking information"""
    
    device_data = device_info.get_complete_info()
    ticket_id = f"TKT-{datetime.now().strftime('%Y%m%d')}-{abs(hash(scenario)) % 10000:04d}"
    
    # Categorize based on device and scenario
    if 'Internet Explorer' in device_data['browser']['family']:
        category = 'Browser Compatibility'
        estimated_resolution = '2-4 hours (browser upgrade required)'
    elif device_data['device_type'] == 'mobile':
        category = 'Mobile Support'
        estimated_resolution = '1-2 hours'
    elif 'file upload' in scenario.lower():
        category = 'Technical Issues'
        estimated_resolution = '30 minutes - 2 hours'
    else:
        category = 'General Support'
        estimated_resolution = '1-3 hours'
    
    return {
        'ticket_id': ticket_id,
        'category': category,
        'estimated_resolution': estimated_resolution,
        'device_info': device_data,
        'created_at': datetime.now().isoformat()
    }

def show_analytics_summary():
    """Show analytics summary based on sample data"""
    
    print("=" * 60)
    print("📈 DEVICE ANALYTICS SUMMARY")
    print("=" * 60)
    
    stats = DeviceAnalytics.get_device_stats()
    
    print("\n🖥️  Device Types Distribution:")
    for device_type, percentage in stats['device_types'].items():
        print(f"   {device_type.capitalize()}: {percentage}%")
    
    print("\n🌐  Browser Usage:")
    for browser, percentage in stats['browsers'].items():
        print(f"   {browser}: {percentage}%")
    
    print("\n💻  Operating Systems:")
    for os, percentage in stats['operating_systems'].items():
        print(f"   {os}: {percentage}%")
    
    print(f"\n💡  Key Insights:")
    print(f"   • {stats['device_types']['mobile']}% of users are on mobile devices")
    print(f"   • Chrome dominates with {stats['browsers']['Chrome']}% usage")
    print(f"   • Windows users make up {stats['operating_systems']['Windows']}% of traffic")
    print(f"   • Consider mobile-first support approach")

def show_support_insights():
    """Show support team insights and recommendations"""
    
    print("\n=" * 60)
    print("🎯 SUPPORT TEAM INSIGHTS & RECOMMENDATIONS")
    print("=" * 60)
    
    print(f"\n🚨  High Priority Actions:")
    print(f"   1. Create IE upgrade guide for legacy users")
    print(f"   2. Develop mobile Safari troubleshooting checklist") 
    print(f"   3. Test file upload functionality across all browsers")
    print(f"   4. Create device-specific help articles")
    
    print(f"\n📋  Support Process Improvements:")
    print(f"   • Automatically detect browser compatibility issues")
    print(f"   • Route mobile users to mobile-optimized support flow")
    print(f"   • Flag IE users for priority browser upgrade assistance")
    print(f"   • Provide device-specific troubleshooting steps")
    
    print(f"\n🔧  Technical Recommendations:")
    print(f"   • Add browser detection to chat widget")
    print(f"   • Implement device-specific UI adaptations")
    print(f"   • Monitor WebSocket connectivity by device type")
    print(f"   • Track file upload success rates by browser")
    
    print(f"\n📊  Metrics to Track:")
    print(f"   • Resolution time by device type")
    print(f"   • Browser compatibility issue frequency")
    print(f"   • Mobile vs desktop user satisfaction")
    print(f"   • Feature usage across different devices")

def demonstrate_integration_code():
    """Show code examples for integration"""
    
    print("\n=" * 60)
    print("💻 INTEGRATION CODE EXAMPLES")
    print("=" * 60)
    
    print("""
🔗 FLASK ROUTE INTEGRATION:

@app.route('/api/tickets', methods=['POST'])
def create_ticket():
    # Get device info from request headers
    device_info = DeviceInfo()
    device_data = device_info.get_complete_info()
    
    # Create ticket with device information
    ticket = Ticket(
        subject=request.json.get('subject'),
        content=request.json.get('content'),
        created_from_device=device_data['device_type'],
        created_from_browser=device_data['browser']['family'],
        created_from_os=device_data['os']['family'],
        user_agent=device_data['user_agent'],
        created_from_ip=device_info.ip_address
    )
    
    # Check for compatibility issues
    compatibility = DeviceAnalytics.get_compatibility_info(device_info)
    if compatibility['issues']:
        # Set higher priority for compatibility issues
        ticket.priority = 'high'
        ticket.notes = f"Compatibility issues: {', '.join(compatibility['issues'])}"
    
    return jsonify({'ticket_id': ticket.id, 'status': 'created'})

🔗 ADMIN DASHBOARD INTEGRATION:

@app.route('/admin/tickets/<int:ticket_id>')
def admin_ticket_view(ticket_id):
    ticket = Ticket.query.get(ticket_id)
    
    # Show device context to support agent
    device_context = {
        'type': ticket.created_from_device,
        'browser': ticket.created_from_browser, 
        'os': ticket.created_from_os,
        'mobile': ticket.created_from_device == 'mobile',
        'needs_upgrade': 'Internet Explorer' in (ticket.created_from_browser or '')
    }
    
    return render_template('admin/ticket.html', 
                         ticket=ticket,
                         device_context=device_context)

🔗 JAVASCRIPT INTEGRATION:

// In your existing chat.js file:
document.addEventListener('DOMContentLoaded', function() {
    // Initialize device tracking
    if (typeof deviceTracker !== 'undefined') {
        // Track chat widget opening
        document.addEventListener('chatOpened', function() {
            deviceTracker.trackChatEvent('opened');
        });
        
        // Track ticket creation
        document.addEventListener('ticketCreated', function(event) {
            deviceTracker.trackTicketCreation(event.detail.ticketId);
        });
        
        // Add device info to ticket forms
        const forms = document.querySelectorAll('.ticket-form');
        forms.forEach(form => {
            const deviceContext = deviceTracker.getDeviceContext();
            
            // Add hidden fields
            ['deviceType', 'browserName', 'osName'].forEach(field => {
                const input = document.createElement('input');
                input.type = 'hidden';
                input.name = field;
                input.value = deviceContext[field] || 'unknown';
                form.appendChild(input);
            });
        });
    }
});
    """)

if __name__ == "__main__":
    print("🔧 Device Tracking Integration Demo")
    print("This demo shows how the device tracking system works with the chatbot")
    print("Press Enter to start the demo...")
    input()
    
    # Run the main demo
    demo_device_tracking()
    
    # Show integration examples
    demonstrate_integration_code()
    
    print("\n" + "=" * 60)
    print("✅ DEMO COMPLETED!")
    print("=" * 60)
    print("📁 Files created:")
    print("   • device_tracker_core.py - Core Python functionality")
    print("   • device_tracker.py - Full Flask integration")
    print("   • static/js/device-tracker.js - JavaScript client")
    print("   • static/device_tracker_test.html - Test page")
    print("   • add_device_tracking_migration.py - Database migration")
    print("   • DEVICE_TRACKING_README.md - Complete documentation")
    print("\n🚀 Ready for integration into your chatbot system!")
    print("📖 See DEVICE_TRACKING_README.md for detailed instructions")
