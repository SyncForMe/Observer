# ⚛️ Frontend Setup - AI Agent Simulation Platform

Modern React application with Tailwind CSS for the AI Agent Simulation Platform.

## 🛠 Technology Stack

- **React** 19.0.0 - Modern UI library with hooks
- **Tailwind CSS** 3.x - Utility-first CSS framework
- **Framer Motion** 12.18.1 - Smooth animations and transitions
- **Axios** 1.8.4 - HTTP client for API communication
- **React Router** 7.5.1 - Navigation and routing
- **JWT Decode** 4.0.0 - Authentication token handling

## 📦 Installation

### 1. Node.js Setup
```bash
# Install Node.js 18+ (using nvm)
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
nvm install 18
nvm use 18

# Or install directly from nodejs.org
```

### 2. Package Installation
```bash
# Navigate to frontend directory
cd frontend

# Install dependencies with Yarn (preferred)
yarn install

# Or with npm
npm install
```

### 3. Environment Configuration
```bash
# Copy environment template
cp .env.example .env

# Edit with your settings
nano .env
```

### 4. Environment Variables
```env
# Backend API URL
REACT_APP_BACKEND_URL=http://localhost:8001

# Development server configuration
WDS_SOCKET_PORT=443
GENERATE_SOURCEMAP=false

# Optional: Google Analytics (if needed)
REACT_APP_GA_TRACKING_ID=your_ga_tracking_id
```

## 🚀 Running the Application

### Development Mode
```bash
# Start development server
yarn start

# Or with npm
npm start
```

The application will open at http://localhost:3000 with hot reload enabled.

### Production Build
```bash
# Create optimized production build
yarn build

# Serve production build locally (for testing)
npx serve -s build -l 3000
```

## 🏗 Project Structure

```
frontend/
├── public/
│   ├── index.html          # HTML template
│   ├── favicon.ico         # App icon
│   └── manifest.json       # PWA manifest
├── src/
│   ├── index.js            # Application entry point
│   ├── App.js              # Main application component
│   ├── App.css             # Global styles
│   ├── index.css           # Tailwind imports
│   │
│   ├── components/         # Reusable UI components
│   │   ├── SimulationControl.js    # Observatory tab
│   │   ├── AgentLibraryComplete.js # Agent Library
│   │   ├── ConversationViewer.js   # Chat history
│   │   ├── DocumentCenter.js       # Document management
│   │   ├── AnalyticsDashboard.js   # Analytics
│   │   └── WeeklySummary.js        # Reports
│   │
│   ├── hooks/              # Custom React hooks
│   │   ├── useAuth.js      # Authentication hook
│   │   └── useSimulation.js # Simulation state hook
│   │
│   ├── services/           # API service functions
│   │   ├── api.js          # Axios configuration
│   │   ├── authService.js  # Authentication API
│   │   └── agentService.js # Agent management API
│   │
│   ├── utils/              # Utility functions
│   │   ├── constants.js    # App constants
│   │   ├── helpers.js      # Helper functions
│   │   └── validation.js   # Form validation
│   │
│   └── styles/             # Additional stylesheets
│       ├── components.css  # Component styles
│       └── animations.css  # Custom animations
├── package.json            # Dependencies and scripts
├── tailwind.config.js      # Tailwind configuration
├── postcss.config.js       # PostCSS configuration
└── .env.example            # Environment template
```

## 🎨 Styling & Design

### Tailwind CSS Configuration
```javascript
// tailwind.config.js
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: '#6366f1',
        secondary: '#8b5cf6',
        accent: '#06b6d4',
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
      },
      animation: {
        'fade-in': 'fadeIn 0.5s ease-in-out',
        'slide-up': 'slideUp 0.3s ease-out',
      }
    },
  },
  plugins: [],
}
```

### Design System
```css
/* Color Palette */
:root {
  --color-primary: #6366f1;
  --color-secondary: #8b5cf6;
  --color-success: #10b981;
  --color-warning: #f59e0b;
  --color-error: #ef4444;
  --color-text: #1f2937;
  --color-text-light: #6b7280;
}

/* Glass Morphism Effects */
.glass {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

/* Gradient Backgrounds */
.gradient-primary {
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
}
```

## 🧩 Key Components

### 1. Observatory Tab (SimulationControl.js)
```javascript
// Main simulation control interface
const SimulationControl = ({ setActiveTab }) => {
  // Features:
  // - Real-time agent monitoring
  // - Play/Pause/Fast Forward controls
  // - Observer chat (hidden by default)
  // - Agent management
  // - Weekly reports
};
```

### 2. Agent Library (AgentLibraryComplete.js)
```javascript
// Complete agent browsing and management
const AgentLibrary = ({ onAddAgent, onRemoveAgent }) => {
  // Features:
  // - 90+ professional agents
  // - 38 categories across 3 sectors
  // - Quick Team Builders
  // - Agent profiles with full details
  // - Add agents to simulations
};
```

### 3. Authentication (App.js)
```javascript
// Authentication context and user management
const useAuth = () => {
  // Features:
  // - JWT token management
  // - Google OAuth integration
  // - User profile management
  // - Session persistence
};
```

## 🔌 API Integration

### Axios Configuration
```javascript
// services/api.js
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

const api = axios.create({
  baseURL: `${API_BASE_URL}/api`,
  timeout: 10000,
});

// Request interceptor for auth tokens
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('authToken');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});
```

### API Service Functions
```javascript
// services/agentService.js
export const agentService = {
  // Get all agents
  getAgents: () => api.get('/agents'),
  
  // Create new agent
  createAgent: (agentData) => api.post('/agents', agentData),
  
  // Update agent
  updateAgent: (id, agentData) => api.put(`/agents/${id}`, agentData),
  
  // Delete agent
  deleteAgent: (id) => api.delete(`/agents/${id}`),
};
```

## 🎭 State Management

### React Context for Authentication
```javascript
// contexts/AuthContext.js
const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem('authToken'));
  
  // Authentication methods
  const login = async (credentials) => { /* ... */ };
  const logout = () => { /* ... */ };
  
  return (
    <AuthContext.Provider value={{ user, token, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};
```

### Component State with Hooks
```javascript
// Example: Simulation state management
const useSimulation = () => {
  const [isRunning, setIsRunning] = useState(false);
  const [isPaused, setIsPaused] = useState(false);
  const [agents, setAgents] = useState([]);
  
  const startSimulation = async () => { /* ... */ };
  const pauseSimulation = async () => { /* ... */ };
  
  return { isRunning, isPaused, agents, startSimulation, pauseSimulation };
};
```

## 🧪 Testing

### Running Tests
```bash
# Run all tests
yarn test

# Run tests in watch mode
yarn test --watch

# Run tests with coverage
yarn test --coverage

# Run specific test file
yarn test SimulationControl.test.js
```

### Testing Configuration
```javascript
// setupTests.js
import '@testing-library/jest-dom';

// Mock environment variables
process.env.REACT_APP_BACKEND_URL = 'http://localhost:8001';
```

### Example Test
```javascript
// __tests__/SimulationControl.test.js
import { render, screen, fireEvent } from '@testing-library/react';
import SimulationControl from '../SimulationControl';

test('renders Observatory control panel', () => {
  render(<SimulationControl setActiveTab={jest.fn()} />);
  expect(screen.getByText('Observatory Control')).toBeInTheDocument();
});

test('shows Add Agents button when no agents', () => {
  render(<SimulationControl setActiveTab={jest.fn()} />);
  expect(screen.getByText('Add Agents')).toBeInTheDocument();
});
```

## 🚀 Build & Deployment

### Production Build
```bash
# Create optimized build
yarn build

# Analyze bundle size
npx webpack-bundle-analyzer build/static/js/*.js
```

### Performance Optimization
```javascript
// Code splitting with React.lazy
const AgentLibrary = React.lazy(() => import('./AgentLibraryComplete'));

// Usage with Suspense
<Suspense fallback={<div>Loading...</div>}>
  <AgentLibrary />
</Suspense>
```

### Environment-specific Builds
```bash
# Development build
REACT_APP_ENV=development yarn build

# Staging build
REACT_APP_ENV=staging yarn build

# Production build
REACT_APP_ENV=production yarn build
```

## 🔧 Development Tips

### VS Code Configuration
```json
// .vscode/settings.json
{
  "emmet.includeLanguages": {
    "javascript": "javascriptreact"
  },
  "editor.codeActionsOnSave": {
    "source.fixAll.eslint": true
  },
  "files.associations": {
    "*.js": "javascriptreact"
  }
}
```

### ESLint Configuration
```json
// .eslintrc.json
{
  "extends": [
    "react-app",
    "react-app/jest"
  ],
  "rules": {
    "no-unused-vars": "warn",
    "no-console": "off"
  }
}
```

### Prettier Configuration
```json
// .prettierrc
{
  "singleQuote": true,
  "trailingComma": "es5",
  "tabWidth": 2,
  "semi": true
}
```

## 🐛 Troubleshooting

### Common Issues

#### Module Not Found Errors
```bash
# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
yarn install
```

#### Build Failures
```bash
# Increase Node.js memory limit
export NODE_OPTIONS="--max-old-space-size=8192"
yarn build
```

#### CORS Issues
```javascript
// Add proxy in package.json for development
{
  "proxy": "http://localhost:8001"
}
```

#### Authentication Issues
```javascript
// Check token storage
console.log('Token:', localStorage.getItem('authToken'));

// Clear auth data
localStorage.removeItem('authToken');
localStorage.removeItem('user');
```

## 📱 PWA Features

### Service Worker
```javascript
// public/sw.js
const CACHE_NAME = 'ai-simulation-v1';
const urlsToCache = [
  '/',
  '/static/js/bundle.js',
  '/static/css/main.css'
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => cache.addAll(urlsToCache))
  );
});
```

### Manifest Configuration
```json
// public/manifest.json
{
  "short_name": "AI Simulation",
  "name": "AI Agent Simulation Platform",
  "icons": [
    {
      "src": "favicon.ico",
      "sizes": "64x64 32x32 24x24 16x16",
      "type": "image/x-icon"
    }
  ],
  "start_url": ".",
  "display": "standalone",
  "theme_color": "#6366f1",
  "background_color": "#ffffff"
}
```

## 📚 Additional Resources

- [React Documentation](https://reactjs.org/docs)
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)
- [Framer Motion Documentation](https://www.framer.com/motion/)
- [React Router Documentation](https://reactrouter.com/)

---

**Frontend is ready!** The React application should now be running at http://localhost:3000