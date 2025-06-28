# Public Chatbot API Reference

## Overview
This document provides the public API endpoints that can be integrated into external applications without requiring admin authentication. These APIs allow you to create tickets, manage conversations, and interact with the chatbot system.

**Base URL:** `http://your-domain.com`  
**Authentication:** Session-based or Guest access  
**Content-Type:** `application/json` (unless specified otherwise)

## Data Models

### Ticket
```json
{
  "ticket_id": "integer",
  "subject": "string",
  "status": "open|in_progress|resolved|closed",
  "category": "string",
  "priority": "low|medium|high|critical",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

### Message
```json
{
  "id": "integer",
  "content": "string",
  "is_admin": "boolean",
  "created_at": "datetime",
  "attachments": "array"
}
```

### Category
```json
{
  "id": "integer",
  "name": "string"
}
```

---

## 1. Categories API

### Get All Categories
Get list of available support categories.

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
  },
  {
    "id": 3,
    "name": "Technical Glitches"
  },
  {
    "id": 4,
    "name": "General Inquiries"
  }
]
```

### Get Common Queries by Category
Get pre-defined common questions and solutions for a specific category.

```http
GET /api/common-queries/{category_id}
```

**Parameters:**
- `category_id` (integer) - Category ID

**Response:**
```json
[
  {
    "id": 1,
    "question": "How do I update my payment method?",
    "solution": "You can update your payment method by going to Account Settings > Billing > Payment Methods..."
  },
  {
    "id": 2,
    "question": "Why was my payment declined?",
    "solution": "Payment declines can happen due to insufficient funds, expired cards..."
  }
]
```

---

## 2. Tickets API

### Create New Ticket
Create a new support ticket.

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

### Create Ticket with File Attachment
Create a ticket with an attached file.

```http
POST /api/tickets/with-attachment
Content-Type: multipart/form-data
```

**Form Parameters:**
- `name` (string, required) - User's name
- `email` (string, required) - User's email
- `category_id` (integer, required) - Category ID
- `subject` (string, optional) - Ticket subject
- `message` (string, required) - Ticket message/description
- `file` (file, optional) - File attachment

**Response:**
```json
{
  "ticket_id": 123,
  "user_id": 456,
  "status": "success",
  "message": "Ticket created successfully"
}
```

### Get Ticket Details
Retrieve details of a specific ticket including all messages.

```http
GET /api/tickets/{ticket_id}
```

**Parameters:**
- `ticket_id` (integer) - Ticket ID

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
      "content": "I'm having trouble with my payment method",
      "is_admin": false,
      "created_at": "2025-06-25T10:30:00Z",
      "attachments": []
    },
    {
      "content": "Thank you for contacting us. We'll help you resolve this issue.",
      "is_admin": true,
      "created_at": "2025-06-25T10:35:00Z",
      "attachments": []
    }
  ]
}
```

---

## 3. Messages API

### Get Messages for Ticket
Retrieve all messages for a specific ticket.

```http
GET /api/tickets/{ticket_id}/messages
```

**Parameters:**
- `ticket_id` (integer) - Ticket ID

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
  },
  {
    "id": 2,
    "content": "Thank you for your message. I see the issue in your screenshot.",
    "is_admin": true,
    "created_at": "2025-06-25T10:35:00Z",
    "attachments": []
  }
]
```

### Add Message to Ticket
Add a new message to an existing ticket.

```http
POST /api/tickets/{ticket_id}/messages
```

**Parameters:**
- `ticket_id` (integer) - Ticket ID

**Request Body:**
```json
{
  "content": "Thank you for your help. This resolves my issue.",
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

### Add Message with Attachment
Add a message with a file attachment to an existing ticket.

```http
POST /api/tickets/{ticket_id}/messages/with-attachment
Content-Type: multipart/form-data
```

**Parameters:**
- `ticket_id` (integer) - Ticket ID

**Form Parameters:**
- `content` (string, required) - Message content
- `user_id` (integer, required) - Sender user ID
- `is_admin` (boolean, optional) - Whether sender is admin (default: false)
- `file` (file, optional) - File attachment

**Response:**
```json
{
  "status": "success",
  "message_id": 789
}
```

---

## 4. File Upload API

### Upload File
Upload a file to the system.

```http
POST /api/upload
Content-Type: multipart/form-data
```

**Form Parameters:**
- `file` (file, required) - File to upload

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

**File Restrictions:**
- Check with your system administrator for allowed file types
- Maximum file size limits apply
- Files are stored securely and accessible via the returned URL

---

## 5. Feedback API

### Submit Feedback
Submit feedback/rating for a resolved ticket.

```http
POST /api/feedback
```

**Request Body:**
```json
{
  "ticket_id": 123,
  "rating": 5,
  "comment": "Excellent support! Issue was resolved quickly."
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Feedback submitted successfully"
}
```

**Rating Scale:** 1-5 (1 = Poor, 5 = Excellent)

---

## 6. System Health API

### Test Database Connection
Check if the system is operational.

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

---

## Integration Examples

### JavaScript Example
```javascript
// Create a new support ticket
async function createSupportTicket(ticketData) {
  try {
    const response = await fetch('/api/tickets', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(ticketData)
    });
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const result = await response.json();
    console.log('Ticket created:', result);
    return result;
  } catch (error) {
    console.error('Error creating ticket:', error);
    throw error;
  }
}

// Usage
const ticketData = {
  name: "John Doe",
  email: "john@example.com",
  category_id: 1,
  subject: "Payment Issue",
  message: "I'm having trouble processing my payment"
};

createSupportTicket(ticketData)
  .then(result => {
    console.log('Success:', result);
  })
  .catch(error => {
    console.error('Failed:', error);
  });
```

### Python Example
```python
import requests
import json

def create_ticket(base_url, ticket_data):
    """Create a new support ticket"""
    url = f"{base_url}/api/tickets"
    headers = {'Content-Type': 'application/json'}
    
    try:
        response = requests.post(url, json=ticket_data, headers=headers)
        response.raise_for_status()  # Raises exception for bad status codes
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error creating ticket: {e}")
        return None

# Usage
base_url = "http://your-domain.com"
ticket_data = {
    "name": "Jane Smith",
    "email": "jane@example.com",
    "category_id": 2,
    "subject": "Product Not Working",
    "message": "The product feature is not responding as expected"
}

result = create_ticket(base_url, ticket_data)
if result:
    print(f"Ticket created successfully: {result}")
else:
    print("Failed to create ticket")
```

### PHP Example
```php
<?php
function createTicket($baseUrl, $ticketData) {
    $url = $baseUrl . '/api/tickets';
    
    $options = [
        'http' => [
            'header' => "Content-type: application/json\r\n",
            'method' => 'POST',
            'content' => json_encode($ticketData)
        ]
    ];
    
    $context = stream_context_create($options);
    $result = file_get_contents($url, false, $context);
    
    if ($result === FALSE) {
        return null;
    }
    
    return json_decode($result, true);
}

// Usage
$baseUrl = "http://your-domain.com";
$ticketData = [
    "name" => "Mike Johnson",
    "email" => "mike@example.com",
    "category_id" => 3,
    "subject" => "Technical Issue",
    "message" => "Having trouble accessing my account"
];

$result = createTicket($baseUrl, $ticketData);
if ($result) {
    echo "Ticket created: " . json_encode($result);
} else {
    echo "Failed to create ticket";
}
?>
```

### cURL Examples
```bash
# Get all categories
curl -X GET "http://your-domain.com/api/categories"

# Create a new ticket
curl -X POST "http://your-domain.com/api/tickets" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john@example.com",
    "category_id": 1,
    "subject": "Need Help",
    "message": "I need assistance with my account"
  }'

# Get ticket details
curl -X GET "http://your-domain.com/api/tickets/123"

# Add message to ticket
curl -X POST "http://your-domain.com/api/tickets/123/messages" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Thank you for the quick response",
    "user_id": 456,
    "is_admin": false
  }'

# Create ticket with file attachment
curl -X POST "http://your-domain.com/api/tickets/with-attachment" \
  -F "name=John Doe" \
  -F "email=john@example.com" \
  -F "category_id=1" \
  -F "subject=Bug Report" \
  -F "message=Please see attached screenshot" \
  -F "file=@screenshot.png"

# Submit feedback
curl -X POST "http://your-domain.com/api/feedback" \
  -H "Content-Type: application/json" \
  -d '{
    "ticket_id": 123,
    "rating": 5,
    "comment": "Great support!"
  }'
```

---

## Error Handling

All endpoints return consistent error responses:

```json
{
  "error": "Error message description",
  "details": "Additional error details (optional)"
}
```

**HTTP Status Codes:**
- `200` - Success
- `201` - Created successfully
- `400` - Bad Request (invalid data)
- `404` - Resource not found
- `500` - Internal server error

### Common Error Scenarios:

1. **Missing Required Fields**
```json
{
  "error": "Missing required fields",
  "details": "Name and email are required"
}
```

2. **Invalid Category ID**
```json
{
  "error": "Invalid category ID",
  "details": "Category 999 does not exist"
}
```

3. **File Upload Error**
```json
{
  "error": "File type not allowed",
  "details": "Only PDF, JPG, PNG files are allowed"
}
```

---

## Rate Limiting & Security

- **Rate Limiting:** Currently no rate limiting implemented (consider for production)
- **File Security:** Uploaded files are scanned and validated
- **Data Validation:** All input is validated server-side
- **CORS:** Configure appropriately for cross-origin requests

---

## Support

For integration support:
1. Test your integration using the `/api/database/test` endpoint first
2. Use the provided error responses to handle edge cases
3. Contact the development team for technical assistance
4. Create a support ticket through the system for questions

**Important Notes:**
- Always validate responses and handle errors gracefully
- Use HTTPS in production environments
- Store user credentials securely if implementing authentication
- Test file uploads with various file types and sizes
