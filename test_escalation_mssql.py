import pyodbc
import sys
import os
from config import Config

def test_escalation_levels():
    """Test that escalation levels are properly set and displayed"""
    
    try:
        # Get database configuration
        config = Config()
        
        print(f"Connecting to MSSQL database...")
        
        # Create pyodbc connection string for direct database access
        if config.DB_USE_WINDOWS_AUTH:
            # Windows Authentication
            connection_string = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={config.DB_SERVER};DATABASE={config.DB_DATABASE};Trusted_Connection=yes;"
        else:
            # SQL Server Authentication
            connection_string = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={config.DB_SERVER};DATABASE={config.DB_DATABASE};UID={config.DB_USERNAME};PWD={config.DB_PASSWORD};"
        
        # Connect to MSSQL database
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()
        
        # Check if EscalationLevel column exists
        cursor.execute("""
            SELECT COLUMN_NAME 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_NAME = 'Tickets'
        """)
        columns = [row[0] for row in cursor.fetchall()]
        print(f"Available columns in Tickets table: {columns}")
        
        if 'EscalationLevel' not in columns:
            print("❌ EscalationLevel column not found in Tickets table!")
            return False
        
        # Check escalation level distribution
        cursor.execute("""
            SELECT EscalationLevel, COUNT(*) as count 
            FROM Tickets 
            GROUP BY EscalationLevel
        """)
        escalation_stats = cursor.fetchall()
        
        print("\n📊 Escalation Level Distribution:")
        total_tickets = 0
        for level, count in escalation_stats:
            print(f"  {level}: {count} tickets")
            total_tickets += count
        
        print(f"\nTotal tickets: {total_tickets}")
        
        # Check some sample tickets
        cursor.execute("""
            SELECT TOP 10 TicketID, Subject, Priority, Status, EscalationLevel 
            FROM Tickets 
        """)
        sample_tickets = cursor.fetchall()
        
        print("\n🎫 Sample Tickets with Escalation Levels:")
        for ticket in sample_tickets:
            ticket_id, subject, priority, status, escalation = ticket
            subject_short = subject[:50] + "..." if len(subject) > 50 else subject
            print(f"  ID: {ticket_id} | Priority: {priority} | Status: {status} | Escalation: {escalation}")
            print(f"    Subject: {subject_short}")
        
        # Test escalation level logic
        print("\n🔍 Testing Escalation Level Logic:")
        test_cases = [
            ('critical', 'admin'),
            ('high', 'supervisor'), 
            ('medium', 'normal'),
            ('low', 'normal')
        ]
        
        for priority, expected_escalation in test_cases:
            cursor.execute("""
                SELECT COUNT(*) FROM Tickets 
                WHERE Priority = ? AND EscalationLevel = ?
            """, (priority, expected_escalation))
            count = cursor.fetchone()[0]
            print(f"  Priority '{priority}' -> Escalation '{expected_escalation}': {count} tickets")
        
        # Check users table for country information
        cursor.execute("""
            SELECT COLUMN_NAME 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_NAME = 'Users'
        """)
        user_columns = [row[0] for row in cursor.fetchall()]
        print(f"\n🌍 User table columns: {user_columns}")
        
        if 'Country' in user_columns:
            cursor.execute("""
                SELECT Country, COUNT(*) as count 
                FROM Users 
                GROUP BY Country
            """)
            country_stats = cursor.fetchall()
            print("\n📍 User Country Distribution:")
            for country, count in country_stats:
                print(f"  {country}: {count} users")
        
        # Check tickets table for country information
        if 'Country' in columns:
            cursor.execute("""
                SELECT Country, COUNT(*) as count 
                FROM Tickets 
                GROUP BY Country
            """)
            ticket_country_stats = cursor.fetchall()
            print("\n🎫 Ticket Country Distribution:")
            for country, count in ticket_country_stats:
                print(f"  {country}: {count} tickets")
        
        conn.close()
        print("\n✅ Escalation level and country test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error testing escalation levels: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_escalation_levels()
