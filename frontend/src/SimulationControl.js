import React, { useState, useEffect, useRef, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import axios from 'axios';
import { useAuth } from './AuthContext';
import AgentCreateModal from './AgentCreateModal';

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
  const { user, token } = useAuth();
  const [simulationState, setSimulationState] = useState(null);
  const [agents, setAgents] = useState([]);
  const [conversations, setConversations] = useState([]);
  const [scenario, setScenario] = useState('');
  const [customScenario, setCustomScenario] = useState('');
  const [scenarioName, setScenarioName] = useState('');
  const [isRunning, setIsRunning] = useState(false);
  const [isPaused, setIsPaused] = useState(false);
  const [autoGenerating, setAutoGenerating] = useState(false);
  const [loading, setLoading] = useState(false);
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
  const [showClearAllModal, setShowClearAllModal] = useState(false);
  const [showStartFreshModal, setShowStartFreshModal] = useState(false);
  const [showReport, setShowReport] = useState(false);
  const [reportData, setReportData] = useState('');
  const [reportLoading, setReportLoading] = useState(false);
  const [reportCardVisible, setReportCardVisible] = useState(false);
  const [reportCardExpanded, setReportCardExpanded] = useState(true);
  const [autoReportEnabled, setAutoReportEnabled] = useState(false);
  const [autoGenerateInterval, setAutoGenerateInterval] = useState(null);
  const [observerMessage, setObserverMessage] = useState('');
  const [observerMessages, setObserverMessages] = useState([]);
  const [isObserverLoading, setIsObserverLoading] = useState(false);
  const [notificationVisible, setNotificationVisible] = useState(false);
  const [notificationText, setNotificationText] = useState('');
  const [scenarioExpanded, setScenarioExpanded] = useState(false);
  const searchRefs = useRef([]);
  const messagesEndRef = useRef(null);
  const fetchingRef = useRef(false); // Performance optimization: Prevent duplicate fetches

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
        const [stateResponse, agentsResponse, conversationsResponse] = await Promise.all([
          axios.get(`${API}/simulation/state`, {
            headers: { Authorization: `Bearer ${token}` }
          }),
          axios.get(`${API}/agents`, {
            headers: { Authorization: `Bearer ${token}` }
          }),
          axios.get(`${API}/conversations`, {
            headers: { Authorization: `Bearer ${token}` }
          })
        ]);

        // Update state
        setSimulationState(stateResponse.data);
        setConversations(conversationsResponse.data || []);
        setIsRunning(stateResponse.data.is_active || false);
        setIsPaused(stateResponse.data.is_paused || false);
        setAgents(agentsResponse.data || []);
        
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
      // Increase interval when simulation is not active (less frequent polling)
      const interval = isRunning ? 3000 : 10000; // 3s when running, 10s when stopped
      
      // Only fetch if page is visible (performance optimization)
      if (!document.hidden) {
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

  // Simple fetch function for use by other functions (non-debounced to avoid hoisting issues)
  const fetchSimulationState = async () => {
    try {
      if (fetchingRef.current) return;
      fetchingRef.current = true;

      const [stateResponse, agentsResponse, conversationsResponse] = await Promise.all([
        axios.get(`${API}/simulation/state`, {
          headers: { Authorization: `Bearer ${token}` }
        }),
        axios.get(`${API}/agents`, {
          headers: { Authorization: `Bearer ${token}` }
        }),
        axios.get(`${API}/conversations`, {
          headers: { Authorization: `Bearer ${token}` }
        })
      ]);

      setSimulationState(stateResponse.data);
      setConversations(conversationsResponse.data || []);
      setIsRunning(stateResponse.data.is_active || false);
      setIsPaused(stateResponse.data.is_paused || false);
      setAgents(agentsResponse.data || []);
      
      console.log('✅ Fetch completed - Conversations:', conversationsResponse.data?.length || 0);
      
    } catch (error) {
      console.error('Error fetching simulation state:', error);
    } finally {
      fetchingRef.current = false;
    }
  };



  // Auto-scroll to bottom of conversations - DISABLED to prevent interrupting reading
  // useEffect(() => {
  //   if (messagesEndRef.current) {
  //     messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
  //   }
  // }, [conversations, observerMessages]);

  // React to refresh trigger from Agent Library
  useEffect(() => {
    if (refreshTrigger > 0) {
      console.log('🔄 Observatory refreshing due to Agent Library change');
      fetchSimulationState();
    }
  }, [refreshTrigger]);

  // Continuous conversation generation when simulation is running
  useEffect(() => {
    if (isRunning && !isPaused && agents.length >= 2) {
      console.log('🔄 Starting continuous conversation generation...');
      
      // Clear any existing interval
      if (autoGenerateInterval) {
        clearInterval(autoGenerateInterval);
      }
      
      // Set up new interval for continuous generation
      const intervalId = setInterval(() => {
        console.log('⏰ Auto-generating conversation...');
        generateNewConversation(true); // Mark as auto-generated
      }, 5000); // Generate new conversation every 5 seconds
      
      setAutoGenerateInterval(intervalId);
      
    } else {
      // Clear interval when simulation stops/pauses or insufficient agents
      if (autoGenerateInterval) {
        console.log('⏹️ Stopping continuous conversation generation');
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
  }, [isRunning, isPaused, agents.length]); // Dependencies: when these change, restart/stop interval

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

  // Optimized simulation control with optimistic updates
  const playPauseSimulation = async () => {
    console.log('🎯 Play button clicked - playPauseSimulation started');
    console.log('🎯 Current state:', { isRunning, isPaused, loading, agentsCount: agents.length });
    
    try {
      setLoading(true);
      
      // Optimistic update: Update UI immediately for better perceived performance
      const targetState = isRunning && !isPaused ? false : true;
      setIsRunning(targetState);
      
      const endpoint = isRunning && !isPaused ? '/simulation/pause' : '/simulation/start';
      console.log('🎯 Calling endpoint:', endpoint);
      
      // Perform API call
      const response = await axios.post(`${API}${endpoint}`, {}, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      console.log('🎯 API call successful, response:', response.data);
      
      // Update with actual server response
      if (response.data) {
        console.log('🎯 Play button response:', response.data);
        
        // Parse state from nested state object
        const simState = response.data.state || response.data;
        setIsRunning(simState.is_active || false);
        setIsPaused(simState.is_paused || false);
        
        console.log('🎯 Parsed simulation state:', {
          is_active: simState.is_active,
          is_paused: simState.is_paused
        });
        
        // Generate conversation whenever simulation becomes active (not paused)
        if (simState.is_active && !simState.is_paused) {
          console.log('🎯 Simulation is active, generating first conversation...');
          // Generate first conversation immediately, then interval takes over
          setTimeout(() => {
            generateNewConversation();
          }, 1000); // Small delay to ensure simulation state is updated
        } else {
          console.log('🎯 Simulation not active for conversation:', {
            is_active: simState.is_active,
            is_paused: simState.is_paused
          });
        }
      }
      
      // Debounced state fetch (only if needed)
      setTimeout(() => fetchSimulationState(), 100);
      
    } catch (error) {
      console.error('❌ Error controlling simulation:', error);
      console.log('❌ Full error details:', error.response?.data || error.message);
      // Revert optimistic update on error
      setIsRunning(!isRunning);
    } finally {
      setLoading(false);
      console.log('🎯 playPauseSimulation completed');
    }
  };

  // Generate new conversation
  const generateNewConversation = async (isAuto = false) => {
    try {
      const logPrefix = isAuto ? '⏰ Auto' : '💬 Manual';
      console.log(`${logPrefix} - Starting conversation generation...`);
      setConversationLoading(true);
      
      const response = await axios.post(`${API}/conversation/generate`, {}, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      if (response.data) {
        console.log(`${logPrefix} - New conversation generated:`, response.data);
        console.log(`${logPrefix} - Conversation has`, response.data.messages?.length || 0, 'messages');
        
        // Refresh conversations to show the new one
        setTimeout(() => fetchSimulationState(), 500);
      }
      
    } catch (error) {
      console.error(`❌ Error generating ${isAuto ? 'auto' : 'manual'} conversation:`, error);
      console.log('❌ Full error details:', error.response?.data || error.message);
    } finally {
      setConversationLoading(false);
    }
  };

  const toggleFastForward = async () => {
    try {
      await axios.post(`${API}/simulation/fast-forward`, {}, {
        headers: { Authorization: `Bearer ${token}` }
      });
      // Debounced refresh instead of immediate
      setTimeout(() => fetchSimulationState(), 200);
    } catch (error) {
      console.error('Error fast forwarding:', error);
    }
  };

  const startFreshSimulation = async () => {
    // Show confirmation modal instead of immediate action
    setShowStartFreshModal(true);
  };

  const confirmStartFresh = async () => {
    setShowStartFreshModal(false);
    
    try {
      setLoading(true);
      
      console.log('🧹 Starting fresh - clearing all data...');
      
      // Call the backend reset endpoint to clear everything
      const response = await axios.post(`${API}/simulation/reset`, {}, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      if (response.data.success) {
        // Clear all frontend state immediately
        setAgents([]);
        setConversations([]);
        setObserverMessages([]);
        setIsRunning(false);
        setIsPaused(false);
        setSimulationState(response.data.state);
        
        // Clear scenario states
        setScenario('');
        setCustomScenario('');
        setScenarioName('');
        setShowSetScenario(false);
        
        console.log('✅ Fresh state created - all data cleared successfully');
        
        // Trigger Observatory refresh if needed
        if (refreshTrigger) {
          // This will update the Observatory component
          console.log('🔄 Triggering Observatory refresh');
        }
      } else {
        throw new Error(response.data.message || 'Failed to reset simulation');
      }
      
    } catch (error) {
      console.error('❌ Error clearing data:', error);
      
      // Fallback: manual clearing if backend fails
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
      
      // Show error message
      alert('Some data may not have been cleared. Please refresh the page if issues persist.');
      
    } finally {
      setLoading(false);
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
      
      // Optimistic update: Add agent to UI immediately
      if (response.data) {
        setAgents(prevAgents => [...prevAgents, response.data]);
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
      // Optimistic update: Remove agent from UI immediately
      setAgents(prevAgents => prevAgents.filter(agent => agent.id !== agentId));
      
      await axios.delete(`${API}/agents/${agentId}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
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
      
      // Optimistic update
      setScenario(customScenario);
      setShowSetScenario(false);
      
      await axios.post(`${API}/simulation/set-scenario`, { // Fixed endpoint name
        scenario: customScenario,
        scenario_name: scenarioName
      }, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      // Debounced refresh
      setTimeout(() => fetchSimulationState(), 200);
    } catch (error) {
      console.error('Error setting scenario:', error);
      // Revert optimistic update on error
      setScenario('');
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

  const handleSendObserverMessage = async () => {
    if (!observerMessage.trim()) return;

    const newMessage = {
      id: Date.now(),
      agent_name: "Observer (You)",
      message: observerMessage,
      timestamp: new Date().toISOString()
    };
    const messageToSend = observerMessage;

    try {
      setIsObserverLoading(true);
      
      // Optimistic update: Add message to UI immediately
      setObserverMessages(prev => [...prev, newMessage]);
      setObserverMessage(''); // Clear input immediately for better UX

      await axios.post(`${API}/observer/send-message`, { // Fixed endpoint name
        observer_message: messageToSend
      }, {
        headers: { Authorization: `Bearer ${token}` }
      });

      // Debounced refresh for new agent responses
      setTimeout(() => fetchSimulationState(), 300);
    } catch (error) {
      console.error('Error sending observer message:', error);
      // Revert optimistic updates on error
      setObserverMessages(prev => prev.filter(msg => msg.id !== newMessage.id));
      setObserverMessage(messageToSend);
    } finally {
      setIsObserverLoading(false);
    }
  };

  const handleGenerateReport = async () => {
    try {
      setReportLoading(true);
      setShowReport(true);
      setReportData(''); // Clear previous report
      
      const response = await axios.post(`${API}/simulation/generate-summary`, {}, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      setReportData(response.data.summary || 'No report data available');
    } catch (error) {
      console.error('Error generating report:', error);
      setReportData('Error generating report: ' + (error.response?.data?.detail || error.message));
    } finally {
      setReportLoading(false);
    }
  };

  const performSearch = (term) => {
    if (!term.trim()) {
      setSearchResults([]);
      setCurrentSearchIndex(0);
      return;
    }

    const results = [];
    
    // Search observer messages
    observerMessages.forEach((message, messageIndex) => {
      if (message.message.toLowerCase().includes(term.toLowerCase())) {
        results.push({
          type: 'observer',
          conversationIndex: -1,
          messageIndex,
          message
        });
      }
    });
    
    // Search regular conversations
    conversations.forEach((conversation, conversationIndex) => {
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
    
    if (searchRefs.current[newIndex]) {
      searchRefs.current[newIndex].scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
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

  return (
    <>
      <div className="relative">
        {/* Notification Bar - Enhanced with Scenario Display */}
        <div className="mb-1 h-[2rem] flex items-center justify-center -mt-1">
          <AnimatePresence>
            {/* Show scenario info when scenario is set */}
            {scenarioName && (
              <motion.div
                initial={{ opacity: 0, x: 400 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -400 }}
                transition={{
                  duration: 1.2,
                  ease: "easeOut"
                }}
                className="flex items-center space-x-2 text-white text-lg font-semibold"
              >
                <span>📋 {scenarioName}</span>
                <button
                  onClick={() => setScenarioExpanded(!scenarioExpanded)}
                  className="text-white/80 hover:text-white transition-colors p-1 rounded-full hover:bg-white/10"
                  title={scenarioExpanded ? "Collapse scenario details" : "Expand scenario details"}
                >
                  <svg 
                    className={`w-4 h-4 transition-transform duration-200 ${scenarioExpanded ? 'rotate-180' : ''}`}
                    fill="none" 
                    stroke="currentColor" 
                    viewBox="0 0 24 24"
                  >
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                  </svg>
                </button>
              </motion.div>
            )}
            
            {/* Show welcome message when no scenario is set */}
            {!scenarioName && notificationVisible && (
              <motion.div
                initial={{ opacity: 0, x: 400 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -400 }}
                transition={{
                  duration: 1.2,
                  ease: "easeOut"
                }}
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
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              transition={{ duration: 0.3 }}
              className="mb-4 bg-white/10 backdrop-blur-lg rounded-xl p-6 border border-white/20 shadow-lg"
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

        {/* Live Conversations Section - 50% width on large screens (Middle Position) */}
        <div className="col-span-1 sm:col-span-1 md:col-span-1 lg:col-span-2 xl:col-span-2 2xl:col-span-2">
          <div className="bg-white/10 backdrop-blur-lg rounded-xl p-6 h-[600px] flex flex-col">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-bold text-white">💬 Live Conversations</h3>
              <div className="flex items-center space-x-1">
                <div className={`w-2 h-2 rounded-full ${isRunning ? 'bg-green-400 animate-pulse' : 'bg-gray-400'}`}></div>
                {autoGenerating && (
                  <div className="w-1.5 h-1.5 rounded-full bg-blue-400 animate-ping"></div>
                )}
                <span className="text-white/60 text-sm">
                  {conversations.length} rounds, {observerMessages.length} messages
                </span>
              </div>
            </div>

            {/* Compact Search Bar */}
            <div className="mb-3">
              <div className="flex space-x-2">
                <div className="flex-1 relative">
                  <input
                    type="text"
                    value={searchTerm}
                    onChange={(e) => {
                      setSearchTerm(e.target.value);
                      performSearch(e.target.value);
                    }}
                    placeholder="Search conversations..."
                    className="w-full bg-white/10 border border-white/20 rounded-2xl px-3 py-2 pl-8 text-white placeholder-white/50 focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
                  />
                  <svg className="absolute left-2 top-2.5 w-4 h-4 text-white/50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                  </svg>
                </div>
                {searchResults.length > 0 && (
                  <div className="flex space-x-1">
                    <button
                      onClick={() => navigateSearch('prev')}
                      className="px-2 py-1 bg-white/10 hover:bg-white/20 text-white rounded-xl text-xs"
                    >
                      ↑
                    </button>
                    <span className="px-2 py-1 text-white/60 text-xs">
                      {currentSearchIndex + 1}/{searchResults.length}
                    </span>
                    <button
                      onClick={() => navigateSearch('next')}
                      className="px-2 py-1 bg-white/10 hover:bg-white/20 text-white rounded-xl text-xs"
                    >
                      ↓
                    </button>
                  </div>
                )}
              </div>
            </div>

            {/* Conversations Display */}
            <div className="flex-1 overflow-y-auto space-y-3">
              {conversations.length === 0 && observerMessages.length === 0 ? (
                <div className="text-center py-8 space-y-4">
                  <div>
                    <p className="text-white/60 text-sm mb-2">No conversations yet</p>
                    <div className="text-white/40 text-xs space-y-1">
                      <p>1. add agents</p>
                      <p>2. set scenario</p>
                      <p>3. observe</p>
                    </div>
                  </div>
                </div>
              ) : (
                <>
                  {/* Display Observer Messages */}
                  {observerMessages.map((message, messageIndex) => (
                    <div
                      key={`observer-${message.id || messageIndex}`}
                      className="rounded-2xl p-3 border-l-4 bg-blue-500/20 border-blue-500 shadow-lg transition-all duration-200"
                    >
                      <div className="flex items-start space-x-3">
                        <div className="flex-shrink-0">
                          <div className="w-8 h-8 rounded-full flex items-center justify-center text-white text-xs font-bold bg-blue-600">
                            👁️
                          </div>
                        </div>
                        <div className="flex-1">
                          <div className="flex items-center space-x-2 mb-1">
                            <span className="font-bold text-blue-300">
                              Observer (You)
                            </span>
                            <span className="text-white/40 text-xs">
                              {message.timestamp ? new Date(message.timestamp).toLocaleTimeString() : 'Now'}
                            </span>
                          </div>
                          <p className="text-sm leading-relaxed text-blue-100 font-medium">
                            {message.message}
                          </p>
                        </div>
                      </div>
                    </div>
                  ))}
                  
                  {/* Display Regular Conversations */}
                  {conversations.map((conversation, conversationIndex) => (
                    <div key={conversation.id || conversationIndex} className="space-y-2">
                      {conversation.messages?.map((message, messageIndex) => {
                        const isCurrentSearch = searchResults.length > 0 && 
                          searchResults[currentSearchIndex]?.conversationIndex === conversationIndex && 
                          searchResults[currentSearchIndex]?.messageIndex === messageIndex;
                        const isHighlighted = searchResults.some(result => 
                          result.conversationIndex === conversationIndex && result.messageIndex === messageIndex
                        );

                        return (
                          <div
                            key={message.id || messageIndex}
                            ref={isCurrentSearch ? (el) => searchRefs.current[currentSearchIndex] = el : null}
                            className={`rounded-2xl p-3 border-l-4 ${
                              message.agent_name === "Observer (You)"
                                ? 'bg-blue-500/20 border-blue-500 shadow-lg'
                                : isCurrentSearch 
                                  ? 'border-yellow-400 bg-yellow-400/10' 
                                  : isHighlighted 
                                    ? 'border-blue-400 bg-blue-400/10' 
                                    : 'bg-white/5 border-white/20'
                            } transition-all duration-200`}
                          >
                        <div className="flex items-start space-x-3">
                          <div className="flex-shrink-0">
                            <div className={`w-8 h-8 rounded-full flex items-center justify-center text-white text-xs font-bold ${
                              message.agent_name === "Observer (You)"
                                ? 'bg-blue-600'
                                : `bg-gradient-to-br from-purple-500 to-pink-500`
                            }`}>
                              {message.agent_name === "Observer (You)" ? '👁️' : message.agent_name.split(' ').map(n => n[0]).join('').slice(0, 2)}
                            </div>
                          </div>
                          <div className="flex-1">
                            <div className="flex items-center space-x-2 mb-1">
                              <span className={`font-bold ${
                                message.agent_name === "Observer (You)"
                                  ? 'text-blue-300'
                                  : 'text-white'
                              }`}>
                                {message.agent_name}
                              </span>
                              <span className="text-white/40 text-xs">
                                {message.timestamp ? new Date(message.timestamp).toLocaleTimeString() : 'Now'}
                              </span>
                            </div>
                            <p className={`text-sm leading-relaxed ${
                              message.agent_name === "Observer (You)"
                                ? 'text-blue-100 font-medium'
                                : 'text-white/90'
                            }`}>
                              {highlightSearchTerm(message.message, searchTerm)}
                            </p>
                          </div>
                        </div>
                      </div>
                    );
                      })}
                    </div>
                  ))}
                  <div ref={messagesEndRef} />
                </>
              )}
            </div>

            {/* Observer Input Section */}
            {showObserverChat && (
              <div className="mt-2 p-4 bg-white/5 rounded-2xl border border-purple-500/30">
                <h4 className="text-white font-medium mb-3 flex items-center space-x-2">
                  <span className="text-blue-400">👁️</span>
                  <span>Observer Control</span>
                </h4>
                <div className="flex space-x-2">
                  <input
                    type="text"
                    value={observerMessage}
                    onChange={(e) => setObserverMessage(e.target.value)}
                    placeholder="Enter observer message..."
                    className="flex-1 bg-white/10 border border-white/20 rounded-2xl px-3 py-2 text-white placeholder-white/50 focus:outline-none focus:ring-2 focus:ring-blue-500"
                    onKeyPress={(e) => {
                      if (e.key === 'Enter') {
                        handleSendObserverMessage();
                      }
                    }}
                  />
                  <button
                    onClick={handleSendObserverMessage}
                    disabled={!observerMessage.trim() || isObserverLoading}
                    className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 text-white px-4 py-2 rounded-2xl transition-colors duration-200 disabled:cursor-not-allowed"
                  >
                    {isObserverLoading ? 'Sending...' : 'Send'}
                  </button>
                </div>
              </div>
            )}
          </div>
          
          {/* Control Buttons - Outside of Live Conversations card but in same column */}
          <div className="mt-4">
            <div className="grid grid-cols-4 gap-1 py-3 max-w-xs mx-auto">
              {/* Play/Pause Button */}
              <div className="flex flex-col items-center group">
                <button
                  onClick={playPauseSimulation}
                  className={`w-8 h-8 rounded-full transition-all duration-200 flex items-center justify-center text-white text-sm ${
                    isRunning && !isPaused
                      ? 'bg-orange-600 hover:bg-orange-700' 
                      : 'bg-emerald-600 hover:bg-emerald-700'
                  }`}
                  title={isRunning && !isPaused ? 'Pause' : 'Play'}
                >
                  {isRunning && !isPaused ? '⏸' : '▶'}
                </button>
                <span className="text-white/60 text-xs mt-1 opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap">
                  {isRunning && !isPaused ? 'Pause' : 'Play'}
                </span>
              </div>

              {/* Observer Button */}
              <div className="flex flex-col items-center group">
                <button
                  onClick={() => setShowObserverChat(!showObserverChat)}
                  className={`w-8 h-8 rounded-full transition-all duration-200 flex items-center justify-center text-white text-sm ${
                    showObserverChat 
                      ? 'bg-blue-600 hover:bg-blue-700' 
                      : 'bg-gray-600 hover:bg-gray-700'
                  }`}
                  title="Observer"
                >
                  👁
                </button>
                <span className="text-white/60 text-xs mt-1 opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap">
                  Observer
                </span>
              </div>

              {/* Fast Forward Button */}
              <div className="flex flex-col items-center group">
                <button
                  onClick={toggleFastForward}
                  disabled={!isRunning || isPaused}
                  className={`w-8 h-8 rounded-full transition-all duration-200 flex items-center justify-center text-white text-sm ${
                    isRunning && !isPaused
                      ? 'bg-purple-600 hover:bg-purple-700' 
                      : 'bg-gray-600 cursor-not-allowed text-gray-400'
                  }`}
                  title="Fast Forward"
                >
                  »
                </button>
                <span className="text-white/60 text-xs mt-1 opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap">
                  Fast Forward
                </span>
              </div>

              {/* Start Fresh Button */}
              <div className="flex flex-col items-center group">
                <button
                  onClick={startFreshSimulation}
                  className="w-8 h-8 rounded-full bg-red-600 hover:bg-red-700 text-white transition-all duration-200 flex items-center justify-center text-sm"
                  title="Start Fresh"
                >
                  ↻
                </button>
                <span className="text-white/60 text-xs mt-1 opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap">
                  Fresh Start
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Scenario Setup Section - 25% width on large screens (Right Position) */}
        <div className="lg:col-span-1">
          <div className="bg-white/10 backdrop-blur-lg rounded-xl p-6 h-[600px] flex flex-col">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-bold text-white">🎛️ Control Desk</h3>
            </div>
            
            {/* Set Scenario Section with expandable functionality */}
            <div className="mb-4">
              <div className="flex justify-between items-center mb-2">
                <h4 className="text-white/80 text-sm font-medium">Set Scenario</h4>
                <button
                  onClick={() => setShowSetScenario(!showSetScenario)}
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
                      className="w-full px-3 py-2 bg-white/10 border border-white/20 rounded-lg text-white placeholder-white/50 focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
                    />
                    <div className="relative">
                      <textarea
                        value={customScenario}
                        onChange={(e) => setCustomScenario(e.target.value)}
                        placeholder="enter your scenario here..."
                        disabled={loading || isRunning || isRecording}
                        className="w-full px-3 py-2 pb-12 bg-white/10 border border-white/20 rounded-lg text-white placeholder-white/50 focus:ring-2 focus:ring-blue-500 disabled:opacity-50 resize-none"
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

            {/* Generate Report Section with expandable functionality */}
            <div className="mb-4">
              <div className="flex justify-between items-center mb-2">
                <h4 className="text-white/80 text-sm font-medium">Generate Report</h4>
                <button
                  onClick={() => setShowReport(!showReport)}
                  className="text-white/60 hover:text-white transition-all duration-200"
                  style={{ transform: showReport ? 'rotate(180deg)' : 'rotate(0deg)' }}
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                  </svg>
                </button>
              </div>
              
              {/* Report Content Section */}
              <div className="flex-1">
                {/* Expandable Report Section */}
                {showReport && (
                  <div className="bg-white/5 rounded-lg p-4 space-y-3 animate-fadeIn">
                    <div className="flex space-x-2 mb-3">
                      <button
                        onClick={handleGenerateReport}
                        disabled={reportLoading || conversations.length === 0}
                        className="flex-1 px-4 py-2 bg-purple-600 hover:bg-purple-700 disabled:bg-gray-600 text-white rounded-lg transition-colors disabled:cursor-not-allowed"
                      >
                        {reportLoading ? 'Generating...' : 'Generate Weekly Report'}
                      </button>
                    </div>
                    
                    {/* Report Display */}
                    {reportData && (
                      <div className="bg-white/5 rounded-lg p-4 max-h-80 overflow-y-auto">
                        <div className="text-white/90 text-sm leading-relaxed whitespace-pre-wrap">
                          {reportData}
                        </div>
                      </div>
                    )}
                    
                    {conversations.length === 0 && (
                      <div className="text-white/50 text-xs text-center py-2">
                        No conversations available for report generation
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>

          </div>
        </div>
      </div>

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
                  disabled={loading}
                  className="px-4 py-2 bg-red-600 hover:bg-red-700 disabled:bg-gray-600 text-white rounded-lg transition-colors"
                >
                  {loading ? 'Clearing...' : 'Start Fresh'}
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
    </>
  );
};

export default SimulationControl;