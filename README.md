# 🤖 AI Agent Simulation Platform

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![React](https://img.shields.io/badge/React-18.0.0-blue.svg)](https://reactjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115.6-green.svg)](https://fastapi.tiangolo.com/)
[![MongoDB](https://img.shields.io/badge/MongoDB-6.0-brightgreen.svg)](https://mongodb.com/)
[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://python.org/)

> **A sophisticated AI-powered simulation platform for creating, managing, and running real-time conversations among multiple AI agents. Perfect for testing scenarios, research, and understanding AI collaboration dynamics.**

## 🎯 **Overview**

The AI Agent Simulation Platform enables users to create diverse AI agents with unique personalities, expertise, and backgrounds, then watch them collaborate in real-time conversations. The platform features advanced memory management, document generation capabilities, and professional PDF export functionality.

### **Key Use Cases**
- **Business Strategy**: Test team dynamics and decision-making processes
- **Research & Development**: Simulate expert consultations and peer reviews  
- **Training & Education**: Practice scenarios with AI-powered role-playing
- **Creative Projects**: Brainstorm with diverse AI personalities
- **Process Optimization**: Test workflow improvements with virtual teams

## ✨ **Features**

### **🧠 Advanced AI Agent Management**
- **9 Unique Archetypes**: Scientist, Engineer, Leader, Skeptic, Optimist, Artist, Adventurer, Mediator, Researcher
- **Personality Customization**: Fine-tune traits like extroversion, optimism, curiosity, cooperativeness, and energy
- **AI Avatar Generation**: Create professional headshots using fal.ai integration
- **Agent Library**: Save, organize, and reuse favorite agents across simulations
- **Cross-Round References**: Agents reference previous conversations and build on past discussions

### **💬 Intelligent Conversation System**
- **Real-Time Conversations**: Agents interact naturally in configurable scenarios
- **Rolling Context Window**: Automatic summarization at 25+ messages for infinite conversation capability
- **Multiple Scenarios**: 8+ pre-built scenarios including business meetings, research discussions, crisis management
- **Multi-Language Support**: Run simulations in 5+ languages with automatic translation
- **Document-Focused Discussions**: Agents actively work toward creating helpful documents

### **📄 Professional Document Generation**
- **Auto-Document Creation**: AI generates protocols, implementation plans, risk assessments, technical specifications
- **Professional PDF Export**: Beautiful formatting with headers, authors, timestamps, and custom styling
- **Document Review Workflow**: Democratic voting system with approval/rejection and suggestions
- **Multiple Document Types**: Protocols, budgets, timelines, training guides, research reports
- **Bulk PDF Download**: Export multiple documents simultaneously

### **🔭 Observatory Control System**
- **Visual Agent Profiles**: Professional cards showing team composition with archetype-specific colors
- **Real-Time Monitoring**: Live simulation status, agent interactions, and progress tracking
- **Observer Intervention**: Real-time guidance and input during active simulations
- **Enhanced Controls**: Start/Pause/Resume, Fast Forward, Auto Mode, Summary generation

### **📊 Analytics & Insights**
- **Real-Time Metrics**: Conversation counts, agent usage, API consumption tracking
- **Visual Charts**: 30-day activity tracking with interactive visualizations
- **Agent Rankings**: Top performers with medal system and usage statistics  
- **Weekly Reports**: AI-generated comprehensive summaries with key discoveries and documents

### **👤 Complete User Management**
- **Authentication**: JWT-based security with Google OAuth and guest access
- **Profile Management**: Custom avatars, preferences, and account settings
- **Data Isolation**: Complete user data separation and privacy protection
- **Themes & Customization**: Multiple color schemes and interface personalization

## 🏗️ **Technical Architecture**

### **Frontend (React + Tailwind CSS)**
- Modern React 18 application with functional components and hooks
- Advanced Tailwind CSS for responsive, professional styling
- Real-time UI updates with optimized state management
- Modal-based interface for complex interactions
- Smooth animations with Framer Motion

### **Backend (FastAPI + MongoDB)**
- FastAPI REST API with comprehensive endpoint coverage
- MongoDB database for persistent data storage with proper indexing
- JWT authentication with secure user session management
- Real-time simulation engine with advanced AI integration
- Professional document generation with WeasyPrint

### **AI Integrations**
- **Claude 3.5 Sonnet**: Primary conversation generation with natural language processing
- **Gemini 2.0 Flash**: Fallback conversation generation and document analysis
- **fal.ai**: AI avatar generation for agent profiles
- **Translation Services**: Multi-language conversation support
- **Streamlined Navigation** with organized Library dropdown containing Agent Library, Conversations, and Documents
- **Enhanced Header** with instant-loading user avatars and real-time profile updates
- **Advanced Search** with filtering by name, expertise, and archetype
- **Smooth Animations** using Framer Motion for engaging interactions
- **Intuitive Navigation** with clear visual hierarchy and user feedback

### 🎯 **Enhanced Scenario Management**
- **Persistent Scenario Display** in notification bar with expandable details
- **Professional Text Formatting** with intelligent color coding and typography
- **Smart Highlighting** - Red for critical terms, white bold for important entities
- **Expandable Scenario Details** with custom scrollbar and clean layout
- **Scenario Persistence** across page refreshes with localStorage caching
- **Clean Control Interface** with streamlined scenario controls

---

## 🆕 **Latest Improvements**

### **Enhanced Navigation & UX**
- **Streamlined Header Navigation** - Reorganized navigation with "About" (renamed from Home) and consolidated Library dropdown
- **Instant Avatar Loading** - User profile pictures now load instantly on page refresh using localStorage caching
- **Real-Time Profile Updates** - Profile changes reflect immediately in the header without page refresh
- **Improved Agent Library Access** - Enhanced + button in Agent List for seamless navigation to Agent Library

### **Advanced Scenario Management**
- **Persistent Scenario Display** - Scenario name now appears in notification bar when active
- **Expandable Scenario Details** - Click to expand scenario for full context with professional formatting
- **Smart Text Formatting** - Intelligent color coding (red for critical terms, white bold for important entities)
- **Clean Interface** - Removed redundant scenario display from control desk for cleaner UI

### **Backend Enhancements**
- **Fixed Profile Persistence** - Profile updates now persist correctly across page refreshes
- **Enhanced Data Merging** - Improved /auth/me endpoint to merge user data from multiple collections
- **Instant Authentication** - localStorage caching ensures immediate user data display on page load

---

## 🚀 Quick Start

### Prerequisites

- **Node.js** 16.0+ and **yarn**
- **Python** 3.8+ and **pip**
- **MongoDB** 4.4+ (local or cloud instance)
- **API Keys** for fal.ai (for avatar generation)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/ai-agent-simulation.git
   cd ai-agent-simulation
   ```

2. **Backend Setup**
   ```bash
   cd backend
   pip install -r requirements.txt
   cp .env.example .env
   # Configure your environment variables in .env
   uvicorn server:app --host 0.0.0.0 --port 8001 --reload
   ```

3. **Frontend Setup**
   ```bash
   cd frontend
   yarn install
   cp .env.example .env
   # Configure your environment variables in .env
   yarn start
   ```

4. **Access the Application**
   - **Frontend**: http://localhost:3000
   - **Backend API**: http://localhost:8001
   - **API Documentation**: http://localhost:8001/docs

---

## 🏗️ Architecture

### Technology Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Frontend** | React 18, Tailwind CSS, Framer Motion | Modern, responsive user interface |
| **Backend** | FastAPI, Python 3.8+, Pydantic | High-performance API with automatic validation |
| **Database** | MongoDB with async motor driver | Flexible document storage for complex data |
| **AI Integration** | fal.ai, Multiple AI providers | Avatar generation and conversation processing |
| **Authentication** | JWT with bcrypt | Secure user management and session handling |

### Project Structure

```
ai-agent-simulation/
├── 📁 frontend/                    # React application
│   ├── 📁 src/
│   │   ├── App.js                 # Main application component
│   │   ├── SimulationControl.js   # Observatory/simulation control panel
│   │   ├── AgentLibraryComplete.js # Agent library and management
│   │   ├── AgentCreateModal.js    # Agent creation modal
│   │   ├── AuthContext.js         # Authentication context
│   │   └── ...                    # Additional components
│   ├── package.json               # Dependencies and scripts
│   └── .env                       # Environment variables
├── 📁 backend/                    # FastAPI application
│   ├── server.py                  # Main FastAPI server
│   ├── smart_conversation.py      # AI conversation engine
│   ├── enhanced_document_system.py # Document generation
│   ├── requirements.txt           # Python dependencies
│   └── .env                       # Environment variables
├── 📁 docs/                       # Documentation
├── 📁 scripts/                    # Utility scripts
└── README.md                      # This file
```

---

## 🤖 Agent Library

### Core Features

#### **⭐ Favorites System**
- **Star Icons** on all agent cards for quick favoriting
- **Visual Feedback** - Empty stars (☆) become filled stars (⭐)
- **Instant Saving** - Agents are immediately saved to favorites when starred
- **Smart Filtering** - Favorites are separate from created agents

#### **🛠️ My Agents Management**
- **Expandable Structure** - MY AGENTS section works like Industry Sectors
- **Two Subsections**:
  - **Created Agents** - Agents you've designed and created
  - **Favourites** - Agents you've starred from the library
- **Auto-Count Updates** - Real-time counts showing number of agents in each section
- **Create Button** - Integrated "+ Create" card in Created Agents section

#### **📚 Agent Categories**
- **Healthcare & Life Sciences** - Medical professionals, researchers, specialists
- **Finance & Business** - Financial experts, analysts, business leaders
- **Technology & Engineering** - Developers, engineers, technical specialists
- **Quick Teams** - Pre-configured expert teams for common scenarios

### Agent Creation Workflow

1. **Browse Library** - Explore 200+ pre-built agents across industries
2. **Star Favorites** - Click star icons to add agents to your favorites
3. **Create Custom** - Use the "+ Create" button in Created Agents section
4. **Auto-Save** - All created agents are automatically saved to your library
5. **Organize** - Separate management of created agents and favorites

---

## 📡 API Reference

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register` | Register new user |
| POST | `/api/auth/login` | User authentication |
| POST | `/api/auth/test-login` | Guest access |
| GET | `/api/auth/me` | Get current user profile |
| PUT | `/api/auth/generate-profile-avatar` | Generate profile avatar |

### Agent Management
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/agents` | List user's agents |
| POST | `/api/agents` | Create new agent |
| PUT | `/api/agents/{id}` | Update agent details |
| DELETE | `/api/agents/{id}` | Delete agent |

### Saved Agents (My Agents Library)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/saved-agents` | Get user's saved agents |
| POST | `/api/saved-agents` | Save agent to library |
| PUT | `/api/saved-agents/{id}` | Update saved agent |
| DELETE | `/api/saved-agents/{id}` | Delete saved agent |
| PUT | `/api/saved-agents/{id}/favorite` | Toggle favorite status |

### Simulation Control
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/simulation/start` | Start new simulation |
| GET | `/api/simulation/state` | Get current simulation state |
| POST | `/api/simulation/pause` | Pause active simulation |
| POST | `/api/simulation/set-scenario` | Configure custom scenario |
| POST | `/api/simulation/init-research-station` | Initialize research team |

### Analytics & Insights
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/analytics/comprehensive` | Complete analytics dashboard |
| GET | `/api/analytics/weekly-summary` | Weekly usage summary |
| GET | `/api/documents` | Get generated documents |
| GET | `/api/conversations` | Get conversation history |
| GET | `/api/conversation-history` | Get detailed conversation history |

### Feedback & Support
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/feedback/send` | Send user feedback |

For complete API documentation with request/response schemas, visit `/docs` when running the backend server.

---

## 🔒 Security & Authentication

### JWT Authentication Flow
- **Secure Registration/Login** with bcrypt password hashing
- **Token-Based Authentication** with configurable expiration
- **Protected Endpoints** with automatic token validation
- **User Data Isolation** ensuring complete privacy and security

### Data Protection
- **Per-User Data Isolation**: All agents, conversations, and documents are user-specific
- **Favorites System Security**: Users can only toggle favorites on their own agents
- **Secure API Access**: All endpoints require valid authentication tokens
- **Input Validation**: Comprehensive request validation using Pydantic models
- **Error Handling**: Proper HTTP status codes and secure error messages

---

## 🚢 Deployment

### Development Setup
```bash
# Using Docker Compose (Recommended)
docker-compose up -d

# Or manually
# Terminal 1: Start MongoDB
mongod

# Terminal 2: Start Backend
cd backend && uvicorn server:app --reload --host 0.0.0.0 --port 8001

# Terminal 3: Start Frontend
cd frontend && yarn start
```

### Production Deployment
```bash
# Build frontend
cd frontend && yarn build

# Deploy with Docker
docker-compose -f docker-compose.production.yml up -d

# Or use Kubernetes
kubectl apply -f k8s/
```

### Environment Variables

**Backend (.env)**
```env
MONGO_URL=mongodb://localhost:27017/ai_agent_simulation
JWT_SECRET=your-secure-jwt-secret-key-here
FAL_KEY=your-fal-ai-api-key-here
```

**Frontend (.env)**
```env
REACT_APP_BACKEND_URL=http://localhost:8001
```

---

## 🧪 Testing

### Comprehensive Testing Suite
```bash
# Backend API testing
cd backend && python -m pytest tests/ -v

# Frontend component testing
cd frontend && yarn test

# Integration testing
./scripts/run-integration-tests.sh
```

### Manual Testing Checklist

#### **Agent Library Testing**
- [ ] Navigate to Agent Library tab
- [ ] Expand/collapse Industry Sectors
- [ ] Click star icons on agent cards
- [ ] Verify favorites appear in Favourites section
- [ ] Test Created Agents section
- [ ] Use "+ Create" button to create new agent
- [ ] Verify agent appears in Created Agents (not Favourites)

#### **Authentication Testing**
- [ ] Register new user account
- [ ] Login with valid credentials
- [ ] Test guest access with "Continue as Guest"
- [ ] Verify user data isolation
- [ ] Test profile avatar generation

#### **Simulation Testing**
- [ ] Start new simulation
- [ ] Add agents from library
- [ ] Configure custom scenarios
- [ ] Test observer mode interaction
- [ ] Verify real-time conversation updates

---

## 🎯 Recent Updates (v1.5.0)

### ⭐ Enhanced User Experience
- **Notification System Redesign**: Professional notification display in header space
- **Right-to-Left Animation**: Smooth sliding text animations with invisible background
- **Observatory Interface**: Removed header text to create dedicated notification space
- **Symmetric Spacing**: Optimized layout with minimal, equal spacing above and below notifications

### 🤖 Agent Library Improvements
- **Simplified Agent Cards**: Removed goal information for cleaner, more focused displays
- **Consistent Design**: Unified agent card appearance across all sections
- **Enhanced Readability**: Reduced information density for better user comprehension
- **Professional Appearance**: Clean, minimalist design emphasizing agent capabilities

### 🎨 UI/UX Enhancements
- **Layout Stability**: Eliminated card movement during notification display
- **Visual Cleanliness**: Text-only notifications without background containers
- **Seamless Animations**: Professional sliding effects that enhance user engagement
- **Responsive Design**: Optimized spacing and positioning across all screen sizes

### 🔧 Technical Improvements
- **Container Optimization**: Fixed main container padding for symmetric spacing
- **Animation Performance**: Smooth 60fps sliding animations with proper timing
- **Space Reservation**: Fixed height containers prevent layout shifts
- **Code Maintainability**: Simplified component logic and improved separation of concerns

---

## 🤝 Contributing

We welcome contributions! Please follow these guidelines:

### Development Workflow
1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Make your changes** and add comprehensive tests
4. **Run the test suite**: `yarn test && pytest`
5. **Update documentation** if needed
6. **Submit a pull request** with detailed description

### Code Standards
- **Python**: Follow PEP 8, use type hints, write comprehensive docstrings
- **JavaScript**: Use ES6+, React hooks, meaningful component names
- **Git**: Use conventional commit messages (`feat:`, `fix:`, `docs:`, etc.)
- **Testing**: Write tests for all new features and bug fixes

### Contribution Areas
- **🐛 Bug Fixes**: Report and fix issues
- **⭐ New Features**: Enhance existing functionality
- **📚 Documentation**: Improve guides and API docs
- **🧪 Testing**: Add test coverage
- **🎨 UI/UX**: Design improvements
- **🔧 Performance**: Optimization and refactoring

---

## 🔧 Troubleshooting

### Common Issues

**Agent Library Not Loading**
```bash
# Check authentication
curl -X GET http://localhost:8001/api/auth/me \
  -H "Authorization: Bearer YOUR_TOKEN"

# Verify saved agents endpoint
curl -X GET http://localhost:8001/api/saved-agents \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Star Icons Not Working**
```bash
# Check browser console for errors
# Verify favorites API endpoint
curl -X PUT http://localhost:8001/api/saved-agents/AGENT_ID/favorite \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**MongoDB Connection Issues**
```bash
# Check MongoDB status
brew services list | grep mongodb  # macOS
sudo systemctl status mongod       # Linux

# Start MongoDB
brew services start mongodb        # macOS
sudo systemctl start mongod        # Linux
```

**Environment Variables**
```bash
# Check if .env files exist
ls -la backend/.env frontend/.env

# Verify required variables
grep -E "MONGO_URL|JWT_SECRET|FAL_KEY" backend/.env
grep "REACT_APP_BACKEND_URL" frontend/.env
```

For more troubleshooting tips, see our [Documentation](docs/) and [GitHub Issues](https://github.com/your-username/ai-agent-simulation/issues).

---

## 📊 Performance Metrics

### System Performance
- **API Response Time**: < 50ms average for agent operations
- **Database Queries**: < 100ms for complex agent searches
- **Real-Time Updates**: < 25ms latency for favorites toggling
- **Conversation Generation**: 2-4 seconds per simulation round
- **Concurrent Users**: 100+ users supported simultaneously

### User Experience
- **Page Load Time**: < 2 seconds initial load
- **Agent Library**: Instant filtering and search
- **Favorites Toggle**: Immediate visual feedback
- **Mobile Responsiveness**: Optimized for all devices
- **Accessibility**: WCAG 2.1 AA compliant

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🆘 Support & Community

### Getting Help
- **📚 Documentation**: Visit our [Wiki](https://github.com/your-username/ai-agent-simulation/wiki)
- **🐛 Issues**: Report bugs on [GitHub Issues](https://github.com/your-username/ai-agent-simulation/issues)
- **💬 Discussions**: Join our [Community Discussions](https://github.com/your-username/ai-agent-simulation/discussions)
- **📧 Email**: Contact us at support@ai-agent-simulation.com

### Community Resources
- **GitHub Discussions**: Ask questions and share ideas
- **Issue Tracker**: Bug reports and feature requests
- **Wiki**: Comprehensive guides and tutorials
- **Discord**: Real-time community chat (coming soon)

---

## 🎯 Roadmap

### Upcoming Features (v1.6.0)
- [ ] **Notification Variants**: Multiple notification types (success, warning, error)
- [ ] **Agent Card Customization**: User-configurable information display options
- [ ] **Animation Presets**: Multiple animation styles for different contexts
- [ ] **Enhanced Accessibility**: Screen reader support and keyboard navigation
- [ ] **Notification Queue**: Support for multiple simultaneous notifications

### Future Enhancements
- [ ] **Multi-language Support**: Full internationalization
- [ ] **Mobile App**: Native iOS and Android applications
- [ ] **Enterprise Features**: SSO, advanced security, audit logs
- [ ] **API Webhooks**: Real-time event notifications
- [ ] **Plugin System**: Extensible architecture for custom integrations

### Version History
- **v1.5.0** - Enhanced UI/UX with notification system redesign and agent card improvements *(Current)*
- **v1.4.0** - Enhanced Agent Library with favorites and improved management
- **v1.3.0** - Enhanced UI/UX with modern design system
- **v1.2.0** - Added agent library and saved agents functionality
- **v1.1.0** - Performance optimizations and conversation improvements
- **v1.0.0** - Initial release with core simulation features

---

<div align="center">

**⭐ If you find this project useful, please consider giving it a star on GitHub!**

**Built with ❤️ for the AI research and development community**

*Transform your AI agent research with the Observatory platform - where artificial intelligence meets real-time collaboration and advanced agent management.*

---

**🚀 Ready to start? [Get Started](#-quick-start) | 📖 Read the [Documentation](docs/) | 🤝 [Contribute](#-contributing)**

</div>