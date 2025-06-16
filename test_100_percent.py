#!/usr/bin/env python3
"""
Quick Application Test - Verify 100% Working System
"""

import requests
import time
import sys

def test_application():
    """Test all key application endpoints"""
    print("🧪 TESTING 100% WORKING APPLICATION")
    print("=" * 50)
    
    base_url = "http://localhost:5000"
    
    # Test endpoints
    endpoints = [
        ("Main Page", "/"),
        ("User Login", "/auth/login"),
        ("Admin Login", "/auth/admin/login"),
        ("Admin Dashboard", "/admin"),
        ("Super Admin Dashboard", "/super-admin/"),
        ("Super Admin Partners", "/super-admin/partners"),
        ("API Test", "/test"),
    ]
    
    results = []
    
    for name, endpoint in endpoints:
        try:
            url = f"{base_url}{endpoint}"
            response = requests.get(url, timeout=10, allow_redirects=False)
            
            if response.status_code in [200, 302]:
                status = "✅ WORKING"
                color = "green"
            elif response.status_code == 404:
                status = "❌ NOT FOUND"
                color = "red"
            else:
                status = f"⚠️ STATUS {response.status_code}"
                color = "yellow"
                
            print(f"{name:25} | {status} | {url}")
            results.append((name, response.status_code, "OK" if response.status_code in [200, 302] else "ISSUE"))
            
        except requests.ConnectionError:
            print(f"{name:25} | ❌ SERVER NOT RUNNING | {url}")
            results.append((name, "NO_CONNECTION", "ISSUE"))
        except Exception as e:
            print(f"{name:25} | ❌ ERROR: {str(e)[:30]} | {url}")
            results.append((name, "ERROR", "ISSUE"))
    
    print("\n" + "=" * 50)
    print("📊 SUMMARY")
    print("=" * 50)
    
    working = len([r for r in results if r[2] == "OK"])
    total = len(results)
    percentage = (working / total) * 100
    
    print(f"Working endpoints: {working}/{total} ({percentage:.1f}%)")
    
    if percentage == 100:
        print("🎉 APPLICATION IS 100% WORKING!")
        return True
    else:
        print("🔧 ISSUES FOUND - Need fixes")
        
        issues = [r for r in results if r[2] == "ISSUE"]
        print("\n❌ Issues to fix:")
        for name, status, _ in issues:
            print(f"   - {name}: {status}")
        
        return False

def test_admin_login():
    """Test admin login functionality"""
    print("\n🔐 TESTING ADMIN LOGIN")
    print("-" * 30)
    
    try:
        session = requests.Session()
        
        # Get login page
        login_response = session.get("http://localhost:5000/auth/admin/login")
        print(f"Login page: {login_response.status_code}")
        
        if login_response.status_code == 200:
            # Try to login
            login_data = {
                'email': 'admin@youcloudtech.com',
                'password': 'admin123'
            }
            
            post_response = session.post(
                "http://localhost:5000/auth/admin/login",
                data=login_data,
                allow_redirects=False
            )
            
            print(f"Login attempt: {post_response.status_code}")
            
            if post_response.status_code == 302:
                redirect_url = post_response.headers.get('Location', '')
                if 'admin' in redirect_url and 'login' not in redirect_url:
                    print("✅ Admin login WORKING!")
                    return True
                else:
                    print(f"❌ Login failed - redirected to: {redirect_url}")
            else:
                print(f"❌ Login failed - status: {post_response.status_code}")
        
        return False
        
    except Exception as e:
        print(f"❌ Login test error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting comprehensive application test...")
    time.sleep(2)  # Wait for server
    
    app_working = test_application()
    login_working = test_admin_login()
    
    print("\n" + "=" * 50)
    print("🎯 FINAL RESULTS")
    print("=" * 50)
    
    if app_working and login_working:
        print("✅ APPLICATION IS 100% WORKING!")
        print("📧 Admin Email: admin@youcloudtech.com")
        print("🔑 Admin Password: admin123")
        print("🌐 Admin URL: http://localhost:5000/auth/admin/login")
        print("🏆 Super Admin URL: http://localhost:5000/super-admin/")
    else:
        print("❌ APPLICATION NEEDS FIXES")
        if not app_working:
            print("   - Some endpoints not working")
        if not login_working:
            print("   - Admin login not working")
        
    print("\n🎯 Next: Open browser and test manually!")
