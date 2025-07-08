# API Documentation

## Overview

The AI Agent Simulation Platform provides a comprehensive REST API built with FastAPI. This documentation covers all available endpoints, request/response formats, and authentication requirements.

## Base URL

```
Development: http://localhost:8001/api
Production: https://your-domain.com/api
```

## Authentication

All API endpoints require JWT authentication unless specified otherwise.

### Authentication Header
```
Authorization: Bearer <your-jwt-token>
```

### Getting Started
1. Register a new account or use test login
2. Use the returned JWT token for all subsequent requests
3. Include the token in the Authorization header

---

## Authentication Endpoints

### POST /auth/register

Register a new user account.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "secure_password",
  "name": "John Doe"
}
```

**Response:**
```json
{
  "user": {
    "id": "user_123",
    "email": "user@example.com",
    "name": "John Doe",
    "created_at": "2024-01-01T00:00:00Z"
  },
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer"
}
```

### POST /auth/login

Authenticate user and get JWT token.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "secure_password"
}
```

**Response:**
```json
{
  "user": {
    "id": "user_123",
    "email": "user@example.com",
    "name": "John Doe"
  },
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer"
}
```

### POST /auth/test-login

Get a test JWT token for guest access.

**Request Body:** None

**Response:**
```json
{
  "user": {
    "id": "guest_user",
    "email": "guest@example.com",
    "name": "Guest User"
  },
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer"
}
```

### GET /auth/me

Get current user information.

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
{
  "id": "user_123",
  "email": "user@example.com",
  "name": "John Doe",
  "created_at": "2024-01-01T00:00:00Z"
}
```

---

## Agent Management

### GET /agents

Get all agents for the current user.

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
[
  {
    "id": "agent_123",
    "name": "Dr. Sarah Chen",
    "archetype": "scientist",
    "goal": "Advance precision medicine research",
    "background": "Harvard-trained physician-scientist...",
    "expertise": "Precision Oncology, Genomics",
    "avatar_url": "https://example.com/avatar.jpg",
    "created_at": "2024-01-01T00:00:00Z"
  }
]
```

### POST /agents

Create a new agent.

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "name": "Dr. Sarah Chen",
  "archetype": "scientist",
  "goal": "Advance precision medicine research",
  "background": "Harvard-trained physician-scientist with 15 years in oncology research",
  "expertise": "Precision Oncology, Genomics, Clinical Trials",
  "memory_summary": "Expert in BRCA mutations and personalized treatment protocols",
  "avatar_url": "https://example.com/avatar.jpg",
  "avatar_prompt": "Professional female scientist with lab coat",
  "personality": {
    "extroversion": 7,
    "optimism": 8,
    "curiosity": 9,
    "cooperativeness": 6,
    "energy": 7
  }
}
```

**Response:**
```json
{
  "id": "agent_123",
  "name": "Dr. Sarah Chen",
  "archetype": "scientist",
  "goal": "Advance precision medicine research",
  "background": "Harvard-trained physician-scientist with 15 years in oncology research",
  "expertise": "Precision Oncology, Genomics, Clinical Trials",
  "avatar_url": "https://example.com/avatar.jpg",
  "created_at": "2024-01-01T00:00:00Z"
}
```

### PUT /agents/{agent_id}

Update an existing agent.

**Headers:** `Authorization: Bearer <token>`

**Path Parameters:**
- `agent_id` (string): The agent ID

**Request Body:**
```json
{
  "name": "Dr. Sarah Chen",
  "archetype": "scientist",
  "goal": "Updated research goal",
  "background": "Updated background information",
  "expertise": "Updated expertise areas"
}
```

**Response:**
```json
{
  "id": "agent_123",
  "name": "Dr. Sarah Chen",
  "archetype": "scientist",
  "goal": "Updated research goal",
  "background": "Updated background information",
  "expertise": "Updated expertise areas",
  "avatar_url": "https://example.com/avatar.jpg",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

### DELETE /agents/{agent_id}

Delete an agent.

**Headers:** `Authorization: Bearer <token>`

**Path Parameters:**
- `agent_id` (string): The agent ID

**Response:**
```json
{
  "message": "Agent deleted successfully"
}
```

---

## Saved Agents (My Agents Library)

### GET /saved-agents

Get all saved agents for the current user.

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
[
  {
    "id": "saved_agent_123",
    "name": "Dr. Sarah Chen",
    "archetype": "scientist",
    "goal": "Advance precision medicine research",
    "background": "Harvard-trained physician-scientist",
    "expertise": "Precision Oncology, Genomics",
    "avatar_url": "https://example.com/avatar.jpg",
    "avatar_prompt": "Professional female scientist",
    "is_favorite": true,
    "created_at": "2024-01-01T00:00:00Z"
  }
]
```

### POST /saved-agents

Save an agent to the user's library.

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "name": "Dr. Sarah Chen",
  "archetype": "scientist",
  "goal": "Advance precision medicine research",
  "background": "Harvard-trained physician-scientist",
  "expertise": "Precision Oncology, Genomics",
  "avatar_url": "https://example.com/avatar.jpg",
  "avatar_prompt": "Professional female scientist",
  "is_favorite": false
}
```

**Response:**
```json
{
  "id": "saved_agent_123",
  "name": "Dr. Sarah Chen",
  "archetype": "scientist",
  "goal": "Advance precision medicine research",
  "background": "Harvard-trained physician-scientist",
  "expertise": "Precision Oncology, Genomics",
  "avatar_url": "https://example.com/avatar.jpg",
  "avatar_prompt": "Professional female scientist",
  "is_favorite": false,
  "created_at": "2024-01-01T00:00:00Z"
}
```

### PUT /saved-agents/{agent_id}

Update a saved agent.

**Headers:** `Authorization: Bearer <token>`

**Path Parameters:**
- `agent_id` (string): The saved agent ID

**Request Body:**
```json
{
  "name": "Updated Agent Name",
  "archetype": "scientist",
  "goal": "Updated goal",
  "background": "Updated background",
  "expertise": "Updated expertise"
}
```

**Response:**
```json
{
  "id": "saved_agent_123",
  "name": "Updated Agent Name",
  "archetype": "scientist",
  "goal": "Updated goal",
  "background": "Updated background",
  "expertise": "Updated expertise",
  "avatar_url": "https://example.com/avatar.jpg",
  "is_favorite": false,
  "updated_at": "2024-01-01T00:00:00Z"
}
```

### PUT /saved-agents/{agent_id}/favorite

Toggle favorite status of a saved agent.

**Headers:** `Authorization: Bearer <token>`

**Path Parameters:**
- `agent_id` (string): The saved agent ID

**Request Body:** None

**Response:**
```json
{
  "id": "saved_agent_123",
  "name": "Dr. Sarah Chen",
  "archetype": "scientist",
  "is_favorite": true,
  "message": "Favorite status updated successfully"
}
```

### DELETE /saved-agents/{agent_id}

Delete a saved agent from the user's library.

**Headers:** `Authorization: Bearer <token>`

**Path Parameters:**
- `agent_id` (string): The saved agent ID

**Response:**
```json
{
  "message": "Saved agent deleted successfully"
}
```

---

## Simulation Control

### POST /simulation/start

Start a new simulation.

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "scenario": "Business strategy meeting for new product launch",
  "agents": ["agent_123", "agent_456"],
  "settings": {
    "auto_generate": true,
    "generation_interval": 4,
    "max_rounds": 10
  }
}
```

**Response:**
```json
{
  "simulation_id": "sim_123",
  "status": "active",
  "scenario": "Business strategy meeting for new product launch",
  "agents": ["agent_123", "agent_456"],
  "started_at": "2024-01-01T00:00:00Z"
}
```

### GET /simulation/state

Get current simulation state.

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
{
  "simulation_id": "sim_123",
  "status": "active",
  "scenario": "Business strategy meeting for new product launch",
  "agents": ["agent_123", "agent_456"],
  "current_round": 3,
  "total_rounds": 10,
  "started_at": "2024-01-01T00:00:00Z",
  "last_activity": "2024-01-01T00:05:00Z"
}
```

### POST /simulation/pause

Pause the current simulation.

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
{
  "simulation_id": "sim_123",
  "status": "paused",
  "message": "Simulation paused successfully"
}
```

### POST /simulation/set-scenario

Set a custom scenario for the simulation.

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "scenario": "Emergency response planning for natural disasters",
  "context": "A major earthquake has struck the region and immediate response is needed"
}
```

**Response:**
```json
{
  "scenario": "Emergency response planning for natural disasters",
  "context": "A major earthquake has struck the region and immediate response is needed",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

---

## Conversations

### GET /conversations

Get conversation history for the current user.

**Headers:** `Authorization: Bearer <token>`

**Query Parameters:**
- `limit` (int, optional): Number of conversations to return (default: 50)
- `offset` (int, optional): Number of conversations to skip (default: 0)

**Response:**
```json
[
  {
    "id": "conv_123",
    "agent_id": "agent_123",
    "agent_name": "Dr. Sarah Chen",
    "message": "Based on the market analysis, I recommend focusing on precision medicine approaches...",
    "timestamp": "2024-01-01T00:00:00Z",
    "simulation_id": "sim_123"
  }
]
```

### GET /conversation-history

Get detailed conversation history with full context.

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
{
  "conversations": [
    {
      "id": "conv_123",
      "agent_id": "agent_123",
      "agent_name": "Dr. Sarah Chen",
      "message": "Based on the market analysis, I recommend focusing on precision medicine approaches...",
      "timestamp": "2024-01-01T00:00:00Z",
      "simulation_id": "sim_123",
      "context": {
        "scenario": "Business strategy meeting",
        "previous_messages": 5,
        "agent_archetype": "scientist"
      }
    }
  ],
  "total_count": 150,
  "metadata": {
    "latest_simulation": "sim_123",
    "active_agents": 3,
    "total_messages": 150
  }
}
```

### POST /conversation/generate

Generate a new conversation round.

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "simulation_id": "sim_123",
  "agent_ids": ["agent_123", "agent_456"],
  "custom_prompt": "Focus on budget considerations for this quarter"
}
```

**Response:**
```json
{
  "conversations": [
    {
      "id": "conv_124",
      "agent_id": "agent_123",
      "agent_name": "Dr. Sarah Chen",
      "message": "Regarding budget considerations, we should prioritize research initiatives...",
      "timestamp": "2024-01-01T00:00:00Z"
    }
  ],
  "generation_time": 2.5,
  "status": "success"
}
```

---

## Analytics

### GET /analytics/comprehensive

Get comprehensive analytics dashboard data.

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
{
  "summary": {
    "total_conversations": 150,
    "total_agents": 12,
    "total_documents": 25,
    "active_simulations": 1
  },
  "daily_activity": [
    {
      "date": "2024-01-01",
      "conversations": 25,
      "agents_created": 2,
      "documents_generated": 3
    }
  ],
  "agent_usage": [
    {
      "agent_id": "agent_123",
      "agent_name": "Dr. Sarah Chen",
      "usage_count": 45,
      "last_used": "2024-01-01T00:00:00Z"
    }
  ],
  "scenario_distribution": {
    "business_strategy": 35,
    "research_planning": 28,
    "emergency_response": 12
  }
}
```

### GET /analytics/weekly-summary

Get weekly analytics summary.

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
{
  "period": {
    "start_date": "2024-01-01",
    "end_date": "2024-01-07"
  },
  "summary": {
    "conversations_count": 75,
    "agents_created": 5,
    "documents_created": 8,
    "most_active_day": "2024-01-03"
  },
  "daily_breakdown": [
    {
      "date": "2024-01-01",
      "conversations": 10,
      "agents_created": 1,
      "documents_generated": 2
    }
  ]
}
```

---

## Documents

### GET /documents

Get generated documents for the current user.

**Headers:** `Authorization: Bearer <token>`

**Query Parameters:**
- `category` (string, optional): Filter by document category
- `limit` (int, optional): Number of documents to return (default: 50)

**Response:**
```json
[
  {
    "id": "doc_123",
    "title": "Q1 Strategy Analysis Report",
    "category": "business_strategy",
    "content": "# Executive Summary\n\nThis report analyzes...",
    "preview": "This report analyzes the first quarter performance...",
    "created_at": "2024-01-01T00:00:00Z",
    "simulation_id": "sim_123",
    "metadata": {
      "word_count": 1250,
      "page_count": 5,
      "contributors": ["Dr. Sarah Chen", "John Smith"]
    }
  }
]
```

### GET /documents/{document_id}

Get a specific document.

**Headers:** `Authorization: Bearer <token>`

**Path Parameters:**
- `document_id` (string): The document ID

**Response:**
```json
{
  "id": "doc_123",
  "title": "Q1 Strategy Analysis Report",
  "category": "business_strategy",
  "content": "# Executive Summary\n\nThis report provides a comprehensive analysis...",
  "created_at": "2024-01-01T00:00:00Z",
  "simulation_id": "sim_123",
  "metadata": {
    "word_count": 1250,
    "page_count": 5,
    "contributors": ["Dr. Sarah Chen", "John Smith"],
    "tags": ["strategy", "analysis", "Q1"]
  }
}
```

---

## Feedback

### POST /feedback/send

Send user feedback.

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "type": "feature_request",
  "subject": "Agent collaboration improvements",
  "message": "It would be great to have better collaboration features between agents...",
  "priority": "medium"
}
```

**Response:**
```json
{
  "id": "feedback_123",
  "status": "received",
  "message": "Thank you for your feedback! We'll review it and get back to you.",
  "created_at": "2024-01-01T00:00:00Z"
}
```

---

## Error Handling

### Standard Error Response

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid request data",
    "details": {
      "field": "email",
      "issue": "Invalid email format"
    }
  },
  "timestamp": "2024-01-01T00:00:00Z",
  "request_id": "req_123"
}
```

### HTTP Status Codes

- `200` - Success
- `201` - Created
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `422` - Validation Error
- `500` - Internal Server Error

### Common Error Codes

- `VALIDATION_ERROR` - Request validation failed
- `AUTHENTICATION_ERROR` - Invalid or missing authentication
- `PERMISSION_DENIED` - Insufficient permissions
- `RESOURCE_NOT_FOUND` - Requested resource not found
- `RATE_LIMIT_EXCEEDED` - Too many requests
- `INTERNAL_ERROR` - Server error

---

## Rate Limiting

API requests are rate limited to prevent abuse:

- **Authentication endpoints**: 10 requests per minute
- **Agent management**: 100 requests per minute
- **Simulation control**: 50 requests per minute
- **Analytics**: 20 requests per minute

Rate limit headers are included in responses:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640995200
```

---

## Webhooks (Coming Soon)

Future support for webhooks to notify external systems of events:

- Agent created/updated
- Simulation started/completed
- Document generated
- Conversation milestones

---

## SDK and Libraries

Official SDKs are planned for:
- Python
- JavaScript/TypeScript
- Go
- Java

---

For more information, visit the [GitHub repository](https://github.com/your-username/ai-agent-simulation) or contact support@ai-agent-simulation.com.