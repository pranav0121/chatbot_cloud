#!/usr/bin/env python3
"""
Quick Route Test
"""
import requests
import sys

def test_routes():
    """Test the critical routes"""
    base_url = "http://127.0.0.1:5000"
    
    routes_to_test = [
        ("/test", "Basic connectivity"),
        ("/super-admin/dashboard", "Super Admin Portal"),
        ("/super-admin/api/partners", "Partner API"),
        ("/auth/admin-login", "Admin Login"),
        ("/chat", "Chat API")
    ]
    
    print("🧪 QUICK ROUTE TEST")
    print("=" * 30)
    
    results = []
    
    for route, description in routes_to_test:
        try:
            if route == "/chat":
                # POST request for chat
                response = requests.post(
                    f"{base_url}{route}",
                    json={"message": "test", "user_id": "test"},
                    timeout=3
                )
            else:
                # GET request for others
                response = requests.get(f"{base_url}{route}", timeout=3)
            
            status = response.status_code
            if status in [200, 302, 401, 403]:
                print(f"✅ {description}: {status}")
                results.append(True)
            else:
                print(f"❌ {description}: {status}")
                results.append(False)
                
        except requests.exceptions.ConnectionError:
            print(f"❌ {description}: Connection Error")
            results.append(False)
        except Exception as e:
            print(f"❌ {description}: {str(e)[:50]}")
            results.append(False)
    
    passed = sum(results)
    total = len(results)
    print(f"\nResults: {passed}/{total} routes working")
    
    if passed >= 4:
        print("🎉 ROUTES ARE WORKING!")
        return True
    else:
        print("⚠️ Some routes need attention")
        return False

if __name__ == "__main__":
    test_routes()
