# =============================================================================
# CHATBOT APPLICATION - OPS DEPLOYMENT VERIFICATION SCRIPT (PowerShell)
# =============================================================================

Write-Host "CHATBOT APPLICATION - DEPLOYMENT VERIFICATION" -ForegroundColor Cyan
Write-Host "Date: $(Get-Date)"
Write-Host "Host: $env:COMPUTERNAME"
Write-Host ""

$TotalChecks = 0
$PassedChecks = 0

function Write-Success {
    param([string]$Message)
    Write-Host "[PASS] $Message" -ForegroundColor Green
    $script:PassedChecks++
}

function Write-Fail {
    param([string]$Message)
    Write-Host "[FAIL] $Message" -ForegroundColor Red
}

function Write-Warn {
    param([string]$Message)
    Write-Host "[WARN] $Message" -ForegroundColor Yellow
}

# =============================================================================
# 1. VERIFY SYSTEM REQUIREMENTS
# =============================================================================
Write-Host "1. CHECKING SYSTEM REQUIREMENTS" -ForegroundColor Yellow
Write-Host "--------------------------------"

$TotalChecks += 3

# Check Docker
try {
    $dockerVersion = docker --version
    Write-Success "Docker installed: $dockerVersion"
}
catch {
    Write-Fail "Docker not found or not working"
    exit 1
}

# Check Docker Compose
try {
    $composeVersion = docker-compose --version
    Write-Success "Docker Compose installed: $composeVersion"
}
catch {
    Write-Fail "Docker Compose not found or not working"
    exit 1
}

# Check Docker daemon
try {
    docker info | Out-Null
    Write-Success "Docker daemon running"
}
catch {
    Write-Fail "Docker daemon not running"
    exit 1
}

Write-Host ""

# =============================================================================
# 2. VERIFY PROJECT FILES
# =============================================================================
Write-Host "2. CHECKING PROJECT FILES" -ForegroundColor Yellow
Write-Host "--------------------------"

$RequiredFiles = @(
    "app.py",
    "config.py", 
    "database.py",
    "requirements.txt",
    "Dockerfile",
    "docker-compose.yml"
)

$TotalChecks += $RequiredFiles.Count

foreach ($file in $RequiredFiles) {
    if (Test-Path $file) {
        Write-Success "Found: $file"
    }
    else {
        Write-Fail "Missing: $file"
        exit 1
    }
}

Write-Host ""

# =============================================================================
# 3. VERIFY DOCKER CONFIGURATION
# =============================================================================
Write-Host "3. VERIFYING DOCKER CONFIGURATION" -ForegroundColor Yellow
Write-Host "---------------------------------"

$TotalChecks += 1

# Validate docker-compose.yml
try {
    docker-compose config | Out-Null
    if ($LASTEXITCODE -eq 0) {
        Write-Success "docker-compose.yml syntax valid"
    }
    else {
        Write-Fail "docker-compose.yml has syntax errors"
        exit 1
    }
}
catch {
    Write-Fail "docker-compose.yml validation failed"
    exit 1
}

Write-Host ""

# =============================================================================
# 4. CALCULATE READINESS
# =============================================================================
Write-Host "4. DEPLOYMENT READINESS SUMMARY" -ForegroundColor Yellow
Write-Host "================================"

$readinessPercent = [math]::Round(($PassedChecks * 100) / $TotalChecks)

Write-Host ""
Write-Host "READINESS SCORE: $PassedChecks/$TotalChecks ($readinessPercent%)"
Write-Host ""

if ($readinessPercent -ge 90) {
    Write-Host "DEPLOYMENT READY - All critical checks passed" -ForegroundColor Green
    Write-Host ""
    Write-Host "NEXT STEPS FOR OPS TEAM:" -ForegroundColor Green
    Write-Host "1. Copy project files to production server"
    Write-Host "2. Configure .env file with production settings"
    Write-Host "3. Run: docker-compose up -d"
    Write-Host "4. Verify: curl http://localhost:5000/health"
    Write-Host "5. Configure reverse proxy for SSL"
    Write-Host ""
    exit 0
}
else {
    Write-Host "NOT READY - Issues must be resolved" -ForegroundColor Red
    exit 1
}
