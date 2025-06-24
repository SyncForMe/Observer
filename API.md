# 📡 API Documentation - AI Agent Simulation Platform

Complete API reference for the FastAPI backend.

## 🔗 Base URL

```
Development: http://localhost:8001/api
Production: https://yourdomain.com/api
```

## 🔐 Authentication

All protected endpoints require a JWT token in the Authorization header:

```bash
Authorization: Bearer <your-jwt-token>
```

### Get Authentication Token

```bash
# Login to get token
curl -X POST "http://localhost:8001/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password"}'

# Response
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": "user_id",
    "email": "user@example.com",
    "name": "User Name"
  }
}
```

---

## 🔑 Authentication Endpoints

### POST /auth/register
Register a new user account.

**Request Body:**
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "password": "securepassword123"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": "507f1f77bcf86cd799439011",
    "name": "John Doe",
    "email": "john@example.com",
    "created_at": "2024-01-15T10:30:00Z"
  }
}
```

### POST /auth/login
Authenticate user and get access token.

**Request Body:**
```json
{
  "email": "john@example.com",
  "password": "securepassword123"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": "507f1f77bcf86cd799439011",
    "name": "John Doe",
    "email": "john@example.com"
  }
}
```

### POST /auth/test-login
Quick authentication for testing (creates test user if not exists).

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": "test-user-id",
    "name": "Test User",
    "email": "test@example.com"
  }
}
```

### GET /auth/me
Get current user information (requires authentication).

**Response:**
```json
{
  "id": "507f1f77bcf86cd799439011",
  "name": "John Doe",
  "email": "john@example.com",
  "created_at": "2024-01-15T10:30:00Z",
  "last_login": "2024-01-20T14:25:00Z"
}
```

---

## 🤖 Agent Management Endpoints

### GET /agents
Get all agents for the current user.

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
[
  {
    "id": "agent_id_1",
    "name": "Dr. Sarah Chen",
    "archetype": "scientist",
    "goal": "To advance personalized medicine through genomic research",
    "background": "Harvard-trained physician-scientist with 15 years in oncology research",
    "expertise": "Precision Oncology, Genomic Medicine, Clinical Trials",
    "personality": {
      "extroversion": 7,
      "optimism": 8,
      "curiosity": 9,
      "cooperativeness": 6,
      "energy": 7
    },
    "avatar_url": "https://example.com/avatar1.png",
    "created_at": "2024-01-15T10:30:00Z"
  }
]
```

### POST /agents
Create a new agent.

**Headers:**
```
Authorization: Bearer <token>
Content-Type: application/json
```

**Request Body:**
```json
{
  "name": "Dr. Marcus Thompson",
  "archetype": "leader",
  "goal": "To advance global health equity through innovative healthcare delivery",
  "background": "Emergency medicine physician and global health advocate",
  "expertise": "Emergency Medicine, Global Health, Telemedicine",
  "personality": {
    "extroversion": 8,
    "optimism": 9,
    "curiosity": 7,
    "cooperativeness": 9,
    "energy": 8
  },
  "avatar_url": "https://example.com/avatar2.png",
  "memory_summary": "Led medical response to Hurricane Maria. Established telemedicine network."
}
```

**Response:**
```json
{
  "id": "507f1f77bcf86cd799439012",
  "name": "Dr. Marcus Thompson",
  "archetype": "leader",
  "goal": "To advance global health equity through innovative healthcare delivery",
  "background": "Emergency medicine physician and global health advocate",
  "expertise": "Emergency Medicine, Global Health, Telemedicine",
  "personality": {
    "extroversion": 8,
    "optimism": 9,
    "curiosity": 7,
    "cooperativeness": 9,
    "energy": 8
  },
  "avatar_url": "https://example.com/avatar2.png",
  "memory_summary": "Led medical response to Hurricane Maria. Established telemedicine network.",
  "created_at": "2024-01-20T11:15:00Z"
}
```

### PUT /agents/{agent_id}
Update an existing agent.

**Headers:**
```
Authorization: Bearer <token>
Content-Type: application/json
```

**Request Body:**
```json
{
  "name": "Dr. Marcus Thompson",
  "expertise": "Emergency Medicine, Global Health, Telemedicine, Disaster Medicine",
  "personality": {
    "extroversion": 8,
    "optimism": 9,
    "curiosity": 8,
    "cooperativeness": 9,
    "energy": 8
  }
}
```

**Response:**
```json
{
  "id": "507f1f77bcf86cd799439012",
  "name": "Dr. Marcus Thompson",
  "archetype": "leader",
  "expertise": "Emergency Medicine, Global Health, Telemedicine, Disaster Medicine",
  "personality": {
    "extroversion": 8,
    "optimism": 9,
    "curiosity": 8,
    "cooperativeness": 9,
    "energy": 8
  },
  "updated_at": "2024-01-20T15:30:00Z"
}
```

### DELETE /agents/{agent_id}
Delete an agent.

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
  "message": "Agent deleted successfully"
}
```

### GET /saved-agents
Get user's saved agents.

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
[
  {
    "id": "saved_agent_id_1",
    "name": "My Custom Agent",
    "archetype": "optimist",
    "saved_at": "2024-01-18T09:20:00Z"
  }
]
```

### GET /archetypes
Get available agent archetypes.

**Response:**
```json
[
  {
    "name": "scientist",
    "display_name": "The Scientist",
    "description": "Analytical, methodical, evidence-based thinking",
    "default_personality": {
      "extroversion": 5,
      "optimism": 6,
      "curiosity": 9,
      "cooperativeness": 7,
      "energy": 6
    }
  },
  {
    "name": "leader",
    "display_name": "The Leader",
    "description": "Natural leader, strategic thinking, team-oriented",
    "default_personality": {
      "extroversion": 8,
      "optimism": 8,
      "curiosity": 7,
      "cooperativeness": 9,
      "energy": 8
    }
  }
]
```

---

## 🎮 Simulation Control Endpoints

### POST /simulation/start
Start a new simulation.

**Headers:**
```
Authorization: Bearer <token>
Content-Type: application/json
```

**Request Body:**
```json
{
  "scenario": "Business Strategy Meeting",
  "agent_ids": ["agent_id_1", "agent_id_2", "agent_id_3"],
  "auto_mode": true,
  "interval_seconds": 30
}
```

**Response:**
```json
{
  "success": true,
  "simulation_id": "sim_507f1f77bcf86cd799439013",
  "message": "Simulation started successfully",
  "state": {
    "is_running": true,
    "is_paused": false,
    "scenario": "Business Strategy Meeting",
    "agent_count": 3,
    "message_count": 0,
    "started_at": "2024-01-20T16:00:00Z"
  }
}
```

### POST /simulation/pause
Pause the current simulation.

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
  "success": true,
  "message": "Simulation paused successfully",
  "state": {
    "is_running": true,
    "is_paused": true,
    "paused_at": "2024-01-20T16:15:00Z"
  }
}
```

### POST /simulation/resume
Resume a paused simulation.

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
  "success": true,
  "message": "Simulation resumed successfully",
  "state": {
    "is_running": true,
    "is_paused": false,
    "resumed_at": "2024-01-20T16:20:00Z"
  }
}
```

### POST /simulation/fast-forward
Toggle fast forward mode.

**Headers:**
```
Authorization: Bearer <token>
Content-Type: application/json
```

**Request Body:**
```json
{
  "enabled": true
}
```

**Response:**
```json
{
  "success": true,
  "fast_forward_enabled": true,
  "message": "Fast forward mode enabled"
}
```

### GET /simulation/state
Get current simulation state.

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
  "simulation_id": "sim_507f1f77bcf86cd799439013",
  "is_running": true,
  "is_paused": false,
  "scenario": "Business Strategy Meeting",
  "agent_count": 3,
  "message_count": 12,
  "fast_forward_enabled": false,
  "started_at": "2024-01-20T16:00:00Z",
  "last_activity": "2024-01-20T16:25:00Z"
}
```

### POST /simulation/generate-summary
Generate a simulation summary report.

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
  "success": true,
  "summary_id": "summary_507f1f77bcf86cd799439014",
  "summary": {
    "title": "Business Strategy Meeting Summary",
    "key_insights": [
      "Team identified three main growth opportunities",
      "Consensus reached on Q2 priorities",
      "Risk mitigation strategies discussed"
    ],
    "action_items": [
      "Conduct market research by end of month",
      "Prepare budget proposal for new initiatives",
      "Schedule follow-up meeting in 2 weeks"
    ],
    "participants": [
      "Dr. Sarah Chen (Scientist)",
      "Dr. Marcus Thompson (Leader)",
      "Alex Johnson (Analyst)"
    ],
    "duration_minutes": 45,
    "message_count": 28,
    "generated_at": "2024-01-20T16:30:00Z"
  }
}
```

---

## 💬 Observer Chat Endpoints

### GET /observer/messages
Get observer chat messages for current simulation.

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
[
  {
    "id": "msg_507f1f77bcf86cd799439015",
    "type": "observer",
    "message": "Please focus on budget constraints",
    "agent_name": "Observer",
    "timestamp": "2024-01-20T16:10:00Z"
  },
  {
    "id": "msg_507f1f77bcf86cd799439016",
    "type": "agent",
    "message": "I understand the budget limitations. Let me propose an alternative approach.",
    "agent_name": "Dr. Sarah Chen",
    "timestamp": "2024-01-20T16:11:00Z"
  }
]
```

### POST /observer/send-message
Send an observer message to the simulation.

**Headers:**
```
Authorization: Bearer <token>
Content-Type: application/json
```

**Request Body:**
```json
{
  "message": "Can we explore the environmental impact of these proposals?"
}
```

**Response:**
```json
{
  "success": true,
  "message_id": "msg_507f1f77bcf86cd799439017",
  "message": "Observer message sent successfully"
}
```

---

## 📊 Analytics Endpoints

### GET /analytics/weekly-summary
Get weekly analytics summary.

**Headers:**
```
Authorization: Bearer <token>
```

**Query Parameters:**
- `week_start` (optional): ISO date string for week start (defaults to current week)

**Response:**
```json
{
  "week_start": "2024-01-15",
  "week_end": "2024-01-21",
  "metrics": {
    "total_conversations": 15,
    "agents_created": 8,
    "documents_created": 5,
    "simulation_hours": 12.5,
    "most_active_day": "2024-01-18",
    "top_scenario": "Business Strategy Meeting"
  },
  "daily_breakdown": [
    {
      "date": "2024-01-15",
      "conversations": 2,
      "agents_created": 1,
      "simulation_minutes": 45
    },
    {
      "date": "2024-01-16",
      "conversations": 3,
      "agents_created": 2,
      "simulation_minutes": 120
    }
  ],
  "agent_usage": [
    {
      "agent_name": "Dr. Sarah Chen",
      "usage_count": 8,
      "total_messages": 156
    }
  ]
}
```

### POST /simulation/auto-weekly-report
Setup automatic weekly report generation.

**Headers:**
```
Authorization: Bearer <token>
Content-Type: application/json
```

**Request Body:**
```json
{
  "enabled": true,
  "email_notifications": true,
  "day_of_week": "monday",
  "time": "09:00"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Auto weekly reports configured successfully",
  "config": {
    "enabled": true,
    "email_notifications": true,
    "day_of_week": "monday",
    "time": "09:00",
    "next_report": "2024-01-22T09:00:00Z"
  }
}
```

---

## 📄 Document Management Endpoints

### GET /documents
Get user's documents.

**Headers:**
```
Authorization: Bearer <token>
```

**Query Parameters:**
- `category` (optional): Filter by category
- `limit` (optional): Number of documents to return (default: 50)
- `offset` (optional): Number of documents to skip (default: 0)

**Response:**
```json
{
  "documents": [
    {
      "id": "doc_507f1f77bcf86cd799439018",
      "title": "Q1 Strategy Meeting Summary",
      "category": "simulation_summary",
      "description": "Summary of quarterly strategy discussion",
      "content": "# Q1 Strategy Meeting Summary\n\n## Key Decisions...",
      "preview": "Summary of quarterly strategy discussion with key decisions and action items...",
      "created_at": "2024-01-20T16:30:00Z",
      "updated_at": "2024-01-20T16:30:00Z",
      "metadata": {
        "simulation_id": "sim_507f1f77bcf86cd799439013",
        "agent_count": 3,
        "duration_minutes": 45
      }
    }
  ],
  "total_count": 1,
  "has_more": false
}
```

### POST /documents
Create a new document.

**Headers:**
```
Authorization: Bearer <token>
Content-Type: application/json
```

**Request Body:**
```json
{
  "title": "Custom Analysis Report",
  "category": "analysis",
  "description": "Custom analysis of agent interactions",
  "content": "# Custom Analysis Report\n\nDetailed analysis of agent behavior patterns...",
  "metadata": {
    "tags": ["analysis", "agents", "behavior"],
    "priority": "high"
  }
}
```

**Response:**
```json
{
  "id": "doc_507f1f77bcf86cd799439019",
  "title": "Custom Analysis Report",
  "category": "analysis",
  "description": "Custom analysis of agent interactions",
  "created_at": "2024-01-20T17:00:00Z",
  "message": "Document created successfully"
}
```

### POST /documents/bulk-delete
Delete multiple documents.

**Headers:**
```
Authorization: Bearer <token>
Content-Type: application/json
```

**Request Body:**
```json
{
  "document_ids": [
    "doc_507f1f77bcf86cd799439018",
    "doc_507f1f77bcf86cd799439019"
  ]
}
```

**Response:**
```json
{
  "message": "Successfully deleted 2 documents",
  "deleted_count": 2,
  "failed_deletes": []
}
```

---

## 🔄 Conversation History Endpoints

### GET /conversations
Get conversation history.

**Headers:**
```
Authorization: Bearer <token>
```

**Query Parameters:**
- `simulation_id` (optional): Filter by simulation
- `limit` (optional): Number of conversations to return (default: 20)
- `offset` (optional): Number of conversations to skip (default: 0)

**Response:**
```json
{
  "conversations": [
    {
      "id": "conv_507f1f77bcf86cd799439020",
      "simulation_id": "sim_507f1f77bcf86cd799439013",
      "title": "Business Strategy Discussion",
      "participants": ["Dr. Sarah Chen", "Dr. Marcus Thompson"],
      "message_count": 28,
      "started_at": "2024-01-20T16:00:00Z",
      "ended_at": "2024-01-20T16:45:00Z",
      "summary": "Productive discussion about Q2 strategy and budget allocation"
    }
  ],
  "total_count": 1,
  "has_more": false
}
```

### GET /conversations/{conversation_id}/messages
Get messages from a specific conversation.

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
  "conversation_id": "conv_507f1f77bcf86cd799439020",
  "messages": [
    {
      "id": "msg_507f1f77bcf86cd799439021",
      "agent_name": "Dr. Sarah Chen",
      "agent_archetype": "scientist",
      "content": "Based on the data analysis, I recommend focusing on three key areas for Q2.",
      "timestamp": "2024-01-20T16:05:00Z",
      "metadata": {
        "sentiment": "positive",
        "confidence": 0.87
      }
    },
    {
      "id": "msg_507f1f77bcf86cd799439022",
      "agent_name": "Dr. Marcus Thompson",
      "agent_archetype": "leader",
      "content": "That's an excellent analysis, Sarah. Can you elaborate on the implementation timeline?",
      "timestamp": "2024-01-20T16:06:30Z",
      "metadata": {
        "sentiment": "neutral",
        "confidence": 0.92
      }
    }
  ],
  "total_messages": 2
}
```

---

## ❌ Error Responses

### Standard Error Format
All error responses follow this format:

```json
{
  "detail": "Error message description",
  "error_code": "SPECIFIC_ERROR_CODE",
  "timestamp": "2024-01-20T16:00:00Z"
}
```

### Common HTTP Status Codes

#### 400 Bad Request
```json
{
  "detail": "Invalid request parameters",
  "error_code": "INVALID_PARAMETERS"
}
```

#### 401 Unauthorized
```json
{
  "detail": "Authentication required",
  "error_code": "UNAUTHORIZED"
}
```

#### 403 Forbidden
```json
{
  "detail": "Access denied",
  "error_code": "FORBIDDEN"
}
```

#### 404 Not Found
```json
{
  "detail": "Resource not found",
  "error_code": "NOT_FOUND"
}
```

#### 422 Validation Error
```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ],
  "error_code": "VALIDATION_ERROR"
}
```

#### 429 Too Many Requests
```json
{
  "detail": "Rate limit exceeded",
  "error_code": "RATE_LIMIT_EXCEEDED",
  "retry_after": 60
}
```

#### 500 Internal Server Error
```json
{
  "detail": "Internal server error",
  "error_code": "INTERNAL_ERROR",
  "request_id": "req_507f1f77bcf86cd799439023"
}
```

---

## 📝 Rate Limits

| Endpoint Category | Rate Limit | Window |
|------------------|------------|---------|
| Authentication | 5 requests | 1 minute |
| Agent Management | 100 requests | 1 minute |
| Simulation Control | 50 requests | 1 minute |
| Analytics | 20 requests | 1 minute |
| Documents | 100 requests | 1 minute |

---

## 🔧 Testing the API

### Using cURL

```bash
# Get auth token
TOKEN=$(curl -s -X POST "http://localhost:8001/api/auth/test-login" | jq -r '.access_token')

# Use token in subsequent requests
curl -H "Authorization: Bearer $TOKEN" "http://localhost:8001/api/agents"

# Create an agent
curl -X POST "http://localhost:8001/api/agents" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Agent",
    "archetype": "scientist",
    "goal": "Test goal",
    "background": "Test background",
    "expertise": "Test expertise"
  }'
```

### Using Python requests

```python
import requests

# Get token
auth_response = requests.post('http://localhost:8001/api/auth/test-login')
token = auth_response.json()['access_token']

# Set headers
headers = {'Authorization': f'Bearer {token}'}

# Get agents
agents_response = requests.get('http://localhost:8001/api/agents', headers=headers)
print(agents_response.json())
```

### Using JavaScript fetch

```javascript
// Get token
const authResponse = await fetch('http://localhost:8001/api/auth/test-login', {
  method: 'POST'
});
const { access_token } = await authResponse.json();

// Use token
const agentsResponse = await fetch('http://localhost:8001/api/agents', {
  headers: {
    'Authorization': `Bearer ${access_token}`
  }
});
const agents = await agentsResponse.json();
console.log(agents);
```

---

## 📖 Interactive Documentation

Visit the interactive API documentation at:
- **Swagger UI**: http://localhost:8001/docs
- **ReDoc**: http://localhost:8001/redoc

These provide a complete interface for testing all endpoints with example requests and responses.

---

**API Reference Complete!** 🎉

All endpoints are documented with examples and ready for integration.