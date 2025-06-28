"""
Urban Vyapari Integration Setup and Test Script
This script helps you set up and test the Urban Vyapari integration features.
"""

import requests
import json
import sys

def test_uv_integration():
    """Test Urban Vyapari integration endpoints"""
    
    base_url = "http://localhost:5000"
    
    print("🎫 Testing Urban Vyapari Integration")
    print("=" * 50)
    
    # Test 1: Generate Access Token
    print("\n1. Testing Token Generation...")
    
    token_data = {
        "uv_api_key": "UV_CHATBOT_API_KEY_2024",
        "admin_id": "uv_admin_001",
        "admin_name": "Test Admin",
        "admin_email": "admin@urbanvyapari.com"
    }
    
    try:
        response = requests.post(f"{base_url}/api/generate-uv-token", json=token_data)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                token = result['access_token']
                print(f"✅ Token generated successfully!")
                print(f"   Token: {token[:20]}...")
                print(f"   Expires in: {result['expires_in']} seconds")
                
                # Test 2: Use Token to Access Tickets API
                print("\n2. Testing Tickets API with Token...")
                
                tickets_response = requests.get(f"{base_url}/api/admin/tickets?token={token}")
                
                if tickets_response.status_code == 200:
                    tickets_data = tickets_response.json()
                    if tickets_data.get('success'):
                        print(f"✅ Tickets API working!")
                        print(f"   Found {len(tickets_data.get('tickets', []))} tickets")
                        if tickets_data.get('uv_metadata'):
                            print(f"   Accessed by: {tickets_data['uv_metadata']['accessed_by']}")
                    else:
                        print(f"❌ Tickets API error: {tickets_data}")
                else:
                    print(f"❌ Tickets API failed: {tickets_response.status_code}")
                
                # Test 3: Use Token to Access Dashboard Stats
                print("\n3. Testing Dashboard Stats API with Token...")
                
                stats_response = requests.get(f"{base_url}/api/admin/dashboard-stats?token={token}")
                
                if stats_response.status_code == 200:
                    stats_data = stats_response.json()
                    if stats_data.get('success'):
                        print(f"✅ Dashboard Stats API working!")
                        print(f"   Total Tickets: {stats_data.get('totalTickets', 0)}")
                        print(f"   Open Tickets: {stats_data.get('pendingTickets', 0)}")
                        if stats_data.get('uv_metadata'):
                            print(f"   Accessed by: {stats_data['uv_metadata']['accessed_by']}")
                    else:
                        print(f"❌ Dashboard Stats error: {stats_data}")
                else:
                    print(f"❌ Dashboard Stats failed: {stats_response.status_code}")
                
                # Test 4: Web Portal Access
                print("\n4. Testing Web Portal Access...")
                
                portal_url = f"{base_url}/tickets-portal?token={token}&status=open"
                portal_response = requests.get(portal_url)
                
                if portal_response.status_code == 200:
                    print(f"✅ Web Portal accessible!")
                    print(f"   URL: {portal_url}")
                    print(f"   Portal loaded successfully")
                else:
                    print(f"❌ Web Portal failed: {portal_response.status_code}")
                
                print("\n" + "=" * 50)
                print("🎉 Integration Test Results:")
                print(f"   • Token Generation: ✅")
                print(f"   • Tickets API: ✅")
                print(f"   • Dashboard API: ✅") 
                print(f"   • Web Portal: ✅")
                print("\n🔗 Ready for Urban Vyapari Integration!")
                
                return True
                
            else:
                print(f"❌ Token generation failed: {result}")
                return False
        else:
            print(f"❌ Token generation request failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Flask app. Make sure it's running on http://localhost:5000")
        return False
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False

def generate_integration_guide():
    """Generate integration guide for Urban Vyapari team"""
    
    guide = """
# Urban Vyapari Integration Guide

## 🔧 Quick Setup

### 1. API Key Configuration
```javascript
const UV_API_KEY = "UV_CHATBOT_API_KEY_2024";
const CHATBOT_URL = "http://localhost:5000";
```

### 2. Get Access Token
```javascript
async function getAccessToken(adminId, adminName, adminEmail) {
    const response = await fetch(`${CHATBOT_URL}/api/generate-uv-token`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            uv_api_key: UV_API_KEY,
            admin_id: adminId,
            admin_name: adminName,
            admin_email: adminEmail
        })
    });
    
    const data = await response.json();
    return data.success ? data.access_token : null;
}
```

### 3. Use Token for API Calls
```javascript
// Get tickets with filters
const tickets = await fetch(`${CHATBOT_URL}/api/admin/tickets?token=${token}&status=open&priority=high`);

// Get dashboard stats
const stats = await fetch(`${CHATBOT_URL}/api/admin/dashboard-stats?token=${token}`);
```

### 4. Open Web Portal
```javascript
function openTicketsPortal(token) {
    const url = `${CHATBOT_URL}/tickets-portal?token=${token}&status=open`;
    window.open(url, '_blank');
}
```

## 📋 Available Endpoints

1. **Token Generation:** `POST /api/generate-uv-token`
2. **Tickets API:** `GET /api/admin/tickets?token=TOKEN`
3. **Dashboard Stats:** `GET /api/admin/dashboard-stats?token=TOKEN`
4. **Web Portal:** `GET /tickets-portal?token=TOKEN`

## 🔍 Query Parameters

- `status=all|open|closed|pending|resolved`
- `priority=all|low|medium|high|critical`
- `category=all|technical|billing|feature|bug`
- `limit=50` (max 100)
- `offset=0`

## ✅ Integration Checklist

- [ ] API key configured
- [ ] Token generation working
- [ ] Tickets API accessible
- [ ] Dashboard stats working
- [ ] Web portal loading
- [ ] Menu item added to Urban Vyapari admin panel

## 🔐 Security Notes

- Tokens expire after 24 hours
- Use HTTPS in production
- Store tokens securely
- Regenerate tokens when needed

## 📞 Support

For integration support, contact the chatbot development team.
"""
    
    with open('URBAN_VYAPARI_INTEGRATION_GUIDE.md', 'w', encoding='utf-8') as f:
        f.write(guide)
    
    print("📄 Integration guide saved to: URBAN_VYAPARI_INTEGRATION_GUIDE.md")

if __name__ == "__main__":
    print("🚀 Urban Vyapari Integration Setup")
    print("=" * 50)
    
    if len(sys.argv) > 1 and sys.argv[1] == "guide":
        generate_integration_guide()
    else:
        print("Starting integration test...")
        print("Make sure your Flask app is running on http://localhost:5000")
        input("Press Enter to continue...")
        
        success = test_uv_integration()
        
        if success:
            print("\n📋 Next Steps:")
            print("1. Share the API key 'UV_CHATBOT_API_KEY_2024' with Urban Vyapari team")
            print("2. Provide them the integration guide")
            print("3. Help them add the tickets menu to their admin panel")
            
            generate_integration_guide()
        else:
            print("\n❌ Integration test failed. Please check your setup.")
