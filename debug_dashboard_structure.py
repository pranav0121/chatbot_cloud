#!/usr/bin/env python3
"""
Debug the escalation dashboard API response structure
"""

import requests
import json

def debug_dashboard_api():
    base_url = "http://127.0.0.1:5000"
    
    print("=== DEBUGGING ESCALATION DASHBOARD API ===")
    
    # Use working admin credentials
    creds = {'email': 'admin@youcloudtech.com', 'password': 'admin123'}
    
    session = requests.Session()
    
    # Login
    print("1. Logging in...")
    login_response = session.post(f"{base_url}/auth/admin/login", data=creds, allow_redirects=True)
    print(f"Login status: {login_response.status_code}")
    
    # Get dashboard data
    print("2. Getting escalation dashboard data...")
    dashboard_response = session.get(f"{base_url}/super-admin/api/escalation/dashboard")
    print(f"Dashboard API status: {dashboard_response.status_code}")
    
    if dashboard_response.status_code == 200:
        try:
            dashboard_data = dashboard_response.json()
            print(f"Dashboard data type: {type(dashboard_data)}")
            print(f"Dashboard data keys: {dashboard_data.keys() if isinstance(dashboard_data, dict) else 'Not a dict'}")
            
            if 'tickets' in dashboard_data:
                tickets = dashboard_data['tickets']
                print(f"Number of tickets: {len(tickets)}")
                
                if tickets:
                    print("\nFirst ticket structure:")
                    first_ticket = tickets[0]
                    print(f"Ticket type: {type(first_ticket)}")
                    if isinstance(first_ticket, dict):
                        for key, value in first_ticket.items():
                            print(f"  {key}: {value}")
                    else:
                        print(f"First ticket: {first_ticket}")
                else:
                    print("No tickets found")
            else:
                print("No 'tickets' key in response")
                
            print(f"\nFull response structure:")
            print(json.dumps(dashboard_data, indent=2, default=str)[:1000])
            
        except Exception as e:
            print(f"Error parsing JSON: {e}")
            print(f"Raw response: {dashboard_response.text[:500]}")
    else:
        print(f"API call failed: {dashboard_response.text}")

if __name__ == "__main__":
    debug_dashboard_api()
