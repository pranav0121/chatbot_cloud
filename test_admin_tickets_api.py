#!/usr/bin/env python3
"""
Test script to verify the admin tickets API endpoint
"""

import requests
import json

BASE_URL = "http://127.0.0.1:5001"

def test_admin_tickets_api():
    """Test the /api/admin/tickets endpoint"""
    
    print("Testing /api/admin/tickets endpoint...")
    
    try:
        # Test the API endpoint
        response = requests.get(f"{BASE_URL}/api/admin/tickets", timeout=10)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response Type: {type(data)}")
            print(f"Response Keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
            
            if isinstance(data, dict):
                print(f"Success: {data.get('success', 'N/A')}")
                print(f"Tickets Count: {len(data.get('tickets', []))}")
                print(f"Pagination: {data.get('pagination', 'N/A')}")
                print(f"Filters: {data.get('filters', 'N/A')}")
                
                tickets = data.get('tickets', [])
                if tickets:
                    print(f"\nFirst ticket example:")
                    print(json.dumps(tickets[0], indent=2))
                else:
                    print("No tickets found in response")
            else:
                print(f"Unexpected response format: {data}")
                
        elif response.status_code == 401:
            print("Authentication required - this is expected if admin session is not active")
            print(f"Response: {response.text}")
        else:
            print(f"Error response: {response.text}")
            
    except Exception as e:
        print(f"Error testing API: {e}")

if __name__ == "__main__":
    test_admin_tickets_api()
