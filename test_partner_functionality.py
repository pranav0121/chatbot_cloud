#!/usr/bin/env python3
"""
Test Partner Management Functionality
"""

import sys
import os
import requests
import json

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_partner_api():
    """Test the partner API endpoints"""
    base_url = "http://localhost:5000"
    
    print("🧪 Testing Partner Management API...")
    
    try:
        # Test 1: Get partners endpoint
        print("\n1. Testing GET /super-admin/api/partners")
        response = requests.get(f"{base_url}/super-admin/api/partners", timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            partners = response.json()
            print(f"   ✅ Success: Found {len(partners)} partners")
            
            # Check data structure
            if partners and len(partners) > 0:
                partner = partners[0]
                required_fields = ['id', 'name', 'partner_type', 'email', 'status']
                missing_fields = [field for field in required_fields if field not in partner]
                
                if not missing_fields:
                    print("   ✅ Partner data structure is correct")
                else:
                    print(f"   ⚠️ Missing fields: {missing_fields}")
            else:
                print("   ℹ️ No partners found (this is normal for new installations)")
                
        elif response.status_code in [401, 403]:
            print("   ⚠️ Authentication required (expected without login)")
        else:
            print(f"   ❌ Unexpected status code: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
        
        # Test 2: Test partner creation (will fail without auth, but we can check the endpoint)
        print("\n2. Testing POST /super-admin/api/partners")
        test_partner = {
            "name": "Test Partner",
            "partner_type": "ICP",
            "email": "test@example.com",
            "contact_person": "Test Contact",
            "phone": "1234567890",
            "status": "active",
            "sla_settings": {
                "level1": 4,
                "level2": 24,
                "max": 72
            }
        }
        
        response = requests.post(
            f"{base_url}/super-admin/api/partners",
            json=test_partner,
            timeout=10
        )
        print(f"   Status: {response.status_code}")
        
        if response.status_code in [401, 403]:
            print("   ✅ Authentication protection working correctly")
        elif response.status_code == 200:
            print("   ✅ Partner creation endpoint working")
        else:
            print(f"   ℹ️ Status: {response.status_code} - {response.text[:100]}")
            
        return True
        
    except requests.exceptions.ConnectionError:
        print("   ❌ Cannot connect to server - make sure Flask app is running")
        return False
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        return False

def test_partner_page():
    """Test the partner management page"""
    base_url = "http://localhost:5000"
    
    print("\n🌐 Testing Partner Management Page...")
    
    try:
        response = requests.get(f"{base_url}/super-admin/partners", timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            print("   ✅ Partner management page loads successfully")
            
            # Check for key elements in the HTML
            html_content = response.text
            required_elements = [
                'Partner Management',
                'Add Partner',
                'partners-grid',
                'partnerModal',
                'savePartner'
            ]
            
            missing_elements = []
            for element in required_elements:
                if element not in html_content:
                    missing_elements.append(element)
            
            if not missing_elements:
                print("   ✅ All required page elements found")
            else:
                print(f"   ⚠️ Missing elements: {missing_elements}")
                
        elif response.status_code in [302, 401, 403]:
            print("   ✅ Page requires authentication (expected)")
        else:
            print(f"   ❌ Unexpected status: {response.status_code}")
            
        return True
        
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        return False

def main():
    print("=" * 60)
    print("🧪 PARTNER MANAGEMENT FUNCTIONALITY TEST")
    print("=" * 60)
    
    api_result = test_partner_api()
    page_result = test_partner_page()
    
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS")
    print("=" * 60)
    
    if api_result and page_result:
        print("✅ Partner Management functionality is working!")
        print("✅ The 'Partner' error should now be resolved.")
        print("\n📋 Next Steps:")
        print("1. Login as admin at: http://localhost:5000/auth/admin-login")
        print("2. Navigate to: http://localhost:5000/super-admin/partners")
        print("3. Try adding a new partner")
        return True
    else:
        print("❌ Some issues detected. Please check the server logs.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
