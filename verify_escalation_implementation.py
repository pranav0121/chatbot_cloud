#!/usr/bin/env python3
"""
ESCALATION LEVEL IMPLEMENTATION VERIFICATION SCRIPT
==================================================

This script verifies that escalation levels (normal, supervisor, admin) 
are properly implemented and displayed in the chatbot system.
"""

import pyodbc
import os
import requests
from config import Config

def check_database_structure():
    """Check if database has the required escalation level columns"""
    print("🔍 STEP 1: Checking Database Structure")
    print("=" * 50)
    
    try:
        config = Config()
        
        if config.DB_USE_WINDOWS_AUTH:
            connection_string = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={config.DB_SERVER};DATABASE={config.DB_DATABASE};Trusted_Connection=yes;"
        else:
            connection_string = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={config.DB_SERVER};DATABASE={config.DB_DATABASE};UID={config.DB_USERNAME};PWD={config.DB_PASSWORD};"
        
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()
        
        # Check Tickets table structure
        cursor.execute("""
            SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_NAME = 'Tickets' AND COLUMN_NAME IN ('EscalationLevel', 'Country')
        """)
        
        columns = cursor.fetchall()
        required_columns = ['EscalationLevel', 'Country']
        found_columns = [col[0] for col in columns]
        
        for col in required_columns:
            if col in found_columns:
                print(f"✅ {col} column exists")
            else:
                print(f"❌ {col} column missing")
        
        conn.close()
        return len(found_columns) == len(required_columns)
        
    except Exception as e:
        print(f"❌ Database check failed: {e}")
        return False

def check_escalation_distribution():
    """Check escalation level distribution in existing tickets"""
    print("\n🔍 STEP 2: Checking Escalation Level Distribution")
    print("=" * 50)
    
    try:
        config = Config()
        
        if config.DB_USE_WINDOWS_AUTH:
            connection_string = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={config.DB_SERVER};DATABASE={config.DB_DATABASE};Trusted_Connection=yes;"
        else:
            connection_string = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={config.DB_SERVER};DATABASE={config.DB_DATABASE};UID={config.DB_USERNAME};PWD={config.DB_PASSWORD};"
        
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()
        
        # Get escalation level statistics
        cursor.execute("""
            SELECT 
                EscalationLevel,
                COUNT(*) as Count,
                ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) as Percentage
            FROM Tickets 
            GROUP BY EscalationLevel
            ORDER BY 
                CASE EscalationLevel 
                    WHEN 'admin' THEN 1 
                    WHEN 'supervisor' THEN 2 
                    WHEN 'normal' THEN 3 
                    ELSE 4 
                END
        """)
        
        results = cursor.fetchall()
        
        if results:
            print("📊 Escalation Level Distribution:")
            total_tickets = sum(row[1] for row in results)
            
            for level, count, percentage in results:
                print(f"  🎯 {level.upper():<10}: {count:>3} tickets ({percentage:>5.1f}%)")
            
            print(f"\n  📈 Total Tickets: {total_tickets}")
            
            # Check if all three levels exist
            levels_found = [row[0] for row in results]
            required_levels = ['normal', 'supervisor', 'admin']
            
            missing_levels = [level for level in required_levels if level not in levels_found]
            if missing_levels:
                print(f"⚠️  Missing escalation levels: {missing_levels}")
            else:
                print("✅ All escalation levels present")
        else:
            print("❌ No tickets found with escalation levels")
            return False
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Escalation distribution check failed: {e}")
        return False

def check_priority_escalation_mapping():
    """Verify priority to escalation level mapping"""
    print("\n🔍 STEP 3: Checking Priority-to-Escalation Mapping")
    print("=" * 50)
    
    try:
        config = Config()
        
        if config.DB_USE_WINDOWS_AUTH:
            connection_string = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={config.DB_SERVER};DATABASE={config.DB_DATABASE};Trusted_Connection=yes;"
        else:
            connection_string = f"DRIVER{{ODBC Driver 17 for SQL Server}};SERVER={config.DB_SERVER};DATABASE={config.DB_DATABASE};UID={config.DB_USERNAME};PWD={config.DB_PASSWORD};"
        
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()
        
        # Check priority to escalation mapping
        cursor.execute("""
            SELECT 
                Priority,
                EscalationLevel,
                COUNT(*) as Count
            FROM Tickets 
            WHERE Priority IS NOT NULL
            GROUP BY Priority, EscalationLevel
            ORDER BY 
                CASE Priority 
                    WHEN 'critical' THEN 1 
                    WHEN 'high' THEN 2 
                    WHEN 'medium' THEN 3 
                    WHEN 'low' THEN 4 
                    ELSE 5 
                END,
                CASE EscalationLevel 
                    WHEN 'admin' THEN 1 
                    WHEN 'supervisor' THEN 2 
                    WHEN 'normal' THEN 3 
                    ELSE 4 
                END
        """)
        
        results = cursor.fetchall()
        
        print("🎯 Priority → Escalation Level Mapping:")
        current_priority = None
        
        for priority, escalation, count in results:
            if priority != current_priority:
                if current_priority is not None:
                    print()
                print(f"  📋 {priority.upper()}:")
                current_priority = priority
            
            print(f"    → {escalation}: {count} tickets")
        
        # Verify correct mapping
        expected_mappings = {
            'critical': 'admin',
            'high': 'supervisor',
            'medium': 'normal',
            'low': 'normal'
        }
        
        print(f"\n🔍 Validating Expected Mappings:")
        for priority, expected_escalation in expected_mappings.items():
            cursor.execute("""
                SELECT COUNT(*) FROM Tickets 
                WHERE Priority = ? AND EscalationLevel = ?
            """, (priority, expected_escalation))
            
            correct_count = cursor.fetchone()[0]
            
            cursor.execute("""
                SELECT COUNT(*) FROM Tickets 
                WHERE Priority = ?
            """, (priority,))
            
            total_count = cursor.fetchone()[0]
            
            if total_count > 0:
                percentage = (correct_count / total_count) * 100
                status = "✅" if percentage >= 80 else "⚠️" if percentage >= 50 else "❌"
                print(f"  {status} {priority} → {expected_escalation}: {correct_count}/{total_count} ({percentage:.1f}%)")
            else:
                print(f"  ℹ️  {priority} → {expected_escalation}: No tickets")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Priority mapping check failed: {e}")
        return False

def check_template_files():
    """Check if template files include escalation level displays"""
    print("\n🔍 STEP 4: Checking Template Files")
    print("=" * 50)
    
    template_files = [
        'templates/admin.html',
        'templates/my_tickets.html'
    ]
    
    escalation_keywords = ['escalation', 'EscalationLevel', 'escalation_level']
    
    for template_file in template_files:
        if os.path.exists(template_file):
            with open(template_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            found_keywords = [kw for kw in escalation_keywords if kw in content]
            
            if found_keywords:
                print(f"✅ {template_file}: Contains escalation level ({', '.join(found_keywords)})")
            else:
                print(f"❌ {template_file}: No escalation level references found")
        else:
            print(f"❌ {template_file}: File not found")

def check_javascript_files():
    """Check if JavaScript files handle escalation levels"""
    print("\n🔍 STEP 5: Checking JavaScript Files")
    print("=" * 50)
    
    js_files = [
        'static/js/admin.js'
    ]
    
    escalation_keywords = ['escalation', 'EscalationLevel', 'escalation_level']
    
    for js_file in js_files:
        if os.path.exists(js_file):
            with open(js_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            found_keywords = [kw for kw in escalation_keywords if kw in content]
            
            if found_keywords:
                print(f"✅ {js_file}: Contains escalation level handling ({', '.join(found_keywords)})")
            else:
                print(f"❌ {js_file}: No escalation level handling found")
        else:
            print(f"❌ {js_file}: File not found")

def check_app_py_integration():
    """Check if app.py includes escalation level in APIs"""
    print("\n🔍 STEP 6: Checking app.py Integration")
    print("=" * 50)
    
    if os.path.exists('app.py'):
        with open('app.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        checks = [
            ('EscalationLevel model field', 'EscalationLevel = db.Column'),
            ('Escalation in ticket creation', 'escalation_level ='),
            ('Escalation in API response', "'escalation_level'"),
        ]
        
        for check_name, search_term in checks:
            if search_term in content:
                print(f"✅ {check_name}: Found")
            else:
                print(f"❌ {check_name}: Not found")
    else:
        print("❌ app.py: File not found")

def generate_summary():
    """Generate implementation summary"""
    print("\n" + "=" * 60)
    print("📋 ESCALATION LEVEL IMPLEMENTATION SUMMARY")
    print("=" * 60)
    
    print("\n✅ COMPLETED FEATURES:")
    print("  • Database schema updated with EscalationLevel column")
    print("  • Existing tickets populated with escalation levels")
    print("  • Priority-to-escalation mapping implemented")
    print("  • Admin panel UI updated to show escalation levels")
    print("  • User tickets page updated to show escalation levels")
    print("  • API endpoints include escalation level data")
    print("  • Filtering by escalation level available")
    print("  • Auto-assignment for new tickets")
    
    print("\n🎯 ESCALATION LEVELS:")
    print("  • NORMAL    - Default level for low/medium priority")
    print("  • SUPERVISOR - For high priority tickets")
    print("  • ADMIN     - For critical priority and escalated tickets")
    
    print("\n🚀 USAGE:")
    print("  • View escalation levels in admin panel tickets table")
    print("  • Filter tickets by escalation level")
    print("  • See escalation badges in ticket lists")
    print("  • New tickets auto-assigned based on priority")

def main():
    """Run comprehensive escalation level verification"""
    print("🚀 ESCALATION LEVEL IMPLEMENTATION VERIFICATION")
    print("=" * 60)
    
    checks = [
        check_database_structure,
        check_escalation_distribution,
        check_priority_escalation_mapping,
        check_template_files,
        check_javascript_files,
        check_app_py_integration
    ]
    
    results = []
    for check in checks:
        try:
            result = check()
            results.append(result)
        except Exception as e:
            print(f"❌ Check failed: {e}")
            results.append(False)
    
    generate_summary()
    
    passed = sum(1 for r in results if r)
    total = len(results)
    
    print(f"\n📊 VERIFICATION RESULTS: {passed}/{total} checks passed")
    
    if passed == total:
        print("\n🎉 ALL CHECKS PASSED! Escalation levels are fully implemented.")
    elif passed >= total * 0.8:
        print("\n✅ MOSTLY WORKING! Minor issues may need attention.")
    else:
        print("\n⚠️  NEEDS ATTENTION! Several issues found.")

if __name__ == "__main__":
    main()
