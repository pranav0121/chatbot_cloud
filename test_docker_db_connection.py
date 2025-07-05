#!/usr/bin/env python3
"""
Test the Docker database connection immediately.
"""
import pyodbc
import os


def test_docker_connection():
    """Test Docker database connection with new credentials."""

    print("🔍 Testing Docker Database Connection...")

    server = "PRANAV\\SQLEXPRESS"  # Local connection for testing
    database = "SupportChatbot"
    username = "dockeruser"
    password = "DockerPass123!"

    # Test local connection first
    conn_str = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password};"

    try:
        print(f"Testing connection: {username}@{server}/{database}")

        with pyodbc.connect(conn_str) as conn:
            cursor = conn.cursor()

            # Test basic connection
            cursor.execute("SELECT @@VERSION")
            version = cursor.fetchone()[0]
            print(f"✅ Connected successfully!")
            print(f"   SQL Server: {version[:80]}...")

            # Test database access
            cursor.execute("SELECT COUNT(*) FROM Tickets")
            ticket_count = cursor.fetchone()[0]
            print(f"✅ Database access confirmed - {ticket_count} tickets")

            # Test SLA logs
            cursor.execute("SELECT COUNT(*) FROM sla_logs")
            sla_count = cursor.fetchone()[0]
            print(f"✅ SLA logs accessible - {sla_count} records")

            # Test specific queries that the app uses
            cursor.execute("""
                SELECT TOP 1 TicketID, Subject, Status, Priority 
                FROM Tickets 
                ORDER BY TicketID
            """)
            ticket = cursor.fetchone()
            print(
                f"✅ Sample ticket query successful - Ticket {ticket[0]}: {ticket[1]}")

            print(f"\\n🎉 ALL DATABASE TESTS PASSED!")
            print(f"✅ Docker connection credentials are working perfectly!")

            return True

    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False


if __name__ == "__main__":
    test_docker_connection()
