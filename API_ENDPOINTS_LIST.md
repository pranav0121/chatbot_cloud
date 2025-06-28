# Complete Chatbot API Reference

## Overview
**Base URL:** `http://your-domain.com`  
**Content-Type:** `application/json` (unless specified otherwise)

## Public APIs (No Authentication Required)

### Categories
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/categories` | Get all support categories |
| GET | `/api/common-queries/{category_id}` | Get common queries for a category |

### Tickets
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/tickets` | Create new ticket |
| POST | `/api/tickets/with-attachment` | Create ticket with file attachment |
| GET | `/api/tickets/{ticket_id}` | Get ticket details and messages |

### Messages
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/tickets/{ticket_id}/messages` | Get all messages for a ticket |
| POST | `/api/tickets/{ticket_id}/messages` | Add message to ticket |
| POST | `/api/tickets/{ticket_id}/messages/with-attachment` | Add message with file attachment |

### File Upload
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/upload` | Upload file |

### Feedback
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/feedback` | Submit ticket feedback/rating |

### System Health
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/database/test` | Test system health and database connection |

---

## Private APIs (Admin Authentication Required)

### Dashboard & Statistics
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/admin/dashboard-stats` | Get dashboard statistics |
| GET | `/api/admin/recent-activity` | Get recent activity feed |
| GET | `/api/admin/analytics` | Get analytics data |

### Admin Ticket Management
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/admin/tickets` | Get all tickets (admin view) |
| GET | `/api/admin/tickets/{ticket_id}` | Get ticket details (admin view) |
| PUT | `/api/admin/tickets/{ticket_id}/status` | Update ticket status |
| GET | `/api/admin/active-conversations` | Get active chat conversations |

### FAQ Management
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/faq-categories` | Get all FAQ categories |
| POST | `/api/faq-categories` | Create new FAQ category |
| PUT | `/api/faq-categories/{category_id}` | Update FAQ category |
| DELETE | `/api/faq-categories/{category_id}` | Delete FAQ category |

---

## Request/Response Formats

### Create Ticket (POST /api/tickets)
**Request:**
```json
{
  "name": "string",
  "email": "string", 
  "category_id": "integer",
  "subject": "string",
  "message": "string",
  "priority": "low|medium|high|critical"
}
```

### Create Ticket with Attachment (POST /api/tickets/with-attachment)
**Content-Type:** `multipart/form-data`
**Form Fields:**
- `name` (required)
- `email` (required)
- `category_id` (required)
- `subject` (optional)
- `message` (required)
- `file` (optional)

### Add Message (POST /api/tickets/{ticket_id}/messages)
**Request:**
```json
{
  "content": "string",
  "user_id": "integer",
  "is_admin": "boolean"
}
```

### Submit Feedback (POST /api/feedback)
**Request:**
```json
{
  "ticket_id": "integer",
  "rating": "integer (1-5)",
  "comment": "string"
}
```

### Update Ticket Status (PUT /api/admin/tickets/{ticket_id}/status)
**Request:**
```json
{
  "status": "open|in_progress|resolved|closed",
  "resolution_notes": "string"
}
```

### Create FAQ Category (POST /api/faq-categories)
**Request:**
```json
{
  "name": "string",
  "description": "string",
  "icon": "string",
  "color": "string"
}
```

---

## Standard Response Formats

### Success Response
```json
{
  "status": "success",
  "message": "Operation completed successfully",
  "data": {}
}
```

### Error Response
```json
{
  "error": "Error description",
  "details": "Additional details (optional)"
}
```

### Ticket Response
```json
{
  "ticket_id": "integer",
  "subject": "string",
  "status": "string",
  "category": "string",
  "user_name": "string",
  "user_email": "string",
  "created_at": "datetime",
  "updated_at": "datetime",
  "messages": []
}
```

### Categories Response
```json
[
  {
    "id": "integer",
    "name": "string"
  }
]
```

### Dashboard Stats Response
```json
{
  "totalTickets": "integer",
  "pendingTickets": "integer", 
  "resolvedTickets": "integer",
  "activeChats": "integer"
}
```

---

## HTTP Status Codes
- `200` - Success
- `201` - Created
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden (Admin required)
- `404` - Not Found
- `500` - Internal Server Error

---

## File Upload Restrictions
- Allowed file types: Check application configuration
- Maximum file size: Check application limits
- Files stored in: `/static/uploads/` directory
- Content-Type: `multipart/form-data`

---

## Authentication Notes
- **Public APIs:** No authentication required
- **Admin APIs:** Require admin session/login
- **Session-based:** Uses Flask session management
- **User Context:** Some endpoints use current logged-in user context
