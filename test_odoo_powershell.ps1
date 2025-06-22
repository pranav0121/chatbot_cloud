# PowerShell script to test Odoo API integration
# Run this in a NEW PowerShell window while keeping Flask app running

Write-Host "🚀 Testing Odoo API Integration" -ForegroundColor Green
Write-Host "=================================" -ForegroundColor Green

# Test 1: Connection Test
Write-Host "`n1️⃣ Testing Odoo Connection..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "http://localhost:5000/api/odoo/test-connection" -Method GET
    Write-Host "✅ Connection Test Result:" -ForegroundColor Green
    $response | ConvertTo-Json -Depth 3
}
catch {
    Write-Host "❌ Connection test failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 2: Create Customer
Write-Host "`n2️⃣ Creating Test Customer in Odoo..." -ForegroundColor Yellow
$customerData = @{
    name    = "API Test Customer $(Get-Date -Format 'yyyy-MM-dd HH:mm')"
    email   = "testcustomer$(Get-Random)@example.com"
    phone   = "+1234567890"
    company = "Test Company API"
} | ConvertTo-Json

try {
    $customerResponse = Invoke-RestMethod -Uri "http://localhost:5000/api/odoo/customers" -Method POST -Body $customerData -ContentType "application/json"
    Write-Host "✅ Customer Created:" -ForegroundColor Green
    $customerResponse | ConvertTo-Json -Depth 3
    $customerId = $customerResponse.data.id
}
catch {
    Write-Host "❌ Customer creation failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 3: Create Ticket
if ($customerId) {
    Write-Host "`n3️⃣ Creating Test Ticket in Odoo..." -ForegroundColor Yellow
    $ticketData = @{
        name        = "API Test Ticket $(Get-Date -Format 'yyyy-MM-dd HH:mm')"
        description = "This is a test ticket created via API integration from PowerShell"
        customer_id = $customerId
        priority    = "1"
        tag_ids     = @("api-test")
    } | ConvertTo-Json

    try {
        $ticketResponse = Invoke-RestMethod -Uri "http://localhost:5000/api/odoo/tickets" -Method POST -Body $ticketData -ContentType "application/json"
        Write-Host "✅ Ticket Created:" -ForegroundColor Green
        $ticketResponse | ConvertTo-Json -Depth 3
    }
    catch {
        Write-Host "❌ Ticket creation failed: $($_.Exception.Message)" -ForegroundColor Red
    }
}

# Test 4: List Recent Customers
Write-Host "`n4️⃣ Listing Recent Customers..." -ForegroundColor Yellow
try {
    $customersResponse = Invoke-RestMethod -Uri "http://localhost:5000/api/odoo/customers?limit=3" -Method GET
    Write-Host "✅ Recent Customers:" -ForegroundColor Green
    $customersResponse | ConvertTo-Json -Depth 3
}
catch {
    Write-Host "❌ Listing customers failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 5: List Recent Tickets
Write-Host "`n5️⃣ Listing Recent Tickets..." -ForegroundColor Yellow
try {
    $ticketsResponse = Invoke-RestMethod -Uri "http://localhost:5000/api/odoo/tickets?limit=3" -Method GET
    Write-Host "✅ Recent Tickets:" -ForegroundColor Green
    $ticketsResponse | ConvertTo-Json -Depth 3
}
catch {
    Write-Host "❌ Listing tickets failed: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`n🎯 Testing Complete!" -ForegroundColor Green
Write-Host "=================================" -ForegroundColor Green
Write-Host "`n📋 Next Steps:" -ForegroundColor Cyan
Write-Host "1. Check your Odoo Online for new records:" -ForegroundColor White
Write-Host "   • Customers: https://youcloudpay.odoo.com/web#action=base.action_partner_form" -ForegroundColor Blue
Write-Host "   • Tickets: https://youcloudpay.odoo.com/web#action=helpdesk.helpdesk_ticket_action_main_tree" -ForegroundColor Blue
Write-Host "2. Integration is working if you see the test records above! ✅" -ForegroundColor White
