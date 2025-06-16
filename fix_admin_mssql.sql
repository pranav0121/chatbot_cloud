-- MSSQL Admin User Fix Script
-- Run this in SQL Server Management Studio

USE SupportChatbot;
GO

-- Check if Users table exists
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Users' AND type='U')
BEGIN
    PRINT 'Creating Users table...'
    CREATE TABLE Users (
        UserID int IDENTITY(1,1) PRIMARY KEY,
        Name nvarchar(100) NOT NULL,
        Email nvarchar(255) NOT NULL UNIQUE,
        PasswordHash nvarchar(255) NOT NULL,
        OrganizationName nvarchar(200),
        Position nvarchar(100),
        PriorityLevel nvarchar(20) DEFAULT 'medium',
        Phone nvarchar(20),
        Department nvarchar(100),
        PreferredLanguage nvarchar(10) DEFAULT 'en',
        IsActive bit DEFAULT 1,
        IsAdmin bit DEFAULT 0,
        LastLogin datetime2,
        CreatedAt datetime2 DEFAULT GETDATE()
    );
    PRINT 'Users table created successfully'
END
ELSE
BEGIN
    PRINT 'Users table already exists'
END
GO

-- Check current admin users
PRINT 'Current admin users:'
SELECT UserID, Name, Email, IsActive, IsAdmin, OrganizationName 
FROM Users 
WHERE IsAdmin = 1;
GO

-- Fix/Create admin user
DECLARE @AdminEmail NVARCHAR(255) = 'admin@youcloudtech.com';
DECLARE @AdminPassword NVARCHAR(255) = '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewlqkkMCHUdE3M2e'; -- Hash of 'admin123'

IF EXISTS (SELECT 1 FROM Users WHERE Email = @AdminEmail)
BEGIN
    -- Update existing admin user
    UPDATE Users 
    SET IsActive = 1, 
        IsAdmin = 1, 
        PasswordHash = @AdminPassword,
        Name = 'System Administrator',
        OrganizationName = 'YouCloudTech',
        Position = 'Administrator',
        PriorityLevel = 'critical',
        LastLogin = GETDATE()
    WHERE Email = @AdminEmail;
    
    PRINT 'Existing admin user updated successfully'
END
ELSE
BEGIN
    -- Create new admin user
    INSERT INTO Users (
        Name, Email, PasswordHash, OrganizationName, Position, 
        PriorityLevel, Department, Phone, IsActive, IsAdmin, 
        CreatedAt, LastLogin
    ) 
    VALUES (
        'System Administrator', 
        @AdminEmail, 
        @AdminPassword,
        'YouCloudTech', 
        'Administrator', 
        'critical', 
        'IT', 
        '+1-555-ADMIN', 
        1, 
        1, 
        GETDATE(), 
        GETDATE()
    );
    
    PRINT 'New admin user created successfully'
END
GO

-- Verify admin user
PRINT 'Admin user verification:'
SELECT 
    UserID,
    Name, 
    Email, 
    OrganizationName,
    Position,
    PriorityLevel,
    IsActive, 
    IsAdmin, 
    CreatedAt,
    LastLogin
FROM Users 
WHERE Email = 'admin@youcloudtech.com';
GO

-- Show all admin users
PRINT 'All admin users in system:'
SELECT 
    UserID,
    Name, 
    Email, 
    IsActive, 
    IsAdmin, 
    OrganizationName
FROM Users 
WHERE IsAdmin = 1;
GO

PRINT '=== ADMIN USER FIX COMPLETE ==='
PRINT 'Admin Credentials:'
PRINT 'Email: admin@youcloudtech.com'  
PRINT 'Password: admin123'
PRINT 'Admin URL: http://localhost:5000/auth/admin/login'
GO
