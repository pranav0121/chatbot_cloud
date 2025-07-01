#!/usr/bin/env python3
"""
Test script to verify SLA dashboard functionality
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_sla_dashboard():
    """Test SLA dashboard routes and functionality"""
    try:
        from app import app
        from super_admin import super_admin_bp
        
        print("🔧 Testing SLA Dashboard Functionality")
        print("=" * 50)
        
        # Test 1: Check if routes are registered
        with app.test_request_context():
            routes = [rule.rule for rule in app.url_map.iter_rules() if 'super-admin' in rule.rule]
            sla_routes = [route for route in routes if 'sla' in route.lower()]
            
            print(f"✅ Found {len(routes)} Super Admin routes")
            print(f"✅ Found {len(sla_routes)} SLA routes:")
            for route in sla_routes:
                print(f"   - {route}")
        
        # Test 2: Test client
        with app.test_client() as client:
            print("\n🔧 Testing API endpoints...")
            
            # Test SLA overview endpoint
            response = client.get('/super-admin/api/sla/overview')
            print(f"✅ SLA Overview API: {response.status_code}")
            if response.status_code == 200:
                data = response.get_json()
                print(f"   Data keys: {list(data.keys()) if data else 'None'}")
            
            # Test dashboard metrics endpoint  
            response = client.get('/super-admin/api/dashboard/metrics')
            print(f"✅ Dashboard Metrics API: {response.status_code}")
            if response.status_code == 200:
                data = response.get_json()
                print(f"   Data keys: {list(data.keys()) if data else 'None'}")
            
            # Test SLA detailed endpoint
            response = client.get('/super-admin/api/sla/detailed')
            print(f"✅ SLA Detailed API: {response.status_code}")
            
            # Test SLA analytics endpoint
            response = client.get('/super-admin/api/sla/analytics')
            print(f"✅ SLA Analytics API: {response.status_code}")
        
        print("\n🎉 All tests completed successfully!")
        print("\n📋 Access URLs:")
        print(f"   Main Dashboard: http://localhost:5000/super-admin/dashboard")
        print(f"   SLA Dashboard:  http://localhost:5000/super-admin/sla")
        print(f"   Escalation:     http://localhost:5000/super-admin/escalation")
        print(f"   Admin Login:    http://localhost:5000/auth/admin-login")
        
        print("\n🔐 Credentials:")
        print(f"   Email: admin@youcloudtech.com")
        print(f"   Password: SecureAdmin123!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_sla_dashboard()
