import React, { useState, useEffect, useRef, useCallback, createContext, useContext } from 'react';
import axios from 'axios';
import { motion, useAnimationControls, AnimatePresence } from 'framer-motion';
import './App.css';
import HomePage from './HomePage';
import AgentLibrary from './AgentLibraryComplete';
import SimulationControl from './SimulationControl';
import ConversationViewer from './ConversationViewer';
import DocumentCenter from './DocumentCenter';
import AnalyticsDashboard from './AnalyticsDashboard';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Debug logging
console.log('Environment variables loaded:', {
  BACKEND_URL,
  NODE_ENV: process.env.NODE_ENV
});

// Authentication Context
const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [token, setToken] = useState(null);

  useEffect(() => {
    console.log('🔍 AuthProvider: Initializing...');
    // Initialize token from localStorage
    const savedToken = localStorage.getItem('auth_token');
    console.log('🔍 AuthProvider: Saved token found:', !!savedToken);
    if (savedToken) {
      setToken(savedToken);
      checkAuthStatus(savedToken);
    } else {
      console.log('🔍 AuthProvider: No saved token, setting loading to false');
      setLoading(false);
    }
  }, []);

  const checkAuthStatus = async (authToken) => {
    console.log('🔍 AuthProvider: Checking auth status with token:', !!authToken);
    try {
      const response = await axios.get(`${API}/auth/me`, {
        headers: { Authorization: `Bearer ${authToken}` }
      });
      console.log('🔍 AuthProvider: Auth check response:', response.data);
      
      // Backend returns user data directly, not wrapped in {success: true, user: ...}
      if (response.data && response.data.id) {
        console.log('✅ AuthProvider: Auth successful, setting user:', response.data);
        setUser(response.data);
        setToken(authToken);
      } else {
        console.log('❌ AuthProvider: Auth failed, no user ID in response');
        localStorage.removeItem('auth_token');
        setToken(null);
        setUser(null);
      }
    } catch (error) {
      console.error('❌ AuthProvider: Auth check failed:', error.response?.status, error.response?.data);
      localStorage.removeItem('auth_token');
      setToken(null);
      setUser(null);
    } finally {
      console.log('🔍 AuthProvider: Setting loading to false');
      setLoading(false);
    }
  };

  const login = async (email, password) => {
    console.log('🔍 AuthProvider: Starting email/password login...');
    try {
      const response = await axios.post(`${API}/auth/login`, { email, password });
      console.log('🔍 AuthProvider: Login response:', response.data);
      
      if (response.data && response.data.access_token) {
        const newToken = response.data.access_token;
        console.log('✅ AuthProvider: Login successful, token received');
        localStorage.setItem('auth_token', newToken);
        setToken(newToken);
        setUser(response.data.user);
        return { success: true };
      }
      console.log('❌ AuthProvider: Login failed - no access_token in response');
      return { success: false, error: response.data?.error || 'Login failed' };
    } catch (error) {
      console.error('❌ AuthProvider: Login error:', error.response?.status, error.response?.data);
      return { success: false, error: error.response?.data?.error || 'Login failed' };
    }
  };

  const logout = () => {
    localStorage.removeItem('auth_token');
    setToken(null);
    setUser(null);
  };

  const testLogin = async () => {
    console.log('🔍 AuthProvider: Starting test login...');
    try {
      const response = await axios.post(`${API}/auth/test-login`);
      console.log('🔍 AuthProvider: Test login response:', response.data);
      
      if (response.data && response.data.access_token) {
        const newToken = response.data.access_token;
        console.log('✅ AuthProvider: Test login successful, token received');
        localStorage.setItem('auth_token', newToken);
        setToken(newToken);
        setUser(response.data.user);
        return { success: true };
      }
      console.log('❌ AuthProvider: Test login failed - no access_token in response');
      return { success: false, error: 'Test login failed' };
    } catch (error) {
      console.error('❌ AuthProvider: Test login error:', error.response?.status, error.response?.data);
      return { success: false, error: error.response?.data?.error || 'Test login failed' };
    }
  };

  // Add a function to handle external authentication
  const handleExternalAuth = (token, userData) => {
    console.log('🔍 AuthProvider: Handling external auth with token:', !!token, 'user:', !!userData);
    if (token && userData) {
      localStorage.setItem('auth_token', token);
      setToken(token);
      setUser(userData);
      console.log('✅ AuthProvider: External auth successful, state updated');
      return true;
    }
    return false;
  };

  return (
    <AuthContext.Provider value={{ 
      user, 
      token, 
      login, 
      logout, 
      testLogin,
      handleExternalAuth,
      loading,
      isAuthenticated: !!token && !!user 
    }}>
      {children}
    </AuthContext.Provider>
  );
};

// Animated Observer Logo Component
const ObserverLogo = () => {
  const pupilControls = useAnimationControls();

  useEffect(() => {
    // Animation sequences
    const animatePupil = async () => {
      try {
        while (true) {
          // Random chance for different movements
          const movementType = Math.random();
          
          if (movementType < 0.4) {
            // Scanning motion (40% chance) - reduced range to prevent touching outline
            await pupilControls.start({
              x: -4,
              y: Math.random() * 2 + 6, // 6-8px (reduced range)
              transition: {
                type: "spring",
                stiffness: 60,
                damping: 20
              }
            });
            
            await new Promise(resolve => setTimeout(resolve, 200));
            
            await pupilControls.start({
              x: 4,
              y: Math.random() * 2 + 6, // 6-8px (reduced range)
              transition: {
                type: "spring",
                stiffness: 60,
                damping: 20
              }
            });
            
            await new Promise(resolve => setTimeout(resolve, 200));
            
          } else if (movementType < 0.7) {
            // Blink motion (30% chance)
            await pupilControls.start({
              scaleY: 0.1,
              transition: { duration: 0.1 }
            });
            
            await new Promise(resolve => setTimeout(resolve, 100));
            
            await pupilControls.start({
              scaleY: 1,
              transition: { duration: 0.1 }
            });
          } else {
            // Focus motion (30% chance) - center position
            await pupilControls.start({
              x: 0,
              y: 7, // Slightly lower center
              transition: {
                type: "spring",
                stiffness: 100,
                damping: 25
              }
            });
          }
          
          // Wait before next animation (1-3 seconds)
          await new Promise(resolve => setTimeout(resolve, Math.random() * 2000 + 1000));
        }
      } catch (error) {
        console.log('Animation stopped');
      }
    };

    animatePupil();
  }, [pupilControls]);

  return (
    <div className="flex items-center space-x-3">
      <motion.div
        className="relative w-12 h-12 rounded-full bg-gradient-to-br from-purple-600 to-blue-700 flex items-center justify-center shadow-lg overflow-hidden"
        whileHover={{ scale: 1.05 }}
        transition={{ type: "spring", stiffness: 300 }}
      >
        {/* Eye white */}
        <div className="w-8 h-8 bg-white rounded-full flex items-center justify-center relative">
          {/* Iris */}
          <div className="w-6 h-6 bg-gradient-to-br from-blue-600 to-purple-700 rounded-full flex items-center justify-center relative">
            {/* Pupil */}
            <motion.div
              className="w-3 h-3 bg-black rounded-full"
              animate={pupilControls}
              initial={{ x: 0, y: 7 }}
            />
            {/* Light reflection */}
            <div className="absolute top-1 left-1 w-1.5 h-1.5 bg-white rounded-full opacity-80"></div>
          </div>
        </div>
      </motion.div>
      <div>
        <h1 className="text-xl font-bold text-white">Observer</h1>
        <p className="text-xs text-white/70">AI Agent Simulation</p>
      </div>
    </div>
  );
};

// Simple Chat History Component  
const ChatHistory = () => {
  return (
    <div className="space-y-6">
      <div className="text-center">
        <h2 className="text-3xl font-bold text-white mb-4">Chat History</h2>
        <p className="text-white/80">Review your past conversations and simulations</p>
      </div>
      
      <div className="bg-white/10 backdrop-blur-lg rounded-xl p-8 text-center">
        <div className="text-6xl mb-4">💬</div>
        <h3 className="text-xl font-semibold text-white mb-2">No Conversations Yet</h3>
        <p className="text-white/70">Start a simulation to begin chatting with agents and generate conversation history</p>
      </div>
    </div>
  );
};

// Simple File Center Component
const FileCenter = () => {
  return (
    <div className="space-y-6">
      <div className="text-center">
        <h2 className="text-3xl font-bold text-white mb-4">File Center</h2>
        <p className="text-white/80">Manage your documents, reports, and generated content</p>
      </div>
      
      <div className="bg-white/10 backdrop-blur-lg rounded-xl p-8 text-center">
        <div className="text-6xl mb-4">📄</div>
        <h3 className="text-xl font-semibold text-white mb-2">No Documents Yet</h3>
        <p className="text-white/70">Documents and reports will appear here after agent conversations and simulations</p>
      </div>
    </div>
  );
};

// Profile Settings Modal Component  
const ProfileSettingsModal = ({ isOpen, onClose }) => {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    bio: ''
  });
  const { user } = useAuth();

  useEffect(() => {
    if (user && isOpen) {
      setFormData({
        name: user.name || '',
        email: user.email || '',
        bio: user.bio || ''
      });
    }
  }, [user, isOpen]);

  const handleInputChange = (e) => {
    if (e && e.target) {
      setFormData({
        ...formData,
        [e.target.name]: e.target.value
      });
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-[100] p-4">
      <div className="bg-white rounded-lg w-full max-w-2xl max-h-[90vh] overflow-hidden">
        {/* Header */}
        <div className="bg-gradient-to-r from-blue-600 to-purple-600 text-white p-6">
          <div className="flex justify-between items-center">
            <div>
              <h2 className="text-2xl font-bold">👤 Profile Settings</h2>
              <p className="text-white/80 mt-1">Manage your account information and preferences</p>
            </div>
            <button
              onClick={onClose}
              className="text-white/70 hover:text-white text-2xl p-2 hover:bg-white/10 rounded-lg transition-colors"
            >
              ✕
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="p-6 overflow-y-auto max-h-[calc(90vh-120px)]">
          {/* Profile Picture */}
          <div className="flex items-center space-x-4 mb-6">
            <div className="w-20 h-20 bg-gray-300 rounded-full flex items-center justify-center text-2xl">
              {user?.name?.[0] || '👤'}
            </div>
            <div>
              <h3 className="text-lg font-semibold text-gray-800">{formData.name || 'User'}</h3>
              <p className="text-gray-600">{formData.email || 'No email'}</p>
              <button className="text-blue-600 text-sm hover:text-blue-700 mt-1">
                Change profile photo
              </button>
            </div>
          </div>

          {/* Basic Information */}
          <div className="space-y-4">
            <h4 className="text-lg font-semibold text-gray-800 border-b border-gray-200 pb-2">Basic Information</h4>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Full Name</label>
                <input
                  type="text"
                  name="name"
                  value={formData.name}
                  onChange={handleInputChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  placeholder="Enter your full name"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Email Address</label>
                <input
                  type="email"
                  name="email"
                  value={formData.email}
                  onChange={handleInputChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  placeholder="Enter your email"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Bio</label>
              <textarea
                name="bio"
                value={formData.bio}
                onChange={handleInputChange}
                rows="3"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                placeholder="Tell us about yourself..."
              ></textarea>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex justify-end space-x-3 pt-4 border-t border-gray-200 mt-6">
            <button
              onClick={onClose}
              className="px-6 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
            >
              Cancel
            </button>
            <button className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
              Save Changes
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

// Preferences Modal Component
const PreferencesModal = ({ isOpen, onClose }) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-[100] p-4">
      <div className="bg-white rounded-lg w-full max-w-4xl max-h-[90vh] overflow-hidden">
        {/* Header */}
        <div className="bg-gradient-to-r from-purple-600 to-pink-600 text-white p-6">
          <div className="flex justify-between items-center">
            <div>
              <h2 className="text-2xl font-bold">⚙️ Preferences</h2>
              <p className="text-white/80 mt-1">Customize your AI simulation experience</p>
            </div>
            <button
              onClick={onClose}
              className="text-white/70 hover:text-white text-2xl p-2 hover:bg-white/10 rounded-lg transition-colors"
            >
              ✕
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="p-6 overflow-y-auto max-h-[calc(90vh-120px)]">
          <div className="text-center text-gray-600">
            <p>Preferences settings coming soon!</p>
            <p className="text-sm mt-2">Theme, language, notifications, and AI behavior customization</p>
          </div>
        </div>
      </div>
    </div>
  );
};

// Help Modal Component
const HelpModal = ({ isOpen, onClose }) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-[100] p-4">
      <div className="bg-white rounded-lg w-full max-w-4xl max-h-[90vh] overflow-hidden">
        {/* Header */}
        <div className="bg-gradient-to-r from-green-600 to-blue-600 text-white p-6">
          <div className="flex justify-between items-center">
            <div>
              <h2 className="text-2xl font-bold">🆘 Help & Support</h2>
              <p className="text-white/80 mt-1">Find answers and get help with AI Agent Simulation</p>
            </div>
            <button
              onClick={onClose}
              className="text-white/70 hover:text-white text-2xl p-2 hover:bg-white/10 rounded-lg transition-colors"
            >
              ✕
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="p-6 overflow-y-auto max-h-[calc(90vh-120px)]">
          <div className="text-center text-gray-600">
            <p>Help and support documentation coming soon!</p>
            <p className="text-sm mt-2">FAQ, tutorials, and contact information</p>
          </div>
        </div>
      </div>
    </div>
  );
};

// Main App Content Component
const AppContent = () => {
  console.log('🔍 AppContent: Component is rendering!');
  
  const [activeTab, setActiveTab] = useState('home');
  const [showAccountDropdown, setShowAccountDropdown] = useState(false);
  const [showProfileModal, setShowProfileModal] = useState(false);
  const [showPreferencesModal, setShowPreferencesModal] = useState(false);
  const [showHelpModal, setShowHelpModal] = useState(false);
  const [showAnalyticsModal, setShowAnalyticsModal] = useState(false);
  const { user, logout, token } = useAuth();

  console.log('🔍 AppContent: User data:', user);
  console.log('🔍 AppContent: Active tab:', activeTab);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (showAccountDropdown && event && event.target && !event.target.closest('.account-dropdown')) {
        setShowAccountDropdown(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [showAccountDropdown]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-900 via-blue-900 to-indigo-900">
      {console.log('🔍 AppContent: About to render dashboard UI')}
      
      {/* Header */}
      <header className="bg-white/10 backdrop-blur-lg border-b border-white/20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <ObserverLogo />
            
            <nav className="hidden md:flex space-x-8">
              <button
                onClick={() => {
                  console.log('🔍 AppContent: Home tab clicked');
                  setActiveTab('home');
                }}
                className={`text-sm font-medium transition-colors duration-200 px-3 py-2 rounded-lg ${
                  activeTab === 'home' 
                    ? 'text-white bg-white/20' 
                    : 'text-white/70 hover:text-white hover:bg-white/10'
                }`}
              >
                🏠 Home
              </button>
              <button
                onClick={() => {
                  console.log('🔍 AppContent: Observatory tab clicked');
                  setActiveTab('simulation');
                }}
                className={`text-sm font-medium transition-colors duration-200 px-3 py-2 rounded-lg ${
                  activeTab === 'simulation' 
                    ? 'text-white bg-white/20' 
                    : 'text-white/70 hover:text-white hover:bg-white/10'
                }`}
              >
                🔭 Observatory
              </button>
              <button
                onClick={() => {
                  console.log('🔍 AppContent: Agents tab clicked');
                  setActiveTab('agents');
                }}
                className={`text-sm font-medium transition-colors duration-200 px-3 py-2 rounded-lg ${
                  activeTab === 'agents' 
                    ? 'text-white bg-white/20' 
                    : 'text-white/70 hover:text-white hover:bg-white/10'
                }`}
              >
                🤖 Agent Library
              </button>
              <button
                onClick={() => {
                  console.log('🔍 AppContent: Conversations tab clicked');
                  setActiveTab('conversations');
                }}
                className={`text-sm font-medium transition-colors duration-200 px-3 py-2 rounded-lg ${
                  activeTab === 'conversations' 
                    ? 'text-white bg-white/20' 
                    : 'text-white/70 hover:text-white hover:bg-white/10'
                }`}
              >
                💬 Conversations
              </button>
              <button
                onClick={() => {
                  console.log('🔍 AppContent: Documents tab clicked');
                  setActiveTab('documents');
                }}
                className={`text-sm font-medium transition-colors duration-200 px-3 py-2 rounded-lg ${
                  activeTab === 'documents' 
                    ? 'text-white bg-white/20' 
                    : 'text-white/70 hover:text-white hover:bg-white/10'
                }`}
              >
                📄 Documents
              </button>
              <button
                onClick={() => {
                  console.log('🔍 AppContent: Chat tab clicked');
                  setActiveTab('chat');
                }}
                className={`text-sm font-medium transition-colors duration-200 px-3 py-2 rounded-lg ${
                  activeTab === 'chat' 
                    ? 'text-white bg-white/20' 
                    : 'text-white/70 hover:text-white hover:bg-white/10'
                }`}
              >
                💬 Chat History
              </button>
            </nav>
            
            {/* User Account Dropdown */}
            <div className="relative account-dropdown">
              <button
                onClick={() => {
                  console.log('🔍 AppContent: Account dropdown clicked');
                  setShowAccountDropdown(!showAccountDropdown);
                }}
                className="flex items-center space-x-2 text-white hover:text-purple-200 transition-colors duration-200"
              >
                <div className="w-8 h-8 bg-purple-600 rounded-full flex items-center justify-center">
                  <span className="text-sm font-semibold">{user?.name?.[0] || 'U'}</span>
                </div>
                <span className="hidden sm:block text-sm font-medium">{user?.name || 'User'}</span>
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </svg>
              </button>
              
              {showAccountDropdown && (
                <div className="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-xl border border-gray-200 z-50">
                  <div className="py-1">
                    <button
                      onClick={() => {
                        console.log('🔍 AppContent: Analytics clicked');
                        setShowAnalyticsModal(true);
                        setShowAccountDropdown(false);
                      }}
                      className="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 flex items-center space-x-2"
                    >
                      <span>📊</span>
                      <span>Analytics Dashboard</span>
                    </button>
                    <button
                      onClick={() => {
                        console.log('🔍 AppContent: Profile clicked');
                        setShowProfileModal(true);
                        setShowAccountDropdown(false);
                      }}
                      className="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 flex items-center space-x-2"
                    >
                      <span>👤</span>
                      <span>Profile Settings</span>
                    </button>
                    <button
                      onClick={() => {
                        console.log('🔍 AppContent: Preferences clicked');
                        setShowPreferencesModal(true);
                        setShowAccountDropdown(false);
                      }}
                      className="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 flex items-center space-x-2"
                    >
                      <span>⚙️</span>
                      <span>Preferences</span>
                    </button>
                    <button
                      onClick={() => {
                        console.log('🔍 AppContent: Help clicked');
                        setShowHelpModal(true);
                        setShowAccountDropdown(false);
                      }}
                      className="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 flex items-center space-x-2"
                    >
                      <span>❓</span>
                      <span>Help & Support</span>
                    </button>
                    <div className="border-t border-gray-100 mt-1 pt-1">
                      <button
                        onClick={() => {
                          console.log('🔍 AppContent: Logout clicked');
                          logout();
                          setShowAccountDropdown(false);
                        }}
                        className="w-full text-left px-4 py-2 text-sm text-red-700 hover:bg-red-50 flex items-center space-x-2"
                      >
                        <span>🚪</span>
                        <span>Sign Out</span>
                      </button>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {console.log('🔍 AppContent: About to render main content, activeTab:', activeTab)}
        
        <div style={{ minHeight: '400px' }}>
          {/* Simple content without AnimatePresence to test */}
          {activeTab === 'home' && (
            <div>
              {console.log('🔍 AppContent: Rendering home content')}
              <div className="text-center space-y-8">
                <div>
                  <h2 className="text-4xl font-bold text-white mb-4">
                    🎉 Welcome to AI Agent Simulation Platform! 
                  </h2>
                  <p className="text-xl text-white/80 max-w-3xl mx-auto">
                    Create, manage, and run sophisticated simulations with multiple AI agents.
                  </p>
                </div>
                
                <div className="grid md:grid-cols-3 gap-6">
                  <div className="bg-white/10 backdrop-blur-lg rounded-xl p-6 text-center">
                    <div className="text-4xl mb-4">🤖</div>
                    <h3 className="text-xl font-semibold text-white mb-2">Create Agents</h3>
                    <p className="text-white/70">Design AI agents with unique personalities</p>
                  </div>
                  
                  <div className="bg-white/10 backdrop-blur-lg rounded-xl p-6 text-center">
                    <div className="text-4xl mb-4">💬</div>
                    <h3 className="text-xl font-semibold text-white mb-2">Run Simulations</h3>
                    <p className="text-white/70">Watch agents interact in real-time</p>
                  </div>
                  
                  <div className="bg-white/10 backdrop-blur-lg rounded-xl p-6 text-center">
                    <div className="text-4xl mb-4">📊</div>
                    <h3 className="text-xl font-semibold text-white mb-2">Analyze Results</h3>
                    <p className="text-white/70">Generate insights from conversations</p>
                  </div>
                </div>
              </div>
            </div>
          )}
          
          {activeTab === 'simulation' && (
            <div>
              {console.log('🔍 AppContent: Rendering simulation content')}
              <SimulationControl setActiveTab={setActiveTab} />
            </div>
          )}
          
          {activeTab === 'agents' && (
            <div>
              {console.log('🔍 AppContent: Rendering agents content')}
              <AgentLibrary 
                onAddAgent={(agent) => console.log('Agent added:', agent)}
                onRemoveAgent={(agent) => console.log('Agent removed:', agent)}
              />
            </div>
          )}
          
          {activeTab === 'conversations' && (
            <div>
              {console.log('🔍 AppContent: Rendering conversations content')}
              <ConversationViewer />
            </div>
          )}
          
          {activeTab === 'documents' && (
            <div>
              {console.log('🔍 AppContent: Rendering documents content')}
              <DocumentCenter />
            </div>
          )}
          
          {activeTab === 'chat' && (
            <div>
              {console.log('🔍 AppContent: Rendering chat content')}
              <ChatHistory />
            </div>
          )}
          
          {activeTab === 'files' && (
            <div>
              {console.log('🔍 AppContent: Rendering files content')}
              <FileCenter />
            </div>
          )}
        </div>
      </main>

      {/* Modals */}
      <ProfileSettingsModal
        isOpen={showProfileModal}
        onClose={() => {
          console.log('🔍 AppContent: Closing profile modal');
          setShowProfileModal(false);
        }}
      />
      
      <PreferencesModal
        isOpen={showPreferencesModal}
        onClose={() => {
          console.log('🔍 AppContent: Closing preferences modal');
          setShowPreferencesModal(false);
        }}
      />
      
      <HelpModal
        isOpen={showHelpModal}
        onClose={() => {
          console.log('🔍 AppContent: Closing help modal');
          setShowHelpModal(false);
        }}
      />

      {/* Analytics Modal */}
      {showAnalyticsModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-[100] p-4">
          <div className="bg-white rounded-lg w-full max-w-7xl max-h-[90vh] overflow-hidden">
            <div className="bg-gradient-to-r from-blue-600 to-purple-600 text-white p-6">
              <div className="flex justify-between items-center">
                <div>
                  <h2 className="text-2xl font-bold">📊 Analytics Dashboard</h2>
                  <p className="text-white/80 mt-1">Comprehensive analytics and insights</p>
                </div>
                <button
                  onClick={() => setShowAnalyticsModal(false)}
                  className="text-white/70 hover:text-white text-2xl p-2 hover:bg-white/10 rounded-lg transition-colors"
                >
                  ✕
                </button>
              </div>
            </div>
            <div className="p-6 overflow-y-auto max-h-[calc(90vh-120px)]">
              <AnalyticsDashboard />
            </div>
          </div>
        </div>
      )}
      
      {console.log('🔍 AppContent: Finished rendering AppContent')}
    </div>
  );
};

// Main App Component
const App = () => {
  const { user, loading, handleExternalAuth } = useAuth();

  console.log('🔍 App: Rendering with user:', !!user, 'loading:', loading);

  // Handler for HomePage authentication
  const handleAuthentication = useCallback((token, userData) => {
    console.log('🔍 App: handleAuthentication called with token:', !!token, 'user:', !!userData);
    const success = handleExternalAuth(token, userData);
    if (success) {
      console.log('✅ App: Authentication successful, state updated');
    } else {
      console.error('❌ App: Authentication failed');
    }
  }, [handleExternalAuth]);

  if (loading) {
    console.log('🔍 App: Showing loading screen');
    return (
      <div className="min-h-screen bg-gradient-to-br from-purple-900 via-blue-900 to-indigo-900 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-white mb-4"></div>
          <p className="text-white/80">Loading...</p>
        </div>
      </div>
    );
  }

  if (!user) {
    console.log('🔍 App: No user, showing HomePage');
    return <HomePage onAuthenticated={handleAuthentication} />;
  }

  console.log('🔍 App: User found, showing AppContent');
  return <AppContent />;
};

// Error Boundary Component
class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error('🔥 Error Boundary caught an error:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen bg-gradient-to-br from-purple-900 via-blue-900 to-indigo-900 flex items-center justify-center">
          <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-8 shadow-2xl max-w-md w-full mx-4">
            <div className="text-center">
              <div className="text-6xl mb-4">🔥</div>
              <h1 className="text-2xl font-bold text-white mb-4">Something went wrong</h1>
              <p className="text-white/80 mb-6">The application encountered an error. Please try refreshing the page.</p>
              <button
                onClick={() => window.location.reload()}
                className="bg-gradient-to-r from-purple-600 to-blue-600 text-white py-3 px-6 rounded-lg font-semibold hover:from-purple-700 hover:to-blue-700 transition-all duration-200"
              >
                Refresh Page
              </button>
            </div>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

// App with Auth Provider and Error Boundary
const AppWithAuth = () => {
  return (
    <ErrorBoundary>
      <AuthProvider>
        <App />
      </AuthProvider>
    </ErrorBoundary>
  );
};

export default AppWithAuth;