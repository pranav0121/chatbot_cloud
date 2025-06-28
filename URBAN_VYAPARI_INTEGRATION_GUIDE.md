
# Urban Vyapari Integration Guide

## 🔧 Quick Setup

### 1. API Key Configuration
```javascript
const UV_API_KEY = "UV_CHATBOT_API_KEY_2024";
const CHATBOT_URL = "http://localhost:5000";
```

### 2. Get Access Token
```javascript
async function getAccessToken(adminId, adminName, adminEmail) {
    const response = await fetch(`${CHATBOT_URL}/api/generate-uv-token`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            uv_api_key: UV_API_KEY,
            admin_id: adminId,
            admin_name: adminName,
            admin_email: adminEmail
        })
    });
    
    const data = await response.json();
    return data.success ? data.access_token : null;
}
```

### 3. Use Token for API Calls
```javascript
// Get tickets with filters
const tickets = await fetch(`${CHATBOT_URL}/api/admin/tickets?token=${token}&status=open&priority=high`);

// Get dashboard stats
const stats = await fetch(`${CHATBOT_URL}/api/admin/dashboard-stats?token=${token}`);
```

### 4. Open Web Portal
```javascript
function openTicketsPortal(token) {
    const url = `${CHATBOT_URL}/tickets-portal?token=${token}&status=open`;
    window.open(url, '_blank');
}
```

## 📋 Available Endpoints

1. **Token Generation:** `POST /api/generate-uv-token`
2. **Tickets API:** `GET /api/admin/tickets?token=TOKEN`
3. **Dashboard Stats:** `GET /api/admin/dashboard-stats?token=TOKEN`
4. **Web Portal:** `GET /tickets-portal?token=TOKEN`

## 🔍 Query Parameters

- `status=all|open|closed|pending|resolved`
- `priority=all|low|medium|high|critical`
- `category=all|technical|billing|feature|bug`
- `limit=50` (max 100)
- `offset=0`

## ✅ Integration Checklist

- [ ] API key configured
- [ ] Token generation working
- [ ] Tickets API accessible
- [ ] Dashboard stats working
- [ ] Web portal loading
- [ ] Menu item added to Urban Vyapari admin panel

## 🔐 Security Notes

- Tokens expire after 24 hours
- Use HTTPS in production
- Store tokens securely
- Regenerate tokens when needed

## 📞 Support

For integration support, contact the chatbot development team.
