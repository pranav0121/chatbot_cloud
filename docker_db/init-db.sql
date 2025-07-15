-- Database initialization script for SupportChatbot
CREATE DATABASE [SupportChatbot];
GO
USE [SupportChatbot];
GO
-- Example table (customize as needed)
CREATE TABLE Users (
    UserID INT PRIMARY KEY IDENTITY(1,1),
    Name NVARCHAR(100),
    Email NVARCHAR(255),
    PasswordHash NVARCHAR(255),
    CreatedAt DATETIME DEFAULT GETDATE()
);
GO
