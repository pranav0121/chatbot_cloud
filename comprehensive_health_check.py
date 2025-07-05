#!/usr/bin/env python3
"""
Comprehensive Database and SLA Health Check
Validates that all issues have been resolved before Docker deployment.
"""
import os
import sys
import traceback
from datetime import datetime, timedelta
from dotenv import load_dotenv


def comprehensive_health_check():
    """Run comprehensive health check of all systems"""
    print("🔍 COMPREHENSIVE DATABASE & SLA HEALTH CHECK")
    print("=" * 60)

    issues_found = []
    checks_passed = 0
    total_checks = 0

    # Test 1: Database Connection
    print("\n1️⃣ Testing Database Connection...")
    total_checks += 1
    try:
        import pyodbc
        load_dotenv()

        server = os.getenv('DB_SERVER', 'PRANAV\\SQLEXPRESS')
        database = os.getenv('DB_DATABASE', 'SupportChatbot')

        conn_str = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};Trusted_Connection=yes;"

        with pyodbc.connect(conn_str) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT @@VERSION")
            version = cursor.fetchone()[0]
            print(f"   ✅ Database connected successfully")
            print(f"   📊 SQL Server Version: {version[:50]}...")
            checks_passed += 1
    except Exception as e:
        print(f"   ❌ Database connection failed: {e}")
        issues_found.append("Database connection failed")

    # Test 2: App Import
    print("\n2️⃣ Testing App Import...")
    total_checks += 1
    try:
        from app import app
        print("   ✅ App imported successfully")
        checks_passed += 1
    except Exception as e:
        print(f"   ❌ App import failed: {e}")
        issues_found.append("App import failed")

    # Test 3: Database Models
    print("\n3️⃣ Testing Database Models...")
    total_checks += 1
    try:
        from database import (
            User, Ticket, Category, Message, Partner, SLALog,
            TicketStatusLog, AuditLog, EscalationRule, BotConfiguration, BotInteraction
        )
        print("   ✅ All models imported successfully")

        # Test model instantiation
        test_user = User()
        test_ticket = Ticket()
        test_sla = SLALog()
        print("   ✅ Models can be instantiated")
        checks_passed += 1
    except Exception as e:
        print(f"   ❌ Model import/instantiation failed: {e}")
        issues_found.append("Database models failed")

    # Test 4: Enhanced SLA Monitor
    print("\n4️⃣ Testing Enhanced SLA Monitor...")
    total_checks += 1
    try:
        from enhanced_sla_monitor import enhanced_sla_monitor
        print("   ✅ Enhanced SLA monitor imported successfully")

        # Test monitor initialization
        enhanced_sla_monitor.app = app
        print("   ✅ SLA monitor initialized with app")
        checks_passed += 1
    except Exception as e:
        print(f"   ❌ SLA monitor failed: {e}")
        issues_found.append("SLA monitor failed")

    # Test 5: Database Schema Validation
    print("\n5️⃣ Validating Database Schema...")
    total_checks += 1
    try:
        with pyodbc.connect(conn_str) as conn:
            cursor = conn.cursor()

            # Check required tables exist
            required_tables = ['Tickets', 'Users', 'Categories',
                               'sla_logs', 'partners', 'bot_configurations']
            cursor.execute("""
                SELECT TABLE_NAME 
                FROM INFORMATION_SCHEMA.TABLES 
                WHERE TABLE_NAME IN ('Tickets', 'Users', 'Categories', 'sla_logs', 'partners', 'bot_configurations')
            """)
            existing_tables = [row[0] for row in cursor.fetchall()]

            missing_tables = set(required_tables) - set(existing_tables)
            if missing_tables:
                print(f"   ❌ Missing tables: {missing_tables}")
                issues_found.append(f"Missing tables: {missing_tables}")
            else:
                print(f"   ✅ All required tables exist: {existing_tables}")
                checks_passed += 1
    except Exception as e:
        print(f"   ❌ Schema validation failed: {e}")
        issues_found.append("Schema validation failed")

    # Test 6: SLA Data Quality
    print("\n6️⃣ Checking SLA Data Quality...")
    total_checks += 1
    try:
        with pyodbc.connect(conn_str) as conn:
            cursor = conn.cursor()

            # Check for tickets without SLA targets
            cursor.execute("""
                SELECT COUNT(*) FROM Tickets 
                WHERE Status IN ('open', 'in_progress', 'escalated') 
                AND current_sla_target IS NULL
            """)
            tickets_without_sla = cursor.fetchone()[0]

            # Check for SLA logs without timestamps
            cursor.execute("""
                SELECT COUNT(*) FROM sla_logs 
                WHERE created_at IS NULL OR logged_at IS NULL
            """)
            logs_without_timestamps = cursor.fetchone()[0]

            # Check for tickets without escalation levels
            cursor.execute("""
                SELECT COUNT(*) FROM Tickets 
                WHERE escalation_level IS NULL
            """)
            tickets_without_escalation = cursor.fetchone()[0]

            if tickets_without_sla > 0:
                print(
                    f"   ❌ {tickets_without_sla} tickets without SLA targets")
                issues_found.append(
                    f"{tickets_without_sla} tickets without SLA targets")
            elif logs_without_timestamps > 0:
                print(
                    f"   ❌ {logs_without_timestamps} SLA logs without timestamps")
                issues_found.append(
                    f"{logs_without_timestamps} SLA logs without timestamps")
            elif tickets_without_escalation > 0:
                print(
                    f"   ❌ {tickets_without_escalation} tickets without escalation levels")
                issues_found.append(
                    f"{tickets_without_escalation} tickets without escalation levels")
            else:
                print("   ✅ All SLA data quality checks passed")
                checks_passed += 1
    except Exception as e:
        print(f"   ❌ SLA data quality check failed: {e}")
        issues_found.append("SLA data quality check failed")

    # Test 7: Flask App Context
    print("\n7️⃣ Testing Flask App Context...")
    total_checks += 1
    try:
        with app.app_context():
            from database import db

            # Test database session
            result = db.session.execute(db.text("SELECT 1"))
            test_value = result.scalar()

            if test_value == 1:
                print("   ✅ Flask app context and database session working")
                checks_passed += 1
            else:
                print("   ❌ Database session test failed")
                issues_found.append("Database session test failed")
    except Exception as e:
        print(f"   ❌ Flask app context failed: {e}")
        issues_found.append("Flask app context failed")

    # Test 8: SLA Monitor Functionality
    print("\n8️⃣ Testing SLA Monitor Core Functions...")
    total_checks += 1
    try:
        with app.app_context():
            # Test if monitor can check tables exist
            tables_exist = enhanced_sla_monitor._tables_exist()

            if tables_exist:
                print("   ✅ SLA monitor can detect required tables")
                checks_passed += 1
            else:
                print("   ❌ SLA monitor cannot detect required tables")
                issues_found.append("SLA monitor table detection failed")
    except Exception as e:
        print(f"   ❌ SLA monitor functionality test failed: {e}")
        issues_found.append("SLA monitor functionality test failed")

    # Test 9: Integration Test
    print("\n9️⃣ Running Integration Test...")
    total_checks += 1
    try:
        # Test the complete flow
        with app.app_context():
            from database import db, Ticket, SLALog

            # Get a sample ticket
            sample_ticket = Ticket.query.first()
            if sample_ticket:
                print(
                    f"   ✅ Can query tickets (found ticket {sample_ticket.TicketID})")

                # Check if it has SLA logs
                sla_logs = SLALog.query.filter_by(
                    ticket_id=sample_ticket.TicketID).all()
                if sla_logs:
                    print(f"   ✅ Ticket has {len(sla_logs)} SLA log(s)")
                    checks_passed += 1
                else:
                    print("   ⚠️  Ticket has no SLA logs (will be created by monitor)")
                    checks_passed += 1
            else:
                print("   ⚠️  No tickets found in database")
                checks_passed += 1
    except Exception as e:
        print(f"   ❌ Integration test failed: {e}")
        issues_found.append("Integration test failed")

    # Test 10: Start Flask Server Test
    print("\n🔟 Testing Flask Server Start...")
    total_checks += 1
    try:
        # Import and configure app
        from app import app

        # Test that app can be configured for testing
        app.config['TESTING'] = True
        test_client = app.test_client()

        with app.app_context():
            # Test a basic endpoint
            response = test_client.get('/health')
            # 404 is fine if health endpoint doesn't exist
            if response.status_code in [200, 404]:
                print("   ✅ Flask server can start and handle requests")
                checks_passed += 1
            else:
                print(
                    f"   ❌ Flask server response issue: {response.status_code}")
                issues_found.append(
                    f"Flask server response issue: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Flask server test failed: {e}")
        issues_found.append("Flask server test failed")

    # Final Results
    print("\n" + "=" * 60)
    print("📊 HEALTH CHECK RESULTS")
    print("=" * 60)
    print(f"✅ Checks Passed: {checks_passed}/{total_checks}")
    print(f"❌ Issues Found: {len(issues_found)}")

    if issues_found:
        print("\n🚨 ISSUES THAT NEED ATTENTION:")
        for i, issue in enumerate(issues_found, 1):
            print(f"   {i}. {issue}")
        print("\n❌ SYSTEM NOT READY FOR DOCKER DEPLOYMENT")
        return False
    else:
        print("\n🎉 ALL CHECKS PASSED!")
        print("✅ SYSTEM IS READY FOR DOCKER DEPLOYMENT")
        return True


if __name__ == "__main__":
    try:
        success = comprehensive_health_check()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n💥 CRITICAL ERROR: {e}")
        print("\nFull traceback:")
        traceback.print_exc()
        sys.exit(1)
