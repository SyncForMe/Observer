# 🤖 AI Agent Simulation Platform

A sophisticated AI Agent Simulation Platform that allows users to create, manage, and run simulations with multiple AI agents that interact with each other in real-time conversations.

## 🎯 **Overview**

This platform enables users to:
- Create custom AI agents with unique personalities and expertise
- Run real-time simulations with multiple agents
- Generate documents from agent conversations
- Analyze simulation results with comprehensive analytics
- Manage agent libraries and conversation history

## 🏗️ **Architecture**

- **Frontend**: React.js with Tailwind CSS
- **Backend**: FastAPI with Python
- **Database**: MongoDB
- **AI Integrations**: Gemini, OpenAI, fal.ai
- **Authentication**: JWT with Google OAuth support

## 🚀 **Features**

### Core Functionality
- ✅ **Agent Management** - Create, edit, and save custom AI agents
- ✅ **Real-time Simulations** - Multi-agent conversations with observer mode
- ✅ **Document Generation** - AI-powered document creation from conversations
- ✅ **Analytics Dashboard** - Comprehensive usage insights and metrics
- ✅ **User Authentication** - Email/password and Google OAuth
- ✅ **Conversation History** - Complete conversation tracking and management

### Advanced Features
- 🎮 **Simulation Control** - Start/stop/pause/resume with fast-forward
- 💬 **Observer Chat** - Real-time interaction during simulations
- 📊 **Weekly Reports** - Automated insights and recommendations
- 🌍 **Multi-language Support** - Real-time translation capabilities
- 🎭 **Custom Scenarios** - Professional scenario creation and templates
- 📄 **Document Center** - Bulk operations and organization

## 📋 **Prerequisites**

- Node.js (v16+ recommended)
- Python (v3.8+ required)
- MongoDB (v4.4+ recommended)
- Yarn package manager

## ⚙️ **Installation**

### 1. Clone the Repository
```bash
git clone https://github.com/YourUsername/ai-agent-simulation.git
cd ai-agent-simulation
```

### 2. Set Up Environment Variables

**Backend Configuration:**
```bash
cd backend
cp .env.example .env
```

Edit `backend/.env` and add your actual API keys:
```env
MONGO_URL="mongodb://localhost:27017"
DB_NAME="ai_simulation"
GEMINI_API_KEY="your_actual_gemini_api_key"
FAL_KEY="your_actual_fal_ai_api_key"
OPENAI_API_KEY="your_actual_openai_api_key"
GOOGLE_CLIENT_ID="your_google_oauth_client_id"
GOOGLE_CLIENT_SECRET="your_google_oauth_client_secret"
JWT_SECRET="your_super_secure_jwt_secret"
```

**Frontend Configuration:**
```bash
cd ../frontend
cp .env.example .env
```

Edit `frontend/.env`:
```env
WDS_SOCKET_PORT=443
REACT_APP_BACKEND_URL=http://localhost:8001
```

### 3. Install Dependencies

**Backend:**
```bash
cd backend
pip install -r requirements.txt
```

**Frontend:**
```bash
cd ../frontend
yarn install
```

### 4. Start MongoDB
```bash
# Using Docker (recommended)
docker run -d -p 27017:27017 --name mongodb mongo:latest

# Or start your local MongoDB service
sudo systemctl start mongod
```

### 5. Run the Application

**Start Backend (Terminal 1):**
```bash
cd backend
python server.py
```

**Start Frontend (Terminal 2):**
```bash
cd frontend
yarn start
```

The application will be available at:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8001

## 🔑 **API Keys Setup**

### Required API Keys

1. **Gemini API Key**
   - Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Create a new API key
   - Add to `GEMINI_API_KEY` in `.env`

2. **OpenAI API Key**
   - Go to [OpenAI Platform](https://platform.openai.com/api-keys)
   - Create a new secret key
   - Add to `OPENAI_API_KEY` in `.env`

3. **fal.ai API Key**
   - Go to [fal.ai](https://fal.ai/)
   - Create an account and get your API key
   - Add to `FAL_KEY` in `.env`

4. **Google OAuth (Optional)**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create OAuth 2.0 credentials
   - Add client ID and secret to `.env`

## 🐳 **Docker Deployment**

### Using Docker Compose
```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Individual Docker Builds
```bash
# Backend
cd backend
docker build -t ai-simulation-backend .

# Frontend
cd frontend
docker build -t ai-simulation-frontend .
```

## 📊 **Usage**

### Creating Agents
1. Navigate to **Agent Library** tab
2. Click **Create New Agent**
3. Define personality traits, expertise, and goals
4. Generate AI avatar (optional)
5. Save to your personal library

### Running Simulations
1. Go to **Simulation** tab
2. Add agents from your library
3. Select or create a scenario
4. Click **Start Simulation**
5. Use **Observer Chat** to interact in real-time

### Generating Documents
1. Simulations automatically generate relevant documents
2. Access via **Documents** tab
3. Create custom documents manually
4. Export in multiple formats

### Analytics
1. View comprehensive metrics in **Analytics** dashboard
2. Track agent performance and usage
3. Generate weekly reports
4. Export data for analysis

## 🛠️ **Development**

### Project Structure
```
ai-agent-simulation/
├── backend/
│   ├── server.py              # Main FastAPI application
│   ├── smart_conversation.py  # Conversation generation logic
│   ├── enhanced_document_system.py  # Document creation system
│   └── requirements.txt       # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── App.js            # Main React component
│   │   ├── SimulationControl.js  # Simulation management
│   │   ├── AgentLibrary.js   # Agent management
│   │   ├── DocumentCenter.js # Document management
│   │   └── AnalyticsDashboard.js  # Analytics display
│   └── package.json          # Node.js dependencies
└── README.md
```

### Adding New Features
1. Backend endpoints go in `server.py`
2. Frontend components go in `src/`
3. Follow existing patterns for consistency
4. Test thoroughly before committing

### API Documentation
Once running, visit: http://localhost:8001/docs

## 🧪 **Testing**

### Backend Testing
```bash
cd backend
python -m pytest tests/
```

### Frontend Testing
```bash
cd frontend
yarn test
```

### Integration Testing
```bash
# Run full test suite
yarn test:integration
```

## 🚀 **Deployment**

### Environment Setup
1. Set up production MongoDB instance
2. Configure environment variables for production
3. Build frontend for production
4. Deploy backend with proper CORS settings

### Production Considerations
- Use environment variables for all secrets
- Enable HTTPS in production
- Set up proper monitoring and logging
- Configure backup strategies for MongoDB
- Implement rate limiting for API endpoints

## 🤝 **Contributing**

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

## 📝 **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 **Support**

- Create an issue for bug reports
- Join our community discussions
- Check the documentation at `/docs`

## 🔄 **Changelog**

### v1.0.0 (Current)
- Initial release with full simulation platform
- Agent creation and management
- Real-time conversation system
- Document generation
- Analytics dashboard
- User authentication

---

**Built with ❤️ for AI researchers, developers, and enthusiasts**
