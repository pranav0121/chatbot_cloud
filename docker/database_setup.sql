-- SQL Server Database Setup Script for Chatbot Application
-- Execute this script to set up the database and user for the chatbot application

-- 1. Create the database
IF NOT EXISTS (SELECT name FROM sys.databases WHERE name = 'SupportChatbot')
BEGIN
    CREATE DATABASE SupportChatbot;
    PRINT 'Database SupportChatbot created successfully.';
END
ELSE
BEGIN
    PRINT 'Database SupportChatbot already exists.';
END
GO

-- 2. Use the database
USE SupportChatbot;
GO

-- 3. Create login and user (uncomment if using SQL Server Authentication)
/*
IF NOT EXISTS (SELECT name FROM sys.server_principals WHERE name = 'chatbot_user')
BEGIN
    CREATE LOGIN [chatbot_user] WITH PASSWORD = 'ChatBot123!';
    PRINT 'Login chatbot_user created successfully.';
END
ELSE
BEGIN
    PRINT 'Login chatbot_user already exists.';
END

IF NOT EXISTS (SELECT name FROM sys.database_principals WHERE name = 'chatbot_user')
BEGIN
    CREATE USER [chatbot_user] FOR LOGIN [chatbot_user];
    ALTER ROLE db_owner ADD MEMBER [chatbot_user];
    PRINT 'User chatbot_user created and added to db_owner role.';
END
ELSE
BEGIN
    PRINT 'User chatbot_user already exists.';
END
*/

-- 4. Create sample tables (these will be auto-created by the application, but included for reference)
-- Note: The application uses SQLAlchemy ORM which will create these automatically

-- Users table for authentication
IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[Users]') AND type in (N'U'))
BEGIN
    CREATE TABLE [dbo].[Users](
        [UserID] [int] IDENTITY(1,1) NOT NULL,
        [Email] [nvarchar](255) NOT NULL,
        [PasswordHash] [nvarchar](255) NOT NULL,
        [FirstName] [nvarchar](100) NULL,
        [LastName] [nvarchar](100) NULL,
        [Role] [nvarchar](50) NULL,
        [IsActive] [bit] NULL,
        [CreatedAt] [datetime] NULL,
        [Country] [nvarchar](100) NULL,
        CONSTRAINT [PK_Users] PRIMARY KEY CLUSTERED ([UserID] ASC)
    );
    PRINT 'Users table created.';
END

-- Tickets table for support tickets
IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[Tickets]') AND type in (N'U'))
BEGIN
    CREATE TABLE [dbo].[Tickets](
        [TicketID] [int] IDENTITY(1,1) NOT NULL,
        [Subject] [nvarchar](255) NOT NULL,
        [Description] [ntext] NULL,
        [Status] [nvarchar](50) NULL,
        [Priority] [nvarchar](50) NULL,
        [CreatedAt] [datetime] NULL,
        [UpdatedAt] [datetime] NULL,
        [EndDate] [datetime] NULL,
        [UserID] [int] NULL,
        [AssignedTo] [int] NULL,
        [Category] [nvarchar](100) NULL,
        [Country] [nvarchar](100) NULL,
        [EscalationLevel] [int] NULL DEFAULT 0,
        [EscalatedAt] [datetime] NULL,
        [OdooTicketID] [int] NULL,
        CONSTRAINT [PK_Tickets] PRIMARY KEY CLUSTERED ([TicketID] ASC),
        CONSTRAINT [FK_Tickets_Users] FOREIGN KEY([UserID]) REFERENCES [dbo].[Users] ([UserID])
    );
    PRINT 'Tickets table created.';
END

-- DeviceInfo table for device tracking
IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[DeviceInfo]') AND type in (N'U'))
BEGIN
    CREATE TABLE [dbo].[DeviceInfo](
        [DeviceID] [int] IDENTITY(1,1) NOT NULL,
        [TicketID] [int] NOT NULL,
        [DeviceType] [nvarchar](100) NULL,
        [DeviceModel] [nvarchar](100) NULL,
        [SerialNumber] [nvarchar](100) NULL,
        [OperatingSystem] [nvarchar](100) NULL,
        [BrowserInfo] [nvarchar](255) NULL,
        [IPAddress] [nvarchar](45) NULL,
        [Location] [nvarchar](255) NULL,
        [CapturedAt] [datetime] NULL,
        CONSTRAINT [PK_DeviceInfo] PRIMARY KEY CLUSTERED ([DeviceID] ASC),
        CONSTRAINT [FK_DeviceInfo_Tickets] FOREIGN KEY([TicketID]) REFERENCES [dbo].[Tickets] ([TicketID])
    );
    PRINT 'DeviceInfo table created.';
END

-- EscalationHistory table for tracking escalations
IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[EscalationHistory]') AND type in (N'U'))
BEGIN
    CREATE TABLE [dbo].[EscalationHistory](
        [EscalationID] [int] IDENTITY(1,1) NOT NULL,
        [TicketID] [int] NOT NULL,
        [EscalatedBy] [int] NULL,
        [EscalatedTo] [int] NULL,
        [EscalationLevel] [int] NOT NULL,
        [EscalationReason] [nvarchar](500) NULL,
        [EscalatedAt] [datetime] NULL,
        [Status] [nvarchar](50) NULL,
        CONSTRAINT [PK_EscalationHistory] PRIMARY KEY CLUSTERED ([EscalationID] ASC),
        CONSTRAINT [FK_EscalationHistory_Tickets] FOREIGN KEY([TicketID]) REFERENCES [dbo].[Tickets] ([TicketID])
    );
    PRINT 'EscalationHistory table created.';
END

-- Partners table for Odoo integration
IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[Partners]') AND type in (N'U'))
BEGIN
    CREATE TABLE [dbo].[Partners](
        [PartnerID] [int] IDENTITY(1,1) NOT NULL,
        [Name] [nvarchar](255) NOT NULL,
        [Email] [nvarchar](255) NULL,
        [Phone] [nvarchar](50) NULL,
        [Company] [nvarchar](255) NULL,
        [OdooPartnerID] [int] NULL,
        [CreatedAt] [datetime] NULL,
        [UpdatedAt] [datetime] NULL,
        [IsActive] [bit] NULL,
        CONSTRAINT [PK_Partners] PRIMARY KEY CLUSTERED ([PartnerID] ASC)
    );
    PRINT 'Partners table created.';
END

-- Create indexes for better performance
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_Tickets_Status')
BEGIN
    CREATE INDEX IX_Tickets_Status ON [dbo].[Tickets] ([Status]);
    PRINT 'Index IX_Tickets_Status created.';
END

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_Tickets_CreatedAt')
BEGIN
    CREATE INDEX IX_Tickets_CreatedAt ON [dbo].[Tickets] ([CreatedAt]);
    PRINT 'Index IX_Tickets_CreatedAt created.';
END

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_Users_Email')
BEGIN
    CREATE UNIQUE INDEX IX_Users_Email ON [dbo].[Users] ([Email]);
    PRINT 'Index IX_Users_Email created.';
END

PRINT 'Database setup completed successfully!';
PRINT 'Note: The application will automatically create/update tables on startup using SQLAlchemy migrations.';
