#!/usr/bin/env python3
"""
Update SLA breach statuses for existing tickets
"""

import pyodbc
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

def update_sla_breach_statuses():
    """Update SLA breach statuses based on current time"""
    print("🔄 UPDATING SLA BREACH STATUSES")
    print("=" * 40)
    
    conn = get_mssql_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        now = datetime.utcnow()
        
        # Update breached tickets
        cursor.execute("""
            UPDATE Tickets 
            SET SLABreachStatus = 'Breached'
            WHERE SLATarget < ? 
            AND Status IN ('open', 'in_progress', 'escalated')
            AND SLABreachStatus != 'Breached'
        """, (now,))
        
        breached_updated = cursor.rowcount
        print(f"✅ Updated {breached_updated} tickets to 'Breached' status")
        
        # Update approaching breach tickets (within 1 hour)
        approaching_time = now + timedelta(hours=1)
        cursor.execute("""
            UPDATE Tickets 
            SET SLABreachStatus = 'Approaching Breach'
            WHERE SLATarget BETWEEN ? AND ?
            AND Status IN ('open', 'in_progress', 'escalated')
            AND SLABreachStatus = 'Within SLA'
        """, (now, approaching_time))
        
        approaching_updated = cursor.rowcount
        print(f"✅ Updated {approaching_updated} tickets to 'Approaching Breach' status")
        
        # Auto-escalate breached tickets that haven't been escalated yet
        cursor.execute("""
            SELECT TicketID, Priority, EscalationLevel, CurrentAssignedRole
            FROM Tickets 
            WHERE SLABreachStatus = 'Breached'
            AND Status IN ('open', 'in_progress', 'escalated')
            AND (AutoEscalated = 0 OR AutoEscalated IS NULL)
            AND EscalationLevel != 'admin'
        """)
        
        tickets_to_escalate = cursor.fetchall()
        
        for ticket_id, priority, current_level, current_role in tickets_to_escalate:
            # Determine next escalation level
            if current_level == 'normal':
                new_level = 'supervisor'
                new_role = 'supervisor'
                escalated_to = 'supervisor_auto'
            elif current_level == 'supervisor':
                new_level = 'admin'
                new_role = 'admin'
                escalated_to = 'admin_auto'
            else:
                continue  # Already at highest level
            
            # Create escalation history entry
            import json
            escalation_entry = {
                "ticketId": f"TCK-{ticket_id}",
                "escalationLevel": 1 if new_level == 'supervisor' else 2,
                "escalatedTo": escalated_to,
                "escalationReason": "SLA breached - automatic escalation",
                "escalationTimestamp": now.isoformat() + "Z",
                "autoEscalated": True,
                "previousLevel": current_level,
                "previousRole": current_role or 'bot',
                "slaBreach": "Breached"
            }
            
            # Get existing history
            cursor.execute("SELECT EscalationHistory FROM Tickets WHERE TicketID = ?", (ticket_id,))
            existing_history = cursor.fetchone()[0]
            
            if existing_history:
                try:
                    history = json.loads(existing_history)
                except:
                    history = []
            else:
                history = []
            
            history.append(escalation_entry)
            
            # Update the ticket
            cursor.execute("""
                UPDATE Tickets 
                SET EscalationLevel = ?,
                    EscalationReason = 'SLA breached - automatic escalation',
                    EscalationTimestamp = ?,
                    EscalatedTo = ?,
                    AutoEscalated = 1,
                    EscalationHistory = ?,
                    CurrentAssignedRole = ?,
                    Status = CASE WHEN Status = 'open' THEN 'escalated' ELSE Status END
                WHERE TicketID = ?
            """, (new_level, now, escalated_to, json.dumps(history), new_role, ticket_id))
            
            print(f"✅ Auto-escalated ticket #{ticket_id} from {current_level} to {new_level}")
        
        conn.commit()
        
        # Show final statistics
        cursor.execute("""
            SELECT SLABreachStatus, COUNT(*) as count
            FROM Tickets 
            WHERE Status IN ('open', 'in_progress', 'escalated')
            GROUP BY SLABreachStatus
        """)
        
        status_counts = cursor.fetchall()
        print(f"\n📊 Updated SLA Status Distribution:")
        for status, count in status_counts:
            print(f"  {status}: {count} tickets")
        
        # Show escalation distribution
        cursor.execute("""
            SELECT EscalationLevel, COUNT(*) as count
            FROM Tickets 
            WHERE Status IN ('open', 'in_progress', 'escalated')
            GROUP BY EscalationLevel
        """)
        
        escalation_counts = cursor.fetchall()
        print(f"\n🎯 Current Escalation Distribution:")
        for level, count in escalation_counts:
            print(f"  {level}: {count} tickets")
        
        conn.close()
        
        print(f"\n🎉 SLA statuses updated successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error updating SLA statuses: {e}")
        conn.rollback()
        conn.close()
        return False

if __name__ == '__main__':
    update_sla_breach_statuses()
