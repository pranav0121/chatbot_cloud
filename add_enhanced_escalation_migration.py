#!/usr/bin/env python3
"""
Enhanced Escalation Migration - Add comprehensive escalation tracking fields
Adds: escalationReason, escalationTimestamp, escalatedTo, slaBreachStatus, autoEscalated
"""

import pyodbc
import logging
from datetime import datetime, timezone

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_mssql_connection():
    """Get MSSQL database connection"""
    try:
        server = r'PRANAV\SQLEXPRESS'
        database = 'SupportChatbot'
        
        connection_string = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};Trusted_Connection=yes;'
        conn = pyodbc.connect(connection_string)
        return conn
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return None

def add_enhanced_escalation_fields():
    """Add enhanced escalation tracking fields to Tickets table"""
    logger.info("🚀 ADDING ENHANCED ESCALATION FIELDS")
    logger.info("=" * 50)
    
    conn = get_mssql_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        
        # Check existing columns
        cursor.execute("""
            SELECT COLUMN_NAME 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_NAME = 'Tickets'
        """)
        existing_columns = [row[0] for row in cursor.fetchall()]
        logger.info(f"📋 Found {len(existing_columns)} existing columns in Tickets table")
        
        # New escalation fields to add
        new_fields = [
            ("EscalationReason", "NVARCHAR(500)", "NULL", "Reason for escalation"),
            ("EscalationTimestamp", "DATETIME", "NULL", "When ticket was escalated"),
            ("EscalatedTo", "NVARCHAR(100)", "NULL", "Role/person ticket was escalated to"),
            ("SLABreachStatus", "NVARCHAR(50)", "'Within SLA'", "SLA breach status"),
            ("AutoEscalated", "BIT", "0", "Whether escalation was automatic"),
            ("EscalationHistory", "NVARCHAR(MAX)", "NULL", "JSON history of escalations"),
            ("CurrentAssignedRole", "NVARCHAR(50)", "'bot'", "Currently assigned role"),
            ("SLATarget", "DATETIME", "NULL", "Target SLA completion time"),
            ("OriginalSLATarget", "DATETIME", "NULL", "Original SLA target (before escalations)")
        ]
        
        # Add new columns if they don't exist
        for field_name, field_type, default_value, description in new_fields:
            if field_name not in existing_columns:
                try:
                    alter_sql = f"""
                    ALTER TABLE Tickets 
                    ADD {field_name} {field_type} DEFAULT {default_value}
                    """
                    cursor.execute(alter_sql)
                    logger.info(f"✅ Added {field_name} ({description})")
                except Exception as e:
                    logger.error(f"❌ Failed to add {field_name}: {e}")
            else:
                logger.info(f"⚪ {field_name} already exists")
        
        # Commit the schema changes
        conn.commit()
        logger.info("📊 Schema changes committed")
        
        # Initialize values for existing tickets
        logger.info("\n🔧 Initializing values for existing tickets...")
        
        # Set default SLA breach status
        cursor.execute("""
            UPDATE Tickets 
            SET SLABreachStatus = 'Within SLA'
            WHERE SLABreachStatus IS NULL
        """)
        sla_updated = cursor.rowcount
        logger.info(f"✅ Set default SLA status for {sla_updated} tickets")
        
        # Set default assigned role based on escalation level
        cursor.execute("""
            UPDATE Tickets 
            SET CurrentAssignedRole = CASE 
                WHEN EscalationLevel = 'admin' THEN 'admin'
                WHEN EscalationLevel = 'supervisor' THEN 'supervisor'
                ELSE 'bot'
            END
            WHERE CurrentAssignedRole IS NULL OR CurrentAssignedRole = 'bot'
        """)
        role_updated = cursor.rowcount
        logger.info(f"✅ Set assigned roles for {role_updated} tickets")
        
        # Set SLA targets based on priority (if not already set)
        cursor.execute("""
            UPDATE Tickets 
            SET SLATarget = DATEADD(hour, 
                CASE Priority
                    WHEN 'critical' THEN 1
                    WHEN 'high' THEN 4
                    WHEN 'medium' THEN 8
                    WHEN 'low' THEN 24
                    ELSE 8
                END, 
                CreatedAt),
                OriginalSLATarget = DATEADD(hour, 
                CASE Priority
                    WHEN 'critical' THEN 1
                    WHEN 'high' THEN 4
                    WHEN 'medium' THEN 8
                    WHEN 'low' THEN 24
                    ELSE 8
                END, 
                CreatedAt)
            WHERE SLATarget IS NULL
        """)
        sla_target_updated = cursor.rowcount
        logger.info(f"✅ Set SLA targets for {sla_target_updated} tickets")
        
        # Initialize escalation history for existing escalated tickets
        cursor.execute("""
            UPDATE Tickets 
            SET EscalationHistory = '[{"level": "' + EscalationLevel + '", "timestamp": "' + 
                CONVERT(varchar, GETDATE(), 126) + '", "reason": "Initial escalation level", "auto": false}]'
            WHERE EscalationLevel != 'normal' AND EscalationHistory IS NULL
        """)
        history_updated = cursor.rowcount
        logger.info(f"✅ Initialized escalation history for {history_updated} tickets")
        
        conn.commit()
        
        # Verify the additions
        cursor.execute("""
            SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE, COLUMN_DEFAULT
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_NAME = 'Tickets' 
            AND COLUMN_NAME IN ('EscalationReason', 'EscalationTimestamp', 'EscalatedTo', 
                               'SLABreachStatus', 'AutoEscalated', 'EscalationHistory',
                               'CurrentAssignedRole', 'SLATarget', 'OriginalSLATarget')
            ORDER BY COLUMN_NAME
        """)
        
        new_columns = cursor.fetchall()
        logger.info(f"\n📊 Verification - Added {len(new_columns)} new escalation fields:")
        for col in new_columns:
            logger.info(f"  {col[0]}: {col[1]} ({'NULL' if col[2] == 'YES' else 'NOT NULL'})")
        
        # Show sample data
        cursor.execute("""
            SELECT TOP 3 TicketID, EscalationLevel, SLABreachStatus, CurrentAssignedRole, 
                   EscalationReason, AutoEscalated
            FROM Tickets 
            ORDER BY TicketID DESC
        """)
        
        sample_data = cursor.fetchall()
        logger.info(f"\n📋 Sample ticket data:")
        for row in sample_data:
            logger.info(f"  Ticket #{row[0]}: {row[1]} level, {row[2]}, assigned to {row[3]}")
        
        conn.close()
        
        logger.info("\n🎉 ENHANCED ESCALATION FIELDS ADDED SUCCESSFULLY!")
        logger.info("✅ All new escalation tracking fields are ready")
        logger.info("✅ Existing tickets initialized with default values")
        logger.info("✅ SLA targets calculated based on priority")
        logger.info("✅ Ready for enhanced escalation API")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")
        conn.rollback()
        conn.close()
        return False

def main():
    """Run the enhanced escalation migration"""
    if add_enhanced_escalation_fields():
        print("\n🚀 Enhanced escalation system is ready!")
        print("Next steps:")
        print("1. Update app.py models with new fields")
        print("2. Create enhanced escalation API endpoints")
        print("3. Update SLA monitoring service")
        print("4. Test auto-escalation functionality")
    else:
        print("❌ Migration failed. Please check the logs above.")

if __name__ == '__main__':
    main()
