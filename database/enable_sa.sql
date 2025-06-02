-- Enable SA login
ALTER LOGIN [sa] ENABLE;
GO

-- Set new password for SA
ALTER LOGIN [sa] WITH PASSWORD = 'YourPassword123';
GO

-- Grant necessary permissions to SA
ALTER SERVER ROLE [sysadmin] ADD MEMBER [sa];
GO
