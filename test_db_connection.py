import pyodbc
import sys

def test_sql_server_connection():
    print("Testing SQL Server connection...")
    
    # Test different connection methods
    connections_to_test = [
        {
            'name': 'Windows Authentication',
            'conn_str': 'DRIVER={SQL Server Native Client 11.0};SERVER=PRANAV\\SQLEXPRESS;Trusted_Connection=yes;'
        },
        {
            'name': 'Windows Authentication (ODBC Driver 17)',
            'conn_str': 'DRIVER={ODBC Driver 17 for SQL Server};SERVER=PRANAV\\SQLEXPRESS;Trusted_Connection=yes;'
        },
        {
            'name': 'Windows Authentication (SQL Server)',
            'conn_str': 'DRIVER={SQL Server};SERVER=PRANAV\\SQLEXPRESS;Trusted_Connection=yes;'
        },
        {
            'name': 'chatbot_user (Native Client 11.0)',
            'conn_str': 'DRIVER={SQL Server Native Client 11.0};SERVER=PRANAV\\SQLEXPRESS;DATABASE=SupportChatbot;UID=chatbot_user;PWD=ChatBot123!;'
        },
        {
            'name': 'chatbot_user (ODBC Driver 17)',
            'conn_str': 'DRIVER={ODBC Driver 17 for SQL Server};SERVER=PRANAV\\SQLEXPRESS;DATABASE=SupportChatbot;UID=chatbot_user;PWD=ChatBot123!;'
        },
        {
            'name': 'sa user (Native Client 11.0)',
            'conn_str': 'DRIVER={SQL Server Native Client 11.0};SERVER=PRANAV\\SQLEXPRESS;DATABASE=SupportChatbot;UID=sa;PWD=YourPassword123;'
        }
    ]
    
    for conn_test in connections_to_test:
        try:
            print(f"\nTesting: {conn_test['name']}")
            print(f"Connection string: {conn_test['conn_str']}")
            
            conn = pyodbc.connect(conn_test['conn_str'], timeout=10)
            cursor = conn.cursor()
            cursor.execute("SELECT @@VERSION")
            version = cursor.fetchone()[0]
            print(f"✓ SUCCESS: {conn_test['name']}")
            print(f"  SQL Server Version: {version[:50]}...")
            cursor.close()
            conn.close()
            
            # If Windows Auth works, try to create the user
            if 'Windows Authentication' in conn_test['name'] and 'ODBC Driver 17' not in conn_test['name']:
                print("\nAttempting to create chatbot_user...")
                try:
                    conn = pyodbc.connect(conn_test['conn_str'])
                    cursor = conn.cursor()
                    
                    # Create login
                    cursor.execute("""
                        IF NOT EXISTS (SELECT name FROM sys.server_principals WHERE name = 'chatbot_user')
                        BEGIN
                            CREATE LOGIN [chatbot_user] WITH PASSWORD = 'ChatBot123!', 
                            CHECK_EXPIRATION = OFF, CHECK_POLICY = OFF
                        END
                    """)
                    
                    # Create database if not exists
                    cursor.execute("""
                        IF NOT EXISTS (SELECT name FROM sys.databases WHERE name = 'SupportChatbot')
                        BEGIN
                            CREATE DATABASE [SupportChatbot]
                        END
                    """)
                    
                    # Switch to the database and create user
                    cursor.execute("USE [SupportChatbot]")
                    cursor.execute("""
                        IF NOT EXISTS (SELECT name FROM sys.database_principals WHERE name = 'chatbot_user')
                        BEGIN
                            CREATE USER [chatbot_user] FOR LOGIN [chatbot_user]
                            ALTER ROLE [db_owner] ADD MEMBER [chatbot_user]
                        END
                    """)
                    
                    conn.commit()
                    print("✓ chatbot_user created successfully")
                    cursor.close()
                    conn.close()
                except Exception as e:
                    print(f"❌ Failed to create user: {str(e)}")
            
        except Exception as e:
            print(f"❌ FAILED: {conn_test['name']}")
            print(f"  Error: {str(e)}")
    
    print("\n" + "="*50)
    print("Available ODBC drivers:")
    try:
        drivers = pyodbc.drivers()
        for driver in drivers:
            if 'SQL Server' in driver:
                print(f"  - {driver}")
    except Exception as e:
        print(f"Error listing drivers: {e}")

if __name__ == "__main__":
    test_sql_server_connection()
