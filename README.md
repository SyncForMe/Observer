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
## 🚀 **Installation & Setup**

### **Prerequisites**
- Python 3.11+
- Node.js 16+
- MongoDB 6.0+
- Yarn package manager

### **Backend Setup**
```bash
# Clone the repository
git clone https://github.com/your-username/ai-agent-simulation.git
cd ai-agent-simulation

# Backend installation
cd backend
pip install -r requirements.txt

# Environment setup
cp .env.example .env
# Configure your MongoDB URL and API keys in .env
```

### **Frontend Setup**
```bash
# Frontend installation  
cd frontend
yarn install

# Environment setup
cp .env.example .env
# Configure your backend URL in .env
```

### **Required Environment Variables**

**Backend (.env):**
```env
MONGO_URL=mongodb://localhost:27017/ai_simulation
JWT_SECRET=your-jwt-secret-key
GOOGLE_CLIENT_ID=your-google-oauth-client-id
GOOGLE_CLIENT_SECRET=your-google-oauth-client-secret
```

**Frontend (.env):**
```env
REACT_APP_BACKEND_URL=http://localhost:8001
```

### **Running the Application**
```bash
# Start MongoDB service
sudo systemctl start mongod

# Start backend (from backend directory)
python server.py

# Start frontend (from frontend directory)
yarn start
```