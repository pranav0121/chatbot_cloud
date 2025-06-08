# YouCloudPay Chatbot - PowerShell Startup Script

Write-Host "================================" -ForegroundColor Cyan
Write-Host "YouCloudPay Chatbot - Quick Start" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan

# Check if Python is available
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python detected: $pythonVersion" -ForegroundColor Green
}
catch {
    Write-Host "❌ ERROR: Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Python 3.9+ and try again" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Install dependencies
Write-Host "`n📦 Installing dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Dependencies installed successfully" -ForegroundColor Green
}
else {
    Write-Host "❌ Failed to install dependencies" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Set environment variables
$env:FLASK_APP = "app.py"
$env:FLASK_ENV = "development"

# Run the startup script
Write-Host "`n🚀 Starting YouCloudPay Chatbot..." -ForegroundColor Cyan
python start.py

Read-Host "`nPress Enter to exit"
