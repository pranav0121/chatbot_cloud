#!/usr/bin/env python3
"""
Create test tickets for deletion testing
"""
import requests
import json

def create_test_tickets():
    """Create a few test tickets"""
    base_url = "http://127.0.0.1:5000"
    
    print("=== Creating Test Tickets for Deletion Testing ===")
    
    test_tickets = [
        {
            "name": "Test User 1",
            "email": "test1@example.com",
            "category_id": 1,
            "subject": "Test Ticket for Deletion - Network Issue",
            "message": "This is a test ticket that can be safely deleted. It's about a network connectivity issue."
        },
        {
            "name": "Test User 2", 
            "email": "test2@example.com",
            "category_id": 1,
            "subject": "Test Ticket for Deletion - Software Bug",
            "message": "This is another test ticket for deletion testing. It reports a software bug that needs fixing."
        },
        {
            "name": "Demo User",
            "email": "demo@example.com", 
            "category_id": 1,
            "subject": "Demo Ticket - Can be Deleted",
            "message": "This is a demonstration ticket that can be safely removed using the new delete feature."
        }
    ]
    
    created_tickets = []
    
    for i, ticket_data in enumerate(test_tickets, 1):
        print(f"\n{i}. Creating test ticket: {ticket_data['subject']}")
        
        try:
            response = requests.post(
                f"{base_url}/api/tickets",
                headers={"Content-Type": "application/json"},
                json=ticket_data
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('status') == 'success':
                    ticket_id = result.get('ticket_id')
                    print(f"   ✅ Created ticket #{ticket_id}")
                    created_tickets.append(ticket_id)
                else:
                    print(f"   ❌ Failed: {result.get('message', 'Unknown error')}")
            else:
                print(f"   ❌ HTTP Error: {response.status_code}")
                print(f"   Response: {response.text}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print(f"\n✅ Successfully created {len(created_tickets)} test tickets")
    if created_tickets:
        print("Ticket IDs created:", created_tickets)
        print("\nYou can now test the delete functionality on these tickets in the admin panel:")
        print("1. Go to http://127.0.0.1:5000/auth/admin/login")
        print("2. Login as admin")
        print("3. Go to the Tickets section")
        print("4. Look for the test tickets and use the delete button (trash icon)")
    
    return created_tickets

if __name__ == "__main__":
    create_test_tickets()
