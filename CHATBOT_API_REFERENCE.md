# Chatbot API Reference Guide

## Overview
This document provides a comprehensive reference for integrating with the Chatbot API. The API supports ticket management, real-time messaging, file uploads, admin functions, and FAQ management.

**Base URL:** `http://your-domain.com`  
**API Version:** v1  
**Content-Type:** `application/json` (unless specified otherwise)

## Authentication
- **User Authentication:** Login required for user-specific endpoints
- **Admin Authentication:** Admin privileges required for admin endpoints
- **Session-based:** Uses Flask session management

## Core Data Models

### User
```json
{
  "UserID": "integer",
  "Name": "string",
  "Email": "string",
  "OrganizationName": "string",
  "Position": "string",
  "PriorityLevel": "low|medium|high|critical",
  "Phone": "string",
  "Department": "string",
  "PreferredLanguage": "string",
  "IsActive": "boolean",
  "IsAdmin": "boolean",
  "CreatedAt": "datetime"
}
```

### Ticket
```json
{
  "TicketID": "integer",
  "UserID": "integer",
  "CategoryID": "integer",
  "Subject": "string",
  "Priority": "low|medium|high|critical",
  "Status": "open|in_progress|resolved|closed",
  "OrganizationName": "string",
  "CreatedBy": "string",
  "AssignedTo": "integer",
  "CreatedAt": "datetime",
  "UpdatedAt": "datetime",
  "escalation_level": "integer",
  "resolution_method": "Bot|ICP|YouCloud",
  "bot_attempted": "boolean"
}
```

### Message
```json
{
  "MessageID": "integer",
  "TicketID": "integer",
  "SenderID": "integer",
  "Content": "string",
  "IsAdminReply": "boolean",
  "IsBotResponse": "boolean",
  "CreatedAt": "datetime",
  "attachments": "array of attachment objects"
}
```

### Category
```json
{
  "CategoryID": "integer",
  "Name": "string",
  "Team": "string",
  "CreatedAt": "datetime"
}
```

## Public API Endpoints

### 1. Categories

#### Get All Categories
```http
GET /api/categories
```
**Response:**
```json
[
  {
    "id": 1,
    "name": "Payments"
  },
  {
    "id": 2,
    "name": "Product Issues"
  }
]
```

#### Get Common Queries by Category
```http
GET /api/common-queries/{category_id}
```
**Response:**
```json
[
  {
    "id": 1,
    "question": "How do I update my payment method?",
    "solution": "You can update your payment method by going to..."
  }
]
```

### 2. Tickets

#### Create New Ticket
```http
POST /api/tickets
```
**Request Body:**
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "category_id": 1,
  "subject": "Payment Issue",
  "message": "I'm having trouble with my payment method",
  "priority": "medium"
}
```
**Response:**
```json
{
  "ticket_id": 123,
  "user_id": 456,
  "status": "success",
  "message": "Ticket created successfully"
}
```

#### Create Ticket with Attachment
```http
POST /api/tickets/with-attachment
Content-Type: multipart/form-data
```
**Form Data:**
- `name`: User's name
- `email`: User's email
- `category_id`: Category ID
- `subject`: Ticket subject
- `message`: Ticket message
- `file`: File attachment (optional)

**Response:**
```json
{
  "ticket_id": 123,
  "user_id": 456,
  "status": "success",
  "message": "Ticket created successfully"
}
```

#### Get Ticket Details
```http
GET /api/tickets/{ticket_id}
```
**Response:**
```json
{
  "id": 123,
  "subject": "Payment Issue",
  "status": "open",
  "category": "Payments",
  "user_name": "John Doe",
  "user_email": "john@example.com",
  "created_at": "2025-06-25T10:30:00Z",
  "updated_at": "2025-06-25T10:30:00Z",
  "messages": [
    {
      "content": "I'm having trouble with payment",
      "is_admin": false,
      "created_at": "2025-06-25T10:30:00Z",
      "attachments": []
    }
  ]
}
```

### 3. Messages

#### Get Messages for Ticket
```http
GET /api/tickets/{ticket_id}/messages
```
**Response:**
```json
[
  {
    "id": 1,
    "content": "I need help with my account",
    "is_admin": false,
    "created_at": "2025-06-25T10:30:00Z",
    "attachments": [
      {
        "id": 1,
        "original_name": "screenshot.png",
        "url": "/static/uploads/stored_filename.png",
        "file_size": 1024000,
        "mime_type": "image/png"
      }
    ]
  }
]
```

#### Add Message to Ticket
```http
POST /api/tickets/{ticket_id}/messages
```
**Request Body:**
```json
{
  "content": "Thank you for your message",
  "user_id": 456,
  "is_admin": false
}
```
**Response:**
```json
{
  "status": "success",
  "message_id": 789
}
```

#### Add Message with Attachment
```http
POST /api/tickets/{ticket_id}/messages/with-attachment
Content-Type: multipart/form-data
```
**Form Data:**
- `content`: Message content
- `user_id`: Sender ID
- `is_admin`: true/false
- `file`: File attachment (optional)

### 4. File Upload

#### Upload File
```http
POST /api/upload
Content-Type: multipart/form-data
```
**Form Data:**
- `file`: File to upload

**Response:**
```json
{
  "status": "success",
  "file_info": {
    "original_name": "document.pdf",
    "stored_name": "uuid_document.pdf",
    "file_size": 2048000,
    "mime_type": "application/pdf"
  }
}
```

### 5. Feedback

#### Submit Feedback
```http
POST /api/feedback
```
**Request Body:**
```json
{
  "ticket_id": 123,
  "rating": 5,
  "comment": "Great support!"
}
```
**Response:**
```json
{
  "status": "success",
  "message": "Feedback submitted successfully"
}
```

### 6. Database Health Check

#### Test Database Connection
```http
GET /api/database/test
```
**Response:**
```json
{
  "status": "success",
  "database": "connected",
  "tables": {
    "categories": 4,
    "tickets": 150,
    "users": 25
  },
  "message": "All database operations successful"
}
```

## Admin API Endpoints

### 1. Dashboard Statistics

#### Get Dashboard Stats
```http
GET /api/admin/dashboard-stats
```
**Authentication:** Admin required
**Response:**
```json
{
  "totalTickets": 150,
  "pendingTickets": 45,
  "resolvedTickets": 105,
  "activeChats": 12
}
```

#### Get Recent Activity
```http
GET /api/admin/recent-activity
```
**Authentication:** Admin required
**Response:**
```json
[
  {
    "icon": "fas fa-ticket-alt",
    "title": "New ticket #123",
    "description": "Payments - John Doe",
    "created_at": "2025-06-25T10:30:00Z"
  }
]
```

### 2. Ticket Management

#### Get All Tickets (Admin)
```http
GET /api/admin/tickets
```
**Authentication:** Admin required
**Response:**
```json
[
  {
    "id": 123,
    "subject": "Payment Issue",
    "category": "Payments",
    "user_name": "John Doe",
    "user_email": "john@example.com",
    "organization": "Acme Corp",
    "priority": "medium",
    "status": "open",
    "created_at": "2025-06-25T10:30:00Z"
  }
]
```

#### Get Ticket Details (Admin)
```http
GET /api/admin/tickets/{ticket_id}
```
**Authentication:** Admin required
**Response:** Same as public ticket details with additional admin fields

#### Update Ticket Status
```http
PUT /api/admin/tickets/{ticket_id}/status
```
**Authentication:** Admin required
**Request Body:**
```json
{
  "status": "resolved",
  "resolution_notes": "Issue resolved by updating payment method"
}
```

#### Get Active Conversations
```http
GET /api/admin/active-conversations
```
**Authentication:** Admin required
**Response:**
```json
[
  {
    "ticket_id": 123,
    "user_name": "John Doe",
    "subject": "Payment Issue",
    "last_message_time": "2025-06-25T10:30:00Z",
    "unread_count": 2
  }
]
```

### 3. Analytics

#### Get Analytics Data
```http
GET /api/admin/analytics
```
**Authentication:** Admin required
**Response:**
```json
{
  "daily_tickets": [10, 15, 8, 12, 20],
  "category_distribution": {
    "Payments": 45,
    "Technical": 30,
    "General": 25
  },
  "resolution_times": {
    "average": 4.5,
    "median": 3.2
  }
}
```

### 4. FAQ Management

#### Get FAQ Categories
```http
GET /api/faq-categories
```
**Authentication:** Admin required
**Response:**
```json
[
  {
    "id": 1,
    "name": "General",
    "description": "General questions",
    "icon": "fas fa-info-circle",
    "color": "#007bff",
    "sort_order": 1,
    "faq_count": 5
  }
]
```

#### Create FAQ Category
```http
POST /api/faq-categories
```
**Authentication:** Admin required
**Request Body:**
```json
{
  "name": "New Category",
  "description": "Category description",
  "icon": "fas fa-question-circle",
  "color": "#28a745"
}
```

#### Update FAQ Category
```http
PUT /api/faq-categories/{category_id}
```
**Authentication:** Admin required
**Request Body:**
```json
{
  "name": "Updated Category",
  "description": "Updated description"
}
```

#### Delete FAQ Category
```http
DELETE /api/faq-categories/{category_id}
```
**Authentication:** Admin required

## Error Responses

All API endpoints return consistent error responses:

```json
{
  "error": "Error message description",
  "details": "Additional error details (optional)"
}
```

**Common HTTP Status Codes:**
- `200` - Success
- `201` - Created
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `500` - Internal Server Error

## Integration Examples

### JavaScript/Node.js Example
```javascript
// Create a new ticket
const createTicket = async (ticketData) => {
  try {
    const response = await fetch('/api/tickets', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(ticketData)
    });
    
    const result = await response.json();
    return result;
  } catch (error) {
    console.error('Error creating ticket:', error);
  }
};

// Usage
const newTicket = await createTicket({
  name: "John Doe",
  email: "john@example.com",
  category_id: 1,
  subject: "Need Help",
  message: "I need assistance with my account"
});
```

### Python Example
```python
import requests

# Create a new ticket
def create_ticket(ticket_data):
    url = 'http://your-domain.com/api/tickets'
    headers = {'Content-Type': 'application/json'}
    
    response = requests.post(url, json=ticket_data, headers=headers)
    return response.json()

# Usage
ticket_data = {
    "name": "John Doe",
    "email": "john@example.com", 
    "category_id": 1,
    "subject": "Need Help",
    "message": "I need assistance with my account"
}

result = create_ticket(ticket_data)
print(result)
```

### cURL Examples
```bash
# Get categories
curl -X GET http://your-domain.com/api/categories

# Create ticket
curl -X POST http://your-domain.com/api/tickets \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john@example.com",
    "category_id": 1,
    "subject": "Need Help",
    "message": "I need assistance"
  }'

# Upload file with ticket
curl -X POST http://your-domain.com/api/tickets/with-attachment \
  -F "name=John Doe" \
  -F "email=john@example.com" \
  -F "category_id=1" \
  -F "subject=Need Help" \
  -F "message=Please see attached file" \
  -F "file=@document.pdf"
```

## Rate Limiting
Currently no rate limiting is implemented, but consider implementing it for production use.

## CORS
Configure CORS headers if accessing the API from different domains.

## Real-time Features
The application supports WebSocket connections for real-time chat updates. Connect to the WebSocket endpoint for live message notifications.

## File Upload Restrictions
- Maximum file size: Check application configuration
- Allowed file types: Check `allowed_file()` function in application
- Files are stored in `/static/uploads/` directory

## Security Considerations
- Always validate and sanitize input data
- Implement proper authentication for sensitive endpoints
- Use HTTPS in production
- Validate file uploads for security
- Implement CSRF protection for state-changing operations

## Support
For API support and questions, contact the development team or create a ticket through the system.
