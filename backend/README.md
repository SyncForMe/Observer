# 🔧 Backend Setup - AI Agent Simulation Platform

FastAPI backend with MongoDB for managing AI agents, simulations, and user data.

## 🛠 Technology Stack

- **FastAPI** 0.115.6 - Modern, fast web framework
- **MongoDB** with Motor 3.3.2 - Async NoSQL database  
- **PyJWT** 2.8.0 - JWT authentication
- **OpenAI** 1.54.5 - AI integrations
- **Emergent Integrations** - Platform-specific tools

## 📦 Installation

### 1. Python Environment
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Environment Configuration
```bash
# Copy environment template
cp .env.example .env

# Edit with your settings
nano .env
```

### 3. Required Environment Variables
```env
# Database Configuration
MONGO_URL=mongodb://localhost:27017/ai_simulation

# JWT Security
JWT_SECRET_KEY=your_super_secure_jwt_secret_key_here
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30

# AI Service Keys
OPENAI_API_KEY=your_openai_api_key_here
FAL_KEY=your_fal_ai_key_here

# Google OAuth (Optional)
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret

# Email Configuration (Optional)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password
```

## 🚀 Running the Server

### Development Mode
```bash
# With auto-reload
python -m uvicorn server:app --host 0.0.0.0 --port 8001 --reload

# Or using the startup script
python server.py
```

### Production Mode
```bash
# Without auto-reload
python -m uvicorn server:app --host 0.0.0.0 --port 8001

# With multiple workers
gunicorn server:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8001
```

### Access Points
- **API Server**: http://localhost:8001
- **Interactive Docs**: http://localhost:8001/docs
- **ReDoc**: http://localhost:8001/redoc

## 📊 Database Setup

### MongoDB Installation
```bash
# Ubuntu/Debian
sudo apt-get install mongodb

# macOS with Homebrew
brew install mongodb-community

# Start MongoDB
sudo systemctl start mongodb  # Linux
brew services start mongodb-community  # macOS
```

### Database Structure
```
ai_simulation/
├── users/              # User accounts and authentication
├── agents/             # AI agent profiles and configurations
├── simulations/        # Simulation sessions and states
├── conversations/      # Chat history and messages
├── documents/          # Generated reports and files
├── analytics/          # Usage metrics and insights
└── saved_agents/       # User's personal agent collections
```

## 🔌 API Endpoints

### Authentication
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `POST /api/auth/test-login` - Test authentication
- `GET /api/auth/me` - Get current user info

### Agents Management
- `GET /api/agents` - List all agents
- `POST /api/agents` - Create new agent
- `PUT /api/agents/{agent_id}` - Update agent
- `DELETE /api/agents/{agent_id}` - Delete agent
- `GET /api/saved-agents` - Get user's saved agents

### Simulation Control
- `POST /api/simulation/start` - Start simulation
- `POST /api/simulation/pause` - Pause simulation
- `POST /api/simulation/resume` - Resume simulation
- `POST /api/simulation/fast-forward` - Toggle fast forward
- `GET /api/simulation/state` - Get simulation state
- `POST /api/simulation/generate-summary` - Generate reports

### Analytics & Reports
- `GET /api/analytics/weekly-summary` - Weekly analytics
- `POST /api/simulation/auto-weekly-report` - Setup auto-reports
- `GET /api/reports/check-auto-generation` - Check auto-report status

### Documents & Files
- `GET /api/documents` - List documents
- `POST /api/documents` - Create document
- `POST /api/documents/bulk-delete` - Delete multiple documents

## 🔒 Security Features

### JWT Authentication
```python
# Token generation
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# Token verification
def verify_token(token: str):
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    return payload
```

### User Isolation
- All user data is isolated by user ID
- Database queries include user filtering
- No cross-user data access possible

### Input Validation
- Pydantic models for all API inputs
- SQL injection protection via Motor ORM
- XSS protection on all text inputs

## 🧪 Testing

### Run Tests
```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run all tests
python -m pytest

# Run with coverage
python -m pytest --cov=. --cov-report=html

# Run specific test file
python -m pytest tests/test_agents.py
```

### API Testing
```bash
# Test with curl
curl -X GET "http://localhost:8001/api/agents" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# Test with httpie
http GET localhost:8001/api/agents Authorization:"Bearer YOUR_JWT_TOKEN"
```

## 📈 Performance Optimization

### Database Indexing
```python
# Create indexes for better performance
await db.users.create_index("email")
await db.agents.create_index([("user_id", 1), ("archetype", 1)])
await db.conversations.create_index("simulation_id")
```

### Caching
```python
# Redis caching (optional)
import redis
redis_client = redis.Redis(host='localhost', port=6379, db=0)

# Cache frequently accessed data
@lru_cache(maxsize=100)
def get_agent_archetypes():
    return AGENT_ARCHETYPES
```

## 🔧 Development Tips

### Code Structure
```
backend/
├── server.py              # Main FastAPI application
├── models/
│   ├── user.py            # User data models
│   ├── agent.py           # Agent data models
│   └── simulation.py      # Simulation data models
├── routers/
│   ├── auth.py            # Authentication routes
│   ├── agents.py          # Agent management routes
│   └── simulation.py      # Simulation control routes
├── services/
│   ├── auth_service.py    # Authentication logic
│   ├── agent_service.py   # Agent business logic
│   └── ai_service.py      # AI integration services
└── utils/
    ├── database.py        # Database connection
    ├── security.py        # Security utilities
    └── helpers.py         # Common helper functions
```

### Adding New Endpoints
```python
from fastapi import APIRouter, Depends
from models.user import User
from utils.security import get_current_user

router = APIRouter(prefix="/api/custom", tags=["custom"])

@router.get("/endpoint")
async def custom_endpoint(current_user: User = Depends(get_current_user)):
    return {"message": "Custom endpoint", "user": current_user.email}
```

### Database Operations
```python
# Create document
result = await db.collection.insert_one(document)

# Find documents
documents = await db.collection.find({"user_id": user_id}).to_list(100)

# Update document
await db.collection.update_one(
    {"_id": ObjectId(doc_id)}, 
    {"$set": update_data}
)

# Delete document
await db.collection.delete_one({"_id": ObjectId(doc_id)})
```

## 🐛 Troubleshooting

### Common Issues

#### MongoDB Connection Issues
```bash
# Check MongoDB status
sudo systemctl status mongodb

# Restart MongoDB
sudo systemctl restart mongodb

# Check logs
sudo journalctl -u mongodb
```

#### Import Errors
```bash
# Install missing dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Check Python path
export PYTHONPATH="${PYTHONPATH}:/path/to/backend"
```

#### JWT Token Issues
```bash
# Verify JWT secret is set
echo $JWT_SECRET_KEY

# Generate new secret
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

#### API Permission Errors
```python
# Check user authentication
@router.get("/debug/user")
async def debug_user(current_user: User = Depends(get_current_user)):
    return {"user_id": current_user.id, "email": current_user.email}
```

## 🚀 Deployment

### Production Configuration
```bash
# Set production environment
export ENVIRONMENT=production

# Install production dependencies
pip install gunicorn

# Start with Gunicorn
gunicorn server:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8001
```

### Docker Deployment
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8001

CMD ["gunicorn", "server:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "-b", "0.0.0.0:8001"]
```

See [DEPLOYMENT.md](../DEPLOYMENT.md) for complete deployment instructions.

## 📚 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Motor (MongoDB) Documentation](https://motor.readthedocs.io/)
- [PyJWT Documentation](https://pyjwt.readthedocs.io/)
- [OpenAI API Documentation](https://platform.openai.com/docs)

---

**Backend is ready!** The API server should now be running at http://localhost:8001