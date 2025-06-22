import requests
import json
import time

def test_connection():
    print("🔄 Testing Flask app connection...")
    try:
        response = requests.get("http://localhost:5000/api/odoo/test-connection", timeout=10)
        if response.status_code == 200:
            result = response.json()
            print("✅ Flask app is running!")
            print("✅ Odoo connection successful!")
            print(f"📊 Result: {json.dumps(result, indent=2)}")
            return True
        else:
            print(f"❌ Error: Status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Flask app is not running on port 5000")
        return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def test_create_customer():
    print("\n🧪 Testing customer creation...")
    customer_data = {
        "name": f"Test Customer {int(time.time())}",
        "email": f"test{int(time.time())}@example.com",
        "phone": "+1234567890",
        "comment": "Company: Test Company"  # Use comment instead of company field
    }
    
    try:
        response = requests.post(
            "http://localhost:5000/api/odoo/customers",
            json=customer_data,
            timeout=30
        )
        if response.status_code in [200, 201]:  # Accept both 200 and 201
            result = response.json()
            print("✅ Customer created successfully!")
            print(f"📊 Result: {json.dumps(result, indent=2)}")            # Try different ways to get customer ID
            customer_id = (result.get('customer_id') or 
                          result.get('data', {}).get('id') or 
                          result.get('id'))
            if customer_id:
                print(f"📊 Customer ID: {customer_id}")
                return customer_id
            else:
                print("⚠️ Customer created but ID not found in response")
                return None
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {json.dumps(response.json(), indent=2)}")
            return None
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return None

def test_create_ticket(customer_id):
    if not customer_id:
        print("⏭️ Skipping ticket creation (no customer ID)")
        return
    
    print("\n🧪 Testing ticket creation...")
    ticket_data = {
        "name": f"Test Ticket {int(time.time())}",
        "description": "This is a test ticket created via API",
        "partner_id": customer_id,  # Use partner_id instead of customer_id
        "priority": "1"
    }
    
    try:
        response = requests.post(
            "http://localhost:5000/api/odoo/tickets",
            json=ticket_data,
            timeout=30        )
        if response.status_code in [200, 201]:  # Accept both 200 and 201
            result = response.json()
            print("✅ Ticket created successfully!")
            print(f"📊 Result: {json.dumps(result, indent=2)}")
            # Try different ways to get ticket ID
            ticket_id = (result.get('ticket_id') or 
                        result.get('data', {}).get('id') or 
                        result.get('id'))
            if ticket_id:
                print(f"📊 Ticket ID: {ticket_id}")
                return ticket_id
            else:
                print("⚠️ Ticket created but ID not found in response")
                return None
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return None

def main():
    print("🚀 COMPLETE ODOO INTEGRATION TEST")
    print("=" * 50)
    
    # Test 1: Connection
    if not test_connection():
        print("\n❌ Flask app is not running. Please start it first:")
        print("   python app.py")
        return
    
    # Test 2: Create Customer
    customer_id = test_create_customer()
    
    # Test 3: Create Ticket
    ticket_id = test_create_ticket(customer_id)
    
    # Test 4: List customers    print("\n🧪 Testing customer listing...")
    try:
        response = requests.get("http://localhost:5000/api/odoo/customers?limit=3")
        if response.status_code == 200:
            result = response.json()
            print("✅ Customer listing successful!")
            customers = result.get('customers', [])
            print(f"📊 Found {len(customers)} customers")
            if customers:
                print("📋 Recent customers:")
                for customer in customers[:2]:  # Show first 2
                    print(f"   • {customer.get('name')} (ID: {customer.get('id')})")
        else:
            print(f"❌ Error: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    
    # Test 5: List tickets
    print("\n🧪 Testing ticket listing...")
    try:
        response = requests.get("http://localhost:5000/api/odoo/tickets?limit=3")
        if response.status_code == 200:
            result = response.json()
            print("✅ Ticket listing successful!")
            tickets = result.get('tickets', [])
            print(f"📊 Found {len(tickets)} tickets")
            if tickets:
                print("📋 Recent tickets:")
                for ticket in tickets[:2]:  # Show first 2
                    print(f"   • {ticket.get('name')} (ID: {ticket.get('id')})")
        else:
            print(f"❌ Error: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    
    print("\n" + "=" * 50)
    print("🎯 INTEGRATION TEST COMPLETE!")
    print("\n📋 Verification Steps:")
    print("1. Check Odoo Online for new records:")
    print("   • Customers: https://youcloudpay.odoo.com/web#action=base.action_partner_form")
    print("   • Tickets: https://youcloudpay.odoo.com/web#action=helpdesk.helpdesk_ticket_action_main_tree")
    
    if customer_id and ticket_id:
        print(f"\n✅ SUCCESS: Customer ID {customer_id} and Ticket ID {ticket_id} created!")
        print("🎉 Chatbot ↔ Flask ↔ Odoo Online integration is WORKING!")
    else:
        print("\n⚠️ Some tests failed. Check the errors above.")

if __name__ == "__main__":
    main()
