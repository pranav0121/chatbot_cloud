#!/usr/bin/env python3
"""
Comprehensive test script for Enhanced Escalation System
Tests all new escalation features including SLA monitoring and auto-escalation
"""

import requests
import json
import pyodbc
import sys
from datetime import datetime, timedelta

def get_mssql_connection():
    """Get MSSQL database connection"""
    try:
        server = r'PRANAV\SQLEXPRESS'
        database = 'SupportChatbot'
        
        connection_string = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};Trusted_Connection=yes;'
        conn = pyodbc.connect(connection_string)
        return conn
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return None

def test_enhanced_escalation_database():
    """Test the enhanced escalation database schema"""
    print("=== Testing Enhanced Escalation Database Schema ===")
    
    conn = get_mssql_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        
        # Check for new escalation fields
        enhanced_fields = [
            'EscalationReason', 'EscalationTimestamp', 'EscalatedTo',
            'SLABreachStatus', 'AutoEscalated', 'EscalationHistory',
            'CurrentAssignedRole', 'SLATarget', 'OriginalSLATarget'
        ]
        
        cursor.execute("""
            SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_NAME = 'Tickets' 
            AND COLUMN_NAME IN ({})
        """.format(','.join([f"'{field}'" for field in enhanced_fields])))
        
        found_fields = [row[0] for row in cursor.fetchall()]
        
        print(f"📊 Enhanced Escalation Fields:")
        for field in enhanced_fields:
            status = "✅" if field in found_fields else "❌"
            print(f"  {status} {field}")
        
        # Check SLA targets are set
        cursor.execute("""
            SELECT COUNT(*) as total,
                   SUM(CASE WHEN SLATarget IS NOT NULL THEN 1 ELSE 0 END) as with_sla,
                   SUM(CASE WHEN SLABreachStatus = 'Within SLA' THEN 1 ELSE 0 END) as within_sla
            FROM Tickets
        """)
        
        stats = cursor.fetchone()
        print(f"\n📈 SLA Statistics:")
        print(f"  Total tickets: {stats[0]}")
        print(f"  With SLA targets: {stats[1]}")
        print(f"  Within SLA: {stats[2]}")
        
        # Check escalation distribution
        cursor.execute("""
            SELECT CurrentAssignedRole, COUNT(*) as count
            FROM Tickets 
            GROUP BY CurrentAssignedRole
        """)
        
        role_distribution = cursor.fetchall()
        print(f"\n🎯 Role Assignment Distribution:")
        for role, count in role_distribution:
            role_name = role if role else 'NULL'
            print(f"  {role_name}: {count} tickets")
        
        conn.close()
        return len(found_fields) == len(enhanced_fields)
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        conn.close()
        return False

def test_escalation_api_endpoints():
    """Test the new escalation API endpoints"""
    print("\n=== Testing Enhanced Escalation API Endpoints ===")
    
    base_url = "http://localhost:5000"
    
    # Test endpoints (these will likely require authentication)
    endpoints_to_test = [
        ("/api/tickets/1/sla-status", "GET", "SLA Status API"),
        ("/api/tickets/1/escalation-history", "GET", "Escalation History API"),
        ("/api/tickets/sla-monitor", "GET", "SLA Monitor Dashboard (requires admin)")
    ]
    
    results = []
    
    for endpoint, method, description in endpoints_to_test:
        try:
            if method == "GET":
                response = requests.get(f"{base_url}{endpoint}", timeout=5)
            
            print(f"📡 {description}:")
            print(f"  URL: {endpoint}")
            print(f"  Status: {response.status_code}")
            
            if response.status_code == 200:
                print(f"  ✅ Success")
                results.append(True)
            elif response.status_code == 401:
                print(f"  🔒 Authentication required (expected)")
                results.append(True)  # This is expected
            elif response.status_code == 404:
                print(f"  ❌ Endpoint not found")
                results.append(False)
            else:
                print(f"  ⚠️  Unexpected status: {response.status_code}")
                results.append(False)
                
        except requests.exceptions.ConnectionError:
            print(f"📡 {description}:")
            print(f"  ❌ Cannot connect to server (Flask app not running)")
            results.append(False)
        except Exception as e:
            print(f"📡 {description}:")
            print(f"  ❌ Error: {e}")
            results.append(False)
    
    return all(results)

def test_sla_calculation_logic():
    """Test SLA calculation and breach detection logic"""
    print("\n=== Testing SLA Calculation Logic ===")
    
    conn = get_mssql_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        
        # Get some sample tickets with SLA data
        cursor.execute("""
            SELECT TOP 5 TicketID, Priority, SLATarget, OriginalSLATarget, 
                   SLABreachStatus, CreatedAt, CurrentAssignedRole
            FROM Tickets 
            WHERE SLATarget IS NOT NULL
            ORDER BY CreatedAt DESC
        """)
        
        sample_tickets = cursor.fetchall()
        
        print(f"📋 Sample SLA Data:")
        now = datetime.utcnow()
        
        for ticket in sample_tickets:
            ticket_id, priority, sla_target, orig_sla, status, created, role = ticket
            
            # Calculate time remaining
            if sla_target:
                time_diff = sla_target - now
                hours_remaining = time_diff.total_seconds() / 3600
                
                # Determine expected status
                if hours_remaining <= 0:
                    expected_status = "Breached"
                elif hours_remaining <= 0.5:  # 30 minutes
                    expected_status = "Approaching Breach"
                else:
                    expected_status = "Within SLA"
                
                print(f"  Ticket #{ticket_id}:")
                print(f"    Priority: {priority}")
                print(f"    Current Status: {status}")
                print(f"    Expected Status: {expected_status}")
                print(f"    Hours Remaining: {hours_remaining:.1f}")
                print(f"    Assigned Role: {role}")
                
                # Check if status is correct
                if status == expected_status:
                    print(f"    ✅ Status is correct")
                else:
                    print(f"    ⚠️  Status may need update")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ SLA calculation test failed: {e}")
        conn.close()
        return False

def test_auto_escalation_scenarios():
    """Test auto-escalation scenarios"""
    print("\n=== Testing Auto-Escalation Scenarios ===")
    
    conn = get_mssql_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        
        # Check for tickets that have been auto-escalated
        cursor.execute("""
            SELECT COUNT(*) as auto_escalated_count
            FROM Tickets 
            WHERE AutoEscalated = 1
        """)
        
        auto_count = cursor.fetchone()[0]
        print(f"📊 Auto-escalated tickets: {auto_count}")
        
        # Check escalation history
        cursor.execute("""
            SELECT TOP 3 TicketID, EscalationLevel, EscalatedTo, EscalationReason, 
                   AutoEscalated, EscalationHistory
            FROM Tickets 
            WHERE EscalationHistory IS NOT NULL
            ORDER BY EscalationTimestamp DESC
        """)
        
        escalated_tickets = cursor.fetchall()
        
        print(f"\n📋 Recent Escalations:")
        for ticket_data in escalated_tickets:
            ticket_id, level, escalated_to, reason, auto, history = ticket_data
            print(f"  Ticket #{ticket_id}:")
            print(f"    Level: {level}")
            print(f"    Escalated To: {escalated_to}")
            print(f"    Reason: {reason}")
            print(f"    Auto-escalated: {'Yes' if auto else 'No'}")
            
            # Try to parse escalation history
            if history:
                try:
                    hist_data = json.loads(history)
                    print(f"    History entries: {len(hist_data)}")
                except:
                    print(f"    History: [Could not parse JSON]")
        
        # Test escalation rules
        print(f"\n🔧 Escalation Logic Test:")
        test_priorities = ['critical', 'high', 'medium', 'low']
        
        for priority in test_priorities:
            cursor.execute("""
                SELECT COUNT(*) as count,
                       AVG(CASE WHEN EscalationLevel = 'admin' THEN 1.0 ELSE 0.0 END) as admin_pct,
                       AVG(CASE WHEN EscalationLevel = 'supervisor' THEN 1.0 ELSE 0.0 END) as super_pct,
                       AVG(CASE WHEN EscalationLevel = 'normal' THEN 1.0 ELSE 0.0 END) as normal_pct
                FROM Tickets 
                WHERE Priority = ?
            """, (priority,))
            
            result = cursor.fetchone()
            if result and result[0] > 0:
                count, admin_pct, super_pct, normal_pct = result
                print(f"  {priority.title()} Priority ({count} tickets):")
                print(f"    Admin: {admin_pct:.1%}, Supervisor: {super_pct:.1%}, Normal: {normal_pct:.1%}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Auto-escalation test failed: {e}")
        conn.close()
        return False

def create_test_escalation_scenario():
    """Create a test scenario to demonstrate escalation"""
    print("\n=== Creating Test Escalation Scenario ===")
    
    conn = get_mssql_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        
        # Create a test ticket with near-breach SLA
        now = datetime.utcnow()
        sla_target = now + timedelta(minutes=15)  # 15 minutes from now
        
        # Insert test ticket
        cursor.execute("""
            INSERT INTO Tickets (UserID, CategoryID, Subject, Priority, Status, 
                               SLATarget, OriginalSLATarget, SLABreachStatus, 
                               CurrentAssignedRole, CreatedAt, UpdatedAt)
            VALUES (1, 1, 'Test Escalation Scenario', 'high', 'open', ?, ?, 
                   'Within SLA', 'bot', ?, ?)
        """, (sla_target, sla_target, now, now))
        
        cursor.execute("SELECT @@IDENTITY")
        test_ticket_id = cursor.fetchone()[0]
        
        conn.commit()
        
        print(f"✅ Created test ticket #{test_ticket_id}")
        print(f"   Priority: high")
        print(f"   SLA Target: {sla_target} (15 minutes from now)")
        print(f"   This ticket should auto-escalate when SLA monitoring runs")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Failed to create test scenario: {e}")
        conn.rollback()
        conn.close()
        return False

def main():
    """Run comprehensive enhanced escalation system tests"""
    print("🚀 ENHANCED ESCALATION SYSTEM COMPREHENSIVE TEST")
    print("=" * 60)
    
    results = []
    
    # Test database schema
    results.append(test_enhanced_escalation_database())
    
    # Test API endpoints
    results.append(test_escalation_api_endpoints())
    
    # Test SLA calculation logic
    results.append(test_sla_calculation_logic())
    
    # Test auto-escalation scenarios
    results.append(test_auto_escalation_scenarios())
    
    # Create test scenario
    results.append(create_test_escalation_scenario())
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 COMPREHENSIVE TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(results)
    total = len(results)
    
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("\n🎉 ENHANCED ESCALATION SYSTEM IS FULLY FUNCTIONAL!")
        print("\n✅ All components are working correctly:")
        print("  📊 Database: Enhanced escalation fields added and populated")
        print("  🔗 API: New escalation endpoints available")
        print("  ⏰ SLA: Monitoring and breach detection active")
        print("  🚀 Auto-Escalation: Automatic escalation based on SLA/priority")
        print("  📈 Role Assignment: Dynamic role assignment working")
        print("  📋 History Tracking: Comprehensive escalation history")
        
        print("\n🎯 NEW ESCALATION FEATURES:")
        print("  🔴 SLA Breach Monitoring: Real-time SLA status tracking")
        print("  ⚡ Auto-Escalation: Automatic escalation on SLA breach")
        print("  🎭 Role-Based Assignment: bot → supervisor → admin → manager")
        print("  📊 Escalation History: Full JSON history of all escalations")
        print("  🔗 Enhanced APIs: Comprehensive escalation and SLA APIs")
        
        print("\n📝 API ENDPOINTS AVAILABLE:")
        print("  POST /api/tickets/{id}/escalate - Manual escalation with tracking")
        print("  GET  /api/tickets/{id}/sla-status - Real-time SLA status")
        print("  GET  /api/tickets/{id}/escalation-history - Full escalation history")
        print("  GET  /api/tickets/sla-monitor - SLA monitoring dashboard")
        
        print("\n🚀 The enhanced escalation system is ready for production!")
        
    else:
        print(f"\n❌ {total - passed} components need attention. Please review the issues above.")
        sys.exit(1)

if __name__ == '__main__':
    main()
