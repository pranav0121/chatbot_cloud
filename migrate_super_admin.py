#!/usr/bin/env python3
"""
Database Migration for Super Admin Portal
Adds new tables and columns for enterprise features
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from sqlalchemy import text
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def migrate_database():
    """Migrate database to support Super Admin Portal features"""
    
    try:
        with app.app_context():
            logger.info("Starting database migration for Super Admin Portal...")
            
            # Create new tables
            logger.info("Creating new tables...")
            
            # Partners table
            logger.info("Creating partners table...")
            db.session.execute(text("""
                IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='partners' AND type='U')
                CREATE TABLE partners (
                    id int IDENTITY(1,1) PRIMARY KEY,
                    name nvarchar(255) NOT NULL,
                    partner_type nvarchar(50) NOT NULL,
                    email nvarchar(255) NOT NULL UNIQUE,
                    contact_person nvarchar(255),
                    phone nvarchar(50),
                    status nvarchar(20) DEFAULT 'active',
                    api_key nvarchar(255),
                    webhook_url nvarchar(500),
                    escalation_settings ntext,
                    sla_settings ntext,
                    total_tickets_handled int DEFAULT 0,
                    avg_resolution_time float DEFAULT 0.0,
                    satisfaction_rating float DEFAULT 0.0,
                    created_at datetime2 DEFAULT GETDATE(),
                    updated_at datetime2 DEFAULT GETDATE()
                )
            """))
            
            # SLA Logs table
            logger.info("Creating sla_logs table...")
            db.session.execute(text("""
                IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='sla_logs' AND type='U')
                CREATE TABLE sla_logs (
                    id int IDENTITY(1,1) PRIMARY KEY,
                    ticket_id int NOT NULL,
                    escalation_level int NOT NULL,
                    level_name nvarchar(50) NOT NULL,
                    sla_target_hours float NOT NULL,
                    created_at datetime2 DEFAULT GETDATE(),
                    escalated_at datetime2,
                    resolved_at datetime2,
                    is_breached bit DEFAULT 0,
                    breach_time datetime2,
                    resolution_method nvarchar(50),
                    assigned_partner_id int,
                    FOREIGN KEY (ticket_id) REFERENCES Tickets(TicketID),
                    FOREIGN KEY (assigned_partner_id) REFERENCES partners(id)
                )
            """))
            
            # Ticket Status Logs table
            logger.info("Creating ticket_status_logs table...")
            db.session.execute(text("""
                IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='ticket_status_logs' AND type='U')
                CREATE TABLE ticket_status_logs (
                    id int IDENTITY(1,1) PRIMARY KEY,
                    ticket_id int NOT NULL,
                    old_status nvarchar(50),
                    new_status nvarchar(50) NOT NULL,
                    changed_by_id int,
                    changed_by_type nvarchar(20) NOT NULL,
                    escalation_level int,
                    comment ntext,
                    metadata ntext,
                    created_at datetime2 DEFAULT GETDATE(),
                    FOREIGN KEY (ticket_id) REFERENCES Tickets(TicketID),
                    FOREIGN KEY (changed_by_id) REFERENCES Users(UserID)
                )
            """))
            
            # Audit Logs table
            logger.info("Creating audit_logs table...")
            db.session.execute(text("""
                IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='audit_logs' AND type='U')
                CREATE TABLE audit_logs (
                    id int IDENTITY(1,1) PRIMARY KEY,
                    action nvarchar(100) NOT NULL,
                    resource_type nvarchar(50) NOT NULL,
                    resource_id int,
                    user_id int,
                    user_type nvarchar(20) NOT NULL,
                    ip_address nvarchar(45),
                    user_agent nvarchar(500),
                    details ntext,
                    created_at datetime2 DEFAULT GETDATE(),
                    FOREIGN KEY (user_id) REFERENCES Users(UserID)
                )
            """))
            
            # Escalation Rules table
            logger.info("Creating escalation_rules table...")
            db.session.execute(text("""
                IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='escalation_rules' AND type='U')
                CREATE TABLE escalation_rules (
                    id int IDENTITY(1,1) PRIMARY KEY,
                    name nvarchar(255) NOT NULL,
                    priority nvarchar(20) NOT NULL,
                    category_id int,
                    level_0_sla_hours float DEFAULT 0.0,
                    level_1_sla_hours float DEFAULT 4.0,
                    level_2_sla_hours float DEFAULT 24.0,
                    auto_escalate bit DEFAULT 1,
                    notification_enabled bit DEFAULT 1,
                    is_active bit DEFAULT 1,
                    created_at datetime2 DEFAULT GETDATE(),
                    updated_at datetime2 DEFAULT GETDATE(),
                    FOREIGN KEY (category_id) REFERENCES Categories(CategoryID)
                )
            """))
            
            # Bot Configurations table
            logger.info("Creating bot_configurations table...")
            db.session.execute(text("""
                IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='bot_configurations' AND type='U')
                CREATE TABLE bot_configurations (
                    id int IDENTITY(1,1) PRIMARY KEY,
                    name nvarchar(255) NOT NULL,
                    bot_type nvarchar(50) NOT NULL,
                    api_endpoint nvarchar(500),
                    api_key nvarchar(255),
                    config_data ntext,
                    is_active bit DEFAULT 1,
                    fallback_to_human bit DEFAULT 1,
                    confidence_threshold float DEFAULT 0.7,
                    created_at datetime2 DEFAULT GETDATE(),
                    updated_at datetime2 DEFAULT GETDATE()
                )
            """))
            
            # Bot Interactions table
            logger.info("Creating bot_interactions table...")
            db.session.execute(text("""
                IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='bot_interactions' AND type='U')
                CREATE TABLE bot_interactions (
                    id int IDENTITY(1,1) PRIMARY KEY,
                    ticket_id int,
                    user_message ntext NOT NULL,
                    bot_response ntext NOT NULL,
                    confidence_score float,
                    intent_detected nvarchar(255),
                    was_resolved bit DEFAULT 0,
                    escalated_to_human bit DEFAULT 0,
                    session_id nvarchar(255),
                    created_at datetime2 DEFAULT GETDATE(),
                    FOREIGN KEY (ticket_id) REFERENCES Tickets(TicketID)
                )
            """))
            
            # Add new columns to existing Tickets table
            logger.info("Adding new columns to Tickets table...")
            
            # Check which columns already exist
            existing_columns = db.session.execute(text("""
                SELECT COLUMN_NAME 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_NAME = 'Tickets'
            """)).fetchall()
            
            existing_column_names = [col[0] for col in existing_columns]
            
            # Add escalation_level column
            if 'escalation_level' not in existing_column_names:
                db.session.execute(text("""
                    ALTER TABLE Tickets 
                    ADD escalation_level int DEFAULT 0
                """))
                logger.info("Added escalation_level column to Tickets")
            
            # Add current_sla_target column
            if 'current_sla_target' not in existing_column_names:
                db.session.execute(text("""
                    ALTER TABLE Tickets 
                    ADD current_sla_target datetime2
                """))
                logger.info("Added current_sla_target column to Tickets")
            
            # Add resolution_method column
            if 'resolution_method' not in existing_column_names:
                db.session.execute(text("""
                    ALTER TABLE Tickets 
                    ADD resolution_method nvarchar(50)
                """))
                logger.info("Added resolution_method column to Tickets")
            
            # Add bot_attempted column
            if 'bot_attempted' not in existing_column_names:
                db.session.execute(text("""
                    ALTER TABLE Tickets 
                    ADD bot_attempted bit DEFAULT 0
                """))
                logger.info("Added bot_attempted column to Tickets")
            
            # Add partner_id column
            if 'partner_id' not in existing_column_names:
                db.session.execute(text("""
                    ALTER TABLE Tickets 
                    ADD partner_id int
                """))
                logger.info("Added partner_id column to Tickets")
            
            # Commit all changes
            db.session.commit()
            logger.info("✅ Database migration completed successfully!")
            
            # Create default escalation rules
            logger.info("Creating default escalation rules...")
            create_default_escalation_rules()
            
            # Create sample super admin user
            logger.info("Creating super admin user...")
            create_super_admin_user()
            
            logger.info("🎉 Super Admin Portal migration completed!")
            
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        db.session.rollback()
        raise

def create_default_escalation_rules():
    """Create default escalation rules for different priorities"""
    
    escalation_rules = [
        {
            'name': 'Critical Priority Escalation',
            'priority': 'critical',
            'level_0_sla_hours': 0.0,  # Immediate bot response
            'level_1_sla_hours': 1.0,  # 1 hour to ICP
            'level_2_sla_hours': 4.0   # 4 hours to YouCloud
        },
        {
            'name': 'High Priority Escalation',
            'priority': 'high',
            'level_0_sla_hours': 0.0,
            'level_1_sla_hours': 2.0,  # 2 hours to ICP
            'level_2_sla_hours': 8.0   # 8 hours to YouCloud
        },
        {
            'name': 'Medium Priority Escalation',
            'priority': 'medium',
            'level_0_sla_hours': 0.0,
            'level_1_sla_hours': 4.0,  # 4 hours to ICP
            'level_2_sla_hours': 24.0  # 24 hours to YouCloud
        },
        {
            'name': 'Low Priority Escalation',
            'priority': 'low',
            'level_0_sla_hours': 0.0,
            'level_1_sla_hours': 8.0,  # 8 hours to ICP
            'level_2_sla_hours': 72.0  # 72 hours to YouCloud
        }
    ]
    
    for rule in escalation_rules:
        db.session.execute(text("""
            IF NOT EXISTS (SELECT * FROM escalation_rules WHERE priority = :priority)
            INSERT INTO escalation_rules (name, priority, level_0_sla_hours, level_1_sla_hours, level_2_sla_hours)
            VALUES (:name, :priority, :level_0_sla_hours, :level_1_sla_hours, :level_2_sla_hours)
        """), rule)
    
    db.session.commit()
    logger.info("✅ Default escalation rules created")

def create_super_admin_user():
    """Create super admin user if it doesn't exist"""
    from werkzeug.security import generate_password_hash
    
    try:
        # Check if super admin already exists
        existing_admin = db.session.execute(text("""
            SELECT UserID FROM Users 
            WHERE Email = 'superadmin@youcloudtech.com' AND IsAdmin = 1
        """)).fetchone()
        
        if not existing_admin:
            db.session.execute(text("""
                INSERT INTO Users (
                    Name, Email, PasswordHash, OrganizationName, Position, 
                    PriorityLevel, IsActive, IsAdmin, CreatedAt
                ) VALUES (
                    'Super Administrator',
                    'superadmin@youcloudtech.com',
                    :password_hash,
                    'YouCloud Technologies',
                    'Super Administrator',
                    'critical',
                    1,
                    1,
                    GETDATE()
                )
            """), {
                'password_hash': generate_password_hash('superadmin123')
            })
            
            db.session.commit()
            logger.info("✅ Super admin user created:")
            logger.info("   Email: superadmin@youcloudtech.com")
            logger.info("   Password: superadmin123")
        else:
            logger.info("✅ Super admin user already exists")
            
    except Exception as e:
        logger.error(f"Error creating super admin user: {e}")

def create_sample_partner():
    """Create a sample partner for testing"""
    import json
    
    try:
        # Check if sample partner already exists
        existing_partner = db.session.execute(text("""
            SELECT id FROM partners WHERE email = 'partner@icp-demo.com'
        """)).fetchone()
        
        if not existing_partner:
            sla_settings = {
                'level1': 4,
                'level2': 24,
                'max': 72
            }
            
            db.session.execute(text("""
                INSERT INTO partners (
                    name, partner_type, email, contact_person, phone,
                    status, sla_settings, created_at, updated_at
                ) VALUES (
                    'Demo ICP Partner',
                    'ICP',
                    'partner@icp-demo.com',
                    'John Demo',
                    '+1-555-0123',
                    'active',
                    :sla_settings,
                    GETDATE(),
                    GETDATE()
                )
            """), {
                'sla_settings': json.dumps(sla_settings)
            })
            
            db.session.commit()
            logger.info("✅ Sample partner created")
        else:
            logger.info("✅ Sample partner already exists")
            
    except Exception as e:
        logger.error(f"Error creating sample partner: {e}")

if __name__ == '__main__':
    migrate_database()
    create_sample_partner()
    print("\n" + "="*60)
    print("🎉 SUPER ADMIN PORTAL SETUP COMPLETE!")
    print("="*60)
    print("\nAccess URLs:")
    print("Regular Admin: http://localhost:5000/admin")
    print("Super Admin:   http://localhost:5000/super-admin")
    print("\nCredentials:")
    print("Admin:       admin@youcloudtech.com / admin123")
    print("Super Admin: superadmin@youcloudtech.com / superadmin123")
    print("="*60)
