-- Create a new SQL login for our application
USE [master]
GO

-- Create new login with password
CREATE LOGIN [chatbot_user] WITH 
    PASSWORD = 'ChatBot123!', 
    DEFAULT_DATABASE = [master],
    CHECK_EXPIRATION = OFF,
    CHECK_POLICY = OFF;
GO

-- Create the database if it doesn't exist
IF NOT EXISTS (SELECT * FROM sys.databases WHERE name = 'SupportChatbot')
BEGIN
    CREATE DATABASE [SupportChatbot]
END;
GO

USE [SupportChatbot]
GO

-- Create database user and grant permissions
IF NOT EXISTS (SELECT * FROM sys.database_principals WHERE name = 'chatbot_user')
BEGIN
    CREATE USER [chatbot_user] FOR LOGIN [chatbot_user];
    ALTER ROLE [db_owner] ADD MEMBER [chatbot_user];
END
GO
