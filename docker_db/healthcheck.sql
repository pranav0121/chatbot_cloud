-- Simple health check for MSSQL
SELECT 1 AS HealthCheck, GETDATE() AS CheckedAt;
