# PowerShell script to setup database connection for the chatbot application
param(
    [string]$ServerName = "PRANAV\SQLEXPRESS",
    [switch]$UseWindowsAuth = $true
)

Write-Host "Setting up database connection for Support Chatbot..." -ForegroundColor Green
Write-Host "Server: $ServerName" -ForegroundColor Yellow
Write-Host "Authentication: $(if($UseWindowsAuth) {'Windows'} else {'SQL Server'})" -ForegroundColor Yellow

try {
    # Load SQL Server assembly
    Add-Type -AssemblyName "System.Data"
    
    # Test SQL Server connection first
    Write-Host "`nTesting SQL Server connection..." -ForegroundColor Yellow
    
    if ($UseWindowsAuth) {
        $connectionString = "Server=$ServerName;Integrated Security=true;TrustServerCertificate=true;Connection Timeout=30;"
    } else {
        $connectionString = "Server=$ServerName;User Id=sa;Password=YourPassword123;TrustServerCertificate=true;Connection Timeout=30;"
    }
    
    $connection = New-Object System.Data.SqlClient.SqlConnection($connectionString)
    $connection.Open()
    
    Write-Host "✓ SQL Server connection successful!" -ForegroundColor Green
    
    # Create database
    Write-Host "`nCreating SupportChatbot database..." -ForegroundColor Yellow
    
    $createDbCommand = @"
IF NOT EXISTS (SELECT name FROM sys.databases WHERE name = 'SupportChatbot')
BEGIN
    CREATE DATABASE [SupportChatbot]
    PRINT 'Database SupportChatbot created successfully'
END
ELSE
BEGIN
    PRINT 'Database SupportChatbot already exists'
END
"@
    
    $command = New-Object System.Data.SqlClient.SqlCommand($createDbCommand, $connection)
    $result = $command.ExecuteNonQuery()
    Write-Host "✓ Database creation command executed" -ForegroundColor Green
    
    # Close connection and reconnect to the new database
    $connection.Close()
    
    if ($UseWindowsAuth) {
        $dbConnectionString = "Server=$ServerName;Database=SupportChatbot;Integrated Security=true;TrustServerCertificate=true;Connection Timeout=30;"
    } else {
        $dbConnectionString = "Server=$ServerName;Database=SupportChatbot;User Id=sa;Password=YourPassword123;TrustServerCertificate=true;Connection Timeout=30;"
    }
    
    $dbConnection = New-Object System.Data.SqlClient.SqlConnection($dbConnectionString)
    $dbConnection.Open()
    
    Write-Host "✓ Connected to SupportChatbot database" -ForegroundColor Green
    
    # Create tables
    Write-Host "`nCreating database tables..." -ForegroundColor Yellow
    
    $createTablesScript = Get-Content "create_database_windows.sql" -Raw
    # Remove the USE statements since we're already connected to the right database
    $createTablesScript = $createTablesScript -replace "USE \[master\].*?GO", ""
    $createTablesScript = $createTablesScript -replace "USE \[SupportChatbot\].*?GO", ""
    
    # Split by GO statements and execute each batch
    $batches = $createTablesScript -split "GO"
    
    foreach ($batch in $batches) {
        $batch = $batch.Trim()
        if ($batch -and $batch.Length -gt 0) {
            try {
                $batchCommand = New-Object System.Data.SqlClient.SqlCommand($batch, $dbConnection)
                $batchCommand.ExecuteNonQuery()
            } catch {
                # Some batches might fail if tables already exist, that's OK
                Write-Host "Note: $($_.Exception.Message)" -ForegroundColor Yellow
            }
        }
    }
    
    Write-Host "✓ Database tables created/verified" -ForegroundColor Green
    
    # Test final connection with the app's connection string
    Write-Host "`nTesting final application connection..." -ForegroundColor Yellow
    
    $dbConnection.Close()
    
    # Test the connection that the app will use
    $testConnection = New-Object System.Data.SqlClient.SqlConnection($dbConnectionString)
    $testConnection.Open()
    
    $testCommand = New-Object System.Data.SqlClient.SqlCommand("SELECT COUNT(*) FROM Categories", $testConnection)
    $categoryCount = $testCommand.ExecuteScalar()
    
    Write-Host "✓ Application connection test successful!" -ForegroundColor Green
    Write-Host "✓ Found $categoryCount categories in database" -ForegroundColor Green
    
    $testConnection.Close()
    
    Write-Host "`n" + ("="*50) -ForegroundColor Green
    Write-Host "DATABASE SETUP COMPLETED SUCCESSFULLY!" -ForegroundColor Green
    Write-Host ("="*50) -ForegroundColor Green
    Write-Host "You can now run the Flask application with:" -ForegroundColor Yellow
    Write-Host "python app.py" -ForegroundColor White
    
} catch {
    Write-Host "`n❌ Error: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "`nTroubleshooting steps:" -ForegroundColor Yellow
    Write-Host "1. Verify SQL Server Express is running:" -ForegroundColor Yellow
    Write-Host "   Get-Service -Name 'MSSQL`$SQLEXPRESS'" -ForegroundColor White
    Write-Host "2. Check if the server name is correct:" -ForegroundColor Yellow
    Write-Host "   Try: $ServerName" -ForegroundColor White
    Write-Host "3. Verify Windows Authentication is enabled" -ForegroundColor Yellow
    Write-Host "4. Try running as Administrator" -ForegroundColor Yellow
    
    if (!$UseWindowsAuth) {
        Write-Host "5. If using SQL Authentication, verify sa account is enabled" -ForegroundColor Yellow
    }
}
