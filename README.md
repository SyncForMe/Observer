# 🤖 AI Agent Simulation Platform

A sophisticated web application that allows users to create, manage, and run simulations with multiple AI agents that interact in real-time conversations. Perfect for testing scenarios, research, and understanding AI agent dynamics.

![Platform Screenshot](docs/images/platform-overview.png)

## ✨ Features

### 🔭 Observatory Tab (Simulation Control)
- **Real-time Agent Monitoring**: Visual display of active agents with profiles
- **Simulation Controls**: Play/Pause/Resume, Fast Forward, Observer Input
- **Agent Management**: Add, edit, remove agents directly from simulation
- **Observer Chat**: Real-time interaction with running simulations (hidden until activated)
- **Weekly Reports**: Generate comprehensive analytics and insights

### 🤖 Agent Library  
- **90+ Professional Agents**: Across Healthcare, Finance, and Technology sectors
- **38 Categories**: Detailed specializations in each industry
- **Quick Team Builders**: Pre-configured teams (Research, Business, Crypto)
- **Agent Profiles**: Complete backgrounds, expertise, goals, and personalities
- **Add Agents**: One-click agent addition to simulations

### 💬 Real-time Simulations
- **Multi-agent Conversations**: Agents interact naturally in scenarios
- **8 Scenario Types**: Business meetings, research discussions, brainstorming
- **Auto-progression**: Conversations continue with configurable intervals
- **Observer Intervention**: Guide simulations in real-time

### 📊 Analytics & Insights
- **Weekly Analytics**: Comprehensive usage metrics and trends
- **Agent Rankings**: Top performers and usage statistics
- **Document Generation**: AI-powered reports from conversations
- **Export Options**: Multiple formats for data analysis

### 👤 User Management
- **Authentication**: Email/password and Google OAuth
- **Profile Management**: Personal settings and preferences
- **My Agents**: Save and reuse custom agent configurations
- **Help System**: Comprehensive documentation and support

## 🚀 Quick Start

### Prerequisites
- **Node.js** 18+ and npm/yarn
- **Python** 3.8+
- **MongoDB** 4.4+
- **Git**

### 1. Clone Repository
```bash
git clone https://github.com/yourusername/ai-agent-simulation.git
cd ai-agent-simulation
```

### 2. Backend Setup
```bash
cd backend
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your configuration
python -m uvicorn server:app --host 0.0.0.0 --port 8001 --reload
```

### 3. Frontend Setup
```bash
cd frontend
yarn install
cp .env.example .env
# Edit .env with your configuration
yarn start
```

### 4. Access Application
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8001
- **API Docs**: http://localhost:8001/docs

## 📁 Project Structure

```
ai-agent-simulation/
├── README.md                 # This file
├── DEPLOYMENT.md            # Deployment instructions
├── API.md                   # API documentation
├── FEATURES.md              # Detailed feature documentation
├── backend/
│   ├── README.md            # Backend-specific setup
│   ├── server.py            # FastAPI application
│   ├── requirements.txt     # Python dependencies
│   └── .env.example         # Environment template
├── frontend/
│   ├── README.md            # Frontend-specific setup
│   ├── package.json         # Node.js dependencies
│   ├── .env.example         # Environment template
│   └── src/
│       ├── App.js           # Main React component
│       ├── SimulationControl.js  # Observatory tab
│       ├── AgentLibraryComplete.js  # Agent Library
│       └── ...              # Other components
├── docs/
│   ├── setup/               # Setup guides
│   ├── features/            # Feature documentation
│   └── api/                 # API examples
└── scripts/
    ├── setup.sh             # Automated setup script
    └── deploy.sh            # Deployment script
```

## 🛠 Technology Stack

### Frontend
- **React** 19.0.0 - Modern UI library
- **Tailwind CSS** - Utility-first styling
- **Framer Motion** 12.18.1 - Smooth animations
- **Axios** 1.8.4 - HTTP client
- **JWT Decode** 4.0.0 - Authentication

### Backend  
- **FastAPI** 0.115.6 - High-performance API framework
- **MongoDB** with Motor 3.3.2 - Async database driver
- **PyJWT** 2.8.0 - JWT authentication
- **OpenAI** 1.54.5 - AI integrations
- **Emergent Integrations** - Platform-specific tools

### Infrastructure
- **Docker** - Containerization
- **Nginx** - Reverse proxy
- **Kubernetes** - Orchestration (production)

## 🔧 Environment Variables

### Backend (.env)
```env
# Database
MONGO_URL=mongodb://localhost:27017/ai_simulation

# Security
JWT_SECRET_KEY=your_super_secure_jwt_secret_key_here
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30

# AI Services
OPENAI_API_KEY=your_openai_api_key_here
FAL_KEY=your_fal_ai_key_here

# Google OAuth (optional)
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
```

### Frontend (.env)
```env
# Backend URL
REACT_APP_BACKEND_URL=http://localhost:8001

# Development
WDS_SOCKET_PORT=443
```

## 📚 Documentation

- [**DEPLOYMENT.md**](DEPLOYMENT.md) - Production deployment guide
- [**API.md**](API.md) - Complete API reference
- [**FEATURES.md**](FEATURES.md) - Detailed feature documentation
- [**backend/README.md**](backend/README.md) - Backend setup and development
- [**frontend/README.md**](frontend/README.md) - Frontend setup and development

## 🧪 Development

### Running Tests
```bash
# Backend tests
cd backend && python -m pytest

# Frontend tests  
cd frontend && yarn test
```

### Development Mode
```bash
# Start both services in development
./scripts/dev.sh

# Or start individually
cd backend && python -m uvicorn server:app --reload
cd frontend && yarn start
```

## 🚀 Deployment

### Production Build
```bash
# Build frontend
cd frontend && yarn build

# Production deployment
./scripts/deploy.sh
```

### Docker Deployment
```bash
docker-compose up -d
```

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed deployment instructions.

## 📈 Key Metrics

- **90+ AI Agents** across 3 sectors (Healthcare, Finance, Technology)
- **38 Categories** with specialized agent types
- **8 Simulation Scenarios** for different use cases
- **Real-time Performance** with sub-500ms API responses
- **Enterprise Security** with JWT and user isolation

## 🎯 Use Cases

1. **Business Strategy**: Test team dynamics and decision-making
2. **Research & Development**: Simulate expert consultations
3. **Training & Education**: Practice scenarios with AI role-playing
4. **Creative Projects**: Brainstorm with diverse AI personalities
5. **Process Optimization**: Test workflow improvements

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: Check docs/ folder
- **Issues**: GitHub Issues
- **Email**: support@yourdomain.com
- **Discord**: [Community Server](https://discord.gg/your-server)

## 🏆 Credits

Built with ❤️ using modern web technologies and AI integrations.

---

**Ready to explore AI agent simulations?** Follow the setup guide and start creating your first simulation!