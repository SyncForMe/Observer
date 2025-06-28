# 🚀 AI Agent Simulation Platform - Backend API

<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.68+-00A86B.svg)](https://fastapi.tiangolo.com/)
[![MongoDB](https://img.shields.io/badge/MongoDB-4.4+-47A248.svg)](https://www.mongodb.com/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

**High-performance FastAPI backend powering intelligent AI agent simulations with real-time conversations and comprehensive analytics.**

[Features](#-features) • [Quick Start](#-quick-start) • [API Documentation](#-api-documentation) • [Architecture](#-architecture) • [Deployment](#-deployment)

</div>

---

## 🌟 Features

### 🔐 **Enterprise Authentication**
- **JWT Authentication** with secure token management
- **User Registration & Login** with bcrypt password hashing
- **Guest Access** for demo purposes
- **Profile Management** with avatar generation using fal.ai
- **Complete User Data Isolation** ensuring privacy and security

### 🤖 **Advanced Agent Management**
- **200+ Pre-built Agents** across multiple professional domains
- **Custom Agent Creation** with personality traits and expertise areas
- **Agent Library Management** with save, edit, and reuse functionality
- **Bulk Operations** for efficient agent management
- **Real-time Agent Updates** with validation and error handling

### ⚡ **Real-Time Simulation Engine**
- **Live Conversation Generation** using Gemini 2.0 Flash
- **Observer System** for real-time intervention and guidance
- **Multi-Language Support** with translation capabilities
- **Scenario Management** with custom and random scenario generation
- **Auto-progression** with configurable conversation intervals

### 📊 **Comprehensive Analytics**
- **Real-time Metrics** tracking conversation quality and user engagement
- **Usage Analytics** with detailed breakdowns and trends
- **Weekly Summaries** with automated report generation
- **Visual Data** preparation for frontend charts and dashboards
- **Export Capabilities** for data analysis and reporting

### 📄 **Document Generation System**
- **AI-Powered Document Creation** from conversation insights
- **Multiple Document Types** (protocols, research, reports, budgets)
- **Professional Formatting** with HTML and CSS styling
- **Chart Integration** with embedded visualizations
- **Bulk Document Management** with category-based organization

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.8+**
- **MongoDB 4.4+** (local or cloud instance)
- **API Keys** for Gemini and fal.ai (for full functionality)

### Installation

1. **Clone and Setup**
   ```bash
   git clone https://github.com/your-username/ai-agent-simulation-backend.git
   cd ai-agent-simulation-backend
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Environment Configuration**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Run the Server**
   ```bash
   uvicorn server:app --host 0.0.0.0 --port 8001 --reload
   ```

5. **Access API Documentation**
   - **API Docs**: http://localhost:8001/docs
   - **Health Check**: http://localhost:8001/health

---

## 📡 API Documentation

### Authentication Endpoints

| Method | Endpoint | Description | Request Body |
|--------|----------|-------------|--------------|
| POST | `/api/auth/register` | Register new user | `{email, password, name}` |
| POST | `/api/auth/login` | User authentication | `{email, password}` |
| POST | `/api/auth/test-login` | Guest access (demo) | None |
| GET | `/api/auth/me` | Get current user profile | None |
| POST | `/api/auth/generate-profile-avatar` | Generate AI avatar | `{prompt}` |

### Agent Management

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/agents` | List user's agents | ✅ |
| POST | `/api/agents` | Create new agent | ✅ |
| PUT | `/api/agents/{id}` | Update agent details | ✅ |
| DELETE | `/api/agents/{id}` | Delete single agent | ✅ |
| POST | `/api/agents/bulk-delete` | Delete multiple agents | ✅ |

### Saved Agents Library

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/saved-agents` | Get user's saved agents | ✅ |
| POST | `/api/saved-agents` | Save agent to library | ✅ |
| PUT | `/api/saved-agents/{id}` | Update saved agent | ✅ |
| DELETE | `/api/saved-agents/{id}` | Remove from library | ✅ |

### Simulation Control

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/simulation/state` | Get current simulation state | ✅ |
| POST | `/api/simulation/start` | Start new simulation | ✅ |
| POST | `/api/simulation/pause` | Pause active simulation | ✅ |
| POST | `/api/simulation/resume` | Resume paused simulation | ✅ |
| POST | `/api/simulation/set-scenario` | Set custom scenario | ✅ |

### Conversation Management

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/conversations` | Get user's conversations | ✅ |
| POST | `/api/conversation/generate` | Generate new conversation | ✅ |
| POST | `/api/conversations/translate` | Translate conversation | ✅ |
| DELETE | `/api/conversations/bulk` | Delete multiple conversations | ✅ |

### Observer System

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/observer/send-message` | Send observer message | ✅ |
| GET | `/api/observer/messages` | Get observer messages | ✅ |

### Document Management

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/documents` | Get user's documents | ✅ |
| POST | `/api/documents` | Create new document | ✅ |
| PUT | `/api/documents/{id}` | Update document | ✅ |
| DELETE | `/api/documents/{id}` | Delete document | ✅ |
| POST | `/api/documents/bulk-delete` | Delete multiple documents | ✅ |
| GET | `/api/documents/categories` | Get document categories | ✅ |

### Analytics & Reporting

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/analytics/comprehensive` | Complete analytics dashboard | ✅ |
| GET | `/api/analytics/weekly-summary` | Weekly usage summary | ✅ |
| POST | `/api/feedback/send` | Submit user feedback | ✅ |

### Admin Endpoints (Role-based)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/admin/dashboard/stats` | Admin dashboard statistics | ✅ Admin |
| GET | `/api/admin/users` | User management | ✅ Admin |
| GET | `/api/admin/activity/recent` | Recent activity logs | ✅ Admin |

---

## 🏗️ Architecture

### Technology Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Web Framework** | FastAPI | High-performance async API framework |
| **Database** | MongoDB | Flexible document storage |
| **Authentication** | JWT + bcrypt | Secure user management |
| **AI Integration** | Gemini 2.0 Flash | Natural language processing |
| **Avatar Generation** | fal.ai | AI-powered profile images |
| **Validation** | Pydantic | Request/response validation |
| **CORS** | FastAPI middleware | Cross-origin resource sharing |

### Project Structure

```
backend/
├── 📄 server.py                    # Main FastAPI application
├── 📄 smart_conversation.py        # AI conversation engine
├── 📄 enhanced_document_system.py  # Document generation system
├── 📄 database.py                  # Database connection and models
├── 📄 cache.py                     # Caching layer
├── 📄 rate_limiter.py             # API rate limiting
├── 📄 monitoring.py               # Performance monitoring
├── 📁 external_integrations/       # Third-party API integrations
├── 📄 requirements.txt            # Python dependencies
├── 📄 requirements-production.txt # Production dependencies
└── 📄 .env.example               # Environment template
```

### Key Components

#### **🔧 Core Application (`server.py`)**
- FastAPI application setup with middleware
- All API endpoints and route handlers
- Authentication and authorization logic
- Error handling and validation
- CORS configuration for frontend integration

#### **🧠 Conversation Engine (`smart_conversation.py`)**
- Gemini 2.0 Flash integration for natural conversations
- Context-aware conversation generation
- Anti-repetition algorithms
- Personality-based response patterns
- Multi-agent coordination logic

#### **📝 Document System (`enhanced_document_system.py`)**
- AI-powered document generation from conversations
- Professional formatting with HTML/CSS
- Chart generation and embedding
- Quality gate system for document creation
- Multiple document types and templates

#### **🗄️ Database Layer (`database.py`)**
- MongoDB connection management
- Async database operations
- User data isolation
- Indexing strategies for performance
- Data validation and sanitization

---

## 🔒 Security & Authentication

### JWT Authentication
```python
# Token generation with expiration
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=JWT_EXPIRATION_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
```

### User Data Isolation
- All database queries filter by `user_id`
- Strict ownership validation for all operations
- No cross-user data access permitted
- Secure bulk operations with user verification

### Security Features
- **Password Hashing**: bcrypt with salt rounds
- **JWT Validation**: Automatic token verification
- **Input Validation**: Pydantic model validation
- **Rate Limiting**: API endpoint protection
- **Error Handling**: Secure error messages without data leakage

---

## 📊 Performance & Monitoring

### Performance Metrics
- **API Response Time**: < 100ms average
- **Database Queries**: Optimized with proper indexing
- **Concurrent Users**: 100+ supported
- **Memory Usage**: Efficient with async operations

### Monitoring Features
```python
# Built-in performance monitoring
async def track_api_usage(endpoint: str, user_id: str, response_time: float):
    await db.api_usage.insert_one({
        "endpoint": endpoint,
        "user_id": user_id,
        "response_time": response_time,
        "timestamp": datetime.utcnow()
    })
```

### Caching Strategy
- **Agent Data**: Cached for 5 minutes
- **Conversation History**: Cached for 2 minutes
- **Analytics Data**: Cached for 10 minutes
- **User Profiles**: Cached for 15 minutes

---

## 🚢 Deployment

### Environment Variables

Create a `.env` file with the following configuration:

```env
# Database
MONGO_URL=mongodb://localhost:27017/ai_agent_simulation

# Authentication
JWT_SECRET=your-super-secure-jwt-secret-key-here
JWT_ALGORITHM=HS256
JWT_EXPIRATION_MINUTES=1440

# AI Services
GEMINI_API_KEY=your-gemini-api-key-here
FAL_KEY=your-fal-api-key-here

# Server Configuration
HOST=0.0.0.0
PORT=8001
DEBUG=false

# CORS
CORS_ORIGINS=["http://localhost:3000", "https://yourdomain.com"]

# Admin User (Optional)
ADMIN_EMAIL=admin@yourdomain.com
ADMIN_PASSWORD=secure-admin-password
```

### Development Deployment

```bash
# Install dependencies
pip install -r requirements.txt

# Start with auto-reload
uvicorn server:app --host 0.0.0.0 --port 8001 --reload

# Or with specific configuration
python -m uvicorn server:app --host 0.0.0.0 --port 8001 --workers 1
```

### Production Deployment

#### **Using Docker**
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements-production.txt .
RUN pip install -r requirements-production.txt

COPY . .
EXPOSE 8001

CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8001", "--workers", "4"]
```

#### **Using Gunicorn (Production)**
```bash
# Install production dependencies
pip install -r requirements-production.txt

# Start with Gunicorn
gunicorn server:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8001
```

#### **Environment-Specific Settings**
```bash
# Production settings
export DEBUG=false
export WORKERS=4
export CORS_ORIGINS='["https://yourdomain.com"]'

# Start production server
uvicorn server:app --host 0.0.0.0 --port 8001 --workers 4
```

---

## 🧪 Testing

### API Testing

```bash
# Test authentication
curl -X POST http://localhost:8001/api/auth/test-login

# Test protected endpoint
curl -X GET http://localhost:8001/api/agents \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# Test agent creation
curl -X POST http://localhost:8001/api/agents \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "Test Agent", "archetype": "scientist", "expertise": "Testing"}'
```

### Health Check

```bash
# Check server status
curl http://localhost:8001/health

# Expected response
{
  "status": "healthy",
  "timestamp": "2025-01-15T10:30:00Z",
  "version": "1.3.0"
}
```

### Database Testing

```python
# Test database connection
from database import db

async def test_db_connection():
    try:
        await db.admin.command('ping')
        print("Database connection: OK")
    except Exception as e:
        print(f"Database connection failed: {e}")
```

---

## 🔧 Troubleshooting

### Common Issues

#### **MongoDB Connection Issues**
```bash
# Check MongoDB status
brew services list | grep mongodb  # macOS
sudo systemctl status mongod       # Linux

# Start MongoDB
brew services start mongodb        # macOS
sudo systemctl start mongod        # Linux

# Test connection
python -c "from pymongo import MongoClient; print(MongoClient().admin.command('ping'))"
```

#### **Environment Variables Not Loading**
```bash
# Check if .env file exists
ls -la .env

# Verify variables are loaded
python -c "import os; print(os.environ.get('MONGO_URL', 'Not found'))"

# Source environment manually
export $(grep -v '^#' .env | xargs)
```

#### **API Key Issues**
```bash
# Test Gemini API key
curl -H "Authorization: Bearer $GEMINI_API_KEY" \
  https://generativelanguage.googleapis.com/v1beta/models

# Test fal.ai key
curl -H "Authorization: Key $FAL_KEY" \
  https://fal.run/fal-ai/fast-sdxl/health
```

#### **Port Conflicts**
```bash
# Check what's using port 8001
lsof -i :8001

# Kill process using port
kill -9 $(lsof -t -i:8001)

# Use different port
uvicorn server:app --port 8002
```

### Debug Mode

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Or set in environment
export DEBUG=true
```

---

## 🤝 Contributing

### Development Setup

1. **Fork the repository**
2. **Create feature branch**: `git checkout -b feature/new-feature`
3. **Install development dependencies**: `pip install -r requirements.txt`
4. **Make your changes**
5. **Run tests**: `python -m pytest`
6. **Submit pull request**

### Code Standards

- **Follow PEP 8** for Python code style
- **Use type hints** for all function parameters and returns
- **Write docstrings** for all public functions and classes
- **Add tests** for new functionality
- **Update documentation** as needed

### Git Commit Messages

```
feat: add new agent personality system
fix: resolve conversation generation timeout
docs: update API documentation
style: format code with black
refactor: simplify authentication logic
test: add integration tests for agents
```

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🆘 Support

### Documentation
- **API Documentation**: http://localhost:8001/docs (interactive)
- **GitHub Issues**: [Report bugs and feature requests](https://github.com/your-username/ai-agent-simulation-backend/issues)
- **GitHub Discussions**: [Community discussions](https://github.com/your-username/ai-agent-simulation-backend/discussions)

### Getting Help

1. **Check the troubleshooting section** above
2. **Review API documentation** at `/docs`
3. **Search existing GitHub issues**
4. **Create a new issue** with:
   - Environment details (Python version, OS)
   - Steps to reproduce
   - Expected vs actual behavior
   - Error logs/stack traces

---

## 🎯 Roadmap

### Current Version (v1.3.0)
- ✅ Enhanced conversation engine with anti-repetition
- ✅ Professional document generation system
- ✅ Comprehensive analytics and reporting
- ✅ Advanced agent management with saved libraries
- ✅ Real-time observer system

### Upcoming Features (v2.0.0)
- [ ] **WebSocket Integration** for real-time updates
- [ ] **Voice API Integration** for audio conversations
- [ ] **Advanced ML Analytics** with prediction models
- [ ] **Plugin System** for custom integrations
- [ ] **Multi-tenancy Support** for enterprise deployments
- [ ] **GraphQL API** alongside REST endpoints

### Future Enhancements
- [ ] **Microservices Architecture** for better scalability
- [ ] **Event-driven Architecture** with message queues
- [ ] **Advanced Caching** with Redis integration
- [ ] **API Versioning** for backward compatibility
- [ ] **Comprehensive Logging** with structured logging

---

<div align="center">

**⭐ Star this repository if you find it useful!**

**Built with ❤️ using FastAPI and modern Python development practices**

*Powering the next generation of AI agent simulations*

---

**[Documentation](http://localhost:8001/docs) • [Issues](https://github.com/your-username/ai-agent-simulation-backend/issues) • [Discussions](https://github.com/your-username/ai-agent-simulation-backend/discussions)**

</div>