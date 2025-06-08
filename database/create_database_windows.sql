-- Create database using Windows Authentication
-- Run this with: sqlcmd -S PRANAV\SQLEXPRESS -E -i create_database_windows.sql

USE [master]
GO

-- Create the database if it doesn't exist
IF NOT EXISTS (SELECT * FROM sys.databases WHERE name = 'SupportChatbot')
BEGIN
    CREATE DATABASE [SupportChatbot]
    PRINT 'Database SupportChatbot created successfully'
END
ELSE
BEGIN
    PRINT 'Database SupportChatbot already exists'
END
GO

USE [SupportChatbot]
GO

-- Create tables if they don't exist
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Users' AND xtype='U')
BEGIN
    CREATE TABLE Users (
        UserID int IDENTITY(1,1) PRIMARY KEY,
        Name nvarchar(100),
        Email nvarchar(255),
        CreatedAt datetime2 DEFAULT GETDATE()
    )
    PRINT 'Users table created'
END

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Categories' AND xtype='U')
BEGIN
    CREATE TABLE Categories (
        CategoryID int IDENTITY(1,1) PRIMARY KEY,
        Name nvarchar(50) NOT NULL,
        Team nvarchar(50) NOT NULL,
        CreatedAt datetime2 DEFAULT GETDATE()
    )
    PRINT 'Categories table created'
END

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Tickets' AND xtype='U')
BEGIN
    CREATE TABLE Tickets (
        TicketID int IDENTITY(1,1) PRIMARY KEY,
        UserID int FOREIGN KEY REFERENCES Users(UserID),
        CategoryID int FOREIGN KEY REFERENCES Categories(CategoryID),
        Subject nvarchar(255) NOT NULL,
        Status nvarchar(20) DEFAULT 'open',
        CreatedAt datetime2 DEFAULT GETDATE(),
        UpdatedAt datetime2 DEFAULT GETDATE()
    )
    PRINT 'Tickets table created'
END

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Messages' AND xtype='U')
BEGIN
    CREATE TABLE Messages (
        MessageID int IDENTITY(1,1) PRIMARY KEY,
        TicketID int FOREIGN KEY REFERENCES Tickets(TicketID),
        SenderID int FOREIGN KEY REFERENCES Users(UserID),
        Content ntext NOT NULL,
        IsAdminReply bit DEFAULT 0,
        CreatedAt datetime2 DEFAULT GETDATE()
    )
    PRINT 'Messages table created'
END

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='CommonQueries' AND xtype='U')
BEGIN
    CREATE TABLE CommonQueries (
        QueryID int IDENTITY(1,1) PRIMARY KEY,
        CategoryID int FOREIGN KEY REFERENCES Categories(CategoryID),
        Question nvarchar(255) NOT NULL,
        Answer ntext NOT NULL,
        CreatedAt datetime2 DEFAULT GETDATE()
    )
    PRINT 'CommonQueries table created'
END

-- Insert sample categories if none exist
IF NOT EXISTS (SELECT * FROM Categories)
BEGIN
    INSERT INTO Categories (Name, Team) VALUES 
    ('Technical Support', 'Technical'),
    ('Billing', 'Finance'),
    ('General Inquiry', 'Support'),
    ('Product Information', 'Sales'),
    ('Bug Report', 'Technical')
    PRINT 'Sample categories inserted'
END

-- Insert sample common queries
IF NOT EXISTS (SELECT * FROM CommonQueries)
BEGIN
    INSERT INTO CommonQueries (CategoryID, Question, Answer) VALUES 
    (1, 'How to reset password?', 'You can reset your password by clicking on the "Forgot Password" link on the login page.'),
    (1, 'Application not loading', 'Please try clearing your browser cache and cookies, then restart your browser.'),
    (2, 'How to update billing information?', 'You can update your billing information in the Account Settings under the Billing section.'),
    (3, 'How to contact support?', 'You can contact support through this chat system or email us at support@company.com'),
    (4, 'What are the system requirements?', 'Our application works on all modern browsers and requires internet connection.')
    PRINT 'Sample common queries inserted'
END

PRINT 'Database setup completed successfully!'
GO
