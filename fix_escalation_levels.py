#!/usr/bin/env python3
"""
Script to correct escalation levels for all tickets to ensure proper business logic.
"""

import pyodbc
import sys

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

def fix_escalation_levels():
    """Fix escalation levels to match business logic"""
    print("🔧 FIXING ESCALATION LEVELS")
    print("=" * 40)
    
    conn = get_mssql_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        
        # First, let's see what we have before fixing
        cursor.execute("""
            SELECT Priority, EscalationLevel, COUNT(*) as count
            FROM Tickets 
            GROUP BY Priority, EscalationLevel
            ORDER BY Priority, EscalationLevel
        """)
        
        print("📊 Current state:")
        current_state = cursor.fetchall()
        for priority, escalation, count in current_state:
            priority_name = priority if priority else 'NULL'
            escalation_name = escalation if escalation else 'NULL'
            print(f"  {priority_name} → {escalation_name}: {count} tickets")
        
        # Fix escalation levels according to business logic
        print("\n🔄 Applying corrections...")
        
        # 1. Critical and escalated tickets → admin
        cursor.execute("""
            UPDATE Tickets 
            SET EscalationLevel = 'admin' 
            WHERE Priority IN ('critical', 'escalated')
        """)
        critical_updated = cursor.rowcount
        print(f"  ✅ Critical/Escalated → Admin: {critical_updated} tickets updated")
        
        # 2. High priority tickets → supervisor
        cursor.execute("""
            UPDATE Tickets 
            SET EscalationLevel = 'supervisor' 
            WHERE Priority = 'high'
        """)
        high_updated = cursor.rowcount
        print(f"  ✅ High → Supervisor: {high_updated} tickets updated")
        
        # 3. Medium and low priority tickets → normal
        cursor.execute("""
            UPDATE Tickets 
            SET EscalationLevel = 'normal' 
            WHERE Priority IN ('medium', 'low')
        """)
        normal_updated = cursor.rowcount
        print(f"  ✅ Medium/Low → Normal: {normal_updated} tickets updated")
        
        # 4. Handle NULL priority tickets (set to normal by default)
        cursor.execute("""
            UPDATE Tickets 
            SET EscalationLevel = 'normal',
                Priority = 'medium'
            WHERE Priority IS NULL
        """)
        null_updated = cursor.rowcount
        print(f"  ✅ NULL Priority → Medium/Normal: {null_updated} tickets updated")
        
        # Commit changes
        conn.commit()
        
        # Verify the changes
        print("\n📊 After corrections:")
        cursor.execute("""
            SELECT Priority, EscalationLevel, COUNT(*) as count
            FROM Tickets 
            GROUP BY Priority, EscalationLevel
            ORDER BY Priority, EscalationLevel
        """)
        
        after_state = cursor.fetchall()
        for priority, escalation, count in after_state:
            priority_name = priority if priority else 'NULL'
            escalation_name = escalation if escalation else 'NULL'
            print(f"  {priority_name} → {escalation_name}: {count} tickets")
        
        # Final validation
        cursor.execute("""
            SELECT 
                SUM(CASE WHEN Priority IN ('critical', 'escalated') AND EscalationLevel = 'admin' THEN 1 ELSE 0 END) as correct_admin,
                SUM(CASE WHEN Priority = 'high' AND EscalationLevel = 'supervisor' THEN 1 ELSE 0 END) as correct_supervisor,
                SUM(CASE WHEN Priority IN ('medium', 'low') AND EscalationLevel = 'normal' THEN 1 ELSE 0 END) as correct_normal,
                COUNT(*) as total
            FROM Tickets
        """)
        
        validation = cursor.fetchone()
        correct_total = validation[0] + validation[1] + validation[2]
        total = validation[3]
        
        print(f"\n✅ Final validation:")
        print(f"  Correct admin escalations: {validation[0]}")
        print(f"  Correct supervisor escalations: {validation[1]}")
        print(f"  Correct normal escalations: {validation[2]}")
        print(f"  Total correct: {correct_total}/{total} ({correct_total/total*100:.1f}%)")
        
        conn.close()
        
        if correct_total == total:
            print("\n🎉 All escalation levels are now correctly assigned!")
            return True
        else:
            print(f"\n⚠️  Still have {total - correct_total} tickets with incorrect escalation levels")
            return False
            
    except Exception as e:
        print(f"❌ Error fixing escalation levels: {e}")
        conn.rollback()
        conn.close()
        return False

def main():
    """Main function to fix escalation levels"""
    if fix_escalation_levels():
        print("\n🚀 Escalation levels have been corrected!")
        print("You can now run verify_escalation_complete.py to confirm everything is working.")
    else:
        print("\n❌ Failed to fix all escalation levels. Please check the errors above.")
        sys.exit(1)

if __name__ == '__main__':
    main()
