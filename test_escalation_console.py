#!/usr/bin/env python3
"""
Test escalation with console output to see the full logs
"""

import requests
import json
import sys

def test_escalation_with_logs():
    base_url = "http://127.0.0.1:5000"
    
    print("=== TESTING ESCALATION WITH CONSOLE LOGS ===")
    
    # Use working admin credentials
    creds = {'email': 'admin@youcloudtech.com', 'password': 'admin123'}
    
    session = requests.Session()
    
    # Login
    print("1. Logging in...")
    login_response = session.post(f"{base_url}/auth/admin/login", data=creds, allow_redirects=True)
    print(f"Login status: {login_response.status_code}")
    
    # Test force escalation on a specific ticket
    ticket_id = 51
    print(f"2. Force escalating ticket {ticket_id}...")
    
    escalation_data = {
        'level': 1,
        'comment': 'Console log test escalation'
    }
    
    escalation_response = session.post(
        f"{base_url}/super-admin/api/escalation/force/{ticket_id}",
        json=escalation_data,
        headers={'Content-Type': 'application/json'}
    )
    
    print(f"Escalation response status: {escalation_response.status_code}")
    
    try:
        response_data = escalation_response.json()
        print(f"Escalation response: {json.dumps(response_data, indent=2)}")
    except:
        print(f"Escalation response text: {escalation_response.text}")
    
    print("\nCheck the Flask console for detailed logs showing the escalation process...")

if __name__ == "__main__":
    test_escalation_with_logs()
