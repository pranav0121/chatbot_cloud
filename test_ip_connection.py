#!/usr/bin/env python3
"""
Test connection using IP address instead of localhost.
"""
import pyodbc


def test_ip_connection():
    """Test connection using IP address."""

    server = "192.168.0.109\\SQLEXPRESS"
    database = "SupportChatbot"
    username = "dockeruser"
    password = "DockerPass123!"

    conn_str = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password};"

    try:
        print(f"Testing IP-based connection: {username}@{server}")

        with pyodbc.connect(conn_str) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM Tickets")
            count = cursor.fetchone()[0]
            print(f"✅ IP-based connection successful! Found {count} tickets")
            return True

    except Exception as e:
        print(f"❌ IP-based connection failed: {e}")
        return False


if __name__ == "__main__":
    test_ip_connection()
