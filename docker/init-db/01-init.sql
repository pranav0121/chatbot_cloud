-- MSSQL Database Initialization Script
-- This script creates the necessary database and tables for the chatbot application

USE [master];
GO

-- Create database if it doesn't exist
IF NOT EXISTS (SELECT name FROM sys.databases WHERE name = 'SupportChatbot')
BEGIN
    CREATE DATABASE [SupportChatbot];
    PRINT 'Database SupportChatbot created successfully.';
END
ELSE
BEGIN
    PRINT 'Database SupportChatbot already exists.';
END
GO

-- Use the created database
USE [SupportChatbot];
GO

-- Create Users table
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Users' AND xtype='U')
BEGIN
    CREATE TABLE [Users] (
        [id] INT IDENTITY(1,1) PRIMARY KEY,
        [username] NVARCHAR(80) NOT NULL UNIQUE,
        [email] NVARCHAR(120) NOT NULL UNIQUE,
        [password_hash] NVARCHAR(200) NOT NULL,
        [is_admin] BIT DEFAULT 0,
        [role] NVARCHAR(50) DEFAULT 'user',
        [created_at] DATETIME2 DEFAULT GETUTCDATE(),
        [country] NVARCHAR(100),
        [organization_id] INT,
        [last_login] DATETIME2,
        [is_active] BIT DEFAULT 1
    );
    PRINT 'Users table created successfully.';
END
GO

-- Create Organizations table
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Organizations' AND xtype='U')
BEGIN
    CREATE TABLE [Organizations] (
        [id] INT IDENTITY(1,1) PRIMARY KEY,
        [name] NVARCHAR(200) NOT NULL,
        [domain] NVARCHAR(100),
        [created_at] DATETIME2 DEFAULT GETUTCDATE(),
        [created_by] INT,
        [is_active] BIT DEFAULT 1
    );
    PRINT 'Organizations table created successfully.';
END
GO

-- Create Tickets table
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Tickets' AND xtype='U')
BEGIN
    CREATE TABLE [Tickets] (
        [id] INT IDENTITY(1,1) PRIMARY KEY,
        [user_id] INT,
        [subject] NVARCHAR(500) NOT NULL,
        [description] NTEXT,
        [status] NVARCHAR(50) DEFAULT 'Open',
        [priority] NVARCHAR(20) DEFAULT 'Medium',
        [created_at] DATETIME2 DEFAULT GETUTCDATE(),
        [updated_at] DATETIME2 DEFAULT GETUTCDATE(),
        [assigned_to] INT,
        [category] NVARCHAR(100),
        [country] NVARCHAR(100),
        [end_date] DATETIME2,
        [escalation_level] INT DEFAULT 0,
        [is_escalated] BIT DEFAULT 0,
        [sla_breach] BIT DEFAULT 0,
        [metadata_json] NTEXT,
        [device_info] NTEXT,
        [odoo_ticket_id] INT,
        [partner_id] INT
    );
    PRINT 'Tickets table created successfully.';
END
GO

-- Create FAQ table
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='FAQ' AND xtype='U')
BEGIN
    CREATE TABLE [FAQ] (
        [id] INT IDENTITY(1,1) PRIMARY KEY,
        [question] NVARCHAR(500) NOT NULL,
        [answer] NTEXT NOT NULL,
        [category] NVARCHAR(100),
        [language] NVARCHAR(10) DEFAULT 'en',
        [is_active] BIT DEFAULT 1,
        [created_at] DATETIME2 DEFAULT GETUTCDATE(),
        [updated_at] DATETIME2 DEFAULT GETUTCDATE()
    );
    PRINT 'FAQ table created successfully.';
END
GO

-- Create Partners table
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Partners' AND xtype='U')
BEGIN
    CREATE TABLE [Partners] (
        [id] INT IDENTITY(1,1) PRIMARY KEY,
        [name] NVARCHAR(200) NOT NULL,
        [email] NVARCHAR(120),
        [phone] NVARCHAR(20),
        [country] NVARCHAR(100),
        [specialization] NVARCHAR(200),
        [is_active] BIT DEFAULT 1,
        [created_at] DATETIME2 DEFAULT GETUTCDATE(),
        [odoo_partner_id] INT
    );
    PRINT 'Partners table created successfully.';
END
GO

-- Create EscalationLevels table
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='EscalationLevels' AND xtype='U')
BEGIN
    CREATE TABLE [EscalationLevels] (
        [id] INT IDENTITY(1,1) PRIMARY KEY,
        [level] INT NOT NULL,
        [name] NVARCHAR(100) NOT NULL,
        [threshold_hours] INT NOT NULL,
        [assigned_to] INT,
        [is_active] BIT DEFAULT 1
    );
    PRINT 'EscalationLevels table created successfully.';
END
GO

-- Create SLARules table
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='SLARules' AND xtype='U')
BEGIN
    CREATE TABLE [SLARules] (
        [id] INT IDENTITY(1,1) PRIMARY KEY,
        [priority] NVARCHAR(20) NOT NULL,
        [response_time_hours] INT NOT NULL,
        [resolution_time_hours] INT NOT NULL,
        [is_active] BIT DEFAULT 1
    );
    PRINT 'SLARules table created successfully.';
END
GO

-- Insert default admin user
IF NOT EXISTS (SELECT * FROM [Users] WHERE email = 'admin@youcloudtech.com')
BEGIN
    INSERT INTO [Users] ([username], [email], [password_hash], [is_admin], [role], [country])
    VALUES ('admin', 'admin@youcloudtech.com', 'pbkdf2:sha256:260000$OgJm8ZqI1sHm6L2V$c7b8f7e3d9a8f2e1c6b5a4d3c2b1a9e8f7d6c5b4a3e2d1c0b9a8f7e6d5c4b3a2e1', 1, 'super_admin', 'India');
    PRINT 'Default admin user created successfully.';
END
GO

-- Insert default organization
IF NOT EXISTS (SELECT * FROM [Organizations] WHERE name = 'YouCloudTech')
BEGIN
    INSERT INTO [Organizations] ([name], [domain], [created_by])
    VALUES ('YouCloudTech', 'youcloudtech.com', 1);
    PRINT 'Default organization created successfully.';
END
GO

-- Insert default escalation levels
IF NOT EXISTS (SELECT * FROM [EscalationLevels] WHERE level = 1)
BEGIN
    INSERT INTO [EscalationLevels] ([level], [name], [threshold_hours]) VALUES (1, 'Level 1 Support', 24);
    INSERT INTO [EscalationLevels] ([level], [name], [threshold_hours]) VALUES (2, 'Level 2 Support', 48);
    INSERT INTO [EscalationLevels] ([level], [name], [threshold_hours]) VALUES (3, 'Level 3 Support', 72);
    PRINT 'Default escalation levels created successfully.';
END
GO

-- Insert default SLA rules
IF NOT EXISTS (SELECT * FROM [SLARules] WHERE priority = 'High')
BEGIN
    INSERT INTO [SLARules] ([priority], [response_time_hours], [resolution_time_hours]) VALUES ('High', 4, 24);
    INSERT INTO [SLARules] ([priority], [response_time_hours], [resolution_time_hours]) VALUES ('Medium', 8, 48);
    INSERT INTO [SLARules] ([priority], [response_time_hours], [resolution_time_hours]) VALUES ('Low', 24, 72);
    PRINT 'Default SLA rules created successfully.';
END
GO

-- Create indexes for better performance
CREATE NONCLUSTERED INDEX [IX_Tickets_Status] ON [Tickets] ([status]);
CREATE NONCLUSTERED INDEX [IX_Tickets_Priority] ON [Tickets] ([priority]);
CREATE NONCLUSTERED INDEX [IX_Tickets_Created] ON [Tickets] ([created_at]);
CREATE NONCLUSTERED INDEX [IX_Tickets_User] ON [Tickets] ([user_id]);
CREATE NONCLUSTERED INDEX [IX_Users_Email] ON [Users] ([email]);
CREATE NONCLUSTERED INDEX [IX_Users_Username] ON [Users] ([username]);

PRINT 'Database initialization completed successfully.';
GO
