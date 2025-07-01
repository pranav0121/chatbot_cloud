import pyodbc
from config import Config

def test_ticket_api_data():
    """Test the data that would be returned by the tickets API"""
    
    try:
        config = Config()
        
        # Create pyodbc connection string for direct database access
        if config.DB_USE_WINDOWS_AUTH:
            connection_string = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={config.DB_SERVER};DATABASE={config.DB_DATABASE};Trusted_Connection=yes;"
        else:
            connection_string = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={config.DB_SERVER};DATABASE={config.DB_DATABASE};UID={config.DB_USERNAME};PWD={config.DB_PASSWORD};"
        
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()
        
        # Query that simulates what the admin tickets API would return
        cursor.execute("""
            SELECT TOP 5
                t.TicketID,
                t.Subject,
                t.Priority,
                t.Status,
                t.EscalationLevel,
                t.Country,
                u.Name as UserName,
                u.Email as UserEmail,
                t.CreatedAt,
                t.EndDate
            FROM Tickets t
            LEFT JOIN Users u ON t.UserID = u.UserID
            ORDER BY t.CreatedAt DESC
        """)
        
        tickets = cursor.fetchall()
        
        print("🎫 Sample API Ticket Data (what would be returned):")
        print("-" * 80)
        
        for ticket in tickets:
            ticket_id, subject, priority, status, escalation, country, user_name, user_email, created_at, end_date = ticket
            
            print(f"ID: {ticket_id}")
            print(f"Subject: {subject}")
            print(f"Priority: {priority}")
            print(f"Status: {status}")
            print(f"Escalation Level: {escalation}")
            print(f"Country: {country}")
            print(f"User: {user_name} ({user_email})")
            print(f"Created: {created_at}")
            print(f"End Date: {end_date}")
            print("-" * 40)
        
        # Test escalation level filtering
        print("\n🔍 Testing Escalation Level Filtering:")
        
        for level in ['normal', 'supervisor', 'admin']:
            cursor.execute("""
                SELECT COUNT(*) FROM Tickets WHERE EscalationLevel = ?
            """, (level,))
            count = cursor.fetchone()[0]
            print(f"  {level.upper()}: {count} tickets")
        
        conn.close()
        print("\n✅ Ticket API data test completed!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_ticket_api_data()
