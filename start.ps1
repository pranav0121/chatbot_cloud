# Customer Support System Startup Script
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "   Customer Support System Startup Script" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Check if Python is installed
try {
    $pythonVersion = python --version 2>$null
    Write-Host "✓ Python is installed: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Python 3.7+ and try again" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Install dependencies
Write-Host ""
Write-Host "Installing dependencies..." -ForegroundColor Yellow
try {
    pip install -r requirements.txt
    Write-Host "✓ Dependencies installed successfully" -ForegroundColor Green
} catch {
    Write-Host "WARNING: Some packages might not have installed correctly" -ForegroundColor Yellow
    Write-Host "You may need to install them manually" -ForegroundColor Yellow
}

# Start the application
Write-Host ""
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "Starting Customer Support System..." -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "User Interface will be available at:" -ForegroundColor Green
Write-Host "  http://localhost:5000" -ForegroundColor White
Write-Host ""
Write-Host "Admin Dashboard will be available at:" -ForegroundColor Green
Write-Host "  http://localhost:5000/admin" -ForegroundColor White
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

try {
    python app.py
} catch {
    Write-Host ""
    Write-Host "Application encountered an error:" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
} finally {
    Write-Host ""
    Write-Host "Application has stopped." -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
}
