import requests
import json

def test_admin_api_escalation():
    """Test that admin API includes escalation levels"""
    
    try:
        # Test admin tickets API
        print("🔍 Testing Admin Tickets API...")
        
        # Test admin tickets API (correct endpoint)
        api_url = "http://localhost:5000/api/admin/tickets"
        
        response = requests.get(api_url)
        
        if response.status_code == 200:
            tickets = response.json()
            print(f"✅ Got {len(tickets)} tickets from API")
            
            # Check if tickets include escalation level
            if tickets and len(tickets) > 0:
                first_ticket = tickets[0]
                print(f"\n📄 First ticket structure:")
                for key, value in first_ticket.items():
                    print(f"  {key}: {value}")
                
                if 'escalation_level' in first_ticket:
                    print("\n✅ escalation_level found in API response!")
                    
                    # Count escalation levels in API response
                    escalation_counts = {}
                    for ticket in tickets:
                        level = ticket.get('escalation_level', 'unknown')
                        escalation_counts[level] = escalation_counts.get(level, 0) + 1
                    
                    print(f"\n📊 Escalation levels in API:")
                    for level, count in escalation_counts.items():
                        print(f"  {level}: {count}")
                else:
                    print("\n❌ escalation_level NOT found in API response!")
            else:
                print("❌ No tickets returned from API")
                
        else:
            print(f"❌ API request failed with status: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error testing admin API: {e}")
        import traceback
        traceback.print_exc()

def test_user_tickets_api():
    """Test user tickets endpoint"""
    try:
        print("\n🔍 Testing User Tickets Endpoint...")
        
        # Test with the correct endpoint
        api_url = "http://localhost:5000/my-tickets"
        
        response = requests.get(api_url)
        
        if response.status_code == 200:
            print("✅ My Tickets page loaded successfully")
        else:
            print(f"❌ My Tickets page failed with status: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error testing user tickets: {e}")

if __name__ == "__main__":
    test_admin_api_escalation()
    test_user_tickets_api()
