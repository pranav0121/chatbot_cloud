#!/usr/bin/env python3
"""
Test script for ticket deletion functionality
"""
import requests
import json

def test_delete_ticket_api():
    """Test the delete ticket API endpoint"""
    base_url = "http://127.0.0.1:5000"
    
    print("=== Testing Ticket Deletion API ===")
    
    # First, let's get the list of tickets to see what we have
    print("1. Getting current tickets...")
    try:
        response = requests.get(f"{base_url}/api/admin/tickets")
        if response.status_code == 200:
            tickets = response.json()
            print(f"   Found {len(tickets)} tickets")
            
            if tickets:
                print("   Sample tickets:")
                for i, ticket in enumerate(tickets[:3]):  # Show first 3 tickets
                    print(f"   - Ticket #{ticket['id']}: {ticket['subject']}")
                
                # Test deletion of the first ticket (if available)
                if len(tickets) > 0:
                    test_ticket_id = tickets[0]['id']
                    print(f"\n2. Testing deletion of ticket #{test_ticket_id}...")
                    
                    # Note: This test would require admin authentication
                    # For now, just show what the request would look like
                    print(f"   DELETE request would be sent to: {base_url}/api/admin/tickets/{test_ticket_id}")
                    print("   (Skipping actual deletion to preserve data)")
                    
                    # Uncomment the following lines to actually test deletion:
                    # delete_response = requests.delete(f"{base_url}/api/admin/tickets/{test_ticket_id}")
                    # print(f"   Delete response status: {delete_response.status_code}")
                    # if delete_response.status_code == 200:
                    #     result = delete_response.json()
                    #     print(f"   Success: {result['message']}")
                    # else:
                    #     print(f"   Error: {delete_response.text}")
            else:
                print("   No tickets found to test deletion")
        else:
            print(f"   Error getting tickets: {response.status_code}")
            
    except Exception as e:
        print(f"   Error: {e}")

if __name__ == "__main__":
    test_delete_ticket_api()
