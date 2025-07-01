# FLASK SUPER ADMIN DASHBOARD URLS

## Complete URL Reference for YouCloud Support Chatbot System

### 🔐 **AUTHENTICATION**

- **Admin Login**: http://127.0.0.1:5000/auth/admin/login
  - Credentials: `admin@youcloudtech.com` / `admin123`
  - Alternative: `admin@supportcenter.com` / `admin123`
  - Alternative: `admin@chatbot.com` / `admin123`

### 🏠 **MAIN DASHBOARDS**

- **Admin Dashboard**: http://127.0.0.1:5000/admin
- **Super Admin Dashboard**: http://127.0.0.1:5000/super-admin
- **Super Admin Dashboard (Alt)**: http://127.0.0.1:5000/super-admin/dashboard

### 📊 **ESCALATION SYSTEM**

- **Escalation Dashboard**: http://127.0.0.1:5000/super-admin/escalation
- **Partners Management**: http://127.0.0.1:5000/super-admin/partners

### 📈 **SLA & MONITORING**

- **SLA Dashboard**: http://127.0.0.1:5000/super-admin/sla-dashboard
- **Logs Dashboard**: http://127.0.0.1:5000/super-admin/logs
- **Audit Dashboard**: http://127.0.0.1:5000/super-admin/audit

### 🤖 **BOT CONFIGURATION**

- **Bot Config**: http://127.0.0.1:5000/super-admin/bot-config

### 🔗 **API ENDPOINTS**

#### Authentication APIs

- `POST /auth/admin/login` - Admin login
- `POST /auth/admin/logout` - Admin logout

#### Dashboard APIs

- `GET /super-admin/api/dashboard-metrics` - Main dashboard metrics
- `GET /super-admin/api/critical-alerts` - Critical alerts

#### Escalation APIs

- `GET /super-admin/api/escalation/dashboard` - Escalation dashboard data
- `POST /super-admin/api/escalation/force/{ticket_id}` - Force escalate ticket
  - Body: `{"level": 1, "comment": "Escalation reason"}`

#### Partners APIs

- `GET /super-admin/api/partners` - List all partners
- `POST /super-admin/api/partners` - Create new partner
- `PUT /super-admin/api/partners/{partner_id}` - Update partner
- `DELETE /super-admin/api/partners/{partner_id}` - Delete partner

#### Logs APIs

- `GET /super-admin/api/logs/timeline/{ticket_id}` - Ticket timeline
- `GET /super-admin/api/logs/search` - Search logs
- `GET /super-admin/api/audit/logs` - Audit logs

#### Bot Configuration APIs

- `GET /super-admin/api/bot/config` - Get bot configuration
- `POST /super-admin/api/bot/config` - Update bot configuration

### 🎯 **TESTING URLS**

#### Quick Test Links

- **Test Escalation**: http://127.0.0.1:5000/super-admin/escalation
- **Test Dashboard**: http://127.0.0.1:5000/super-admin/dashboard
- **Test Partners**: http://127.0.0.1:5000/super-admin/partners

### 📋 **ADMIN PANEL TICKETS**

- **Admin Tickets**: http://127.0.0.1:5000/admin (login required)
- **Tickets API**: Accessible after admin login via JavaScript on admin page

### 🔧 **SYSTEM STATUS**

- **Flask Server**: http://127.0.0.1:5000
- **Health Check**: Server responds to any GET request to base URL

### 📝 **WORKING CREDENTIALS**

```
Email: admin@youcloudtech.com
Password: admin123
Role: Super Admin
Access: Full system access including escalation management
```

### 🚀 **ESCALATION WORKFLOW**

1. Login: http://127.0.0.1:5000/auth/admin/login
2. Navigate to: http://127.0.0.1:5000/super-admin/escalation
3. Use force escalation API or dashboard controls
4. View results in real-time on dashboard

### ✅ **VERIFIED WORKING FEATURES**

- ✅ Admin authentication with session management
- ✅ Force escalation API with partner assignment
- ✅ Escalation dashboard showing correct ticket states
- ✅ Partner management (1 ICP partner, 1 YouCloud partner)
- ✅ SLA tracking and logging
- ✅ Real-time dashboard updates
- ✅ Admin panel tickets display

### 🛡️ **SECURITY NOTES**

- All super-admin routes require authentication
- Session-based security with admin_logged_in flag
- API endpoints return 401 for unauthorized access
- Database changes are properly committed and logged

### 📊 **CURRENT SYSTEM STATE**

- **Total Tickets**: 41+ active tickets
- **Escalated Tickets**: 5 tickets with escalation levels > 0
- **Partners**: 2 active partners (ICP + YouCloud)
- **SLA Logs**: Multiple escalation events tracked
- **Status**: Fully operational
