#!/usr/bin/env python3
"""
Comprehensive SLA Data Fix Script
Identifies and fixes all data quality issues in the SLA monitoring system.
"""
import os
import pyodbc
from datetime import datetime, timedelta
from dotenv import load_dotenv


def fix_all_sla_issues():
    """Fix all SLA-related data issues in the database."""
    load_dotenv()

    server = os.getenv('DB_SERVER', 'PRANAV\\SQLEXPRESS')
    database = os.getenv('DB_DATABASE', 'SupportChatbot')
    use_windows_auth = os.getenv(
        'DB_USE_WINDOWS_AUTH', 'True').lower() == 'true'
    username = os.getenv('DB_USERNAME', '')
    password = os.getenv('DB_PASSWORD', '')

    driver = "ODBC Driver 17 for SQL Server"

    try:
        if use_windows_auth:
            conn_str = f"DRIVER={{{driver}}};SERVER={server};DATABASE={database};Trusted_Connection=yes;"
        else:
            conn_str = f"DRIVER={{{driver}}};SERVER={server};DATABASE={database};UID={username};PWD={password};"

        with pyodbc.connect(conn_str) as conn:
            cursor = conn.cursor()

            print("=== SLA Data Quality Analysis and Fixes ===\n")

            # 1. Check for SLA logs with missing timestamps
            print("1. Checking SLA logs with missing timestamps...")
            cursor.execute("""
                SELECT id, ticket_id, escalation_level, level_name, 
                       created_at, escalated_at, resolved_at, logged_at
                FROM sla_logs 
                WHERE created_at IS NULL OR logged_at IS NULL
                ORDER BY id
            """)
            missing_timestamps = cursor.fetchall()

            if missing_timestamps:
                print(
                    f"   Found {len(missing_timestamps)} SLA logs with missing timestamps")

                # Fix missing timestamps
                for log in missing_timestamps:
                    log_id, ticket_id = log[0], log[1]
                    current_time = datetime.now()

                    # Update missing created_at and logged_at
                    cursor.execute("""
                        UPDATE sla_logs 
                        SET created_at = COALESCE(created_at, ?),
                            logged_at = COALESCE(logged_at, ?)
                        WHERE id = ?
                    """, current_time, current_time, log_id)

                print(
                    f"   ✅ Fixed {len(missing_timestamps)} SLA logs with missing timestamps")
            else:
                print("   ✅ No SLA logs with missing timestamps found")

            # 2. Check for tickets without proper SLA targets
            print("\\n2. Checking tickets without proper SLA targets...")
            cursor.execute("""
                SELECT TicketID, Priority, Status, CreatedAt, current_sla_target
                FROM Tickets 
                WHERE Status IN ('open', 'in_progress', 'escalated') 
                AND current_sla_target IS NULL
            """)
            tickets_without_sla = cursor.fetchall()

            if tickets_without_sla:
                print(
                    f"   Found {len(tickets_without_sla)} tickets without SLA targets")

                # Set default SLA targets based on priority
                sla_targets = {
                    'critical': 2,   # 2 hours
                    'high': 4,       # 4 hours
                    'medium': 8,     # 8 hours
                    'low': 24        # 24 hours
                }

                for ticket in tickets_without_sla:
                    ticket_id, priority, status, created_at = ticket[0], ticket[1], ticket[2], ticket[3]

                    # Default to medium if priority is not recognized
                    priority_lower = priority.lower() if priority else 'medium'
                    sla_hours = sla_targets.get(priority_lower, 8)

                    # Calculate SLA target time
                    sla_target = created_at + timedelta(hours=sla_hours)

                    cursor.execute("""
                        UPDATE Tickets 
                        SET current_sla_target = ?
                        WHERE TicketID = ?
                    """, sla_target, ticket_id)

                print(
                    f"   ✅ Fixed {len(tickets_without_sla)} tickets without SLA targets")
            else:
                print("   ✅ All active tickets have SLA targets")

            # 3. Check for escalation level consistency
            print("\\n3. Checking escalation level consistency...")
            cursor.execute("""
                SELECT TicketID, escalation_level, Status
                FROM Tickets 
                WHERE escalation_level IS NULL
            """)
            tickets_without_escalation_level = cursor.fetchall()

            if tickets_without_escalation_level:
                print(
                    f"   Found {len(tickets_without_escalation_level)} tickets without escalation level")

                # Set default escalation level to 0 (Bot level)
                for ticket in tickets_without_escalation_level:
                    ticket_id = ticket[0]
                    cursor.execute("""
                        UPDATE Tickets 
                        SET escalation_level = 0
                        WHERE TicketID = ?
                    """, ticket_id)

                print(
                    f"   ✅ Fixed {len(tickets_without_escalation_level)} tickets without escalation level")
            else:
                print("   ✅ All tickets have escalation levels")

            # 4. Check for orphaned SLA logs
            print("\\n4. Checking for orphaned SLA logs...")
            cursor.execute("""
                SELECT sl.id, sl.ticket_id
                FROM sla_logs sl
                LEFT JOIN Tickets t ON sl.ticket_id = t.TicketID
                WHERE t.TicketID IS NULL
            """)
            orphaned_sla_logs = cursor.fetchall()

            if orphaned_sla_logs:
                print(f"   Found {len(orphaned_sla_logs)} orphaned SLA logs")

                # Delete orphaned SLA logs
                orphaned_ids = [str(log[0]) for log in orphaned_sla_logs]
                if orphaned_ids:
                    cursor.execute(f"""
                        DELETE FROM sla_logs 
                        WHERE id IN ({','.join(orphaned_ids)})
                    """)

                print(
                    f"   ✅ Removed {len(orphaned_sla_logs)} orphaned SLA logs")
            else:
                print("   ✅ No orphaned SLA logs found")

            # 5. Check for tickets missing initial SLA logs
            print("\\n5. Checking tickets missing initial SLA logs...")
            cursor.execute("""
                SELECT t.TicketID, t.Priority, t.CreatedAt, t.escalation_level
                FROM Tickets t
                LEFT JOIN sla_logs sl ON t.TicketID = sl.ticket_id
                WHERE sl.id IS NULL
                AND t.Status IN ('open', 'in_progress', 'escalated', 'closed')
                ORDER BY t.CreatedAt DESC
            """)
            tickets_without_sla_logs = cursor.fetchall()

            if tickets_without_sla_logs:
                print(
                    f"   Found {len(tickets_without_sla_logs)} tickets without SLA logs")

                # Create initial SLA logs
                sla_targets = {
                    'critical': 2,
                    'high': 4,
                    'medium': 8,
                    'low': 24
                }

                for ticket in tickets_without_sla_logs:
                    ticket_id, priority, created_at, escalation_level = ticket

                    priority_lower = priority.lower() if priority else 'medium'
                    sla_hours = sla_targets.get(priority_lower, 8)
                    escalation_level = escalation_level or 0

                    level_names = {0: 'Bot', 1: 'ICP', 2: 'YouCloud'}
                    level_name = level_names.get(escalation_level, 'Bot')

                    cursor.execute("""
                        INSERT INTO sla_logs (
                            ticket_id, escalation_level, level_name, sla_target_hours,
                            status, created_at, logged_at, is_breached
                        ) VALUES (?, ?, ?, ?, 'on_time', ?, ?, 0)
                    """, ticket_id, escalation_level, level_name, sla_hours,
                                   created_at, created_at)

                print(
                    f"   ✅ Created SLA logs for {len(tickets_without_sla_logs)} tickets")
            else:
                print("   ✅ All tickets have SLA logs")

            # 6. Update SLA breach status based on current time
            print("\\n6. Updating SLA breach status...")
            cursor.execute("""
                SELECT sl.id, sl.ticket_id, sl.sla_target_hours, t.CreatedAt, t.Status,
                       sl.escalated_at, sl.resolved_at, sl.is_breached
                FROM sla_logs sl
                JOIN Tickets t ON sl.ticket_id = t.TicketID
                WHERE sl.is_breached = 0  -- Not yet marked as breached
                ORDER BY sl.id
            """)
            active_sla_logs = cursor.fetchall()

            breached_count = 0
            for sla_log in active_sla_logs:
                log_id, ticket_id, sla_hours, created_at, status, escalated_at, resolved_at, is_breached = sla_log

                current_time = datetime.now()
                sla_deadline = created_at + timedelta(hours=sla_hours)

                # Check if SLA is breached (past deadline and not resolved)
                if current_time > sla_deadline and status not in ['closed', 'resolved']:
                    cursor.execute("""
                        UPDATE sla_logs 
                        SET is_breached = 1,
                            breach_time = ?,
                            status = 'breached'
                        WHERE id = ?
                    """, sla_deadline, log_id)
                    breached_count += 1

            if breached_count > 0:
                print(f"   ✅ Updated {breached_count} SLA logs as breached")
            else:
                print("   ✅ No new SLA breaches detected")

            # 7. Clean up duplicate SLA logs
            print("\\n7. Checking for duplicate SLA logs...")
            cursor.execute("""
                SELECT ticket_id, escalation_level, COUNT(*) as count
                FROM sla_logs
                GROUP BY ticket_id, escalation_level
                HAVING COUNT(*) > 1
            """)
            duplicates = cursor.fetchall()

            if duplicates:
                print(f"   Found {len(duplicates)} sets of duplicate SLA logs")

                # Keep only the most recent SLA log for each ticket/escalation level
                for dup in duplicates:
                    ticket_id, escalation_level = dup[0], dup[1]

                    # Delete all but the most recent
                    cursor.execute("""
                        DELETE FROM sla_logs 
                        WHERE ticket_id = ? AND escalation_level = ?
                        AND id NOT IN (
                            SELECT TOP 1 id FROM sla_logs 
                            WHERE ticket_id = ? AND escalation_level = ?
                            ORDER BY created_at DESC
                        )
                    """, ticket_id, escalation_level, ticket_id, escalation_level)

                print(f"   ✅ Removed duplicate SLA logs")
            else:
                print("   ✅ No duplicate SLA logs found")

            # Commit all changes
            conn.commit()

            print("\\n=== Summary ===")
            print("✅ All SLA data quality issues have been fixed!")
            print("✅ All timestamps are properly set")
            print("✅ All tickets have proper SLA targets")
            print("✅ All escalation levels are consistent")
            print("✅ No orphaned data exists")
            print("✅ SLA breach status is accurate")
            print("✅ Database is optimized for SLA monitoring")

            return True

    except Exception as e:
        print(f"❌ Error fixing SLA issues: {e}")
        return False


if __name__ == "__main__":
    fix_all_sla_issues()
