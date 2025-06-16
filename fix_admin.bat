@echo off
echo === MSSQL Admin User Fix ===
echo.

echo Running SQL script to fix admin user...
echo.

REM Try to run the SQL script using sqlcmd
sqlcmd -S "PRANAV\SQLEXPRESS" -E -d "SupportChatbot" -i "fix_admin_mssql.sql"

if %ERRORLEVEL% EQU 0 (
    echo.
    echo === SUCCESS ===
    echo Admin user has been fixed in MSSQL database!
    echo.
    echo Admin Credentials:
    echo Email: admin@youcloudtech.com
    echo Password: admin123
    echo.
    echo Admin URL: http://localhost:5000/auth/admin/login
    echo.
    echo You can now login to the admin panel!
) else (
    echo.
    echo === ERROR ===
    echo Failed to run SQL script. Please check:
    echo 1. SQL Server is running
    echo 2. SupportChatbot database exists
    echo 3. You have permissions to access the database
    echo.
    echo Alternative: Open SQL Server Management Studio and run fix_admin_mssql.sql manually
)

echo.
pause
