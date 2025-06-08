USE SupportChatbot;
GO

-- Verify tables exist
SELECT TABLE_NAME 
FROM INFORMATION_SCHEMA.TABLES 
WHERE TABLE_TYPE = 'BASE TABLE';
GO

-- Verify Categories data
SELECT * FROM Categories;
GO

-- Verify Common Queries data
SELECT * FROM CommonQueries;
GO
