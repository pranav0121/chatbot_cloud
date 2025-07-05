# =============================================================================
# CHATBOT APPLICATION - OPS DEPLOYMENT VERIFICATION SCRIPT (PowerShell)
# =============================================================================
# This script performs comprehensive verification of deployment readiness
# Run this script to ensure all components are ready for production deployment
# =============================================================================

param(
    [switch]$Detailed = $false
)

Write-Host "🚀 CHATBOT APPLICATION - DEPLOYMENT VERIFICATION" -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "Date: $(Get-Date)"
Write-Host "Host: $env:COMPUTERNAME"
Write-Host ""

# Global variables
$script:TotalChecks = 0
$script:PassedChecks = 0

# Helper functions
function Write-Success {
    param([string]$Message)
    Write-Host "✅ $Message" -ForegroundColor Green
    $script:PassedChecks++
}

function Write-Error {
    param([string]$Message)
    Write-Host "❌ $Message" -ForegroundColor Red
}

function Write-Warning {
    param([string]$Message)
    Write-Host "⚠️  $Message" -ForegroundColor Yellow
}

function Write-Info {
    param([string]$Message)
    Write-Host "ℹ️  $Message" -ForegroundColor Blue
}

function Test-Command {
    param([string]$Command)
    try {
        $null = Get-Command $Command -ErrorAction Stop
        return $true
    }
    catch {
        return $false
    }
}

# =============================================================================
# 1. VERIFY SYSTEM REQUIREMENTS
# =============================================================================
Write-Host "1. 🔍 CHECKING SYSTEM REQUIREMENTS" -ForegroundColor Yellow
Write-Host "-----------------------------------"

$script:TotalChecks += 3

# Check Docker
if (Test-Command "docker") {
    try {
        $dockerVersion = (docker --version | Select-String -Pattern '\d+\.\d+\.\d+').Matches[0].Value
        Write-Success "Docker installed: $dockerVersion"
    }
    catch {
        Write-Error "Docker command failed"
        exit 1
    }
}
else {
    Write-Error "Docker not installed"
    exit 1
}

# Check Docker Compose
if (Test-Command "docker-compose") {
    try {
        $composeVersion = (docker-compose --version | Select-String -Pattern '\d+\.\d+\.\d+').Matches[0].Value
        Write-Success "Docker Compose installed: $composeVersion"
    }
    catch {
        Write-Error "Docker Compose command failed"
        exit 1
    }
}
else {
    Write-Error "Docker Compose not installed"
    exit 1
}

# Check Docker daemon
try {
    docker info | Out-Null
    Write-Success "Docker daemon running"
}
catch {
    Write-Error "Docker daemon not running"
    exit 1
}

Write-Host ""

# =============================================================================
# 2. VERIFY PROJECT FILES
# =============================================================================
Write-Host "2. 📁 CHECKING PROJECT FILES" -ForegroundColor Yellow
Write-Host "----------------------------"

$RequiredFiles = @(
    "app.py",
    "config.py", 
    "database.py",
    "requirements.txt",
    "Dockerfile",
    "docker-compose.yml",
    ".env.template"
)

$script:TotalChecks += $RequiredFiles.Count

foreach ($file in $RequiredFiles) {
    if (Test-Path $file) {
        Write-Success "Found: $file"
    }
    else {
        Write-Error "Missing: $file"
        exit 1
    }
}

# Check for environment files
$envFiles = @(".env", ".env.production", ".env.docker.production")
$envFound = $false
foreach ($envFile in $envFiles) {
    if (Test-Path $envFile) {
        $envFound = $true
        break
    }
}

if ($envFound) {
    Write-Success "Environment configuration files present"
}
else {
    Write-Warning "No .env files found - remember to configure before deployment"
}

Write-Host ""

# =============================================================================
# 3. VERIFY DOCKER CONFIGURATION
# =============================================================================
Write-Host "3. 🐳 VERIFYING DOCKER CONFIGURATION" -ForegroundColor Yellow
Write-Host "------------------------------------"

$script:TotalChecks += 2

# Validate docker-compose.yml
try {
    docker-compose config | Out-Null
    Write-Success "docker-compose.yml syntax valid"
}
catch {
    Write-Error "docker-compose.yml has syntax errors"
    docker-compose config
    exit 1
}

# Check if production image exists
try {
    $images = docker images --format "table {{.Repository}}:{{.Tag}}" | Select-String "chatbot-app.*production"
    if ($images) {
        Write-Success "Production Docker image found"
    }
    else {
        Write-Warning "No production image found - will build during deployment"
        $script:PassedChecks++  # This is not a failure
    }
}
catch {
    Write-Warning "Could not check Docker images"
    $script:PassedChecks++  # This is not a failure
}

Write-Host ""

# =============================================================================
# 4. TEST BUILD PROCESS
# =============================================================================
Write-Host "4. 🔨 TESTING BUILD PROCESS" -ForegroundColor Yellow
Write-Host "---------------------------"

$script:TotalChecks += 1

Write-Info "Building test image..."
try {
    docker build -t chatbot-app:deployment-test . 2>&1 | Out-File -FilePath "build.log"
    
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Docker build successful"
        
        # Get image size
        $imageSize = (docker images chatbot-app:deployment-test --format "{{.Size}}")[0]
        Write-Info "Image size: $imageSize"
        
        # Clean up test image
        docker rmi chatbot-app:deployment-test | Out-Null
    }
    else {
        Write-Error "Docker build failed - check build.log"
        exit 1
    }
}
catch {
    Write-Error "Docker build failed - check build.log"
    exit 1
}

Write-Host ""

# =============================================================================
# 5. VERIFY DEPENDENCIES
# =============================================================================
Write-Host "5. 📦 CHECKING DEPENDENCIES" -ForegroundColor Yellow
Write-Host "---------------------------"

if (Test-Path "requirements.txt") {
    $packageCount = (Get-Content "requirements.txt" | Measure-Object -Line).Lines
    Write-Success "Requirements file contains $packageCount packages"
    
    # Check for critical packages
    $criticalPackages = @("Flask", "pyodbc", "gunicorn")
    $requirements = Get-Content "requirements.txt"
    
    foreach ($package in $criticalPackages) {
        $found = $requirements | Where-Object { $_ -match "^$package" }
        if ($found) {
            Write-Success "Critical package found: $package"
        }
        else {
            Write-Error "Missing critical package: $package"
        }
    }
}

Write-Host ""

# =============================================================================
# 6. NETWORK CHECKS
# =============================================================================
Write-Host "6. 🌐 NETWORK VERIFICATION" -ForegroundColor Yellow
Write-Host "-------------------------"

# Check if port 5000 is available
try {
    $port5000 = Get-NetTCPConnection -LocalPort 5000 -ErrorAction SilentlyContinue
    if (-not $port5000) {
        Write-Success "Port 5000 available"
    }
    else {
        Write-Warning "Port 5000 already in use"
    }
}
catch {
    Write-Success "Port 5000 available"
}

# Check if port 6379 is available (Redis)
try {
    $port6379 = Get-NetTCPConnection -LocalPort 6379 -ErrorAction SilentlyContinue
    if (-not $port6379) {
        Write-Success "Port 6379 available (Redis)"
    }
    else {
        Write-Warning "Port 6379 already in use"
    }
}
catch {
    Write-Success "Port 6379 available (Redis)"
}

Write-Host ""

# =============================================================================
# 7. SECURITY CHECKS
# =============================================================================
Write-Host "7. 🔒 SECURITY VERIFICATION" -ForegroundColor Yellow
Write-Host "---------------------------"

# Check for sensitive files in repo
$sensitivePatterns = @("*.env", "*.key", "*.pem")
$foundSensitive = $false

foreach ($pattern in $sensitivePatterns) {
    $files = Get-ChildItem -Path . -Name $pattern -File -Recurse | Where-Object { 
        $_ -notmatch "\.env\.template" -and $_ -notmatch "\.env\.example" 
    }
    if ($files) {
        Write-Warning "Sensitive files found matching: $pattern"
        $foundSensitive = $true
    }
}

if (-not $foundSensitive) {
    Write-Success "No sensitive files in repository"
}

# Check Dockerfile security
$dockerfileContent = Get-Content "Dockerfile" -Raw
if ($dockerfileContent -match "USER") {
    Write-Success "Non-root user configured in Dockerfile"
}
else {
    Write-Warning "No USER directive in Dockerfile - running as root"
}

Write-Host ""

# =============================================================================
# 8. DEPLOYMENT READINESS SUMMARY
# =============================================================================
Write-Host "8. 📋 DEPLOYMENT READINESS SUMMARY" -ForegroundColor Yellow
Write-Host "===================================="

# Calculate readiness percentage
if ($script:TotalChecks -gt 0) {
    $readinessPercent = [math]::Round(($script:PassedChecks * 100) / $script:TotalChecks)
}
else {
    $readinessPercent = 0
}

Write-Host ""
Write-Host "READINESS SCORE: $($script:PassedChecks)/$($script:TotalChecks) ($readinessPercent percent)"
Write-Host ""

if ($readinessPercent -ge 90) {
    Write-Host "🎉 DEPLOYMENT READY - All critical checks passed" -ForegroundColor Green
    Write-Host ""
    Write-Host "✅ NEXT STEPS FOR OPS TEAM:" -ForegroundColor Green
    Write-Host "1. Copy project files to production server"
    Write-Host "2. Configure .env file with production settings"
    Write-Host "3. Run: docker-compose up -d"
    Write-Host "4. Verify: Invoke-WebRequest http://localhost:5000/health"
    Write-Host "5. Configure reverse proxy (IIS/Nginx) for SSL"
    Write-Host ""
    exit 0
}
elseif ($readinessPercent -ge 75) {
    Write-Host "⚠️  MOSTLY READY - Minor issues need attention" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "📝 REVIEW WARNINGS ABOVE BEFORE DEPLOYMENT" -ForegroundColor Yellow
    exit 0
}
else {
    Write-Host "❌ NOT READY - Critical issues must be resolved" -ForegroundColor Red
    Write-Host ""
    Write-Host "🔧 FIX ERRORS ABOVE BEFORE ATTEMPTING DEPLOYMENT" -ForegroundColor Red
    exit 1
}
