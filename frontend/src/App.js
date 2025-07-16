import React, { useState, useEffect, useRef, useCallback, createContext, useContext } from 'react';
import { createPortal } from 'react-dom';
import axios from 'axios';
import { motion, useAnimationControls } from 'framer-motion';
import './App.css';
import HomePage from './HomePage';
import AgentLibrary from './AgentLibraryComplete';
import ConversationViewer from './ConversationViewer';
import AnalyticsDashboard from './AnalyticsDashboard';
import { ProfileSettingsModal, PreferencesModal, HelpSupportModal, FeedbackModal } from './AccountModals';
import SimulationControl from './SimulationControl';
import { AuthProvider, useAuth } from './AuthContext';

// Simple FileCenter Component
const FileCenter = () => {
  return (
    <div className="space-y-6">
      <div className="text-center">
        <h2 className="text-3xl font-bold text-white mb-4">File Center</h2>
        <p className="text-white/80">Manage your files, documents, and generated content</p>
      </div>
      
      <div className="bg-white/10 backdrop-blur-lg rounded-xl p-8 text-center">
        <div className="text-6xl mb-4">📁</div>
        <h3 className="text-xl font-semibold text-white mb-2">No Files Yet</h3>
        <p className="text-white/70">Files and documents will appear here after agent conversations and simulations</p>
      </div>
    </div>
  );
};

// Simple DocumentCenter Component
const DocumentCenter = () => {
  return (
    <div className="space-y-6">
      <div className="text-center">
        <h2 className="text-3xl font-bold text-white mb-4">Document Center</h2>
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
    console.error('Error caught by boundary:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen bg-gradient-to-br from-gray-900 via-blue-900 to-purple-900 flex items-center justify-center p-4">
          <div className="bg-white/10 backdrop-blur-lg rounded-xl p-8 border border-white/20 text-center max-w-md">
            <div className="text-6xl mb-4">⚠️</div>
            <h2 className="text-xl font-bold text-white mb-4">Something went wrong</h2>
            <p className="text-gray-300 mb-6">Please refresh the page to continue.</p>
            <button 
              onClick={() => window.location.reload()} 
              className="px-6 py-3 bg-purple-600 hover:bg-purple-700 text-white rounded-lg transition-colors"
            >
              Refresh Page
            </button>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Debug logging
console.log('Environment variables loaded:', {
  BACKEND_URL,
  NODE_ENV: process.env.NODE_ENV
});

// Authentication Context
const AuthContext = createContext();

// useAuth hook is imported from AuthContext

// AuthProvider is imported from AuthContext

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



// Main App Content Component
const AppContent = () => {
  // Initialize state with safe defaults
  const [activeTab, setActiveTab] = useState(() => {
    try {
      return localStorage.getItem('activeTab') || 'home';
    } catch (error) {
      console.warn('Error accessing localStorage:', error);
      return 'home';
    }
  });
  
  const [showAccountMenu, setShowAccountMenu] = useState(false);
  const [showAccountModals, setShowAccountModals] = useState(false);
  const { user, token, logout } = useAuth() || {};

  // Safely persist active tab
  useEffect(() => {
    try {
      if (activeTab) {
        localStorage.setItem('activeTab', activeTab);
      }
    } catch (error) {
      console.warn('Error saving to localStorage:', error);
    }
  }, [activeTab]);

  // Safe tab setter with validation
  const safeSetActiveTab = useCallback((tab) => {
    const validTabs = ['home', 'simulation', 'agents', 'history', 'analytics', 'files', 'account'];
    if (validTabs.includes(tab)) {
      setActiveTab(tab);
    } else {
      console.warn('Invalid tab:', tab);
      setActiveTab('home');
    }
  }, []);
  const [showAccountDropdown, setShowAccountDropdown] = useState(false);
  const [dropdownPosition, setDropdownPosition] = useState({ top: 0, right: 0 });
  const accountButtonRef = useRef(null);
  const [showProfileModal, setShowProfileModal] = useState(false);
  const [showPreferencesModal, setShowPreferencesModal] = useState(false);
  const [showHelpModal, setShowHelpModal] = useState(false);
  const [showAnalyticsModal, setShowAnalyticsModal] = useState(false);
  const [showFeedbackModal, setShowFeedbackModal] = useState(false);
  
  // Observatory refresh trigger for Agent Library synchronization
  const [observatoryRefreshTrigger, setObservatoryRefreshTrigger] = useState(0);
  const triggerObservatoryRefresh = () => {
    setObservatoryRefreshTrigger(prev => prev + 1);
    console.log('🔄 Observatory refresh triggered from Agent Library');
  };

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
      
      {/* Sticky Header */}
      <header className="sticky top-0 bg-white/10 backdrop-blur-lg border-b border-white/20 z-[9998] shadow-lg">
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
            </nav>
            
            {/* User Account Dropdown - WORKING VERSION */}
            <div className="relative account-dropdown">
              <button
                onClick={() => {
                  console.log('🔍 Account button clicked - toggling dropdown');
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
              
              {/* Working Dropdown Menu */}
              {showAccountDropdown && (
                <div className="absolute right-0 top-full mt-2 w-48 bg-white rounded-lg shadow-xl border border-gray-200 z-[9999]">
                  <div className="py-1">
                    <button
                      onClick={() => {
                        console.log('🔍 Analytics clicked');
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
                        console.log('🔍 Profile clicked - setting modal to true');
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
                        console.log('🔍 Preferences clicked');
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
                        console.log('🔍 Help clicked');
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
                          console.log('🔍 Logout clicked');
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
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-2">
        {console.log('🔍 AppContent: About to render main content, activeTab:', activeTab)}
        
        <div style={{ minHeight: '400px' }}>
          {/* Simple content without AnimatePresence to test */}
          {activeTab === 'home' && (
            <div className="relative overflow-hidden">
              {console.log('🔍 AppContent: Rendering optimized home content')}
              
              {/* Preload Critical Images */}
              <div style={{ display: 'none' }}>
                <img src="https://images.unsplash.com/photo-1677442136019-21780ecad995" alt="preload" />
                <img src="https://images.unsplash.com/photo-1517048676732-d65bc937f952" alt="preload" />
                <img src="https://images.unsplash.com/photo-1600880292089-90a7e086ee0c" alt="preload" />
              </div>
              
              {/* 1. OPTIMIZED HERO SECTION */}
              <section className="relative py-20 px-4">
                {/* Simplified Background Animation */}
                <div className="absolute inset-0 overflow-hidden pointer-events-none">
                  <div className="absolute -top-40 -right-40 w-80 h-80 bg-purple-500/5 rounded-full blur-3xl"></div>
                  <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-blue-500/5 rounded-full blur-3xl"></div>
                </div>
                
                <div className="relative max-w-7xl mx-auto">
                  <div className="grid lg:grid-cols-2 gap-12 items-center">
                    {/* Hero Content - Restored Animations */}
                    <motion.div 
                      initial={{ opacity: 0, x: -50 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ duration: 0.8 }}
                      className="text-left space-y-8"
                    >
                      <div className="space-y-4">
                        <motion.div 
                          initial={{ opacity: 0, y: 20 }}
                          animate={{ opacity: 1, y: 0 }}
                          transition={{ delay: 0.2 }}
                          className="inline-flex items-center px-4 py-2 bg-purple-600/20 rounded-full border border-purple-400/30"
                          style={{ display: 'none' }}
                        >
                          <span className="text-purple-300 text-sm font-medium">🚀 Next-Gen AI Simulation Platform</span>
                        </motion.div>
                        
                        <h1 className="text-5xl lg:text-7xl font-bold text-white leading-tight">
                          Transform Ideas into{' '}
                          <span className="bg-gradient-to-r from-purple-400 to-blue-400 bg-clip-text text-transparent">
                            Reality
                          </span>
                        </h1>
                        
                        <p className="text-xl text-gray-300 leading-relaxed max-w-xl">
                          Create intelligent AI agents, run sophisticated simulations, and unlock breakthrough insights. 
                          Turn complex scenarios into actionable intelligence.
                        </p>
                      </div>
                      
                      {/* CTA Buttons */}
                      <div className="flex flex-col sm:flex-row gap-4">
                        <motion.button
                          whileHover={{ scale: 1.05 }}
                          whileTap={{ scale: 0.95 }}
                          onClick={() => safeSetActiveTab('simulation')}
                          className="px-8 py-4 bg-gradient-to-r from-purple-600 to-blue-600 text-white font-semibold rounded-xl shadow-2xl hover:shadow-purple-500/25 transition-all duration-300"
                        >
                          🎯 Start Simulation
                        </motion.button>
                        
                        <motion.button
                          whileHover={{ scale: 1.05 }}
                          whileTap={{ scale: 0.95 }}
                          onClick={() => safeSetActiveTab('agents')}
                          className="px-8 py-4 bg-white/10 backdrop-blur-lg text-white font-semibold rounded-xl border border-white/20 hover:bg-white/20 transition-all duration-300"
                        >
                          🤖 Explore Agents
                        </motion.button>
                      </div>
                      
                      {/* Stats */}
                      <div className="flex items-center space-x-8 pt-8">
                        <div>
                          <div className="text-2xl font-bold text-white">10,000+</div>
                          <div className="text-gray-400 text-sm">Simulations Run</div>
                        </div>
                        <div>
                          <div className="text-2xl font-bold text-white">50+</div>
                          <div className="text-gray-400 text-sm">Agent Types</div>
                        </div>
                        <div>
                          <div className="text-2xl font-bold text-white">99.9%</div>
                          <div className="text-gray-400 text-sm">Uptime</div>
                        </div>
                      </div>
                    </motion.div>
                    
                    {/* Hero Visual - Optimized Loading */}
                    <div className="relative">
                      <div className="relative bg-gradient-to-br from-gray-900/50 to-gray-800/50 backdrop-blur-lg rounded-2xl p-8 border border-white/10">
                        <div className="w-full h-64 bg-gray-800/50 rounded-xl mb-6 flex items-center justify-center">
                          <img 
                            src="https://images.unsplash.com/photo-1677442136019-21780ecad995?w=800&q=80" 
                            alt="AI Technology"
                            className="w-full h-64 object-cover rounded-xl"
                            loading="eager"
                            onError={(e) => {
                              e.target.style.display = 'none';
                              e.target.parentElement.innerHTML = '<div class="w-full h-64 bg-gradient-to-br from-purple-600/20 to-blue-600/20 rounded-xl flex items-center justify-center"><span class="text-4xl">🤖</span></div>';
                            }}
                          />
                        </div>
                        <div className="space-y-4">
                          <div className="flex items-center space-x-3">
                            <div className="w-10 h-10 bg-green-600 rounded-full flex items-center justify-center">
                              <span className="text-white font-bold">AI</span>
                            </div>
                            <div>
                              <div className="text-white font-medium">Smart Agent Active</div>
                              <div className="text-gray-400 text-sm">Processing scenario...</div>
                            </div>
                          </div>
                          <div className="bg-blue-600/20 p-4 rounded-lg border border-blue-400/30">
                            <div className="text-blue-300 text-sm font-medium mb-2">💡 AI Insight Generated</div>
                            <div className="text-white text-sm">"Based on market analysis, I recommend focusing on user acquisition..."</div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </section>

              {/* 3. OPTIMIZED USE CASE GALLERY */}
              <section className="py-20 px-4">
                <div className="max-w-7xl mx-auto">
                  <div className="text-center mb-16">
                    <h2 className="text-4xl lg:text-5xl font-bold text-white mb-6">
                      Perfect for{' '}
                      <span className="bg-gradient-to-r from-pink-400 to-red-400 bg-clip-text text-transparent">
                        Any team
                      </span>
                    </h2>
                    <p className="text-xl text-gray-300 max-w-3xl mx-auto">
                      Whether you're planning strategy, conducting research, or exploring new ideas - our platform adapts to your needs.
                    </p>
                  </div>
                  
                  <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
                    {/* Business Strategy - Optimized */}
                    <div className="group bg-gradient-to-br from-blue-600/10 to-purple-600/10 backdrop-blur-lg rounded-xl p-6 border border-blue-400/20 hover:border-blue-400/50 transition-all duration-300">
                      <div className="w-16 h-16 bg-blue-600/20 rounded-full flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                        <span className="text-3xl">🎯</span>
                      </div>
                      <h3 className="text-lg font-bold text-white mb-2">Business Strategy</h3>
                      <p className="text-gray-300 text-sm leading-relaxed mb-4">
                        Test market strategies, explore scenarios, and validate decisions with expert AI advisors.
                      </p>
                      <div className="space-y-1 text-xs text-gray-400">
                        <div>• Market analysis simulations</div>
                        <div>• Strategic planning sessions</div>
                        <div>• Risk assessment scenarios</div>
                      </div>
                    </div>

                    {/* Research & Development - Optimized */}
                    <div className="group bg-gradient-to-br from-green-600/10 to-emerald-600/10 backdrop-blur-lg rounded-xl p-6 border border-green-400/20 hover:border-green-400/50 transition-all duration-300">
                      <div className="w-16 h-16 bg-green-600/20 rounded-full flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                        <span className="text-3xl">🔬</span>
                      </div>
                      <h3 className="text-lg font-bold text-white mb-2">Research & Development</h3>
                      <p className="text-gray-300 text-sm leading-relaxed mb-4">
                        Simulate expert consultations and peer reviews to accelerate innovation and discovery.
                      </p>
                      <div className="space-y-1 text-xs text-gray-400">
                        <div>• Expert panel discussions</div>
                        <div>• Hypothesis validation</div>
                        <div>• Technical feasibility analysis</div>
                      </div>
                    </div>

                    {/* Training & Education - Optimized */}
                    <div className="group bg-gradient-to-br from-purple-600/10 to-pink-600/10 backdrop-blur-lg rounded-xl p-6 border border-purple-400/20 hover:border-purple-400/50 transition-all duration-300">
                      <div className="w-16 h-16 bg-purple-600/20 rounded-full flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                        <span className="text-3xl">📚</span>
                      </div>
                      <h3 className="text-lg font-bold text-white mb-2">Training & Education</h3>
                      <p className="text-gray-300 text-sm leading-relaxed mb-4">
                        Practice scenarios, role-play situations, and learn from AI-powered educational experiences.
                      </p>
                      <div className="space-y-1 text-xs text-gray-400">
                        <div>• Leadership training scenarios</div>
                        <div>• Conflict resolution practice</div>
                        <div>• Skill development sessions</div>
                      </div>
                    </div>

                    {/* Creative Projects - Optimized */}
                    <div className="group bg-gradient-to-br from-orange-600/10 to-yellow-600/10 backdrop-blur-lg rounded-xl p-6 border border-orange-400/20 hover:border-orange-400/50 transition-all duration-300">
                      <div className="w-16 h-16 bg-orange-600/20 rounded-full flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                        <span className="text-3xl">🎨</span>
                      </div>
                      <h3 className="text-lg font-bold text-white mb-2">Creative Projects</h3>
                      <p className="text-gray-300 text-sm leading-relaxed mb-4">
                        Brainstorm with diverse AI personalities to unlock creativity and generate breakthrough ideas.
                      </p>
                      <div className="space-y-1 text-xs text-gray-400">
                        <div>• Creative brainstorming</div>
                        <div>• Product ideation sessions</div>
                        <div>• Innovation workshops</div>
                      </div>
                    </div>
                  </div>
                </div>
              </section>

              {/* 4. OPTIMIZED DEMO SECTION */}
              <section className="py-20 px-4 bg-gradient-to-br from-gray-900/30 to-gray-800/30">
                <div className="max-w-7xl mx-auto">
                  <div className="text-center mb-16">
                    <h2 className="text-4xl lg:text-5xl font-bold text-white mb-6">
                      See It In{' '}
                      <span className="bg-gradient-to-r from-yellow-400 to-orange-400 bg-clip-text text-transparent">
                        Action
                      </span>
                    </h2>
                    <p className="text-xl text-gray-300 max-w-3xl mx-auto">
                      Watch a live demonstration of AI agents collaborating on a real business challenge.
                    </p>
                  </div>
                  
                  <div className="grid lg:grid-cols-2 gap-12 items-center">
                    {/* Live Demo Preview - Static for Performance */}
                    <div className="bg-gray-900/60 backdrop-blur-lg rounded-2xl p-6 border border-white/10">
                      <div className="flex items-center justify-between mb-4">
                        <h3 className="text-lg font-semibold text-white">💬 Live Simulation</h3>
                        <div className="flex items-center space-x-2">
                          <div className="w-2 h-2 bg-green-400 rounded-full"></div>
                          <span className="text-green-400 text-sm">Active</span>
                        </div>
                      </div>
                      
                      <div className="space-y-4 h-80 overflow-y-auto">
                        <div className="bg-blue-600/20 p-4 rounded-lg border-l-4 border-blue-400">
                          <div className="flex items-center space-x-3 mb-2">
                            <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center">
                              <span className="text-white text-xs font-bold">AI</span>
                            </div>
                            <span className="text-blue-300 font-medium">Strategy Agent</span>
                          </div>
                          <p className="text-white text-sm leading-relaxed">
                            "Based on market analysis, I recommend focusing on user acquisition through targeted social media campaigns..."
                          </p>
                        </div>
                        
                        <div className="bg-green-600/20 p-4 rounded-lg border-l-4 border-green-400">
                          <div className="flex items-center space-x-3 mb-2">
                            <div className="w-8 h-8 bg-green-600 rounded-full flex items-center justify-center">
                              <span className="text-white text-xs font-bold">AI</span>
                            </div>
                            <span className="text-green-300 font-medium">Finance Agent</span>
                          </div>
                          <p className="text-white text-sm leading-relaxed">
                            "The budget allocation looks solid. I suggest reserving 30% for testing and optimization to maximize ROI..."
                          </p>
                        </div>
                        
                        <div className="bg-purple-600/20 p-4 rounded-lg border-l-4 border-purple-400">
                          <div className="flex items-center space-x-3 mb-2">
                            <div className="w-8 h-8 bg-purple-600 rounded-full flex items-center justify-center">
                              <span className="text-white text-xs font-bold">AI</span>
                            </div>
                            <span className="text-purple-300 font-medium">Risk Agent</span>
                          </div>
                          <p className="text-white text-sm leading-relaxed">
                            "I've identified potential risks in the timeline. We should consider a phased rollout approach..."
                          </p>
                        </div>
                      </div>
                    </div>
                    
                    {/* Real-time Analytics - Static Bars for Performance */}
                    <div className="bg-gray-900/60 backdrop-blur-lg rounded-2xl p-6 border border-white/10">
                      <h3 className="text-lg font-semibold text-white mb-6">📊 Real-time Analytics</h3>
                      
                      <div className="space-y-6">
                        <div>
                          <div className="flex justify-between mb-2">
                            <span className="text-gray-300 text-sm">Conversation Quality</span>
                            <span className="text-green-400 text-sm font-medium">94%</span>
                          </div>
                          <div className="w-full bg-gray-700 rounded-full h-2">
                            <motion.div
                              initial={{ width: 0 }}
                              whileInView={{ width: "94%" }}
                              transition={{ delay: 0.5, duration: 1 }}
                              viewport={{ once: true }}
                              className="bg-gradient-to-r from-green-400 to-blue-400 h-2 rounded-full"
                            />
                          </div>
                        </div>
                        
                        <div>
                          <div className="flex justify-between mb-2">
                            <span className="text-gray-300 text-sm">Solution Consensus</span>
                            <span className="text-blue-400 text-sm font-medium">87%</span>
                          </div>
                          <div className="w-full bg-gray-700 rounded-full h-2">
                            <motion.div
                              initial={{ width: 0 }}
                              whileInView={{ width: "87%" }}
                              transition={{ delay: 0.7, duration: 1 }}
                              viewport={{ once: true }}
                              className="bg-gradient-to-r from-blue-400 to-purple-400 h-2 rounded-full"
                            />
                          </div>
                        </div>
                        
                        <div>
                          <div className="flex justify-between mb-2">
                            <span className="text-gray-300 text-sm">Action Items Generated</span>
                            <span className="text-purple-400 text-sm font-medium">12</span>
                          </div>
                          <div className="w-full bg-gray-700 rounded-full h-2">
                            <motion.div
                              initial={{ width: 0 }}
                              whileInView={{ width: "80%" }}
                              transition={{ delay: 0.9, duration: 1 }}
                              viewport={{ once: true }}
                              className="bg-gradient-to-r from-purple-400 to-pink-400 h-2 rounded-full"
                            />
                          </div>
                        </div>
                        
                        <div className="pt-4 border-t border-gray-700">
                          <h4 className="text-white font-medium mb-3">Key Insights Detected</h4>
                          <div className="space-y-2">
                            <div className="flex items-center space-x-2 text-sm text-gray-300">
                              <span className="w-2 h-2 bg-yellow-400 rounded-full"></span>
                              <span>Market opportunity identified</span>
                            </div>
                            <div className="flex items-center space-x-2 text-sm text-gray-300">
                              <span className="w-2 h-2 bg-green-400 rounded-full"></span>
                              <span>Budget optimization suggested</span>
                            </div>
                            <div className="flex items-center space-x-2 text-sm text-gray-300">
                              <span className="w-2 h-2 bg-blue-400 rounded-full"></span>
                              <span>Risk mitigation planned</span>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </section>









              {/* 6. OPTIMIZED GETTING STARTED FLOW */}
              <section className="py-20 px-4 bg-gradient-to-br from-indigo-900/20 to-purple-900/20">
                <div className="max-w-7xl mx-auto">
                  <div className="text-center mb-16">
                    <h2 className="text-4xl lg:text-5xl font-bold text-white mb-6">
                      Get Started in{' '}
                      <span className="bg-gradient-to-r from-cyan-400 to-blue-400 bg-clip-text text-transparent">
                        3 Simple Steps
                      </span>
                    </h2>
                    <p className="text-xl text-gray-300 max-w-3xl mx-auto">
                      From idea to insight in minutes.
                    </p>
                  </div>
                  
                  <div className="relative">
                    {/* Connection Lines - Static */}
                    <div className="hidden lg:block absolute top-1/2 left-0 right-0 h-0.5 bg-gradient-to-r from-purple-600/50 via-blue-600/50 to-green-600/50 transform -translate-y-1/2"></div>
                    
                    <div className="grid lg:grid-cols-3 gap-8 relative">
                      {/* Step 1 - Optimized */}
                      <div className="relative text-center">
                        <div className="relative mx-auto">
                          <div className="w-20 h-20 bg-gradient-to-br from-purple-600 to-purple-700 rounded-full flex items-center justify-center text-white text-2xl font-bold shadow-2xl mb-6 mx-auto relative z-10">
                            1
                          </div>
                          <div className="absolute inset-0 w-20 h-20 bg-purple-600/20 rounded-full mx-auto"></div>
                        </div>
                        
                        <div className="bg-gray-900/60 backdrop-blur-lg rounded-xl p-6 border border-purple-400/30">
                          <div className="mb-4">
                            <div className="w-full h-32 bg-gray-800/50 rounded-lg flex items-center justify-center">
                              <img 
                                src="https://images.unsplash.com/photo-1716436329475-4c55d05383bb?w=400&q=80" 
                                alt="Create Agents"
                                className="w-full h-32 object-cover rounded-lg"
                                loading="lazy"
                                onError={(e) => {
                                  e.target.style.display = 'none';
                                  e.target.parentElement.innerHTML = '<div class="w-full h-32 bg-gradient-to-br from-purple-600/20 to-blue-600/20 rounded-lg flex items-center justify-center"><span class="text-2xl">🤖</span></div>';
                                }}
                              />
                            </div>
                          </div>
                          <h3 className="text-xl font-bold text-white mb-3">Create Your Agents</h3>
                          <p className="text-gray-300 text-sm leading-relaxed mb-4">
                            Choose from 9+ professional archetypes or create custom agents with unique personalities, expertise, and goals.
                          </p>
                          <button 
                            onClick={() => setActiveTab('agents')}
                            className="w-full py-2 bg-purple-600 hover:bg-purple-700 text-white font-medium rounded-lg transition-colors"
                          >
                            🤖 Browse Agent Library
                          </button>
                        </div>
                      </div>

                      {/* Step 2 - Optimized */}
                      <div className="relative text-center">
                        <div className="relative mx-auto">
                          <div className="w-20 h-20 bg-gradient-to-br from-blue-600 to-blue-700 rounded-full flex items-center justify-center text-white text-2xl font-bold shadow-2xl mb-6 mx-auto relative z-10">
                            2
                          </div>
                          <div className="absolute inset-0 w-20 h-20 bg-blue-600/20 rounded-full mx-auto"></div>
                        </div>
                        
                        <div className="bg-gray-900/60 backdrop-blur-lg rounded-xl p-6 border border-blue-400/30">
                          <div className="mb-4">
                            <div className="w-full h-32 bg-gray-800/50 rounded-lg flex items-center justify-center">
                              <img 
                                src="https://images.unsplash.com/photo-1640109341881-1cd3eaf50909?w=400&q=80" 
                                alt="Set Scenario"
                                className="w-full h-32 object-cover rounded-lg"
                                loading="lazy"
                                onError={(e) => {
                                  e.target.style.display = 'none';
                                  e.target.parentElement.innerHTML = '<div class="w-full h-32 bg-gradient-to-br from-blue-600/20 to-purple-600/20 rounded-lg flex items-center justify-center"><span class="text-2xl">📝</span></div>';
                                }}
                              />
                            </div>
                          </div>
                          <h3 className="text-xl font-bold text-white mb-3">Set Your Scenario</h3>
                          <p className="text-gray-300 text-sm leading-relaxed mb-4">
                            Define the context, goals, and parameters for your simulation. From business meetings to research discussions.
                          </p>
                          <button 
                            onClick={() => setActiveTab('simulation')}
                            className="w-full py-2 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg transition-colors"
                          >
                            📝 Configure Scenario
                          </button>
                        </div>
                      </div>

                      {/* Step 3 - Optimized */}
                      <div className="relative text-center">
                        <div className="relative mx-auto">
                          <div className="w-20 h-20 bg-gradient-to-br from-green-600 to-green-700 rounded-full flex items-center justify-center text-white text-2xl font-bold shadow-2xl mb-6 mx-auto relative z-10">
                            3
                          </div>
                          <div className="absolute inset-0 w-20 h-20 bg-green-600/20 rounded-full mx-auto"></div>
                        </div>
                        
                        <div className="bg-gray-900/60 backdrop-blur-lg rounded-xl p-6 border border-green-400/30">
                          <div className="mb-4">
                            <div className="w-full h-32 bg-gray-800/50 rounded-lg flex items-center justify-center">
                              <img 
                                src="https://images.pexels.com/photos/32755751/pexels-photo-32755751.jpeg?w=400&q=80" 
                                alt="Watch Magic Happen"
                                className="w-full h-32 object-cover rounded-lg"
                                loading="lazy"
                                onError={(e) => {
                                  e.target.style.display = 'none';
                                  e.target.parentElement.innerHTML = '<div class="w-full h-32 bg-gradient-to-br from-green-600/20 to-blue-600/20 rounded-lg flex items-center justify-center"><span class="text-2xl">📊</span></div>';
                                }}
                              />
                            </div>
                          </div>
                          <h3 className="text-xl font-bold text-white mb-3">Watch Magic Happen</h3>
                          <p className="text-gray-300 text-sm leading-relaxed mb-4">
                            Observe real-time conversations, interact as an observer, and generate comprehensive insights and reports.
                          </p>
                          <button 
                            onClick={() => setActiveTab('analytics')}
                            className="w-full py-2 bg-green-600 hover:bg-green-700 text-white font-medium rounded-lg transition-colors"
                          >
                            📊 View Analytics
                          </button>
                        </div>
                      </div>
                    </div>
                  </div>
                  
                  {/* Final CTA - Optimized */}
                  <div className="text-center mt-16">
                    <div className="bg-gradient-to-r from-purple-600/20 to-blue-600/20 backdrop-blur-lg rounded-2xl p-8 border border-white/10">
                      <h3 className="text-2xl font-bold text-white mb-4">Ready to Transform Your Decision Making?</h3>
                      <p className="text-gray-300 mb-6 max-w-2xl mx-auto">
                        Join thousands of teams already using AI simulation to accelerate innovation, reduce risk, and make better decisions.
                      </p>
                      <div className="flex flex-col sm:flex-row gap-4 justify-center">
                        <button
                          onClick={() => safeSetActiveTab('simulation')}
                          className="px-8 py-4 bg-gradient-to-r from-purple-600 to-blue-600 text-white font-semibold rounded-xl shadow-2xl hover:shadow-purple-500/25 transition-all duration-300 hover:scale-[1.02]"
                        >
                          🚀 Start Your First Simulation
                        </button>
                        
                        <button
                          onClick={() => setActiveTab('agents')}
                          className="px-8 py-4 bg-white/10 backdrop-blur-lg text-white font-semibold rounded-xl border border-white/20 hover:bg-white/20 transition-all duration-300 hover:scale-[1.02]"
                        >
                          🤖 Explore Agent Library
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              </section>
            </div>
          )}
          
          {activeTab === 'simulation' && (
            <div>
              {console.log('🔍 AppContent: Rendering simulation content')}
              <SimulationControl 
                setActiveTab={setActiveTab} 
                activeTab={activeTab} 
                refreshTrigger={observatoryRefreshTrigger}
              />
            </div>
          )}
          
          {activeTab === 'agents' && (
            <div>
              {console.log('🔍 AppContent: Rendering agents content')}
              <AgentLibrary 
                onAddAgent={async (agent) => {
                  try {
                    const token = localStorage.getItem('auth_token');
                    if (!token) {
                      alert('Please log in to add agents');
                      return { success: false, message: 'Not authenticated' };
                    }

                    const API = process.env.REACT_APP_BACKEND_URL ? `${process.env.REACT_APP_BACKEND_URL}/api` : 'http://localhost:8001/api';
                    
                    // Create agent in user's agent database
                    // Since the backend automatically includes all user agents in simulations,
                    // this agent will immediately appear in the Observatory
                    const response = await fetch(`${API}/agents`, {
                      method: 'POST',
                      headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${token}`
                      },
                      body: JSON.stringify(agent)
                    });

                    const result = await response.json();
                    if (response.ok) {
                      console.log('✅ Agent added successfully and will appear in Observatory:', result);
                      
                      // Trigger Observatory refresh to show the new agent
                      triggerObservatoryRefresh();
                      
                      return { success: true, message: 'Agent added successfully' };
                    } else {
                      console.error('❌ Failed to add agent:', result);
                      return { success: false, message: result.detail || 'Failed to create agent' };
                    }

                  } catch (error) {
                    console.error('❌ Error adding agent:', error);
                    return { success: false, message: error.message };
                  }
                }}
                onRemoveAgent={async (agent) => {
                  try {
                    const token = localStorage.getItem('auth_token');
                    if (!token) {
                      console.log('⚠️ Not authenticated for agent removal');
                      return { success: false, message: 'Not authenticated' };
                    }

                    const API = process.env.REACT_APP_BACKEND_URL ? `${process.env.REACT_APP_BACKEND_URL}/api` : 'http://localhost:8001/api';
                    
                    // Remove agent from user's agent database
                    // Since the backend automatically includes all user agents in simulations,
                    // removing the agent from the database will remove it from simulations too
                    const response = await fetch(`${API}/agents/${agent.id}`, {
                      method: 'DELETE',
                      headers: {
                        'Authorization': `Bearer ${token}`
                      }
                    });

                    if (response.ok) {
                      console.log('✅ Agent removed successfully:', agent.name);
                      
                      // Trigger Observatory refresh to update the agent list
                      triggerObservatoryRefresh();
                      
                      return { success: true, message: 'Agent removed successfully' };
                    } else {
                      const error = await response.json();
                      console.error('❌ Failed to remove agent:', error);
                      return { success: false, message: error.detail || 'Failed to remove agent' };
                    }
                    
                  } catch (error) {
                    console.error('❌ Error removing agent:', error);
                    return { success: false, message: error.message };
                  }
                }}
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
          
          {activeTab === 'files' && (
            <div>
              {console.log('🔍 AppContent: Rendering files content')}
              <FileCenter />
            </div>
          )}
        </div>
      </main>

      {/* Comprehensive Account Modals - Now Working! */}
      <ProfileSettingsModal
        isOpen={showProfileModal}
        onClose={() => {
          console.log('🔍 Closing profile modal');
          setShowProfileModal(false);
        }}
        user={user}
        token={token}
        analyticsData={{}} // Can be populated with actual analytics data later
      />
      
      <PreferencesModal
        isOpen={showPreferencesModal}
        onClose={() => {
          console.log('🔍 Closing preferences modal');
          setShowPreferencesModal(false);
        }}
        audioNarrativeEnabled={false} // Can be managed with state later
      />
      
      <HelpSupportModal
        isOpen={showHelpModal}
        onClose={() => {
          console.log('🔍 Closing help modal');
          setShowHelpModal(false);
        }}
        onOpenFeedback={() => setShowFeedbackModal(true)}
      />

      <FeedbackModal
        isOpen={showFeedbackModal}
        onClose={() => {
          console.log('🔍 Closing feedback modal');
          setShowFeedbackModal(false);
        }}
      />

      {console.log('🔍 AppContent: Finished rendering AppContent')}

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

// Main App Component - Restored with full functionality
const App = () => {
  console.log('🔍 App: Component mounting');
  
  try {
    const authContext = useAuth();
    console.log('🔍 App: Auth context available:', !!authContext);
    
    const { user, loading } = authContext;
    console.log('🔍 App: Rendering with user:', !!user, 'loading:', loading);

    // Handler for HomePage authentication
    const handleAuthentication = useCallback((token, userData) => {
      console.log('🔍 App: handleAuthentication called with token:', !!token, 'user:', !!userData);
      // This will be handled by the AuthContext
    }, []);

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
    return (
      <ErrorBoundary>
        <AppContent />
      </ErrorBoundary>
    );
  } catch (error) {
    console.error('🔥 App: Error in component:', error);
    return (
      <div className="min-h-screen bg-gradient-to-br from-red-900 via-red-800 to-red-900 flex items-center justify-center">
        <div className="text-center text-white">
          <h1 className="text-2xl font-bold mb-4">App Error</h1>
          <p>{error.message}</p>
          <button 
            onClick={() => window.location.reload()}
            className="mt-4 px-4 py-2 bg-white/20 hover:bg-white/30 rounded-lg transition-colors"
          >
            Refresh Page
          </button>
        </div>
      </div>
    );
  }
};

// Main App wrapper with AuthProvider
const AppWithProvider = () => {
  return (
    <AuthProvider>
      <div className="min-h-screen bg-gradient-to-br from-gray-900 via-blue-900 to-purple-900">
        <App />
      </div>
    </AuthProvider>
  );
};

export default AppWithProvider;