# Chatbot API Endpoints List

## Public APIs (No Authentication Required)

### Categories
- `GET /api/categories` - Get all support categories
- `GET /api/common-queries/{category_id}` - Get common queries for category

### Tickets
- `POST /api/tickets` - Create new ticket
- `POST /api/tickets/with-attachment` - Create ticket with file attachment
- `GET /api/tickets/{ticket_id}` - Get ticket details

### Messages
- `GET /api/tickets/{ticket_id}/messages` - Get messages for ticket
- `POST /api/tickets/{ticket_id}/messages` - Add message to ticket
- `POST /api/tickets/{ticket_id}/messages/with-attachment` - Add message with attachment

### File Upload
- `POST /api/upload` - Upload file

### Feedback
- `POST /api/feedback` - Submit feedback/rating

### Health Check
- `GET /api/database/test` - Test system health

---

## Admin APIs (Authentication Required)

**Admin Login Credentials:**
- **Email:** `admin@youcloudtech.com`
- **Password:** `admin123` or `SecureAdmin123!`
- **Login URL:** `/admin/login` or `/admin-login`

### Dashboard
- `GET /api/admin/dashboard-stats` - Get dashboard statistics
- `GET /api/admin/recent-activity` - Get recent activity
- `GET /api/admin/analytics` - Get analytics data

### Admin Tickets
- `GET /api/admin/tickets` - Get all tickets (admin view)
- `GET /api/admin/tickets/{ticket_id}` - Get ticket details (admin view)
- `PUT /api/admin/tickets/{ticket_id}/status` - Update ticket status
- `GET /api/admin/active-conversations` - Get active conversations

### Urban Vyapari Integration (NEW)
- `POST /api/generate-uv-token` - Generate access token for Urban Vyapari
- `GET /tickets-portal` - Web portal for tickets (token-based access)
- `GET /api/admin/tickets` (with token) - Get tickets with token authentication
- `GET /api/admin/dashboard-stats` (with token) - Get stats with token authentication

### FAQ Management
- `GET /api/faq-categories` - Get FAQ categories
- `POST /api/faq-categories` - Create FAQ category
- `PUT /api/faq-categories/{category_id}` - Update FAQ category
- `DELETE /api/faq-categories/{category_id}` - Delete FAQ category

---

## Authentication Information

### For Admin APIs:
1. **Login first** at `/admin/login` or `/admin-login`
2. **Credentials:**
   - Email: `admin@youcloudtech.com`
   - Password: `admin123` or `SecureAdmin123!`
3. **Session-based authentication** - login creates admin session
4. **Auto-creation:** Admin user is created automatically if it doesn't exist
5. **Logout:** Use `/admin/logout` to end admin session

### For Urban Vyapari Integration (NEW):
1. **Token-based authentication** for external integration
2. **API Key Required:** `UV_CHATBOT_API_KEY_2024` (shared with Urban Vyapari)
3. **Token Generation:** POST `/api/generate-uv-token` with admin credentials
4. **Token Usage:** Add `?token=JWT_TOKEN` to API calls or use `Authorization: Bearer JWT_TOKEN`
5. **Query Parameters:** Support for filtering with `?status=open&priority=high&category=technical`
6. **Web Portal:** Direct access via `/tickets-portal?token=JWT_TOKEN`

### For Public APIs:
- No authentication required
- Can be used directly by external applications

---

## Total: 23 API Endpoints
- **Public APIs:** 10 endpoints
- **Admin APIs:** 9 endpoints  
- **Urban Vyapari Integration:** 4 new endpoints

---

## Urban Vyapari Integration Guide

### Quick Integration for Urban Vyapari Team:

1. **Get Access Token:**
```javascript
POST /api/generate-uv-token
{
  "uv_api_key": "UV_CHATBOT_API_KEY_2024",
  "admin_id": "your_admin_id", 
  "admin_name": "Admin Name",
  "admin_email": "admin@urbanvyapari.com"
}
```

2. **Use Token in API Calls:**
```
GET /api/admin/tickets?token=JWT_TOKEN&status=open&priority=high
GET /api/admin/dashboard-stats?token=JWT_TOKEN
```

3. **Direct Web Portal Access:**
```
http://localhost:5000/tickets-portal?token=JWT_TOKEN&status=open
```

4. **Supported Query Parameters:**
- `status=all|open|closed|pending|resolved`
- `priority=all|low|medium|high|critical`  
- `category=all|technical|billing|feature|bug`
- `limit=50` (pagination)
- `offset=0` (pagination)
