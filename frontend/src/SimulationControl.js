import React, { useState, useEffect, useRef, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import axios from 'axios';
import { useAuth } from './AuthContext';
import { useSimulation } from './App';
import AgentCreateModal from './AgentCreateModal';
import StartButton from './StartButton';
import SetupFlow from './SetupFlow';

const API = process.env.REACT_APP_BACKEND_URL ? `${process.env.REACT_APP_BACKEND_URL}/api` : 'http://localhost:8001/api';

// Performance optimization utility: Debounce function
const debounce = (func, wait) => {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
};

// Helper function to format scenario text for better readability
const formatScenarioText = (text) => {
  if (!text) return <p className="text-white/70 italic">No scenario details available</p>;
  
  // Split text into sentences and paragraphs
  const sentences = text.split(/\.\s+/);
  const paragraphs = [];
  let currentParagraph = [];
  
  sentences.forEach((sentence, index) => {
    if (sentence.trim()) {
      // Add the period back except for the last sentence
      const formattedSentence = index === sentences.length - 1 ? sentence : sentence + '.';
      currentParagraph.push(formattedSentence);
      
      // Create paragraph breaks for longer texts (every 3-4 sentences)
      if (currentParagraph.length >= 3 || sentence.length > 200) {
        paragraphs.push(currentParagraph.join(' '));
        currentParagraph = [];
      }
    }
  });
  
  // Add any remaining sentences
  if (currentParagraph.length > 0) {
    paragraphs.push(currentParagraph.join(' '));
  }
  
  // If no paragraphs were created, treat as single paragraph
  if (paragraphs.length === 0) {
    paragraphs.push(text);
  }
  
  // Function to format individual text segments
  const formatTextSegments = (text) => {
    // Simple approach: split by words and apply very selective formatting
    const words = text.split(/(\s+)/);
    
    return words.map((word, index) => {
      if (!word.trim()) return word; // Return whitespace as-is
      
      // Clean word for pattern matching (remove punctuation for matching)
      const cleanWord = word.replace(/[^\w\s-]/g, '');
      const originalWord = word;
      
      // RED - Only for extremely critical/dangerous words
      const criticalWords = /^(crisis|emergency|catastrophic|critical|urgent|breach|attack|failure|disaster|pandemic|outbreak|bioterrorism|terrorism|threat|danger|alert|warning|evacuation|lockdown|quarantine)$/i;
      if (criticalWords.test(cleanWord)) {
        return (
          <span key={index} className="text-red-300 font-semibold">
            {word}
          </span>
        );
      }
      
      // BLUE - Removed number formatting (keeping numbers as regular white text)
      // Numbers will now appear as regular white text
      
      // WHITE BOLD - For important names and organizations
      
      // Virus names and variants (H7N9-X, COVID-19, etc.)
      if (/^[A-Z]\d+[A-Z]\d*(-[A-Z])?$|^COVID-\d+$|^H\d+N\d+(-[A-Z])?$/i.test(cleanWord)) {
        return (
          <span key={index} className="text-white font-bold">
            {word}
          </span>
        );
      }
      
      // Key organizations (acronyms)
      const importantOrgs = /^(WHO|UN|EU|FDA|CDC|NASA|FBI|CIA|NATO|G20|NYSE|NASDAQ|ACE2)$/i;
      if (importantOrgs.test(cleanWord)) {
        return (
          <span key={index} className="text-white font-bold">
            {word}
          </span>
        );
      }
      
      // Scientific/Technical terms
      const techTerms = /^(bioengineering|zero-day|authentication|infrastructure|cybersecurity|antiviral|vaccine|genome|sequencing|mutations|receptor|transmissibility|asymptomatic|mortality|bioterrorism)$/i;
      if (techTerms.test(cleanWord)) {
        return (
          <span key={index} className="text-white font-bold">
            {word}
          </span>
        );
      }
      
      // Company names with suffixes (simplified)
      if (/^[A-Z][a-zA-Z]+(?:Tech|Corp|Inc|Ltd|LLC|Industries|Group|Company|Corporation|Technologies|Systems|Solutions)$/i.test(cleanWord)) {
        return (
          <span key={index} className="text-white font-bold">
            {word}
          </span>
        );
      }
      
      // Proper nouns (capitalized words) that are likely important names
      // Only if they're substantial words (4+ characters) and not common words
      const commonWords = /^(The|This|That|With|From|Into|Over|Under|Above|Below|After|Before|During|While|Since|Until|When|Where|What|Which|Who|Why|How|And|But|Or|So|Yet|For|Nor|As|If|Because|Although|Though|Unless|Whether|Initial|Unlike|Within|Among|Between|Through|Upon|Across|Against|Around|Behind|Beside|Beyond|Inside|Outside|Toward|Without|According|Another|Several|Various|Different|Similar|Current|Recent|Future|Next|Previous|Following|Final|Total|Overall|General|Specific|Particular|Certain|Possible|Potential|Actual|Real|True|False|Right|Wrong|Good|Bad|New|Old|Young|Large|Small|Big|Little|Long|Short|High|Low|Fast|Slow|Early|Late|First|Last|Best|Worst|Most|Least|More|Less|Many|Few|All|Some|Each|Every|Any|No|None|Both|Either|Neither|Other|Same|Different)$/i;
      
      if (cleanWord.length >= 4 && /^[A-Z][a-zA-Z]+$/.test(cleanWord) && !commonWords.test(cleanWord)) {
        return (
          <span key={index} className="text-white font-bold">
            {word}
          </span>
        );
      }
      
      // Quoted text (keep italic styling)
      if (word.includes('"') && word.length > 3) {
        return (
          <span key={index} className="text-white/90 italic">
            {word}
          </span>
        );
      }
      
      // Return regular text for everything else
      return word;
    });
  };
  
  return (
    <div className="space-y-4">
      {paragraphs.map((paragraph, index) => (
        <p key={index} className="text-white/85 text-sm leading-relaxed">
          {formatTextSegments(paragraph)}
        </p>
      ))}
    </div>
  );
};

const WELCOME_MESSAGES = [
  "Welcome, Observer",
  "Hey, Observer is back! Agents, rejoice!",
  "What will you observe today, almighty Observer?"
];

// Agent Edit Modal Component
const AgentEditModal = ({ isOpen, onClose, agent, onSave }) => {
  const [formData, setFormData] = useState({
    name: '',
    archetype: 'scientist',
    expertise: '',
    background: '',
    goal: '',
    memories: '',
    avatar_url: '',
    avatar_prompt: '',
    personality: {
      extroversion: 5,
      optimism: 5,
      curiosity: 5,
      cooperativeness: 5,
      energy: 5
    }
  });
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (agent && isOpen) {
      setFormData({
        name: agent.name || '',
        archetype: agent.archetype || 'scientist',
        expertise: agent.expertise || '',
        background: agent.background || '',
        goal: agent.goal || '',
        memories: agent.memory_summary || '',
        avatar_url: agent.avatar_url || '',
        avatar_prompt: agent.avatar_prompt || '',
        personality: agent.personality || {
          extroversion: 5,
          optimism: 5,
          curiosity: 5,
          cooperativeness: 5,
          energy: 5
        }
      });
    }
  }, [agent, isOpen]);

  const handleSave = async () => {
    setSaving(true);
    try {
      await onSave(formData);
      onClose();
    } catch (error) {
      console.error('Error saving agent:', error);
    } finally {
      setSaving(false);
    }
  };

  const handleInputChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handlePersonalityChange = (trait, value) => {
    setFormData(prev => ({
      ...prev,
      personality: {
        ...prev.personality,
        [trait]: parseInt(value)
      }
    }));
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
      <div className="bg-gradient-to-br from-purple-900 to-pink-900 p-8 rounded-xl shadow-2xl max-w-4xl w-full mx-4 border border-purple-500/30 max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-2xl font-bold text-white">Edit Agent</h2>
          <button
            onClick={onClose}
            className="text-white/60 hover:text-white transition-colors"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Agent Avatar */}
          <div className="text-center">
            <div className="w-32 h-32 rounded-full bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center mx-auto mb-4">
              {formData.avatar_url ? (
                <img src={formData.avatar_url} alt={formData.name} className="w-full h-full rounded-full object-cover" />
              ) : (
                <span className="text-white text-4xl font-bold">
                  {formData.name ? formData.name.charAt(0).toUpperCase() : '👤'}
                </span>
              )}
            </div>
          </div>

          {/* Agent Details */}
          <div className="space-y-4">
            <div>
              <label className="block text-white/80 text-sm font-medium mb-2">Name</label>
              <input
                type="text"
                value={formData.name}
                onChange={(e) => handleInputChange('name', e.target.value)}
                className="w-full bg-white/10 border border-white/20 rounded-lg px-3 py-2 text-white placeholder-white/50 focus:outline-none focus:ring-2 focus:ring-purple-500"
              />
            </div>

            <div>
              <label className="block text-white/80 text-sm font-medium mb-2">Archetype</label>
              <select
                value={formData.archetype}
                onChange={(e) => handleInputChange('archetype', e.target.value)}
                className="w-full bg-white/10 border border-white/20 rounded-lg px-3 py-2 text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
              >
                <option value="scientist">Scientist</option>
                <option value="artist">Artist</option>
                <option value="leader">Leader</option>
                <option value="skeptic">Skeptic</option>
                <option value="optimist">Optimist</option>
                <option value="introvert">Introvert</option>
                <option value="adventurer">Adventurer</option>
                <option value="mediator">Mediator</option>
                <option value="researcher">Researcher</option>
              </select>
            </div>

            <div>
              <label className="block text-white/80 text-sm font-medium mb-2">Goal</label>
              <input
                type="text"
                value={formData.goal}
                onChange={(e) => handleInputChange('goal', e.target.value)}
                className="w-full bg-white/10 border border-white/20 rounded-lg px-3 py-2 text-white placeholder-white/50 focus:outline-none focus:ring-2 focus:ring-purple-500"
              />
            </div>

            <div>
              <label className="block text-white/80 text-sm font-medium mb-2">Expertise</label>
              <input
                type="text"
                value={formData.expertise}
                onChange={(e) => handleInputChange('expertise', e.target.value)}
                className="w-full bg-white/10 border border-white/20 rounded-lg px-3 py-2 text-white placeholder-white/50 focus:outline-none focus:ring-2 focus:ring-purple-500"
              />
            </div>
          </div>
        </div>

        <div className="mt-6">
          <label className="block text-white/80 text-sm font-medium mb-2">Background</label>
          <textarea
            value={formData.background}
            onChange={(e) => handleInputChange('background', e.target.value)}
            rows={3}
            className="w-full bg-white/10 border border-white/20 rounded-lg px-3 py-2 text-white placeholder-white/50 focus:outline-none focus:ring-2 focus:ring-purple-500"
          />
        </div>

        <div className="mt-6">
          <label className="block text-white/80 text-sm font-medium mb-2">Memories</label>
          <textarea
            value={formData.memories}
            onChange={(e) => handleInputChange('memories', e.target.value)}
            rows={3}
            className="w-full bg-white/10 border border-white/20 rounded-lg px-3 py-2 text-white placeholder-white/50 focus:outline-none focus:ring-2 focus:ring-purple-500"
          />
        </div>

        {/* Personality Traits */}
        <div className="mt-6">
          <h3 className="text-white/80 text-sm font-medium mb-4">Personality Traits</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {Object.entries(formData.personality).map(([trait, value]) => (
              <div key={trait}>
                <label className="block text-white/60 text-xs mb-1 capitalize">{trait}</label>
                <input
                  type="range"
                  min="1"
                  max="10"
                  value={value}
                  onChange={(e) => handlePersonalityChange(trait, e.target.value)}
                  className="w-full"
                />
                <div className="text-white/40 text-xs text-center">{value}/10</div>
              </div>
            ))}
          </div>
        </div>

        <div className="mt-6 flex justify-end space-x-3">
          <button
            onClick={onClose}
            className="px-4 py-2 text-white/80 hover:text-white transition-colors"
          >
            Cancel
          </button>
          <button
            onClick={handleSave}
            disabled={saving}
            className="bg-purple-600 hover:bg-purple-700 disabled:bg-gray-600 text-white px-6 py-2 rounded-lg transition-colors"
          >
            {saving ? 'Saving...' : 'Save Changes'}
          </button>
        </div>
      </div>
    </div>
  );
};

const SimulationControl = ({ setActiveTab, activeTab, refreshTrigger }) => {
  // Interactive Loading Messages Component
  const { user, token } = useAuth();
  const { simulationData, updateSimulationData, clearSimulationData } = useSimulation();
  
  // Extract data from global context
  const {
    simulationState,
    agents,
    conversations,
    scenario,
    customScenario,
    scenarioName,
    isRunning,
    isPaused,
    observerMessages,
    isDataLoaded
  } = simulationData;
  
  // Helper functions for updating specific parts of simulation data
  const setScenario = (value) => updateSimulationData({ scenario: value });
  const setCustomScenario = (value) => updateSimulationData({ customScenario: value });
  const setScenarioName = (value) => updateSimulationData({ scenarioName: value });
  const setIsRunning = (value) => updateSimulationData({ isRunning: value });
  const setIsPaused = (value) => updateSimulationData({ isPaused: value });
  const setAgents = (value) => updateSimulationData({ agents: value });
  const setConversations = (value) => updateSimulationData({ conversations: value });
  const setObserverMessages = (value) => updateSimulationData({ observerMessages: value });
  
  // Local state for UI-only concerns
  const [autoGenerating, setAutoGenerating] = useState(false);
  const [loading, setLoading] = useState(false);
  const [simulationLoading, setSimulationLoading] = useState(false); // Separate loading state for play/pause operations
  const [startFreshLoading, setStartFreshLoading] = useState(false); // Separate loading state for start fresh operations
  const [conversationLoading, setConversationLoading] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [currentSearchIndex, setCurrentSearchIndex] = useState(0);
  const [editingAgent, setEditingAgent] = useState(null);
  const [showEditModal, setShowEditModal] = useState(false);
  const [showCreateAgentModal, setShowCreateAgentModal] = useState(false);
  const [showSetScenario, setShowSetScenario] = useState(false);
  const [showObserverChat, setShowObserverChat] = useState(false);
  const [showSetupFlow, setShowSetupFlow] = useState(false);
  const [showClearAllModal, setShowClearAllModal] = useState(false);
  const [showStartFreshModal, setShowStartFreshModal] = useState(false);
  const [setupFlowData, setSetupFlowData] = useState(null);
  const [simulationType, setSimulationType] = useState(null); // business, entertainment, research
  const [simulationTrack, setSimulationTrack] = useState(null); // fast, research, strategic, etc.
  const [showReports, setShowReports] = useState(false); // New state for Reports section
  const [showDocs, setShowDocs] = useState(false); // New state for Docs section
  const [selectedDocument, setSelectedDocument] = useState(null); // For viewing specific documents
  const [documentCardVisible, setDocumentCardVisible] = useState(false); // For showing document card
  const [selectedReport, setSelectedReport] = useState(null); // For viewing specific reports
  const [showReport, setShowReport] = useState(false);
  const [reportData, setReportData] = useState('');
  const [reportLoading, setReportLoading] = useState(false);
  const [reportCardVisible, setReportCardVisible] = useState(false);
  const [reportCardExpanded, setReportCardExpanded] = useState(true);
  const [autoReportEnabled, setAutoReportEnabled] = useState(true); // Weekly reports - default ON
  const [autoDailyReportEnabled, setAutoDailyReportEnabled] = useState(true); // Daily reports - default ON
  const [autoGenerateInterval, setAutoGenerateInterval] = useState(null);
  const [observerMessage, setObserverMessage] = useState('');
  const [isObserverLoading, setIsObserverLoading] = useState(false);
  const [notificationVisible, setNotificationVisible] = useState(false);
  const [notificationText, setNotificationText] = useState('');
  const [scenarioExpanded, setScenarioExpanded] = useState(false);
  const searchRefs = useRef([]);
  const messagesEndRef = useRef(null);
  const fetchingRef = useRef(false); // Performance optimization: Prevent duplicate fetches
  const conversationBuildingRef = useRef(false); // Prevent polling conflicts during message display
  const lastScrollTimeRef = useRef(0); // Track when user last scrolled
  const conversationUpdateRef = useRef(false); // Prevent concurrent conversation updates

  // Check if user is actively scrolling (to prevent polling during active reading)
  const isUserScrolling = () => {
    const now = Date.now();
    return now - lastScrollTimeRef.current < 5000; // Consider scrolling active for 5 seconds
  };

  const [newAgent, setNewAgent] = useState({
    name: '',
    archetype: '',
    expertise: '',
    background: '',
    goal: '',
    avatar_url: ''
  });

  // Initialize with performance optimizations


  // Initialize with performance optimizations
  useEffect(() => {
    // Define fetch function directly inside useEffect to avoid hoisting issues
    const performFetch = debounce(async (forceRefresh = false) => {
      try {
        // Only fetch if not already fetching (prevent duplicate calls)
        if (fetchingRef.current && !forceRefresh) {
          return;
        }
        fetchingRef.current = true;

        // Parallel API calls for better performance
        const [stateResponse, agentsResponse, conversationsResponse, documentsResponse] = await Promise.all([
          axios.get(`${API}/simulation/state`, {
            headers: { Authorization: `Bearer ${token}` }
          }),
          axios.get(`${API}/agents`, {
            headers: { Authorization: `Bearer ${token}` }
          }),
          axios.get(`${API}/conversations/active`, {  // Changed to active conversations only
            headers: { Authorization: `Bearer ${token}` }
          }),
          axios.get(`${API}/documents`, {
            headers: { Authorization: `Bearer ${token}` }
          })
        ]);

        // Store scroll position before DOM update to prevent disruption
        // Use more specific selector for Live Conversations section only
        const conversationContainer = document.querySelector('[data-conversation-container="true"]');
        const scrollTop = conversationContainer ? conversationContainer.scrollTop : 0;
        const scrollLeft = conversationContainer ? conversationContainer.scrollLeft : 0;

        // Update global simulation data
        updateSimulationData({
          simulationState: stateResponse.data,
          conversations: conversationsResponse.data || [],
          isRunning: stateResponse.data.is_active || false,
          isPaused: stateResponse.data.is_paused || false,
          agents: agentsResponse.data || [],
          // IMPORTANT: Include reports from backend response
          reports: stateResponse.data.reports || [],
          // IMPORTANT: Include documents from documents endpoint
          documents: documentsResponse.data.documents || [],
          isDataLoaded: true
        });
        
        // Restore scroll position after DOM update to prevent reading interruption
        // Use multiple attempts with increasing delays for maximum reliability
        const restoreScrollPosition = () => {
          const conversationContainer = document.querySelector('[data-conversation-container="true"]');
          if (conversationContainer && (scrollTop > 0 || scrollLeft > 0)) {
            conversationContainer.scrollTop = scrollTop;
            conversationContainer.scrollLeft = scrollLeft;
            console.log('🔒 Polling: Restored scroll position to:', scrollTop, scrollLeft);
          }
        };
        
        // Multiple restoration attempts for maximum reliability
        setTimeout(restoreScrollPosition, 100);
        setTimeout(restoreScrollPosition, 300);
        setTimeout(restoreScrollPosition, 500);
        
        console.log('✅ Optimized fetch completed - Agents:', agentsResponse.data.length, 'Conversations:', conversationsResponse.data?.length || 0);
        
      } catch (error) {
        console.error('Error fetching simulation state:', error);
        // Don't clear agents on error to maintain UI state
      } finally {
        fetchingRef.current = false;
      }
    }, 300);

    // Initial fetch
    performFetch(true);
    const welcomeMessage = WELCOME_MESSAGES[Math.floor(Math.random() * WELCOME_MESSAGES.length)];
    showNotification(welcomeMessage);
    
    // Smart refresh function (defined inside useEffect to avoid circular dependency)
    const smartRefresh = () => {
      // EXTREMELY SLOW polling to prevent ANY scroll disruption while reading
      const interval = isRunning ? 60000 : 120000; // 60 seconds active, 120 seconds idle (was 30s/60s)
      
      // Only fetch if page is visible and user isn't actively scrolling
      if (!document.hidden && !isUserScrolling()) {
        performFetch();
      }
      
      return interval;
    };
    
    // Smart interval that adapts based on simulation state
    let intervalId;
    const setupInterval = () => {
      if (intervalId) clearInterval(intervalId);
      const interval = smartRefresh();
      intervalId = setInterval(smartRefresh, interval);
    };
    
    setupInterval();
    
    // Page visibility optimization: Pause polling when tab is hidden
    const handleVisibilityChange = () => {
      if (document.hidden) {
        if (intervalId) clearInterval(intervalId);
      } else {
        setupInterval();
        performFetch(true); // Fetch immediately when tab becomes visible
      }
    };
    
    document.addEventListener('visibilitychange', handleVisibilityChange);
    
    return () => {
      if (intervalId) clearInterval(intervalId);
      document.removeEventListener('visibilitychange', handleVisibilityChange);
    };
  }, [token, isRunning]); // Removed fetchSimulationState from dependencies

  // Load simulation data immediately if not already loaded
  useEffect(() => {
    if (!isDataLoaded && token) {
      console.log('🔄 Loading simulation data immediately - not loaded yet');
      fetchSimulationState();
    } else if (isDataLoaded) {
      console.log('✅ Simulation data already loaded, showing immediately');
    }
  }, [token, isDataLoaded]);

  // Auto-show setup flow for new users or users without agents/scenario - DISABLED for now
  useEffect(() => {
    // Temporarily disabled auto-trigger to fix the immediate popup issue
    // if (isDataLoaded && token) {
    //   const needsSetup = (
    //     (!agents || agents.length === 0) || 
    //     !scenarioName || 
    //     scenarioName.trim() === '' ||
    //     scenarioName === 'General Discussion'
    //   );

    //   if (needsSetup && !showSetupFlow) {
    //     console.log('🚀 Auto-showing setup flow for new user or incomplete setup');
    //     setShowSetupFlow(true);
    //   }
    // }
  }, [isDataLoaded, agents, scenarioName, token, showSetupFlow]);

  // Enhanced cursor tracking for Observer eye - immediate tracking with blinking
  useEffect(() => {
    let idleTimer = null;
    let isIdle = false;
    let blinkInterval = null;

    const handleMouseMove = (e) => {
      const pupil = document.getElementById('observer-pupil');
      if (!pupil) return;

      // IMMEDIATE cursor tracking - no delays
      const eye = pupil.parentElement;
      const eyeRect = eye.getBoundingClientRect();
      const eyeCenterX = eyeRect.left + eyeRect.width / 2;
      const eyeCenterY = eyeRect.top + eyeRect.height / 2;

      const deltaX = e.clientX - eyeCenterX;
      const deltaY = e.clientY - eyeCenterY;
      
      // Calculate angle and limit movement within eye bounds
      const angle = Math.atan2(deltaY, deltaX);
      const distance = Math.sqrt(deltaX * deltaX + deltaY * deltaY);
      const maxDistance = 8; // Maximum pupil movement from center
      
      const pupilX = Math.cos(angle) * Math.min(maxDistance, distance * 0.3);
      const pupilY = Math.sin(angle) * Math.min(maxDistance, distance * 0.3);

      // Apply immediate tracking
      pupil.style.transform = `translate(${pupilX}px, ${pupilY}px)`;
      
      // Stop natural animation when tracking
      if (!isIdle) {
        pupil.classList.remove('animate-observer-eye');
      }

      // Clear and reset idle timer
      if (idleTimer) {
        clearTimeout(idleTimer);
      }
      
      isIdle = false;

      // Set new idle timer (3 seconds)
      idleTimer = setTimeout(() => {
        if (pupil) {
          isIdle = true;
          pupil.classList.add('animate-observer-eye');
          pupil.style.transform = 'translate(0px, 0px)';
        }
      }, 3000);
    };

    const handleMouseLeave = () => {
      const pupil = document.getElementById('observer-pupil');
      if (pupil) {
        isIdle = true;
        pupil.classList.add('animate-observer-eye');
        pupil.style.transform = 'translate(0px, 0px)';
      }
      if (idleTimer) {
        clearTimeout(idleTimer);
        idleTimer = null;
      }
    };

    // Enhanced blinking functionality
    const startBlinking = () => {
      const pupil = document.getElementById('observer-pupil');
      const eyeContainer = pupil?.parentElement;
      if (!pupil || !eyeContainer) return;

      const blink = () => {
        // Create smooth blink effect with natural easing
        const blinkOverlay = document.createElement('div');
        blinkOverlay.className = 'absolute inset-0 bg-white rounded-full';
        blinkOverlay.style.transform = 'scaleY(0)';
        blinkOverlay.style.transformOrigin = 'center center';
        blinkOverlay.style.transition = 'transform 0.08s cubic-bezier(0.4, 0.0, 1, 1)'; // Fast close
        blinkOverlay.style.zIndex = '10';
        blinkOverlay.style.willChange = 'transform';
        
        eyeContainer.appendChild(blinkOverlay);
        
        // Animate smooth blink with natural timing
        requestAnimationFrame(() => {
          // Fast close (like real eyes)
          blinkOverlay.style.transform = 'scaleY(1)';
          
          setTimeout(() => {
            // Slower open (more natural)
            blinkOverlay.style.transition = 'transform 0.12s cubic-bezier(0.0, 0.0, 0.2, 1)';
            blinkOverlay.style.transform = 'scaleY(0)';
          }, 80); // Eye closed for 80ms
          
          setTimeout(() => {
            if (blinkOverlay.parentElement) {
              blinkOverlay.parentElement.removeChild(blinkOverlay);
            }
          }, 220); // Total animation: 80ms + 120ms + cleanup
        });
      };

      // Blink every 3-7.5 seconds (50% slower intervals)
      const scheduleNextBlink = () => {
        const randomDelay = 3000 + Math.random() * 4500; // 3-7.5 seconds (was 2-5 seconds)
        blinkInterval = setTimeout(() => {
          blink();
          scheduleNextBlink();
        }, randomDelay);
      };

      // Start first blink after 3 seconds (50% slower)
      setTimeout(() => {
        blink();
        scheduleNextBlink();
      }, 3000);
    };

    // Start tracking immediately
    document.addEventListener('mousemove', handleMouseMove, { passive: true });
    document.addEventListener('mouseleave', handleMouseLeave);
    
    // Start blinking
    startBlinking();

    return () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseleave', handleMouseLeave);
      if (idleTimer) clearTimeout(idleTimer);
      if (blinkInterval) clearTimeout(blinkInterval);
    };
  }, []);

  // Simple fetch function for use by other functions (non-debounced to avoid hoisting issues)
  // Handle PDF download with authentication
  const handleReportPdfDownload = async (reportId) => {
    try {
      const token = localStorage.getItem('auth_token');
      if (!token) {
        alert('Please log in to download PDF');
        return;
      }

      const response = await fetch(`${API}/reports/${reportId}/download-pdf`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.style.display = 'none';
        a.href = url;
        a.download = `report_${reportId}.pdf`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
      } else {
        const errorText = await response.text();
        console.error('PDF download failed:', errorText);
        alert('Failed to download PDF. Please try again.');
      }
    } catch (error) {
      console.error('PDF download error:', error);
      alert('Failed to download PDF. Please try again.');
    }
  };

  const fetchSimulationState = async () => {
    try {
      if (fetchingRef.current) return;
      fetchingRef.current = true;

      const [stateResponse, agentsResponse, conversationsResponse, documentsResponse] = await Promise.all([
        axios.get(`${API}/simulation/state`, {
          headers: { Authorization: `Bearer ${token}` }
        }),
        axios.get(`${API}/agents`, {
          headers: { Authorization: `Bearer ${token}` }
        }),
        axios.get(`${API}/conversations/active`, {  // Changed to active conversations only
          headers: { Authorization: `Bearer ${token}` }
        }),
        axios.get(`${API}/documents`, {
          headers: { Authorization: `Bearer ${token}` }
        })
      ]);

      // Update global simulation data
      updateSimulationData({
        simulationState: stateResponse.data,
        conversations: conversationsResponse.data || [],
        isRunning: stateResponse.data.is_active || false,
        isPaused: stateResponse.data.is_paused || false,
        agents: agentsResponse.data || [],
        // IMPORTANT: Restore scenario state from backend
        scenario: stateResponse.data.scenario || '',
        customScenario: stateResponse.data.scenario || '',
        scenarioName: stateResponse.data.scenario_name || '',
        // IMPORTANT: Include reports from backend response
        reports: stateResponse.data.reports || [],
        // IMPORTANT: Include documents from documents endpoint
        documents: documentsResponse.data.documents || [],
        isDataLoaded: true
      });
      
      console.log('✅ Fetch completed - ACTIVE Conversations only:', conversationsResponse.data?.length || 0);
      console.log('✅ Scenario restored:', stateResponse.data.scenario ? 'Yes' : 'No');
      
    } catch (error) {
      console.error('Error fetching simulation state:', error);
    } finally {
      fetchingRef.current = false;
    }
  };



  // MANUAL SCROLL CONTROL ONLY - No automatic scrolling
  // Users have complete control over their scroll position
  const scrollPositionRef = useRef({ top: 0, isAtBottom: false });
  
  // Track scroll position for potential future use (but take no automatic actions)
  useEffect(() => {
    const conversationContainer = document.querySelector('[data-conversation-container="true"]');
    if (!conversationContainer) return;
    
    const trackScrollPosition = () => {
      const scrollTop = conversationContainer.scrollTop;
      const scrollHeight = conversationContainer.scrollHeight;
      const clientHeight = conversationContainer.clientHeight;
      const isAtBottom = Math.abs((scrollTop + clientHeight) - scrollHeight) <= 10;
      
      scrollPositionRef.current = { top: scrollTop, isAtBottom };
      lastScrollTimeRef.current = Date.now(); // Record when user scrolled
      
      // Note: We track position but take NO automatic scroll actions
    };
    
    conversationContainer.addEventListener('scroll', trackScrollPosition);
    trackScrollPosition(); // Initial tracking
    
    return () => {
      conversationContainer.removeEventListener('scroll', trackScrollPosition);
    };
  }, []);

  // NO automatic scroll behavior - user has full manual control
  // Removed all conversation-based scroll triggers

  // React to refresh trigger from Agent Library
  useEffect(() => {
    if (refreshTrigger > 0) {
      console.log('🔄 Observatory refreshing due to Agent Library change');
      fetchSimulationState();
    }
  }, [refreshTrigger]);

  // Natural conversation flow when simulation is running
  useEffect(() => {
    const agentsCount = Array.isArray(agents) ? agents.length : 0;
    
    if (isRunning && !isPaused && agentsCount >= 2) {
      console.log('🔄 Starting natural conversation flow...');
      
      // Clear any existing interval
      if (autoGenerateInterval) {
        clearInterval(autoGenerateInterval);
      }
      
      // Set up new interval for contextual message generation
      const intervalId = setInterval(() => {
        console.log('💬 Adding contextual message for natural conversation...');
        addContextualMessage(); // Add contextually aware message
      }, 15000); // Add new contextual message every 15 seconds - optimized for engaging pace
      
      setAutoGenerateInterval(intervalId);
      
    } else {
      // Clear interval when simulation stops/pauses or insufficient agents
      if (autoGenerateInterval) {
        console.log('⏹️ Stopping natural conversation flow');
        clearInterval(autoGenerateInterval);
        setAutoGenerateInterval(null);
      }
    }
    
    // Cleanup function
    return () => {
      if (autoGenerateInterval) {
        clearInterval(autoGenerateInterval);
      }
    };
  }, [isRunning, isPaused, Array.isArray(agents) ? agents.length : 0]);

  const showNotification = (text) => {
    // Only show notification if no scenario is currently set
    if (!scenarioName) {
      setNotificationText(text);
      setNotificationVisible(true);
      setTimeout(() => {
        setNotificationVisible(false);
      }, 8000);
    }
  };

  // Play/Pause simulation function with immediate visual feedback
  const playPauseSimulation = async () => {
    console.log('🎯 Current state:', { isRunning, isPaused, simulationLoading, agentsCount: agents.length });
    
    if (simulationLoading) {
      console.log('🚫 Simulation operation already in progress, ignoring click');
      return;
    }
    
    // ✨ IMMEDIATE VISUAL FEEDBACK: Update button state instantly
    const targetIsRunning = !isRunning;
    const targetIsPaused = !targetIsRunning;
    
    console.log(`🎯 Target state: isRunning=${targetIsRunning}, isPaused=${targetIsPaused}`);
    
    // Show loading state briefly
    setSimulationLoading(true);
    
    // ✨ IMMEDIATE UI UPDATE: Provide instant visual feedback
    setTimeout(() => {
      setIsRunning(targetIsRunning);
      setIsPaused(targetIsPaused);
      console.log('⚡ Immediate UI feedback applied - user sees button change instantly');
    }, 100); // 100ms delay for smooth transition
    
    // Declare endpoint variable outside try block for error handling
    let endpoint, targetState;
    
    try {
      // Determine the correct endpoint
      if (isRunning) {
        endpoint = '/simulation/pause';
        targetState = 'pause';
      } else {
        endpoint = '/simulation/start';
        targetState = 'start';
      }
      
      console.log(`📡 API Call: ${endpoint}`);
      
      // Make API call with shorter timeout
      const response = await axios.post(`${API}${endpoint}`, {}, {
        headers: { Authorization: `Bearer ${token}` },
        timeout: 8000 // Reduced timeout for faster failure detection
      });
      
      console.log(`✅ ${targetState} operation completed:`, response.data);
      
      // Handle post-operation actions based on endpoint
      if (endpoint === '/simulation/start') {
        console.log('🔄 Starting - with manual conversation control for proper alternation');
        
        // ✨ MANUAL CONVERSATION CONTROL: Frontend manages generation for proper agent alternation
        if (response.data && response.data.manual_control) {
          console.log('🎬 Starting loading animations for manual conversation generation...');
          
          // Start interactive loading animations immediately
          startInteractiveLoadingAnimations(3);
          
          // Trigger immediate first conversation generation
          setTimeout(() => {
            console.log('🎯 Triggering first conversation manually...');
            generateNewConversation(false);
          }, 500); // Small delay to ensure simulation state is ready
          
          // Set up scheduled follow-up generations for faster pacing
          const scheduleFollowUpConversations = () => {
            let generationCount = 0;
            const maxGenerations = 10; // Limit to prevent endless generation
            
            const generateNext = () => {
              if (generationCount < maxGenerations && isRunning) {
                generationCount++;
                console.log(`🔄 Scheduled conversation generation ${generationCount}/${maxGenerations}`);
                generateNewConversation(true); // Mark as auto generation
                
                // Schedule next generation
                setTimeout(generateNext, 25000); // 25 second intervals for good pacing
              }
            };
            
            // Start follow-up generations after initial one completes
            setTimeout(generateNext, 30000); // Wait 30s after first generation
          };
          
          scheduleFollowUpConversations();
        }
        
        fetchSimulationState();
        
      } else if (endpoint === '/simulation/resume') {
        console.log('🔄 Resuming - continuing conversation generation');
        fetchSimulationState();
        
      } else if (endpoint === '/simulation/pause') {
        console.log('⏸️ Paused - stopping all conversation generation');
        
        // ✨ STOP ALL ANIMATIONS: Pause should stop everything
        setLoadingAnimations({
          active: false,
          currentStep: 0,
          expectedMessages: 0,
          receivedMessages: 0,
          agentStatuses: {}
        });
        
        fetchSimulationState();
      }
      
    } catch (error) {
      console.error(`❌ Error during ${endpoint}:`, error);
      
      // ✨ REVERT UI STATE: If API fails, revert to original state
      setIsRunning(isRunning);
      setIsPaused(isPaused);
      console.log('🔄 Reverted UI state due to API failure');
      
      // Show user-friendly error message
      const errorMsg = error.response?.data?.detail || error.message || 'Failed to update simulation';
      showNotification(`❌ Simulation Error: ${errorMsg}`);
      
    } finally {
      // ✨ QUICK LOADING RESET: Stop loading state quickly for responsiveness
      setTimeout(() => {
        setSimulationLoading(false);
        console.log('🎯 Play/Pause loading state cleared');
      }, 500); // Quick reset for better UX
    }
  };

  // Simplified conversation display - no complex animations needed
  const displayConversation = (conversationData) => {
    if (!conversationData) return;
    
    console.log('📝 Displaying conversation directly:', conversationData.id);
    
    // ✨ IMMEDIATE ANIMATION STOP: Stop animations immediately when displaying conversation
    if (loadingAnimations.active) {
      console.log('🛑 IMMEDIATE STOP: Stopping animations because conversation is being displayed');
      setLoadingAnimations({
        active: false,
        currentStep: 0,
        expectedMessages: 0,
        receivedMessages: 0,
        agentStatuses: {}
      });
    }
    
    // Simply add the conversation to the list
    const currentConversations = Array.isArray(conversations) ? [...conversations] : [];
    const existingIndex = currentConversations.findIndex(conv => conv.id === conversationData.id);
    
    if (existingIndex >= 0) {
      currentConversations[existingIndex] = conversationData;
    } else {
      currentConversations.push(conversationData);
    }
    
    updateSimulationData({
      conversations: currentConversations
    });
  };

  // Add contextual message from agents for natural conversation flow
  const addContextualMessage = async () => {
    if (conversationLoading) {
      console.log('🚫 Contextual message generation already in progress, skipping...');
      return;
    }
    
    setConversationLoading(true);
    
    try {
      console.log('💬 Adding contextual message for natural conversation flow...');
      
      const response = await axios.post(`${API}/conversation/add-contextual-message`, {}, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      console.log('✅ Contextual message added:', response.data);
      
      // Update the conversation data directly
      if (response.data && response.data.messages) {
        const updatedConversations = Array.isArray(conversations) ? [...conversations] : [];
        
        // Find existing ongoing conversation or add new one
        const existingIndex = updatedConversations.findIndex(
          conv => conv.id === response.data.id
        );
        
        if (existingIndex >= 0) {
          // Update existing conversation
          updatedConversations[existingIndex] = response.data;
        } else {
          // Add new ongoing conversation
          updatedConversations.push(response.data);
        }
        
        // Update via global context
        updateSimulationData({
          conversations: updatedConversations
        });
        
        // Log conversation state for debugging
        if (response.data.conversation_state) {
          const state = response.data.conversation_state;
          console.log('🔄 Conversation state:', state);
          console.log('📊 Goal progress:', state.goal_progress || 0);
          
          // Log round-robin statistics
          if (state.round_robin_stats) {
            console.log('🎯 Round-robin stats:', state.round_robin_stats);
            console.log('⚖️ Participation fairness:', state.participation_fairness || 'Not calculated');
            
            // Show agent participation equality
            const stats = state.round_robin_stats;
            const participation = Object.keys(stats).map(agent => 
              `${agent}: ${stats[agent].message_count} messages`
            ).join(', ');
            console.log('📈 Agent participation:', participation);
          }
        }
        
        // Check if we have a new message with context info
        const newMessages = response.data.messages || [];
        if (newMessages.length > 0) {
          const lastMessage = newMessages[newMessages.length - 1];
          if (lastMessage.context_info) {
            console.log('🎯 Message type:', lastMessage.context_info.conversation_contribution);
            if (lastMessage.context_info.addresses_agent) {
              console.log('👥 Addresses:', lastMessage.context_info.addresses_agent);
            }
            if (lastMessage.context_info.contains_question) {
              console.log('❓ Contains question - other agents should respond');
            }
          }
        }
      }
      
    } catch (error) {
      console.error('Error adding contextual message:', error);
    } finally {
      setConversationLoading(false);
    }
  };

  // ✨ SAFETY ANIMATION STOPPER: Continuously check and stop animations if messages are visible
  useEffect(() => {
    const animationSafetyCheck = setInterval(() => {
      if (loadingAnimations.active && conversations && conversations.length > 0) {
        console.log('🚨 SAFETY STOP: Found conversations while animations active - force stopping!');
        setLoadingAnimations({
          active: false,
          currentStep: 0,
          expectedMessages: 0,
          receivedMessages: 0,
          agentStatuses: {}
        });
      }
    }, 1000); // Check every second

    return () => clearInterval(animationSafetyCheck);
  }, [loadingAnimations.active, conversations]);

  // Helper function to get archetype colors
  const getArchetypeColor = (archetype) => {
    const colors = {
      scientist: 'from-blue-500 to-cyan-500',
      artist: 'from-purple-500 to-pink-500',
      leader: 'from-red-500 to-orange-500',
      skeptic: 'from-gray-500 to-slate-500',
      optimist: 'from-yellow-500 to-amber-500',
      introvert: 'from-indigo-500 to-blue-500',
      adventurer: 'from-green-500 to-emerald-500',
      mediator: 'from-teal-500 to-cyan-500',
      researcher: 'from-violet-500 to-purple-500'
    };
    return colors[archetype] || 'from-gray-500 to-gray-600';
  };

  // ✨ INTERACTIVE LOADING ANIMATION SYSTEM
  const [loadingAnimations, setLoadingAnimations] = useState({
    active: false,
    currentStep: 0,
    expectedMessages: 0,
    receivedMessages: 0,
    agentStatuses: {}
  });

  const loadingSteps = [
    { icon: '🚪', text: 'Agents are entering the room...', duration: 2500 },
    { icon: '🔍', text: 'Examining the scenario...', duration: 2500 },
    { icon: '💭', text: 'Agents are preparing responses...', duration: 2500 },
    { icon: '💬', text: 'Conversation starting...', duration: 2500 }
  ];

  const startInteractiveLoadingAnimations = (expectedMessageCount = 3) => {
    console.log('🎭 Starting interactive loading animations...');
    
    setLoadingAnimations({
      active: true,
      currentStep: 0,
      expectedMessages: expectedMessageCount,
      receivedMessages: 0,
      agentStatuses: {}
    });

    // Cycle through loading steps
    let stepIndex = 0;
    const cycleSteps = () => {
      if (stepIndex < loadingSteps.length) {
        setLoadingAnimations(prev => ({
          ...prev,
          currentStep: stepIndex
        }));
        
        setTimeout(() => {
          stepIndex++;
          if (stepIndex < loadingSteps.length) {
            cycleSteps();
          }
          // Note: Removed agent thinking state transition since we removed that display
        }, loadingSteps[stepIndex].duration);
      }
    };

    cycleSteps();
  };

  const stopLoadingAnimations = () => {
    console.log('🎭 Stopping loading animations...');
    setLoadingAnimations({
      active: false,
      currentStep: 0,
      expectedMessages: 0,
      receivedMessages: 0,
      agentStatuses: {}
    });
  };

  // ✨ PROGRESSIVE MESSAGE STREAMING: Generate conversation with real-time message display
  const generateNewConversation = async (isAuto = false) => {
    // Prevent overlapping conversation generations
    if (conversationLoading) {
      console.log(`🚫 ${isAuto ? 'Auto' : 'Manual'} - Conversation generation already in progress, skipping...`);
      return;
    }
    
    // Prevent multiple auto-generations
    if (isAuto && conversationBuildingRef.current) {
      console.log('🚫 Auto - Skipping generation, messages are still being built');
      return;
    }
    
    setConversationLoading(true);
    
    try {
      const logPrefix = isAuto ? '⏰ Auto' : '💬 Manual';
      console.log(`${logPrefix} - Starting PROGRESSIVE conversation generation...`);
      
      // Start conversation generation (this returns immediately while backend processes)
      const generateResponse = await axios.post(`${API}/conversation/generate`, {}, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      console.log(`${logPrefix} - Conversation generation started:`, generateResponse.data);
      
      if (generateResponse.data && generateResponse.data.type === 'streaming') {
        const conversationId = generateResponse.data.id;
        console.log(`🎯 Starting progressive message polling for conversation: ${conversationId}`);
        
        // ✨ START INTERACTIVE LOADING ANIMATION SYSTEM
        startInteractiveLoadingAnimations(generateResponse.data.message_count || 3);
        
        // Start progressive message polling
        await pollForProgressiveMessages(conversationId, logPrefix);
      } else {
        // Fallback to old method if streaming not available
        console.log(`${logPrefix} - Using fallback method for non-streaming response`);
        if (generateResponse.data && generateResponse.data.messages && generateResponse.data.messages.length > 0) {
          displayConversation(generateResponse.data);
        }
      }
      
      // Reset loading state
      setConversationLoading(false);
      
      // Refresh simulation state
      setTimeout(() => fetchSimulationState(), 1000);
      
    } catch (error) {
      console.error('Error generating conversation:', error);
      setConversationLoading(false);
    }
  };
  
  // ✨ PROGRESSIVE MESSAGE POLLING: Poll for new messages as they're generated
  const pollForProgressiveMessages = async (conversationId, logPrefix = '💬') => {
    let lastTimestamp = null;
    let receivedMessages = [];
    let pollCount = 0;
    const maxPolls = 60; // Poll for up to 2 minutes (60 * 2 seconds)
    
    console.log(`${logPrefix} - Starting progressive message polling...`);
    
    const pollForMessages = async () => {
      try {
        pollCount++;
        
        // Build query params
        const params = new URLSearchParams();
        if (lastTimestamp) {
          params.append('since', lastTimestamp);
        }
        
        // Fetch new streaming messages
        const response = await axios.get(`${API}/messages/stream?${params.toString()}`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        
        const newMessages = response.data.messages || [];
        
        if (newMessages.length > 0) {
          console.log(`${logPrefix} - 📨 Received ${newMessages.length} new messages (Poll ${pollCount})`);
          
          // Add new messages to our collection
          receivedMessages.push(...newMessages);
          
          // Display each new message individually
          for (const message of newMessages) {
            displayProgressiveMessage(message, conversationId);
            
            // Update last timestamp
            if (message.timestamp) {
              lastTimestamp = message.timestamp;
            }
          }
          
          // Check if we have all expected messages
          const lastMessage = newMessages[newMessages.length - 1];
          if (lastMessage.message_index >= lastMessage.total_expected) {
            console.log(`${logPrefix} - ✅ All ${lastMessage.total_expected} messages received! Completing stream...`);
            
            // Complete the message stream on backend
            try {
              await axios.post(`${API}/messages/stream/complete`, null, {
                params: { conversation_id: conversationId },
                headers: { Authorization: `Bearer ${token}` }
              });
              console.log(`${logPrefix} - 🎯 Message stream completed successfully`);
            } catch (completeError) {
              console.error(`${logPrefix} - ⚠️ Error completing message stream:`, completeError);
            }
            
            return; // Stop polling
          }
        } else {
          console.log(`${logPrefix} - ⏳ No new messages (Poll ${pollCount}/${maxPolls})`);
        }
        
        // Continue polling if we haven't exceeded max polls
        if (pollCount < maxPolls) {
          setTimeout(pollForMessages, 2000); // Poll every 2 seconds
        } else {
          console.log(`${logPrefix} - ⏰ Polling timeout after ${maxPolls} attempts`);
          
          // If we have some messages, complete what we have
          if (receivedMessages.length > 0) {
            try {
              await axios.post(`${API}/messages/stream/complete`, null, {
                params: { conversation_id: conversationId },
                headers: { Authorization: `Bearer ${token}` }
              });
              console.log(`${logPrefix} - 🎯 Partial message stream completed with ${receivedMessages.length} messages`);
            } catch (completeError) {
              console.error(`${logPrefix} - ⚠️ Error completing partial stream:`, completeError);
            }
          }
        }
        
      } catch (error) {
        console.error(`${logPrefix} - ❌ Error during progressive polling:`, error);
        
        // Continue polling even if there's an error (network hiccup)
        if (pollCount < maxPolls) {
          setTimeout(pollForMessages, 3000); // Slower retry on error
        }
      }
    };
    
    // Start first poll immediately
    pollForMessages();
  };
  
  // ✨ DISPLAY PROGRESSIVE MESSAGE: Show individual messages as they arrive
  const displayProgressiveMessage = (messageData, conversationId) => {
    console.log(`📨 Displaying progressive message from ${messageData.agent_name}: ${messageData.message.substring(0, 50)}...`);
    console.log(`🎭 Animation status before stopping: active=${loadingAnimations.active}, currentStep=${loadingAnimations.currentStep}`);
    
    // ✨ FORCE STOP ALL ANIMATIONS: Immediately hide all loading animations when any message appears
    console.log('🛑 FORCE STOPPING all loading animations - message appeared!');
    setLoadingAnimations({
      active: false,
      currentStep: 0,
      expectedMessages: 0,
      receivedMessages: 0,
      agentStatuses: {}
    });
    
    console.log('🎭 Animation forcibly stopped - should be hidden now');
    
    // Create conversation structure for this message
    const newMessage = {
      agent_id: messageData.agent_id,
      agent_name: messageData.agent_name,
      message: messageData.message,
      mood: messageData.mood,
      timestamp: messageData.timestamp
    };
    
    // Update global conversation state progressively
    const currentConversations = Array.isArray(conversations) ? [...conversations] : [];
    
    // Find existing progressive conversation or create new one
    const existingIndex = currentConversations.findIndex(conv => 
      conv.id === conversationId && conv.type === 'progressive'
    );
    
    if (existingIndex >= 0) {
      // ✨ ADD MESSAGE TO EXISTING CONVERSATION (not replace)
      const existingConv = { ...currentConversations[existingIndex] };
      existingConv.messages = [...existingConv.messages, newMessage];
      existingConv.message_index = messageData.message_index;
      currentConversations[existingIndex] = existingConv;
      
      console.log(`📝 Added message to existing conversation (${existingConv.messages.length} messages total)`);
    } else {
      // Create new progressive conversation with first message
      const progressiveConversation = {
        id: conversationId,
        type: 'progressive',
        scenario: messageData.scenario,
        scenario_name: messageData.scenario_name,
        messages: [newMessage],
        message_index: messageData.message_index,
        total_expected: messageData.total_expected,
        status: 'progressive',
        created_at: messageData.timestamp
      };
      
      currentConversations.push(progressiveConversation);
      console.log(`🆕 Created new progressive conversation with first message`);
    }
    
    // Update simulation data
    updateSimulationData({
      conversations: currentConversations
    });
    
    console.log(`✅ Progressive message added to conversation ${conversationId} (${messageData.message_index}/${messageData.total_expected})`);
    
    // Note: Animation stopping moved to top of function for immediate response
  };

  const toggleFastForward = async () => {
    try {
      await axios.post(`${API}/simulation/fast-forward`, {}, {
        headers: { Authorization: `Bearer ${token}` }
      });
      // Smart refresh will automatically pick up the fast-forward state change
    } catch (error) {
      console.error('Error fast forwarding:', error);
    }
  };

  const handleSetupFlowComplete = async (setupData) => {
    console.log('🚀 SETUP FLOW COMPLETE - Function called with data:', setupData);
    console.log('🔍 Setup data structure:', JSON.stringify(setupData, null, 2));
    
    try {
      // Show loading state
      alert('Setup completed! Creating agents and saving scenario...');
      
      setSetupFlowData(setupData);
      setSimulationType(setupData.category);
      setSimulationTrack(setupData.track);
      
      // CRITICAL FIX: Check if setupData contains scenario
      if (!setupData.scenario || !setupData.scenario.trim()) {
        console.error('❌ SETUP FLOW ERROR: No scenario provided in setupData');
        console.log('🔍 setupData.scenario:', setupData.scenario);
        alert('Error: No scenario was provided during setup. Please try again.');
        setShowSetupFlow(false);
        return;
      }
      
      // Set scenario from setup flow using the global simulation context
      console.log('📝 Setting scenario:', setupData.scenario);
      console.log('📝 Current scenario before update:', scenario);
      console.log('📝 Current customScenario before update:', customScenario);
      
      // Update scenario states using global context for consistency
      updateSimulationData({
        scenario: setupData.scenario,
        customScenario: setupData.scenario,
        scenarioName: `${setupData.category} - ${setupData.track} Simulation`
      });
      
      console.log('📝 Scenario state updated via global context');
      
      // Update simulation state in backend with new scenario
      console.log('💾 Saving scenario to backend...');
      console.log('🔍 Auth token available:', !!token);
      console.log('🔍 Token preview:', token ? token.substring(0, 20) + '...' : 'No token');
      
      try {
        // Prepare scenario data
        const scenarioText = setupData.scenario;
        const scenarioNameText = `${setupData.category} - ${setupData.track} Simulation`;
        
        // Update states needed for handleSetScenario
        setCustomScenario(scenarioText);
        setScenarioName(scenarioNameText);
        
        // Make direct API call with proper token
        const response = await axios.post(`${API}/simulation/set-scenario`, {
          scenario: scenarioText,
          scenario_name: scenarioNameText
        }, {
          headers: { 
            Authorization: `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        });
        
        console.log('✅ Scenario saved to backend successfully:', response.data);
        
      } catch (error) {
        console.error('❌ Error saving scenario:', error);
        // Continue anyway - we have the scenario in frontend state
        console.log('⚠️ Continuing with frontend scenario state despite backend error');
      }
      
      // Create agents from setup flow using the existing agent creation system
      if (setupData.agents && setupData.agents.length > 0) {
        console.log(`🤖 Creating ${setupData.agents.length} agents from setup flow...`);
        
        let agentsCreated = 0;
        const newAgents = []; // Collect created agents
        
        try {
          // Create each agent using the existing handleCreateAgent function
          for (const agentRequest of setupData.agents) {
            if (agentRequest.status === 'completed') {
              console.log('🔄 Creating agent from prompt:', agentRequest.prompt);
              
              // Extract a better name from the prompt
              const promptWords = agentRequest.prompt.split(' ');
              const possibleName = promptWords.find(word => 
                word.toLowerCase().includes('doctor') || 
                word.toLowerCase().includes('manager') || 
                word.toLowerCase().includes('expert') ||
                word.toLowerCase().includes('analyst') ||
                word.toLowerCase().includes('director') ||
                word.toLowerCase().includes('specialist')
              ) || 'Professional';
              
              const agentData = {
                name: `${possibleName} ${Math.floor(Math.random() * 100)}`,
                archetype: setupData.category === 'business' ? 'leader' : 
                          setupData.category === 'entertainment' ? 'entertainer' : 'researcher',
                goal: agentRequest.prompt.substring(0, 100),
                expertise: agentRequest.prompt.substring(0, 100),
                background: agentRequest.prompt,
                personality: {
                  extroversion: 7,
                  optimism: 8,
                  curiosity: 8,
                  cooperativeness: 8,
                  energy: 7
                }
              };
              
              console.log('📤 Sending agent data to backend:', agentData);
              
              // Use the existing handleCreateAgent function that's already working
              const createdAgent = await handleCreateAgent(agentData);
              if (createdAgent) {
                newAgents.push(createdAgent);
              }
              agentsCreated++;
              console.log(`✅ Created agent ${agentsCreated}: ${agentData.name}`);
            }
          }
          
          // CRITICAL: Update the main agents state with the new agents
          console.log('🔄 Updating main agents state with new agents...');
          
          // Use updateSimulationData to ensure global state consistency
          updateSimulationData({
            agents: [...(agents || []), ...newAgents]
          });
          
          console.log(`✅ Main agents state updated via global context: ${[...(agents || []), ...newAgents].length} total agents`);
          
          console.log(`🎉 Successfully created ${agentsCreated} agents!`);
          
        } catch (error) {
          console.error('❌ Error creating agents from setup flow:', error);
        }
      } else {
        console.log('⚠️ No agents to create from setup flow');
      }
      
      // Close setup flow
      setShowSetupFlow(false);
      
      // Refresh simulation state to ensure all data is properly loaded and UI updates
      console.log('🔄 Refreshing simulation state to ensure UI update...');
      setTimeout(() => {
        fetchSimulationState();
      }, 500);
      
      console.log('✅ Setup completed - should now show Live Conversations');
      console.log('🔍 Final setup state - agents:', agents?.length || 0, 'scenario:', !!setupData.scenario);
      
      // Show success message
      setTimeout(() => {
        alert('Setup completed successfully! Your agents and scenario are ready.');
      }, 1000);
      
      console.log('✨ Setup flow integration completed successfully');
      
    } catch (error) {
      console.error('💥 SETUP FLOW ERROR:', error);
      alert('Error completing setup: ' + error.message);
    }
  };

  const handleSetupFlowCancel = () => {
    setShowSetupFlow(false);
  };

  const startFreshSimulation = async () => {
    // Show confirmation modal instead of immediate action
    setShowStartFreshModal(true);
  };

  const confirmStartFresh = async () => {
    setShowStartFreshModal(false);
    
    try {
      setStartFreshLoading(true);
      
      console.log('🧹 Starting fresh - clearing all data...');
      
      // OPTIMISTIC UPDATE: Clear frontend state immediately for better UX
      setAgents([]);
      setConversations([]);
      setObserverMessages([]);
      setIsRunning(false);
      setIsPaused(false);
      
      // Clear scenario states
      setScenario('');
      setCustomScenario('');
      setScenarioName('');
      setShowSetScenario(false);
      
      // Clear reports and documents from Observatory
      updateSimulationData({
        agents: [],
        conversations: [],
        observerMessages: [],
        reports: [],  // Clear reports
        documents: [],  // Clear documents  
        isRunning: false,
        isPaused: false,
        scenario: '',
        customScenario: '',
        scenarioName: ''
      });
      
      // Show immediate feedback
      showNotification('🧹 Starting fresh cleanup...');
      
      // Show progress feedback after a short delay
      const progressNotification = setTimeout(() => {
        showNotification('🔄 Clearing database collections... This may take up to 60 seconds for large datasets.');
      }, 3000);
      
      // Call the backend reset endpoint to clear everything
      const response = await axios.post(`${API}/simulation/reset`, {}, {
        headers: { Authorization: `Bearer ${token}` },
        timeout: 60000 // 60 second timeout to allow for large dataset cleanup
      });
      
      // Clear the progress notification
      clearTimeout(progressNotification);
      
      if (response.data.success) {
        // Update simulation state from backend
        updateSimulationData({
          simulationState: response.data.state,
          agents: [],
          conversations: [],
          observerMessages: [],
          reports: [],  // Clear reports from Observatory
          documents: [],  // Clear documents from Observatory
          isRunning: false,
          isPaused: false,
          scenario: '',
          customScenario: '',
          scenarioName: '',
          isDataLoaded: true
        });
        
        console.log('✅ Fresh state created - all data cleared successfully');
        console.log(`📊 Cleared ${response.data.cleared_collections || 5} collections`);
        
        // Show success notification
        showNotification('✅ Fresh state created - all data cleared!');
        
        // Trigger Observatory refresh if needed
        if (refreshTrigger) {
          console.log('🔄 Triggering Observatory refresh');
        }
      } else {
        throw new Error(response.data.message || 'Failed to reset simulation');
      }
      
    } catch (error) {
      console.error('❌ Error clearing data:', error);
      
      // Since we already cleared frontend state optimistically, 
      // we don't need to clear it again in the error case
      
      // Show error notification instead of alert
      showNotification('⚠️ Some data may not have been cleared. Please refresh if issues persist.');
      
      // If it's a timeout, the optimistic update is still valuable
      if (error.code === 'ECONNABORTED' || error.message.includes('timeout')) {
        console.log('🕐 Request timed out but optimistic update completed');
        showNotification('✅ UI cleared successfully! Backend cleanup completed in the background.');
      }
      
    } finally {
      setStartFreshLoading(false);
    }
  };

  const handleAddAgent = () => {
    setShowCreateAgentModal(true);
  };

  const handleCreateAgent = async (agentData) => {
    try {
      const response = await axios.post(`${API}/agents`, agentData, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      // Optimistic update: Add agent to UI immediately using global state
      if (response.data) {
        updateSimulationData({
          agents: [...agents, response.data]
        });
        console.log('✅ Agent created and added to UI:', response.data.name);
      }
      
      setShowCreateAgentModal(false);
      
      // Debounced refresh for consistency
      setTimeout(() => fetchSimulationState(), 100);
    } catch (error) {
      console.error('Error creating agent:', error);
    }
  };

  const handleRemoveAgent = async (agentId) => {
    try {
      // Optimistic update: Remove agent from UI immediately using global state
      updateSimulationData({
        agents: agents.filter(agent => agent.id !== agentId)
      });
      
      await axios.delete(`${API}/agents/${agentId}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      console.log('✅ Agent removed from UI and backend');
      
      // Debounced refresh for consistency
      setTimeout(() => fetchSimulationState(), 100);
    } catch (error) {
      console.error('Error removing agent:', error);
      // Revert optimistic update on error
      fetchSimulationState(true);
    }
  };

  const handleClearAllAgents = async () => {
    if (agents.length === 0) return;
    
    // Show custom confirmation modal instead of window.confirm
    setShowClearAllModal(true);
  };

  const confirmClearAllAgents = async () => {
    setShowClearAllModal(false);
    
    try {
      setLoading(true);
      
      // Get all agent IDs
      const agentIds = agents.map(agent => agent.id);
      
      // Call the existing bulk delete endpoint
      const response = await axios.post(`${API}/agents/bulk-delete`, agentIds, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      if (response.data) {
        console.log('✅ All agents cleared successfully:', response.data.message);
        
        // Optimistic update: Clear agents from UI immediately
        setAgents([]);
        
        // Trigger Observatory refresh
        setTimeout(() => fetchSimulationState(), 100);
      }
      
    } catch (error) {
      console.error('❌ Error clearing all agents:', error);
      // Revert optimistic update on error
      fetchSimulationState();
    } finally {
      setLoading(false);
    }
  };

  const handleEditAgent = (agent) => {
    setEditingAgent(agent);
    setShowEditModal(true);
  };

  const handleSaveAgent = async (formData) => {
    try {
      const response = await axios.put(`${API}/agents/${editingAgent.id}`, formData, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      // Optimistic update: Update agent in UI immediately
      if (response.data) {
        setAgents(prevAgents => 
          prevAgents.map(agent => 
            agent.id === editingAgent.id ? response.data : agent
          )
        );
      }
      
      setShowEditModal(false);
      setEditingAgent(null);
      
      // Debounced refresh for consistency
      setTimeout(() => fetchSimulationState(), 100);
    } catch (error) {
      console.error('Error saving agent:', error);
    }
  };

  const getRandomScenario = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API}/simulation/random-scenario`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setCustomScenario(response.data.scenario);
      setScenarioName(response.data.scenario_name);
    } catch (error) {
      console.error('Error getting random scenario:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSetScenario = async () => {
    try {
      setLoading(true);
      
      // Validate inputs
      if (!customScenario.trim() || !scenarioName.trim()) {
        alert('Please enter both a scenario name and description.');
        return;
      }
      
      // Check authentication
      if (!token) {
        alert('Please log in to set scenarios.');
        return;
      }
      
      console.log('🎯 Setting scenario:', { customScenario, scenarioName });
      console.log('🔑 Using token:', token ? 'Token available' : 'No token');
      
      const API = process.env.REACT_APP_BACKEND_URL ? `${process.env.REACT_APP_BACKEND_URL}/api` : 'http://localhost:8001/api';
      
      // Make backend call first to ensure data is saved
      const response = await axios.post(`${API}/simulation/set-scenario`, {
        scenario: customScenario,
        scenario_name: scenarioName
      }, {
        headers: { 
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      
      console.log('✅ Backend call completed, scenario set successfully:', response.data);
      
      // Update global context after successful backend call
      updateSimulationData({
        scenario: customScenario,
        customScenario: customScenario,
        scenarioName: scenarioName
      });
      
      setShowSetScenario(false);
      
      console.log('✅ Frontend state updated with scenario');
      
    } catch (error) {
      console.error('Error setting scenario:', error);
      console.error('Error response:', error.response?.data);
      console.error('Error status:', error.response?.status);
      
      if (error.response?.status === 401) {
        alert('Authentication failed. Please log in again.');
        // Try to refresh the token or redirect to login
        window.location.reload();
      } else if (error.response?.status === 400) {
        alert('Invalid scenario data. Please check your inputs.');
      } else {
        alert(`Failed to set scenario: ${error.response?.data?.detail || error.message}`);
      }
    } finally {
      setLoading(false);
    }
  };

  const handleVoiceInput = () => {
    if (!isRecording) {
      setIsRecording(true);
      // Voice recording logic would go here
      setTimeout(() => {
        setIsRecording(false);
        setCustomScenario("A team of researchers discovers an unexpected signal from deep space and must decide how to respond.");
      }, 3000);
    } else {
      setIsRecording(false);
    }
  };

  // Fetch conversations only - with aggressive animation stopping
  const fetchConversationsOnly = async () => {
    // Prevent concurrent conversation updates that cause message jumping
    if (conversationUpdateRef.current) {
      console.log('🔒 Conversation update in progress, skipping duplicate request');
      return;
    }
    
    try {
      conversationUpdateRef.current = true;
      
      // Store scroll position before DOM update
      const conversationContainer = document.querySelector('[data-conversation-container="true"]');
      const scrollTop = conversationContainer ? conversationContainer.scrollTop : 0;
      const scrollLeft = conversationContainer ? conversationContainer.scrollLeft : 0;

      // Use /conversations/active endpoint to get only current simulation conversations
      const conversationsResponse = await axios.get(`${API}/conversations/active`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      // Update via global context - with validation to prevent corrupted data
      const conversationsData = conversationsResponse.data || [];
      
      if (conversationsData && conversationsData.length > 0) {
        console.log(`📊 Fetched ${conversationsData.length} conversations - STOPPING ANIMATIONS AGGRESSIVELY!`);
        
        // ✨ AGGRESSIVE ANIMATION STOP: Stop animations whenever conversations are fetched
        setLoadingAnimations({
          active: false,
          currentStep: 0,
          expectedMessages: 0,
          receivedMessages: 0,
          agentStatuses: {}
        });
        
        console.log('🛑 FORCED animation stop due to conversation fetch');
        
        // Update conversations
        updateSimulationData({
          conversations: conversationsData
        });
      }
      
      // Restore scroll position after DOM update
      // Use multiple attempts with increasing delays for maximum reliability
      const restoreScrollPosition = () => {
        const conversationContainer = document.querySelector('[data-conversation-container="true"]');
        if (conversationContainer && (scrollTop > 0 || scrollLeft > 0)) {
          conversationContainer.scrollTop = scrollTop;
          conversationContainer.scrollLeft = scrollLeft;
          console.log('🔒 Polling: Restored scroll position to:', scrollTop, scrollLeft);
        }
      };
      
      // Multiple restoration attempts for maximum reliability
      setTimeout(restoreScrollPosition, 100);
      setTimeout(restoreScrollPosition, 300);
      setTimeout(restoreScrollPosition, 500);
      
      console.log('✅ Conversations refreshed - Count:', conversationsData.length);
    } catch (error) {
      console.error('Error fetching conversations:', error);
    } finally {
      conversationUpdateRef.current = false;
    }
  };

  const handleSendObserverMessage = async () => {
    if (!observerMessage.trim()) return;

    const messageToSend = observerMessage;

    try {
      setIsObserverLoading(true);
      
      // Clear input immediately for better UX
      setObserverMessage('');

      // Send observer message to backend - IMMEDIATE DISPLAY VERSION
      const response = await axios.post(`${API}/observer/send-message`, {
        observer_message: messageToSend
      }, {
        headers: { Authorization: `Bearer ${token}` }
      });

      // IMMEDIATE: Observer message is now stored and visible immediately
      // Agent responses will be generated progressively in background
      console.log('✅ Observer message sent immediately:', response.data.observer_message);
      console.log('🔄 Agent responses generating in background...');

      // Refresh conversations immediately to show the observer message
      // (Agent responses will appear as they're generated in background)
      setTimeout(() => {
        fetchConversationsOnly(); // Immediate refresh to show observer message
      }, 100);

      // Also refresh state to get any updates
      setTimeout(() => fetchSimulationState(), 300);
      
    } catch (error) {
      console.error('Error sending observer message:', error);
      // Restore input on error
      setObserverMessage(messageToSend);
    } finally {
      setIsObserverLoading(false);
    }
  };

  const handleGenerateReport = async () => {
    try {
      setReportLoading(true);
      setReportData(''); // Clear previous report
      
      // Generate daily report with manual flag
      const response = await axios.post(`${API}/simulation/generate-daily-report`, {
        manual: true
      }, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      if (response.data.success) {
        setReportData(response.data.report.content || 'No report data available');
        setSelectedReport(response.data.report); // Set the selected report for proper header display
        setReportCardVisible(true); // Show the report card
        
        // Refresh simulation data to show the new report in the list
        setTimeout(() => fetchSimulationState(), 1000);
        
        showNotification('✅ Daily report generated successfully!');
      } else {
        throw new Error(response.data.message || 'Failed to generate report');
      }
    } catch (error) {
      console.error('Error generating daily report:', error);
      setReportData('Error generating report. Please try again.');
      setReportCardVisible(true);
      showNotification('❌ Failed to generate daily report');
    } finally {
      setReportLoading(false);
    }
  };

  // Enhanced auto report toggle handlers for both daily and weekly reports
  const handleAutoReportToggle = async () => {
    try {
      const newStatus = !autoReportEnabled;
      setAutoReportEnabled(newStatus);
      
      // Call backend to enable/disable auto weekly reports
      await axios.post(`${API}/simulation/auto-weekly-report`, {
        enabled: newStatus
      }, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      console.log(`Auto weekly reports ${newStatus ? 'enabled' : 'disabled'}`);
    } catch (error) {
      console.error('Error toggling auto weekly report:', error);
      // Revert on error
      setAutoReportEnabled(!autoReportEnabled);
    }
  };

  const handleAutoDailyReportToggle = async () => {
    try {
      const newStatus = !autoDailyReportEnabled;
      setAutoDailyReportEnabled(newStatus);
      
      // Call backend to enable/disable auto daily reports
      await axios.post(`${API}/simulation/auto-daily-report`, {
        enabled: newStatus
      }, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      console.log(`Auto daily reports ${newStatus ? 'enabled' : 'disabled'}`);
    } catch (error) {
      console.error('Error toggling auto daily report:', error);
      // Revert on error
      setAutoDailyReportEnabled(!autoDailyReportEnabled);
    }
  };

  const performSearch = (term) => {
    if (!term.trim()) {
      setSearchResults([]);
      setCurrentSearchIndex(0);
      searchRefs.current = []; // Clear refs when clearing search
      return;
    }

    const results = [];
    
    // Search regular conversations
    (Array.isArray(conversations) ? conversations : []).forEach((conversation, conversationIndex) => {
      if (conversation.messages) {
        conversation.messages.forEach((message, messageIndex) => {
          if (message.message.toLowerCase().includes(term.toLowerCase())) {
            results.push({
              type: 'conversation',
              conversationIndex,
              messageIndex,
              message
            });
          }
        });
      }
    });

    setSearchResults(results);
    setCurrentSearchIndex(0);
    searchRefs.current = new Array(results.length); // Initialize refs array with correct length
  };

  const navigateSearch = (direction) => {
    if (searchResults.length === 0) return;

    let newIndex = currentSearchIndex;
    if (direction === 'next') {
      newIndex = (currentSearchIndex + 1) % searchResults.length;
    } else {
      newIndex = currentSearchIndex === 0 ? searchResults.length - 1 : currentSearchIndex - 1;
    }
    
    setCurrentSearchIndex(newIndex);
    
    // Enhanced scrolling with fallback
    setTimeout(() => {
      const targetElement = searchRefs.current[newIndex];
      if (targetElement) {
        targetElement.scrollIntoView({ 
          behavior: 'smooth', 
          block: 'center',
          inline: 'nearest'
        });
        
        // Fallback: Try scrolling the conversation container directly
        const conversationContainer = document.querySelector('[data-conversation-container="true"]');
        if (conversationContainer) {
          const elementRect = targetElement.getBoundingClientRect();
          const containerRect = conversationContainer.getBoundingClientRect();
          const scrollTop = conversationContainer.scrollTop + elementRect.top - containerRect.top - containerRect.height / 2;
          conversationContainer.scrollTo({ top: scrollTop, behavior: 'smooth' });
        }
      }
    }, 100); // Small delay to ensure DOM is updated
  };

  const highlightSearchTerm = (text, term) => {
    if (!term) return text;
    
    const regex = new RegExp(`(${term})`, 'gi');
    const parts = text.split(regex);
    
    return parts.map((part, index) => 
      regex.test(part) ? 
        <span key={index} className="bg-yellow-400 text-black px-1 rounded">{part}</span> : 
        part
    );
  };

  // Helper function to render markdown bold text
  const renderMarkdownBold = (text) => {
    if (!text) return '';
    
    // Split text by **bold** patterns and render accordingly
    const parts = text.split(/(\*\*[^*]+\*\*)/g);
    
    return parts.map((part, index) => {
      if (part.startsWith('**') && part.endsWith('**')) {
        // Remove the ** and render as bold
        const boldText = part.slice(2, -2);
        return <strong key={index} className="font-bold">{boldText}</strong>;
      }
      return part;
    });
  };

  // Helper function to calculate day and time period - SIMPLIFIED SYSTEM
  // Each agent sends 9 messages per time period (1 message per conversation)
  // With 3 agents = 27 messages per time period (Morning/Afternoon/Evening)
  const calculateDayAndTime = (totalMessages, agentCount) => {
    if (totalMessages === 0 || agentCount === 0) return { day: 1, period: "Morning" };
    
    // Simple calculation: 9 messages per agent per time period
    // Since we now have 1 message per agent per conversation, we need 9 conversations per agent
    const messagesPerTimePeriod = agentCount * 9;
    const timePeriodNumber = Math.floor(totalMessages / messagesPerTimePeriod);
    
    const day = Math.floor(timePeriodNumber / 3) + 1;
    const periods = ["Morning", "Afternoon", "Evening"];
    const period = periods[timePeriodNumber % 3];
    
    return { day, period };
  };

  // Helper function to render markdown bold text with search highlighting
  const renderMarkdownBoldWithSearch = (text, searchTerm) => {
    if (!text) return '';
    
    // First handle bold markdown, then search highlighting
    const parts = text.split(/(\*\*[^*]+\*\*)/g);
    
    return parts.map((part, index) => {
      if (part.startsWith('**') && part.endsWith('**')) {
        // Remove the ** and render as bold
        const boldText = part.slice(2, -2);
        return <strong key={index} className="font-bold">{highlightSearchTerm(boldText, searchTerm)}</strong>;
      }
      return highlightSearchTerm(part, searchTerm);
    });
  };

  return (
    <>
      <div className="relative">
        {/* Notification Bar - Enhanced with Scenario Display */}
        <div className="mb-1 h-[2rem] flex items-center justify-center -mt-1">
          <AnimatePresence mode="wait">
            {/* Show scenario info when scenario is set */}
            {scenarioName && (
              <motion.div
                key="scenario-notification"
                initial={{ opacity: 0, x: 300, scale: 0.95 }}
                animate={{ opacity: 1, x: 0, scale: 1 }}
                exit={{ opacity: 0, x: -300, scale: 0.95 }}
                transition={{
                  type: "spring",
                  stiffness: 120,
                  damping: 25,
                  mass: 1.2
                }}
                style={{ willChange: 'transform, opacity' }}
                className="flex items-center space-x-2 text-white text-lg font-semibold"
              >
                <span>📋 {scenarioName}</span>
                <button
                  onClick={() => {
                    // Accordion behavior: Always close Generate Report when expanding Set Scenario
                    if (scenarioExpanded) {
                      // If already expanded, just collapse it
                      setScenarioExpanded(false);
                    } else {
                      // If collapsed, expand it and ensure Generate Report is closed
                      setShowReport(false);
                      setScenarioExpanded(true);
                    }
                  }}
                  className="text-white/80 hover:text-white transition-colors duration-150 p-1 rounded-full hover:bg-white/10"
                  title={scenarioExpanded ? "Collapse scenario details" : "Expand scenario details"}
                >
                  <svg 
                    className={`w-4 h-4 transition-transform duration-300 ease-out ${scenarioExpanded ? 'rotate-180' : ''}`}
                    fill="none" 
                    stroke="currentColor" 
                    viewBox="0 0 24 24"
                    style={{ willChange: 'transform' }}
                  >
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                  </svg>
                </button>
              </motion.div>
            )}
            
            {/* Show welcome message when no scenario is set */}
            {!scenarioName && notificationVisible && (
              <motion.div
                key="welcome-notification"
                initial={{ opacity: 0, x: 300, scale: 0.95 }}
                animate={{ opacity: 1, x: 0, scale: 1 }}
                exit={{ opacity: 0, x: -300, scale: 0.95 }}
                transition={{
                  type: "spring",
                  stiffness: 120,
                  damping: 25,
                  mass: 1.2
                }}
                style={{ willChange: 'transform, opacity' }}
                className="text-white text-lg font-semibold"
              >
                {notificationText}
              </motion.div>
            )}
          </AnimatePresence>
        </div>
        
        {/* Expanded Scenario Details */}
        <AnimatePresence>
          {scenarioExpanded && scenarioName && (
            <motion.div
              initial={{ opacity: 0, scaleY: 0, transformOrigin: 'top' }}
              animate={{ opacity: 1, scaleY: 1, transformOrigin: 'top' }}
              exit={{ opacity: 0, scaleY: 0, transformOrigin: 'top' }}
              transition={{
                type: "spring",
                stiffness: 400,
                damping: 35,
                mass: 0.6
              }}
              style={{ willChange: 'transform, opacity' }}
              className="mb-4 bg-white/10 backdrop-blur-lg rounded-xl p-6 border border-white/20 shadow-lg overflow-hidden"
            >
              <div className="flex items-start space-x-4">
                <div className="text-3xl flex-shrink-0">📋</div>
                <div className="flex-1 min-w-0">
                  <h4 className="text-xl font-bold text-white mb-4 border-b border-white/20 pb-2">
                    {scenarioName}
                  </h4>
                  <div className="max-h-96 overflow-y-auto pr-2 custom-scrollbar">
                    {formatScenarioText(scenario || customScenario)}
                  </div>
                </div>
                <button
                  onClick={() => setScenarioExpanded(false)}
                  className="text-white/60 hover:text-white transition-colors p-2 rounded-full hover:bg-white/10 flex-shrink-0"
                  title="Close scenario details"
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* Main Grid Layout - 3 Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-4 md:gap-5 lg:gap-6 xl:gap-6 2xl:gap-8 mt-1">
        
        {/* Agent List Section - 25% width on large screens (Left Position) */}
        <div className="lg:col-span-1">
          <div className="bg-white/10 backdrop-blur-lg rounded-xl p-6 h-[600px] flex flex-col">
            <div className="flex justify-between items-center mb-4">
              <div className="flex items-center space-x-2">
                <h3 className="text-lg font-bold text-white">🤖 Agent List</h3>
                <div className="flex items-center space-x-1">
                  <div className={`w-2 h-2 rounded-full ${agents.length > 0 ? 'bg-green-400' : 'bg-gray-400'}`}></div>
                  <span className="text-white/60 text-sm">{agents.length}</span>
                </div>
              </div>
              <div className="flex items-center space-x-2">
                
                {/* Clear All button - only show when there are agents */}
                {agents.length > 0 && (
                  <button
                    onClick={handleClearAllAgents}
                    disabled={loading}
                    className="w-6 h-6 bg-red-600 hover:bg-red-700 disabled:bg-gray-600 text-white rounded-full flex items-center justify-center transition-colors text-xs"
                    title={`Clear all ${agents.length} agents`}
                  >
                    ✕
                  </button>
                )}
                
                <button
                  onClick={() => {
                    // Navigate to Agent Library tab using the setActiveTab prop
                    if (setActiveTab) {
                      setActiveTab('agents');
                    }
                  }}
                  className="w-6 h-6 bg-green-600 hover:bg-green-700 text-white rounded-full flex items-center justify-center transition-colors text-sm"
                  title="Open Agent Library"
                >
                  +
                </button>
              </div>
            </div>
            
            {/* Agent List Display with Scroll */}
            <div className="flex-1 overflow-y-auto space-y-3">
              {agents.length > 0 ? (
                <>
                  {agents.map((agent) => (
                    <div
                      key={agent.id}
                      className="bg-white/5 rounded-lg p-4 border border-white/10 hover:border-white/20 transition-colors group"
                    >
                      <div className="flex items-start justify-between mb-2">
                        <div className="flex items-center space-x-3">
                          <div className="w-10 h-10 rounded-full bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center flex-shrink-0 overflow-hidden">
                            {agent.avatar_url ? (
                              <img 
                                src={agent.avatar_url} 
                                alt={agent.name} 
                                className="w-full h-full object-cover"
                                loading="eager"
                                style={{
                                  imageRendering: 'crisp-edges',
                                  minWidth: '100%',
                                  minHeight: '100%'
                                }}
                                onError={(e) => {
                                  e.target.style.display = 'none';
                                  e.target.nextSibling.style.display = 'flex';
                                }}
                              />
                            ) : null}
                            <span 
                              className="text-white text-sm font-semibold absolute"
                              style={{
                                display: agent.avatar_url ? 'none' : 'flex'
                              }}
                            >
                              {agent.name?.charAt(0) || '🤖'}
                            </span>
                          </div>
                          <div>
                            <h4 className="text-white font-medium text-sm">{agent.name}</h4>
                            <p className="text-white/60 text-xs capitalize">{agent.archetype}</p>
                          </div>
                        </div>
                        
                        <div className="flex items-center space-x-1 opacity-0 group-hover:opacity-100 transition-opacity">
                          <button
                            onClick={() => handleEditAgent(agent)}
                            className="w-6 h-6 text-white/60 hover:text-white rounded transition-colors flex items-center justify-center text-xs"
                            title="Edit Agent"
                          >
                            ✏️
                          </button>
                          <button
                            onClick={() => handleRemoveAgent(agent.id)}
                            className="w-6 h-6 text-white/60 hover:text-red-400 rounded transition-colors flex items-center justify-center text-xs"
                            title="Remove Agent"
                          >
                            🗑️
                          </button>
                        </div>
                      </div>
                      
                      <p className="text-white/70 text-xs line-clamp-2 mb-2">
                        {agent.background || agent.expertise}
                      </p>
                    </div>
                  ))}
                </>
              ) : (
                <div className="text-center py-8">
                  <p className="text-white/60 text-sm mb-4">No Agents in List</p>
                  <p className="text-white/40 text-xs mb-4">Click + to add agents from library</p>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Live Conversations Section OR Setup Card - 50% width on large screens (Middle Position) */}
        <div className="col-span-1 sm:col-span-1 md:col-span-1 lg:col-span-2 xl:col-span-2 2xl:col-span-2">
          {/* Show Setup Card if user needs setup, otherwise show Live Conversations */}
          {(!agents || agents.length === 0) || !scenarioName || scenarioName.trim() === '' || scenarioName === 'General Discussion' ? (
            /* Setup Card - Simple & Beautiful */
            <div className="relative bg-gradient-to-br from-purple-600/20 to-blue-600/20 backdrop-blur-lg rounded-xl h-[600px] flex items-center justify-center border border-purple-500/30 overflow-hidden">
              
              {/* Simple Background Glow */}
              <div className="absolute inset-0">
                <div className="absolute top-1/4 left-1/4 w-64 h-64 bg-purple-500/10 rounded-full blur-3xl"></div>
                <div className="absolute bottom-1/4 right-1/4 w-48 h-48 bg-blue-500/10 rounded-full blur-3xl"></div>
              </div>

              {/* Main Content */}
              <div className="relative z-10 text-center">
                
                {/* Beautiful Observer Eye Icon */}
                <div className="mb-12">
                  {/* Just the Eye - Proper 30% size reduction (32->22, closest is w-20 h-20 = 80px) */}
                  <div className="relative w-20 h-20 mx-auto">
                    {/* Eye circle */}
                    <div className="w-20 h-20 bg-white rounded-full flex items-center justify-center shadow-2xl">
                      {/* Cursor-tracking pupil with default animation */}
                      <div 
                        id="observer-pupil"
                        className="w-5 h-5 bg-black rounded-full transition-transform duration-100 ease-out animate-observer-eye"
                      ></div>
                    </div>
                  </div>
                </div>

                {/* Simple Message */}
                <div className="mb-12">
                  <h2 className="text-3xl font-light text-white mb-4">
                    Ready to observe?
                  </h2>
                  <p className="text-white/60 text-lg">
                    Create your simulation
                  </p>
                </div>

                {/* Beautiful Button */}
                <button
                  onClick={() => setShowSetupFlow(true)}
                  className="group relative bg-white/5 hover:bg-white/10 backdrop-blur border border-white/20 hover:border-white/40 text-white px-16 py-5 rounded-full text-lg font-medium transition-all duration-500 hover:scale-105"
                >
                  <span className="flex items-center space-x-3">
                    <span>Start</span>
                    <div className="w-2 h-2 bg-white rounded-full group-hover:w-6 group-hover:h-6 transition-all duration-500 flex items-center justify-center">
                      <svg className="w-3 h-3 text-black opacity-0 group-hover:opacity-100 transition-opacity duration-300" fill="currentColor" viewBox="0 0 24 24">
                        <path d="M8 5v14l11-7z"/>
                      </svg>
                    </div>
                  </span>
                </button>
              </div>
            </div>
          ) : (
            /* Original Live Conversations Card */
            <div className="bg-white/10 backdrop-blur-lg rounded-xl p-6 h-[600px] flex flex-col">
              <h3 className="text-lg font-bold text-white mb-4">💬 Live Conversations</h3>
              <div className="flex-1 overflow-y-auto" data-conversation-container="true">
                {/* ✨ INTERACTIVE LOADING ANIMATIONS - NUCLEAR SAFETY: Never show if conversations exist */}
                {loadingAnimations.active && (!conversations || conversations.length === 0) && (
                  <div className="space-y-4 mb-6">
                    {/* Main Loading Step */}
                    {loadingAnimations.currentStep >= 0 && loadingAnimations.currentStep < loadingSteps.length && (
                      <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -20 }}
                        className="bg-gradient-to-r from-purple-500/20 to-blue-500/20 backdrop-blur-sm rounded-lg border border-purple-400/30 p-4"
                      >
                        <div className="flex items-center space-x-3">
                          <div className="text-2xl animate-pulse">
                            {loadingSteps[loadingAnimations.currentStep].icon}
                          </div>
                          <div className="flex-1">
                            <div className="text-white font-medium">
                              {loadingSteps[loadingAnimations.currentStep].text}
                            </div>
                            <div className="flex space-x-1 mt-2">
                              {[...Array(3)].map((_, i) => (
                                <div
                                  key={i}
                                  className={`w-2 h-2 bg-purple-400 rounded-full animate-pulse`}
                                  style={{
                                    animationDelay: `${i * 0.2}s`,
                                    animationDuration: '0.8s'
                                  }}
                                />
                              ))}
                            </div>
                          </div>
                        </div>
                      </motion.div>
                    )}
                  </div>
                )}

                {conversations && conversations.length > 0 ? (
                  <div className="space-y-3">
                    {conversations.map((conversation, index) => (
                      <div key={conversation.id || index}>
                        {/* Round Header */}
                        <div className="text-center mb-3">
                          <span className="bg-white/10 text-white/70 text-xs px-3 py-1 rounded-full">
                            Day {conversation.round || index + 1} - {conversation.time_period || 'Morning'}
                          </span>
                        </div>
                        
                        {/* Messages */}
                        <div className="space-y-3">
                          {conversation.messages && conversation.messages.map((message, msgIndex) => {
                            // Find the agent data for this message to get avatar
                            const agent = agents.find(a => a.name === message.agent_name || a.id === message.agent_id);
                            
                            return (
                              <div key={msgIndex} className="bg-white/5 backdrop-blur-sm rounded-lg border-l-4 border-purple-400 p-4 hover:bg-white/8 transition-colors duration-200">
                                <div className="flex items-start space-x-3">
                                  {/* Agent Avatar */}
                                  <div className="w-10 h-10 rounded-full overflow-hidden flex-shrink-0 shadow-lg">
                                    {agent && agent.avatar_url ? (
                                      <img 
                                        src={agent.avatar_url} 
                                        alt={message.agent_name}
                                        className="w-full h-full object-cover"
                                        onError={(e) => {
                                          // Fallback to gradient circle if image fails to load
                                          e.target.style.display = 'none';
                                          e.target.nextSibling.style.display = 'flex';
                                        }}
                                      />
                                    ) : null}
                                    {/* Fallback gradient circle */}
                                    <div 
                                      className="w-full h-full bg-gradient-to-br from-purple-400 to-blue-400 flex items-center justify-center"
                                      style={{display: agent && agent.avatar_url ? 'none' : 'flex'}}
                                    >
                                      <span className="text-white text-sm font-semibold">
                                        {message.agent_name ? message.agent_name.charAt(0) : 'A'}
                                      </span>
                                    </div>
                                  </div>
                                  
                                  {/* Message Content */}
                                  <div className="flex-1 min-w-0">
                                    <div className="flex items-center justify-between mb-2">
                                      <div className="flex items-center space-x-2">
                                        <span className="text-white font-semibold text-sm">
                                          {message.agent_name || 'Agent'}
                                        </span>
                                        {message.mood && (
                                          <span className="text-white/60 text-xs px-2 py-1 bg-white/10 rounded-full">
                                            {message.mood}
                                          </span>
                                        )}
                                      </div>
                                      <span className="text-white/50 text-xs flex-shrink-0">
                                        {message.timestamp ? 
                                          new Date(message.timestamp).toLocaleTimeString([], {hour: '2-digit', minute: '2-digit'}) : 
                                          new Date().toLocaleTimeString([], {hour: '2-digit', minute: '2-digit'})
                                        }
                                      </span>
                                    </div>
                                    <p className="text-white/90 text-sm leading-relaxed">
                                      {message.message || message.content}
                                    </p>
                                  </div>
                                </div>
                              </div>
                            );
                          })}
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-8">
                    {simulationLoading ? (
                      <div className="space-y-4">
                        <div className="w-12 h-12 border-2 border-white/30 border-t-white rounded-full animate-spin mx-auto"></div>
                        <p className="text-white/60 text-sm">Starting simulation...</p>
                      </div>
                    ) : isRunning ? (
                      <div className="space-y-4">
                        <div className="w-12 h-12 border-2 border-white/30 border-t-white rounded-full animate-spin mx-auto"></div>
                        <p className="text-white/60 text-sm">Conversations in progress...</p>
                      </div>
                    ) : (
                      <p className="text-white/60 text-sm">Live conversations will appear here</p>
                    )}
                  </div>
                )}
              </div>
              
              {/* Observer Chat Interface - Inside Live Conversations card */}
              {showObserverChat && (
                <div className="mt-4 pt-4 border-t border-white/20">
                  {/* Observer Header */}
                  <div className="flex items-center space-x-3 mb-4">
                    <div className="w-8 h-8 rounded-full bg-gradient-to-br from-yellow-400 to-orange-500 flex items-center justify-center shadow-lg">
                      <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 616 0z" />
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                      </svg>
                    </div>
                    <div className="flex-1">
                      <h4 className="text-white font-semibold text-sm">Observer Control</h4>
                      <p className="text-white/60 text-xs">Guide the conversation</p>
                    </div>
                  </div>
                  
                  {/* Observer Input */}
                  <div className="flex space-x-2">
                    <input
                      type="text"
                      value={observerMessage}
                      onChange={(e) => setObserverMessage(e.target.value)}
                      placeholder="Type your guidance..."
                      className="flex-1 bg-white/10 border border-white/20 rounded-lg px-3 py-2 text-white placeholder-white/40 text-sm focus:outline-none focus:border-yellow-400/50 focus:bg-white/15"
                      onKeyPress={(e) => {
                        if (e.key === 'Enter' && !isObserverLoading) {
                          handleSendObserverMessage();
                        }
                      }}
                    />
                    <button
                      onClick={handleSendObserverMessage}
                      disabled={isObserverLoading || !observerMessage.trim()}
                      className="bg-gradient-to-r from-yellow-400 to-orange-500 hover:from-yellow-500 hover:to-orange-600 disabled:from-gray-600 disabled:to-gray-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition-all disabled:cursor-not-allowed flex items-center space-x-1"
                    >
                      {isObserverLoading ? (
                        <svg className="w-4 h-4 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                        </svg>
                      ) : (
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                        </svg>
                      )}
                    </button>
                  </div>
                  
                  <div className="mt-2 text-xs text-white/40">
                    Press Enter to send • Guides agent responses
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Control Buttons - Only show when properly set up */}
          {scenarioName && scenarioName !== 'General Discussion' && agents && agents.length >= 2 && (
            <div className="flex justify-center mt-5">
              <div className="flex items-center space-x-7">
                {/* Play/Pause Button */}
                <button
                  onClick={playPauseSimulation}
                  disabled={simulationLoading || !scenarioName || agents.length < 2}
                  className={`w-8 h-8 rounded-full flex items-center justify-center transition-all duration-300 transform hover:scale-110 shadow-xl ${
                    simulationLoading 
                      ? 'bg-gray-500 cursor-not-allowed'
                      : isRunning
                      ? 'bg-orange-500 hover:bg-orange-600 shadow-orange-500/30' 
                      : 'bg-green-500 hover:bg-green-600 shadow-green-500/30'
                  } text-white disabled:bg-gray-500 disabled:cursor-not-allowed`}
                  title={simulationLoading ? 'Generating conversations... (30-60 seconds)' : isRunning ? 'Pause Simulation' : 'Start Simulation'}
                >
                  {simulationLoading ? (
                    <div className="w-3 h-3 border border-white border-t-transparent rounded-full animate-spin"></div>
                  ) : isRunning ? (
                    <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
                      <path d="M6 4h4v16H6V4zm8 0h4v16h-4V4z"/>
                    </svg>
                  ) : (
                    <svg className="w-4 h-4 ml-0.5" fill="currentColor" viewBox="0 0 24 24">
                      <path d="M8 5v14l11-7z"/>
                    </svg>
                  )}
                </button>

                {/* Observer Button */}
                <button
                  onClick={() => setShowObserverChat(!showObserverChat)}
                  className={`w-8 h-8 rounded-full flex items-center justify-center transition-all duration-300 transform hover:scale-110 shadow-xl ${
                    showObserverChat
                      ? 'bg-yellow-600 hover:bg-yellow-700 shadow-yellow-500/30' 
                      : 'bg-yellow-500 hover:bg-yellow-600 shadow-yellow-500/30'
                  } text-white`}
                  title={showObserverChat ? 'Hide Observer Chat' : 'Show Observer Chat'}
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 616 0z" />
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                  </svg>
                </button>

                {/* Fast Forward Button */}
                <button
                  onClick={toggleFastForward}
                  disabled={simulationLoading || !scenarioName || agents.length < 2}
                  className="w-8 h-8 rounded-full bg-blue-500 hover:bg-blue-600 text-white flex items-center justify-center transition-all duration-300 transform hover:scale-110 shadow-xl shadow-blue-500/30 disabled:bg-gray-500 disabled:cursor-not-allowed"
                  title="Fast Forward (Generate Next Round)"
                >
                  <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M4 18l8.5-6L4 6v12zm9-12v12l8.5-6L13 6z"/>
                  </svg>
                </button>

                {/* Fresh Start Button */}
                <button
                  onClick={startFreshSimulation}
                  disabled={simulationLoading}
                  className="w-8 h-8 rounded-full bg-red-500 hover:bg-red-600 text-white flex items-center justify-center transition-all duration-300 transform hover:scale-110 shadow-xl shadow-red-500/30 disabled:bg-gray-500 disabled:cursor-not-allowed"
                  title="Start Fresh (Clear All Data)"
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                  </svg>
                </button>
              </div>
            </div>
          )}
        </div>
        
        {/* Scenario Setup Section - 25% width on large screens (Right Position) */}
        <div className="lg:col-span-1">
          <div className="bg-white/10 backdrop-blur-lg rounded-xl p-6 h-[600px] flex flex-col">
            <div className="flex justify-between items-center mb-2">
              <h3 className="text-lg font-bold text-white">🎛️ Control Room</h3>
            </div>
            
            {/* Statistics Counters Row - Perfectly aligned with Live Conversations search bar */}
            <div className="flex items-center justify-center space-x-2 mb-6 mt-2">
              {/* Message Count Display */}
              <div className="bg-white/10 border border-white/20 rounded-2xl px-2 py-1 hover:bg-white/15 transition-colors group relative">
                <div className="flex items-center justify-center space-x-1">
                  <svg className="w-4 h-4 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                  </svg>
                  <span className="text-white text-sm font-medium">
                    {(() => {
                      // Calculate total messages across all conversations
                      const totalMessages = Array.isArray(conversations) ? 
                        conversations.reduce((total, conv) => {
                          const messages = conv.messages || [];
                          // Filter out observer messages (they don't count toward progression)
                          const agentMessages = messages.filter(msg => msg.agent_id !== "observer");
                          return total + agentMessages.length;
                        }, 0) : 0;
                      
                      return totalMessages;
                    })()}
                  </span>
                </div>
                
                {/* Tooltip on hover */}
                <div className="absolute top-full left-1/2 transform -translate-x-1/2 mt-2 w-48 bg-gray-900/95 backdrop-blur-sm rounded-lg p-3 border border-white/20 shadow-lg opacity-0 group-hover:opacity-100 transition-opacity duration-200 pointer-events-none z-50">
                  <div className="text-white/80 text-xs space-y-1">
                    <div className="font-medium text-white mb-1">Message Breakdown:</div>
                    <div>Total Conversations: {Array.isArray(conversations) ? conversations.length : 0}</div>
                    <div>
                      Agent Messages: {(() => {
                        const totalMessages = Array.isArray(conversations) ? 
                          conversations.reduce((total, conv) => {
                            const messages = conv.messages || [];
                            const agentMessages = messages.filter(msg => msg.agent_id !== "observer");
                            return total + agentMessages.length;
                          }, 0) : 0;
                        return totalMessages;
                      })()}
                    </div>
                    <div>
                      Observer Messages: {(() => {
                        const observerMessages = Array.isArray(conversations) ? 
                          conversations.reduce((total, conv) => {
                            const messages = conv.messages || [];
                            const observerMsgs = messages.filter(msg => msg.agent_id === "observer");
                            return total + observerMsgs.length;
                          }, 0) : 0;
                        return observerMessages;
                      })()}
                    </div>
                    <div className="text-blue-400 mt-1">
                      {(() => {
                        const agentCount = Array.isArray(agents) ? agents.length : 3;
                        const totalMessages = Array.isArray(conversations) ? 
                          conversations.reduce((total, conv) => {
                            const messages = conv.messages || [];
                            const agentMessages = messages.filter(msg => msg.agent_id !== "observer");
                            return total + agentMessages.length;
                          }, 0) : 0;
                        const messagesPerPeriod = agentCount * 9;
                        const currentPeriodMessages = totalMessages % messagesPerPeriod;
                        const messagesUntilNext = messagesPerPeriod - currentPeriodMessages;
                        
                        // Determine what we're progressing to
                        const currentPeriodNumber = Math.floor(totalMessages / messagesPerPeriod);
                        const periods = ["morning", "afternoon", "evening"];
                        const currentPeriodIndex = currentPeriodNumber % 3;
                        const nextPeriodIndex = (currentPeriodIndex + 1) % 3;
                        const nextPeriod = periods[nextPeriodIndex];
                        
                        if (messagesUntilNext === messagesPerPeriod) {
                          return `Progress to ${nextPeriod}: 0%`;
                        }
                        return `Progress to ${nextPeriod}: ${Math.round((currentPeriodMessages / messagesPerPeriod) * 100)}%`;
                      })()}
                      <div className="w-32 bg-gray-700 rounded-full h-1.5 mt-2">
                        <div 
                          className="bg-blue-500 h-1.5 rounded-full transition-all duration-300" 
                          style={{ 
                            width: `${(() => {
                              const agentCount = Array.isArray(agents) ? agents.length : 3;
                              const totalMessages = Array.isArray(conversations) ? 
                                conversations.reduce((total, conv) => {
                                  const messages = conv.messages || [];
                                  const agentMessages = messages.filter(msg => msg.agent_id !== "observer");
                                  return total + agentMessages.length;
                                }, 0) : 0;
                              const messagesPerPeriod = agentCount * 9;
                              const currentPeriodMessages = totalMessages % messagesPerPeriod;
                              return Math.min(100, (currentPeriodMessages / messagesPerPeriod) * 100);
                            })()}%` 
                          }}
                        ></div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Agent Count Display */}
              <div className="bg-white/10 border border-white/20 rounded-2xl px-2 py-1 hover:bg-white/15 transition-colors group relative">
                <div className="flex items-center justify-center space-x-1">
                  <svg className="w-4 h-4 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                  </svg>
                  <span className="text-white text-sm font-medium">
                    {Array.isArray(agents) ? agents.length : 0}
                  </span>
                </div>
                
                {/* Tooltip on hover */}
                <div className="absolute top-full left-1/2 transform -translate-x-1/2 mt-2 w-48 bg-gray-900/95 backdrop-blur-sm rounded-lg p-3 border border-white/20 shadow-lg opacity-0 group-hover:opacity-100 transition-opacity duration-200 pointer-events-none z-50">
                  <div className="text-white/80 text-xs space-y-1">
                    <div className="font-medium text-white mb-1">Agent Breakdown:</div>
                    <div>Active Agents: {Array.isArray(agents) ? agents.length : 0}</div>
                    <div>
                      Favorite Agents: {(() => {
                        const favoriteCount = Array.isArray(agents) ? 
                          agents.filter(agent => agent.is_favorite).length : 0;
                        return favoriteCount;
                      })()}
                    </div>
                    <div className="text-white/80 mt-1 text-xs">
                      {(() => {
                        const agentCount = Array.isArray(agents) ? agents.length : 0;
                        return agentCount > 0 ? `progress interval: ${agentCount * 9} msgs` : '';
                      })()}
                    </div>
                    <div className="text-green-300 mt-1">
                      {(() => {
                        const agentCount = Array.isArray(agents) ? agents.length : 0;
                        if (agentCount === 0) return '';
                        
                        const totalMessages = Array.isArray(conversations) ? 
                          conversations.reduce((total, conv) => {
                            const messages = conv.messages || [];
                            const agentMessages = messages.filter(msg => msg.agent_id !== "observer");
                            return total + agentMessages.length;
                          }, 0) : 0;
                        
                        const messagesPerDay = agentCount * 9 * 3; // 3 time periods per day
                        const currentDayMessages = totalMessages % messagesPerDay;
                        const messagesUntilNextDay = messagesPerDay - currentDayMessages;
                        
                        if (messagesUntilNextDay === messagesPerDay) {
                          return `Next day in ${messagesPerDay} messages`;
                        }
                        return `Next day in ${messagesUntilNextDay} messages`;
                      })()}
                    </div>
                  </div>
                </div>
              </div>

              {/* Report Count Display */}
              <div className="bg-white/10 border border-white/20 rounded-2xl px-2 py-1 hover:bg-white/15 transition-colors group relative">
                <div className="flex items-center justify-center space-x-1">
                  <svg className="w-4 h-4 text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                  <span className="text-white text-sm font-medium">
                    {(() => {
                      // Count reports from simulationData
                      const reportCount = simulationData?.reports ? simulationData.reports.length : 0;
                      return reportCount;
                    })()}
                  </span>
                </div>
                
                {/* Tooltip on hover */}
                <div className="absolute top-full left-1/2 transform -translate-x-1/2 mt-2 w-48 bg-gray-900/95 backdrop-blur-sm rounded-lg p-3 border border-white/20 shadow-lg opacity-0 group-hover:opacity-100 transition-opacity duration-200 pointer-events-none z-50">
                  <div className="text-white/80 text-xs space-y-1">
                    <div className="font-medium text-white mb-1">Report Breakdown:</div>
                    <div>Generated Reports: {(() => {
                      const reportCount = simulationData?.reports ? simulationData.reports.length : 0;
                      return reportCount;
                    })()}</div>
                    <div>
                      Latest Report: {(() => {
                        const reports = simulationData?.reports || [];
                        if (reports.length > 0) {
                          const latest = reports[reports.length - 1];
                          const date = new Date(latest.created_at || latest.timestamp);
                          return date.toLocaleDateString();
                        }
                        return "None";
                      })()}
                    </div>
                    <div className="text-white/80 mt-1">
                      Auto generated daily: <span className={autoDailyReportEnabled ? "text-green-400" : "text-white/80"}>
                        {autoDailyReportEnabled ? "on" : "off"}
                      </span>
                    </div>
                    <div className="text-white/80 mt-1">
                      Auto generated weekly: <span className={autoReportEnabled ? "text-green-400" : "text-white/80"}>
                        {autoReportEnabled ? "on" : "off"}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            
            {/* Set Scenario Section with expandable functionality */}
            <div className="mb-4">
              <div className="flex justify-between items-center mb-2">
                <h4 className="text-white/80 text-sm font-medium">Set Scenario</h4>
                <button
                  onClick={() => {
                    // Accordion behavior: Always close Generate Report when expanding Set Scenario
                    if (showSetScenario) {
                      // If already expanded, just collapse it
                      setShowSetScenario(false);
                    } else {
                      // If collapsed, expand it and ensure Generate Report is closed
                      setShowReport(false);
                      setShowSetScenario(true);
                    }
                  }}
                  className="text-white/60 hover:text-white transition-all duration-200"
                  style={{ transform: showSetScenario ? 'rotate(180deg)' : 'rotate(0deg)' }}
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                  </svg>
                </button>
              </div>
              
              {/* Scenario Content Section */}
              <div className="flex-1">
                {/* Expandable Scenario Input */}
                {showSetScenario && (
                  <div className="bg-white/5 rounded-lg p-4 space-y-3 animate-fadeIn">
                    <input
                      type="text"
                      value={scenarioName}
                      onChange={(e) => setScenarioName(e.target.value)}
                      placeholder="Scenario name"
                      disabled={loading || isRunning}
                      className="w-full px-3 py-2 bg-white/10 border border-white/20 rounded-lg text-white text-sm placeholder-white/50 focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
                    />
                    <div className="relative">
                      <textarea
                        value={customScenario}
                        onChange={(e) => setCustomScenario(e.target.value)}
                        placeholder="enter your scenario here..."
                        disabled={loading || isRunning || isRecording}
                        className="w-full px-3 py-2 pb-12 bg-white/10 border border-white/20 rounded-lg text-white text-sm placeholder-white/50 focus:ring-2 focus:ring-blue-500 disabled:opacity-50 resize-none"
                        rows="6"
                      />
                      <button
                        onClick={handleVoiceInput}
                        disabled={loading || isRunning}
                        className={`absolute left-2 bottom-2 p-2 rounded-lg transition-colors disabled:opacity-50 ${
                          isRecording 
                            ? 'bg-red-500/20 text-red-400 animate-pulse' 
                            : 'text-white/60 hover:text-white hover:bg-white/10'
                        }`}
                        title={isRecording ? 'Recording... Click to stop' : 'Click to record scenario with voice'}
                      >
                        <svg 
                          width="16" 
                          height="16" 
                          viewBox="0 0 24 24" 
                          fill="currentColor"
                        >
                          <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"/>
                          <path d="M19 10v2a7 7 0 0 1-14 0v-2"/>
                          <path d="M12 19v4"/>
                          <path d="M8 23h8"/>
                        </svg>
                      </button>
                    </div>
                    <div className="flex space-x-2">
                      <button
                        onClick={handleSetScenario}
                        disabled={loading || isRunning || !customScenario.trim()}
                        className="flex-1 px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 text-white rounded-lg transition-colors disabled:cursor-not-allowed"
                      >
                        {loading ? 'Setting...' : 'Set Scenario'}
                      </button>
                      <button
                        onClick={getRandomScenario}
                        disabled={loading || isRunning}
                        className="px-3 py-2 text-white/60 hover:text-white transition-colors disabled:opacity-50"
                        title="Generate random scenario"
                      >
                        🎲
                      </button>
                    </div>
                  </div>
                )}
                
                {/* Current Scenario Display - REMOVED since scenario name is shown in notification bar */}
              </div>
            </div>

            {/* Reports Section */}
            <div className="mb-4">
              <div className="flex justify-between items-center mb-2">
                <h4 className="text-white/80 text-sm font-medium">Reports</h4>
                <button
                  onClick={() => {
                    // Accordion behavior: Close other sections when expanding Reports
                    if (showReports) {
                      setShowReports(false);
                    } else {
                      setShowSetScenario(false);
                      setShowReport(false);
                      setShowDocs(false);
                      setShowReports(true);
                    }
                  }}
                  className="text-white/60 hover:text-white transition-all duration-200"
                  style={{ transform: showReports ? 'rotate(180deg)' : 'rotate(0deg)' }}
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                  </svg>
                </button>
              </div>

              {showReports && (
                <div className="bg-white/10 backdrop-blur-sm rounded-lg p-3 border border-white/20">
                  <div className="space-y-3">
                    {/* Generate Report Button - Moved here and made smaller */}
                    <div className="pb-2 border-b border-white/10">
                      <button
                        onClick={handleGenerateReport}
                        disabled={reportLoading || (Array.isArray(conversations) ? conversations : []).length === 0}
                        className="w-full px-3 py-1.5 bg-purple-600/80 hover:bg-purple-700 disabled:bg-gray-600 text-white text-sm rounded transition-colors disabled:cursor-not-allowed"
                      >
                        {reportLoading ? 'Generating...' : 'Generate Daily Report'}
                      </button>
                      {(Array.isArray(conversations) ? conversations : []).length === 0 && (
                        <div className="text-white/50 text-xs text-center mt-1">
                          No conversations available
                        </div>
                      )}
                    </div>

                    {/* Auto Report Toggles - Moved from Settings */}
                    <div className="pb-2 border-b border-white/10">
                      <div className="grid grid-cols-1 gap-2">
                        {/* Auto Daily Report Toggle */}
                        <div className="flex items-center justify-between">
                          <span className="text-white/80 text-xs font-medium">Auto Daily Reports</span>
                          <button
                            onClick={handleAutoDailyReportToggle}
                            className={`relative w-8 h-4 rounded-full transition-colors duration-200 flex-shrink-0 ${
                              autoDailyReportEnabled ? 'bg-green-600' : 'bg-gray-600'
                            }`}
                          >
                            <div
                              className={`absolute top-0.5 left-0.5 w-3 h-3 bg-white rounded-full transition-transform duration-200 ${
                                autoDailyReportEnabled ? 'transform translate-x-4' : ''
                              }`}
                            />
                          </button>
                        </div>
                        
                        {/* Auto Weekly Report Toggle */}
                        <div className="flex items-center justify-between">
                          <span className="text-white/80 text-xs font-medium">Auto Weekly Reports</span>
                          <button
                            onClick={handleAutoReportToggle}
                            className={`relative w-8 h-4 rounded-full transition-colors duration-200 flex-shrink-0 ${
                              autoReportEnabled ? 'bg-green-600' : 'bg-gray-600'
                            }`}
                          >
                            <div
                              className={`absolute top-0.5 left-0.5 w-3 h-3 bg-white rounded-full transition-transform duration-200 ${
                                autoReportEnabled ? 'transform translate-x-4' : ''
                              }`}
                            />
                          </button>
                        </div>
                      </div>
                    </div>

                    {/* Daily Reports */}
                    <div>
                      <h5 className="text-white text-xs font-medium mb-2 flex items-center">
                        <svg className="w-3 h-3 text-blue-400 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                        </svg>
                        Daily Reports
                      </h5>
                      <div className="bg-white/5 rounded border border-white/10 max-h-32 overflow-y-auto">
                        {simulationData?.reports?.filter(report => report.type === 'daily').length > 0 ? (
                          <div className="space-y-1 p-2">
                            {simulationData.reports.filter(report => report.type === 'daily').map((report, index) => (
                              <button
                                key={report.id || index}
                                onClick={() => {
                                  setSelectedReport(report);
                                  setReportData(report.content || 'No content available');
                                  setReportCardVisible(true);
                                }}
                                className={`w-full text-left p-2 text-xs rounded transition-colors ${
                                  selectedReport?.id === report.id 
                                    ? 'bg-blue-600/30 border border-blue-400/50 text-blue-200' 
                                    : 'bg-white/5 hover:bg-white/10 text-white/70 hover:text-white/90'
                                }`}
                              >
                                <div className="font-medium flex items-center justify-between">
                                  <span>{report.title || `Day ${report.day || index + 1}`}</span>
                                  <span className={`text-xs px-1.5 py-0.5 rounded ${
                                    report.subtitle === 'auto' || report.generation_type === 'automatic'
                                      ? 'bg-green-600/20 text-green-300'
                                      : 'bg-purple-600/20 text-purple-300'
                                  }`}>
                                    {report.subtitle || (report.generation_type === 'automatic' ? 'auto' : 'manual')}
                                  </span>
                                </div>
                                <div className="text-white/50 text-xs">
                                  {new Date(report.created_at || report.timestamp).toLocaleDateString()}
                                  {report.conversation_count && ` • ${report.conversation_count} conversations`}
                                </div>
                              </button>
                            ))}
                          </div>
                        ) : (
                          <div className="text-white/50 text-xs text-center py-4">
                            No daily reports generated yet
                          </div>
                        )}
                      </div>
                    </div>

                    {/* Weekly Reports */}
                    <div>
                      <h5 className="text-white text-xs font-medium mb-2 flex items-center">
                        <svg className="w-3 h-3 text-purple-400 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                        </svg>
                        Weekly Reports
                      </h5>
                      <div className="bg-white/5 rounded border border-white/10 max-h-32 overflow-y-auto">
                        {simulationData?.reports?.filter(report => report.type === 'weekly').length > 0 ? (
                          <div className="space-y-1 p-2">
                            {simulationData.reports.filter(report => report.type === 'weekly').map((report, index) => (
                              <button
                                key={report.id || index}
                                onClick={() => {
                                  setSelectedReport(report);
                                  setReportData(report.content || 'No content available');
                                  setReportCardVisible(true);
                                }}
                                className={`w-full text-left p-2 text-xs rounded transition-colors ${
                                  selectedReport?.id === report.id 
                                    ? 'bg-purple-600/30 border border-purple-400/50 text-purple-200' 
                                    : 'bg-white/5 hover:bg-white/10 text-white/70 hover:text-white/90'
                                }`}
                              >
                                <div className="font-medium flex items-center justify-between">
                                  <span>{report.title || `Week ${report.week || index + 1}`}</span>
                                  <span className={`text-xs px-1.5 py-0.5 rounded ${
                                    report.subtitle === 'auto' || report.generation_type === 'automatic'
                                      ? 'bg-green-600/20 text-green-300'
                                      : 'bg-purple-600/20 text-purple-300'
                                  }`}>
                                    {report.subtitle || (report.generation_type === 'automatic' ? 'auto' : 'manual')}
                                  </span>
                                </div>
                                <div className="text-white/50 text-xs">
                                  {new Date(report.created_at || report.timestamp).toLocaleDateString()}
                                  {report.conversation_count && ` • ${report.conversation_count} conversations`}
                                </div>
                              </button>
                            ))}
                          </div>
                        ) : (
                          <div className="text-white/50 text-xs text-center py-4">
                            No weekly reports generated yet
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>

            {/* Docs Section */}
            <div className="mb-4">
              <div className="flex justify-between items-center mb-2">
                <h4 className="text-white/80 text-sm font-medium">Docs</h4>
                <button
                  onClick={() => {
                    // Accordion behavior: Close other sections when expanding Docs
                    if (showDocs) {
                      setShowDocs(false);
                    } else {
                      setShowSetScenario(false);
                      setShowReports(false);
                      setShowDocs(true);
                    }
                  }}
                  className="text-white/60 hover:text-white transition-all duration-200"
                  style={{ transform: showDocs ? 'rotate(180deg)' : 'rotate(0deg)' }}
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                  </svg>
                </button>
              </div>

              {showDocs && (
                <div className="bg-white/10 backdrop-blur-sm rounded-lg p-3 border border-white/20">
                  <div className="bg-white/5 rounded border border-white/10 max-h-96 overflow-y-auto">
                    {simulationData?.documents && simulationData.documents.length > 0 ? (
                      <div className="space-y-3 p-3">
                        {simulationData.documents
                          .sort((a, b) => new Date(b.metadata?.created_at || b.created_at) - new Date(a.metadata?.created_at || a.created_at))
                          .map((doc, index) => (
                            <div 
                              key={doc.id || index} 
                              className="bg-gradient-to-r from-white/10 to-white/5 rounded-lg p-4 border border-white/20 hover:border-white/40 transition-all duration-200 cursor-pointer group"
                              onClick={() => {
                                setSelectedDocument(doc);
                                setDocumentCardVisible(true);
                              }}
                            >
                              <div className="flex items-start justify-between">
                                <div className="flex-1">
                                  <div className="flex items-center space-x-2 mb-2">
                                    <svg className="w-4 h-4 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                                    </svg>
                                    <span className="text-sm font-medium text-white group-hover:text-blue-200 transition-colors">
                                      {doc.metadata?.title || 'Untitled Document'}
                                    </span>
                                    <span className="px-2 py-1 text-xs bg-blue-500/20 text-blue-300 rounded-full">
                                      {doc.metadata?.category || 'Document'}
                                    </span>
                                  </div>
                                  <div className="text-xs text-white/60 space-y-1">
                                    <div className="flex items-center space-x-4">
                                      <span>👤 {doc.metadata?.authors?.[0] || 'Unknown Author'}</span>
                                      <span>📅 {doc.metadata?.created_at ? new Date(doc.metadata.created_at).toLocaleDateString() : 'Unknown Date'}</span>
                                      <span className="px-2 py-1 bg-green-500/20 text-green-300 rounded-full">
                                        {doc.metadata?.status || 'Draft'}
                                      </span>
                                    </div>
                                    {doc.metadata?.description && (
                                      <div className="text-white/50 text-xs mt-1 line-clamp-2">
                                        {doc.metadata.description}
                                      </div>
                                    )}
                                  </div>
                                </div>
                                <div className="flex items-center space-x-2 opacity-0 group-hover:opacity-100 transition-opacity">
                                  <button
                                    onClick={(e) => {
                                      e.stopPropagation();
                                      // Add download functionality
                                      window.open(`${API}/documents/${doc.id}/download-pdf`, '_blank');
                                    }}
                                    className="p-2 text-white/60 hover:text-white hover:bg-white/10 rounded-full transition-all"
                                    title="Download PDF"
                                  >
                                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                                    </svg>
                                  </button>
                                  <svg className="w-4 h-4 text-white/40 group-hover:text-white/60 transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                                  </svg>
                                </div>
                              </div>
                            </div>
                          ))}
                      </div>
                    ) : (
                      <div className="text-white/50 text-xs text-center py-8">
                        <div className="mb-3 flex justify-center">
                          <svg className="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                          </svg>
                        </div>
                        <div className="font-medium text-white mb-2">No documents generated yet</div>
                        <div className="text-xs opacity-75">
                          Start a conversation and agents will automatically create relevant documents
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>
            
        </div>
      </div>

      {/* Report Modal - Popup overlay instead of inline card */}
      {reportCardVisible && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4 pt-12">
          <div className="bg-gradient-to-br from-slate-800 to-blue-800 rounded-2xl shadow-2xl w-full max-w-4xl max-h-[85vh] overflow-hidden mt-2">
            {/* Modal Header */}
            <div className="flex justify-between items-center p-6 border-b border-white/10">
              <div className="flex items-center space-x-3">
                <div className="w-8 h-8 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
                  <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                  </svg>
                </div>
                <div>
                  <h3 className="text-xl font-bold text-white">
                    {selectedReport?.type === 'weekly' ? 'Weekly Strategic Report' : 'Daily Strategic Report'} - Day {selectedReport?.day || '1'}
                  </h3>
                  <p className="text-sm text-white/60">
                    Generated: {selectedReport?.created_at ? new Date(selectedReport.created_at).toLocaleDateString() : 'Today'} | Phase: {selectedReport?.time_period || 'Morning'}
                  </p>
                </div>
              </div>
              <div className="flex items-center space-x-2">
                <button
                  onClick={() => handleReportPdfDownload(selectedReport?.id)}
                  className="text-white/60 hover:text-white transition-colors p-2 rounded-full hover:bg-white/10"
                  title="Download PDF"
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                </button>
                <button
                  onClick={() => setReportCardVisible(false)}
                  className="text-white/60 hover:text-white transition-colors p-2 rounded-full hover:bg-white/10"
                  title="Close report"
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
            </div>
            
            {/* Modal Content */}
            <div className="overflow-y-auto max-h-[calc(90vh-80px)]">
              {reportLoading ? (
                <div className="flex items-center justify-center p-12">
                  <div className="animate-pulse flex items-center space-x-4">
                    <div className="w-10 h-10 bg-blue-500/30 rounded-full animate-bounce"></div>
                    <div className="text-white/80 text-xl">Generating comprehensive strategic report...</div>
                  </div>
                </div>
              ) : (
                <div className="p-6">
                  <div className="min-h-[400px]">
                    <style jsx>{`
                      .report-section {
                        margin-bottom: 2rem;
                        background: rgba(255, 255, 255, 0.12) !important;
                        border-radius: 0.75rem;
                        padding: 1.5rem;
                        border-left: 4px solid;
                      }
                      .executive { border-left-color: #f59e0b !important; }
                      .strategic { border-left-color: #3b82f6 !important; }
                      .performance { border-left-color: #10b981 !important; }
                      .operational { border-left-color: #8b5cf6 !important; }
                      .challenges { border-left-color: #ef4444 !important; }
                      .recommendations { border-left-color: #06b6d4 !important; }
                      .section-header {
                        font-size: 1.25rem !important;
                        font-weight: bold !important;
                        margin-bottom: 1rem !important;
                      }
                      .executive-header { color: #fbbf24 !important; }
                      .strategic-header { color: #60a5fa !important; }
                      .performance-header { color: #34d399 !important; }
                      .operational-header { color: #a78bfa !important; }
                      .challenges-header { color: #f87171 !important; }
                      .recommendations-header { color: #22d3ee !important; }
                      .section-content {
                        color: #f3f4f6 !important;
                        line-height: 1.7 !important;
                        font-size: 0.95rem !important;
                      }
                      .section-content p {
                        margin-bottom: 0.75rem !important;
                        color: #f3f4f6 !important;
                      }
                      .section-content ul, .section-content ol {
                        margin: 1rem 0 !important;
                        padding-left: 1.5rem !important;
                      }
                      .section-content li {
                        margin-bottom: 0.5rem !important;
                        color: #f3f4f6 !important;
                        line-height: 1.6 !important;
                      }
                      .section-content strong {
                        color: #ffffff !important;
                        font-weight: 700 !important;
                      }
                    `}</style>
                    <div 
                      className="text-gray-100 leading-relaxed"
                      dangerouslySetInnerHTML={{ 
                        __html: reportData ? reportData.replace(/Daily Strategic Report - Day \d+/g, '').replace(/Generated: [^|]*\|[^<]*/g, '') : '<div class="text-center text-white p-8">No report data available</div>' 
                      }}
                    />
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Document Card - Only visible when document is selected */}
      {documentCardVisible && selectedDocument && (
        <div className="mt-6 flex justify-center">
          <div className="col-span-1 sm:col-span-1 md:col-span-1 lg:col-span-2 xl:col-span-2 2xl:col-span-2 w-full max-w-5xl">
            <div className="bg-white/10 backdrop-blur-lg rounded-xl p-6 flex flex-col">
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-lg font-bold text-white">
                  📄 {selectedDocument.metadata?.title || 'Document'}
                </h3>
                <div className="flex items-center space-x-2">
                  <button
                    onClick={() => window.open(`${API}/documents/${selectedDocument.id}/download-pdf`, '_blank')}
                    className="text-white/60 hover:text-white transition-colors p-2 rounded-full hover:bg-white/10"
                    title="Download PDF"
                  >
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                  </button>
                  <button
                    onClick={() => setDocumentCardVisible(false)}
                    className="text-white/60 hover:text-white transition-colors p-2 rounded-full hover:bg-white/10"
                    title="Close document"
                  >
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </div>
              </div>
              
              {/* Document Content with Professional Styling */}
              <div className="flex-1 overflow-y-auto">
                <div className="bg-gradient-to-br from-white/8 to-white/12 rounded-xl p-6 max-h-[600px] overflow-y-auto custom-scrollbar">
                  <style jsx>{`
                    .document-header {
                      text-align: center;
                      margin-bottom: 2rem;
                      border-bottom: 2px solid rgba(255, 255, 255, 0.2);
                      padding-bottom: 1rem;
                    }
                    .document-title {
                      font-size: 2rem;
                      font-weight: bold;
                      color: #ffffff;
                      margin-bottom: 0.5rem;
                    }
                    .document-meta {
                      color: #cbd5e0;
                      font-size: 0.875rem;
                    }
                    .document-section {
                      margin-bottom: 2rem;
                      background: rgba(255, 255, 255, 0.05);
                      border-radius: 0.75rem;
                      padding: 1.5rem;
                      border-left: 4px solid;
                    }
                    .overview { border-left-color: #3b82f6; }
                    .details { border-left-color: #10b981; }
                    .recommendations { border-left-color: #f59e0b; }
                    .next-steps { border-left-color: #ef4444; }
                    .budget-header { color: #fbbf24; }
                    .strategic-header { color: #60a5fa; }
                    .performance-header { color: #34d399; }
                    .operational-header { color: #a78bfa; }
                    .challenges-header { color: #f87171; }
                    .recommendations-header { color: #22d3ee; }
                    .section-header {
                      font-size: 1.25rem;
                      font-weight: bold;
                      margin-bottom: 1rem;
                    }
                    .section-content {
                      color: #1f2937;
                      line-height: 1.7;
                      font-size: 0.95rem;
                    }
                    .section-content p {
                      margin-bottom: 0.75rem;
                      color: #1f2937;
                    }
                    .section-content ul, .section-content ol {
                      margin: 1rem 0;
                      padding-left: 1.5rem;
                    }
                    .section-content li {
                      margin-bottom: 0.5rem;
                      color: #1f2937;
                      line-height: 1.6;
                    }
                    .section-content strong {
                      color: #111827;
                      font-weight: 700;
                    }
                    .doc-list {
                      padding-left: 1.5rem;
                      margin: 1rem 0;
                    }
                    .doc-list li {
                      margin-bottom: 0.5rem;
                      color: #1f2937;
                      line-height: 1.6;
                    }
                    .phase-block {
                      background: rgba(255, 255, 255, 0.05);
                      border-radius: 0.5rem;
                      padding: 1rem;
                      margin: 1rem 0;
                    }
                    .phase-block h3 {
                      color: #ffffff;
                      margin-bottom: 0.5rem;
                    }
                    .custom-scrollbar::-webkit-scrollbar {
                      width: 6px;
                    }
                    .custom-scrollbar::-webkit-scrollbar-track {
                      background: rgba(255, 255, 255, 0.1);
                      border-radius: 3px;
                    }
                    .custom-scrollbar::-webkit-scrollbar-thumb {
                      background: rgba(255, 255, 255, 0.3);
                      border-radius: 3px;
                    }
                    .custom-scrollbar::-webkit-scrollbar-thumb:hover {
                      background: rgba(255, 255, 255, 0.5);
                    }
                  `}</style>
                  <div 
                    className="text-white/90 leading-relaxed"
                    dangerouslySetInnerHTML={{ 
                      __html: selectedDocument.content || '<div class="text-center text-white/60">No document content available</div>' 
                    }}
                  />
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Custom Start Fresh Confirmation Modal */}
      {showStartFreshModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
          <div className="bg-gradient-to-br from-purple-900 to-pink-900 p-6 rounded-xl shadow-2xl border border-purple-500/30 max-w-md mx-4">
            <div className="text-center">
              <h3 className="text-lg font-bold text-white mb-3">Are you sure?</h3>
              <p className="text-white/70 mb-6">
                This will delete <strong>all {agents.length} agents</strong>, clear all conversations, and reset the scenario. This action cannot be undone.
              </p>
              <div className="flex space-x-3 justify-center">
                <button
                  onClick={() => setShowStartFreshModal(false)}
                  className="px-4 py-2 bg-gray-600 hover:bg-gray-700 text-white rounded-lg transition-colors"
                >
                  Cancel
                </button>
                <button
                  onClick={confirmStartFresh}
                  disabled={startFreshLoading}
                  className="px-4 py-2 bg-red-600 hover:bg-red-700 disabled:bg-gray-600 text-white rounded-lg transition-colors"
                >
                  {startFreshLoading ? 'Clearing...' : 'Start Fresh'}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Custom Clear All Confirmation Modal */}
      {showClearAllModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
          <div className="bg-gradient-to-br from-purple-900 to-pink-900 p-6 rounded-xl shadow-2xl border border-purple-500/30 max-w-md mx-4">
            <div className="text-center">
              <h3 className="text-lg font-bold text-white mb-3">Are you sure?</h3>
              <p className="text-white/70 mb-6">
                This will remove all {agents.length} agents from the list. This action cannot be undone.
              </p>
              <div className="flex space-x-3 justify-center">
                <button
                  onClick={() => setShowClearAllModal(false)}
                  className="px-4 py-2 bg-gray-600 hover:bg-gray-700 text-white rounded-lg transition-colors"
                >
                  Cancel
                </button>
                <button
                  onClick={confirmClearAllAgents}
                  disabled={loading}
                  className="px-4 py-2 bg-red-600 hover:bg-red-700 disabled:bg-gray-600 text-white rounded-lg transition-colors"
                >
                  {loading ? 'Removing...' : 'Remove All'}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Agent Edit Modal */}
      <AgentEditModal
        isOpen={showEditModal}
        onClose={() => {
          setShowEditModal(false);
          setEditingAgent(null);
        }}
        agent={editingAgent}
        onSave={handleSaveAgent}
      />

      {/* Agent Create Modal */}
      {showCreateAgentModal && (
        <AgentCreateModal
          onClose={() => setShowCreateAgentModal(false)}
          onAgentCreated={handleCreateAgent}
        />
      )}

      <style jsx>{`
        .animate-pulse {
          animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
        }
        
        @keyframes pulse {
          0%, 100% {
            opacity: 1;
          }
          50% {
            opacity: 0.5;
          }
        }
        
        .animate-fadeIn {
          animation: fadeIn 0.3s ease-out;
        }
        
        @keyframes fadeIn {
          from {
            opacity: 0;
          }
          to {
            opacity: 1;
          }
        }
      `}</style>

      {/* Setup Flow Modal */}
      <AnimatePresence>
        {showSetupFlow && (
          <SetupFlow
            onComplete={handleSetupFlowComplete}
            onCancel={handleSetupFlowCancel}
            existingAgents={agents}
            onAddAgent={handleAddAgent}
          />
        )}
      </AnimatePresence>

      </div> {/* Close main container div */}
    </>
  );
};

export default SimulationControl;