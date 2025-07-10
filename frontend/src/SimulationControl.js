import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import axios from 'axios';
import { useAuth } from './AuthContext';
import AgentCreateModal from './AgentCreateModal';

const API = process.env.REACT_APP_BACKEND_URL ? `${process.env.REACT_APP_BACKEND_URL}/api` : 'http://localhost:8001/api';

// Welcome messages for notification bar
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

const SimulationControl = () => {
  const { user } = useAuth();
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
  const [observerMessage, setObserverMessage] = useState('');
  const [observerMessages, setObserverMessages] = useState([]);
  const [isObserverLoading, setIsObserverLoading] = useState(false);
  const [notificationVisible, setNotificationVisible] = useState(false);
  const [notificationText, setNotificationText] = useState('');
  const searchRefs = useRef([]);
  const messagesEndRef = useRef(null);

  const [newAgent, setNewAgent] = useState({
    name: '',
    archetype: '',
    expertise: '',
    background: '',
    goal: '',
    avatar_url: ''
  });

  // Initialize
  useEffect(() => {
    fetchSimulationState();
    const welcomeMessage = WELCOME_MESSAGES[Math.floor(Math.random() * WELCOME_MESSAGES.length)];
    showNotification(welcomeMessage);
    
    // Set up periodic refresh to check for new agents
    const interval = setInterval(() => {
      fetchSimulationState();
    }, 5000); // Refresh every 5 seconds
    
    return () => clearInterval(interval);
  }, []);

  // Auto-scroll to bottom of conversations
  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [conversations, observerMessages]);

  const showNotification = (text) => {
    setNotificationText(text);
    setNotificationVisible(true);
    setTimeout(() => {
      setNotificationVisible(false);
    }, 3000);
  };

  const fetchSimulationState = async () => {
    try {
      const response = await axios.get(`${API}/simulation/state`, {
        headers: { Authorization: `Bearer ${user?.token}` }
      });
      setSimulationState(response.data);
      setAgents(response.data.agents || []);
      setConversations(response.data.conversations || []);
      setIsRunning(response.data.is_active || false);
      setIsPaused(response.data.is_paused || false);
      
      // Also try to fetch available agents that might not be in simulation yet
      try {
        const agentsResponse = await axios.get(`${API}/agents`, {
          headers: { Authorization: `Bearer ${user?.token}` }
        });
        console.log('Available agents:', agentsResponse.data);
      } catch (agentError) {
        console.log('Could not fetch additional agents:', agentError);
      }
    } catch (error) {
      console.error('Error fetching simulation state:', error);
    }
  };

  const playPauseSimulation = async () => {
    try {
      setLoading(true);
      const endpoint = isRunning && !isPaused ? '/simulation/pause' : '/simulation/start';
      await axios.post(`${API}${endpoint}`, {}, {
        headers: { Authorization: `Bearer ${user?.token}` }
      });
      await fetchSimulationState();
    } catch (error) {
      console.error('Error controlling simulation:', error);
    } finally {
      setLoading(false);
    }
  };

  const toggleFastForward = async () => {
    try {
      await axios.post(`${API}/simulation/fast-forward`, {}, {
        headers: { Authorization: `Bearer ${user?.token}` }
      });
      await fetchSimulationState();
    } catch (error) {
      console.error('Error fast forwarding:', error);
    }
  };

  const startFreshSimulation = async () => {
    try {
      setLoading(true);
      await axios.post(`${API}/simulation/reset`, {}, {
        headers: { Authorization: `Bearer ${user?.token}` }
      });
      await fetchSimulationState();
      setConversations([]);
      setObserverMessages([]);
    } catch (error) {
      console.error('Error starting fresh:', error);
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
        headers: { Authorization: `Bearer ${user?.token}` }
      });
      
      // Add to simulation
      await axios.post(`${API}/simulation/agents`, { agent_id: response.data.id }, {
        headers: { Authorization: `Bearer ${user?.token}` }
      });
      
      await fetchSimulationState();
      setShowCreateAgentModal(false);
    } catch (error) {
      console.error('Error creating agent:', error);
    }
  };

  const handleRemoveAgent = async (agentId) => {
    try {
      await axios.delete(`${API}/simulation/agents/${agentId}`, {
        headers: { Authorization: `Bearer ${user?.token}` }
      });
      await fetchSimulationState();
    } catch (error) {
      console.error('Error removing agent:', error);
    }
  };

  const handleEditAgent = (agent) => {
    setEditingAgent(agent);
    setShowEditModal(true);
  };

  const handleSaveAgent = async (formData) => {
    try {
      await axios.put(`${API}/agents/${editingAgent.id}`, formData, {
        headers: { Authorization: `Bearer ${user?.token}` }
      });
      await fetchSimulationState();
      setShowEditModal(false);
      setEditingAgent(null);
    } catch (error) {
      console.error('Error saving agent:', error);
    }
  };

  const getRandomScenario = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API}/scenarios/random`, {
        headers: { Authorization: `Bearer ${user?.token}` }
      });
      setCustomScenario(response.data.description);
      setScenarioName(response.data.name);
    } catch (error) {
      console.error('Error getting random scenario:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSetScenario = async () => {
    try {
      setLoading(true);
      await axios.post(`${API}/simulation/scenario`, {
        scenario: customScenario,
        scenario_name: scenarioName
      }, {
        headers: { Authorization: `Bearer ${user?.token}` }
      });
      setScenario(customScenario);
      setShowSetScenario(false);
      await fetchSimulationState();
    } catch (error) {
      console.error('Error setting scenario:', error);
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

    try {
      setIsObserverLoading(true);
      const newMessage = {
        id: Date.now(),
        agent_name: "Observer (You)",
        message: observerMessage,
        timestamp: new Date().toISOString()
      };
      
      setObserverMessages(prev => [...prev, newMessage]);
      setObserverMessage('');

      await axios.post(`${API}/simulation/observer-message`, {
        message: observerMessage
      }, {
        headers: { Authorization: `Bearer ${user?.token}` }
      });

      await fetchSimulationState();
    } catch (error) {
      console.error('Error sending observer message:', error);
    } finally {
      setIsObserverLoading(false);
    }
  };

  const performSearch = (term) => {
    if (!term.trim()) {
      setSearchResults([]);
      setCurrentSearchIndex(0);
      return;
    }

    const results = [];
    [...conversations, ...observerMessages].forEach((conversation, conversationIndex) => {
      if (conversation.messages) {
        conversation.messages.forEach((message, messageIndex) => {
          if (message.message.toLowerCase().includes(term.toLowerCase())) {
            results.push({
              conversationIndex,
              messageIndex,
              message
            });
          }
        });
      } else if (conversation.message && conversation.message.toLowerCase().includes(term.toLowerCase())) {
        results.push({
          conversationIndex: -1,
          messageIndex: conversationIndex,
          message: conversation
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
        <div className="flex justify-between items-center">
          <h2 className="text-2xl font-bold text-white mb-0">🔬 Observatory</h2>
          <div className="text-white/60 text-sm">
            {agents.length} agents • {conversations.length} rounds
          </div>
        </div>
        
        {/* Notification Bar - Between header and cards */}
        <AnimatePresence>
          {notificationVisible && (
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className="text-center mt-4 mb-2 text-white text-sm font-medium"
            >
              {notificationText}
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* Main Grid Layout - 3 Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-4 md:gap-5 lg:gap-6 xl:gap-6 2xl:gap-8">
        
        {/* Agent List Section - 25% width on large screens (Left Position) */}
        <div className="lg:col-span-1">
          <div className="bg-white/10 backdrop-blur-lg rounded-xl p-6 h-full min-h-[400px] md:min-h-[450px] lg:min-h-[500px] xl:min-h-[550px] 2xl:min-h-[600px]">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-bold text-white">🤖 Agent List</h3>
              <div className="flex items-center space-x-2">
                <div className={`w-2 h-2 rounded-full ${agents.length > 0 ? 'bg-green-400' : 'bg-gray-400'}`}></div>
                <span className="text-white/60 text-sm">{agents.length}</span>
                <button
                  onClick={() => {
                    // Click the Agent Library tab in the navigation
                    const tabs = document.querySelectorAll('a, button');
                    for (const tab of tabs) {
                      if (tab.textContent && tab.textContent.toLowerCase().includes('agent library')) {
                        tab.click();
                        break;
                      }
                    }
                  }}
                  className="ml-2 w-6 h-6 bg-green-600 hover:bg-green-700 text-white rounded-full flex items-center justify-center transition-colors text-sm"
                  title="Open Agent Library"
                >
                  +
                </button>
              </div>
            </div>
            
            {agents.length > 0 ? (
              <div className="space-y-3 mb-4">
                {agents.map((agent) => (
                  <div
                    key={agent.id}
                    className="bg-white/5 rounded-lg p-4 border border-white/10 hover:border-white/20 transition-colors group"
                  >
                    <div className="flex items-start justify-between mb-2">
                      <div className="flex items-center space-x-3">
                        <div className="w-10 h-10 rounded-full bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center">
                          {agent.avatar_url ? (
                            <img src={agent.avatar_url} alt={agent.name} className="w-full h-full rounded-full object-cover" />
                          ) : (
                            <span className="text-white text-sm font-semibold">
                              {agent.name?.charAt(0) || '🤖'}
                            </span>
                          )}
                        </div>
                        <div>
                          <h4 className="text-white font-medium text-sm">{agent.name}</h4>
                          <p className="text-white/60 text-xs capitalize">{agent.archetype}</p>
                        </div>
                      </div>
                      
                      <div className="flex items-center space-x-1 opacity-0 group-hover:opacity-100 transition-opacity">
                        <button
                          onClick={() => handleEditAgent(agent)}
                          className="text-white/60 hover:text-white p-1 rounded transition-colors"
                          title="Edit Agent"
                        >
                          ✏️
                        </button>
                        <button
                          onClick={() => handleRemoveAgent(agent.id)}
                          className="text-white/60 hover:text-red-400 p-1 rounded transition-colors"
                          title="Remove Agent"
                        >
                          🗑️
                        </button>
                      </div>
                    </div>
                    
                    <p className="text-white/70 text-xs line-clamp-2 mb-2">
                      {agent.background || agent.expertise}
                    </p>
                    
                    {agent.goal && (
                      <div className="text-white/50 text-xs">
                        Goal: {agent.goal}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8">
                <div className="text-4xl mb-2">🤖</div>
                <p className="text-white/60 text-sm mb-4">No Agents in List</p>
                <p className="text-white/40 text-xs mb-4">Click + to add agents from library</p>
              </div>
            )}
          </div>
        </div>

        {/* Live Conversations Section - 50% width on large screens (Middle Position) */}
        <div className="col-span-1 sm:col-span-1 md:col-span-1 lg:col-span-2 xl:col-span-2 2xl:col-span-2">
          <div className="bg-white/10 backdrop-blur-lg rounded-xl p-4 sm:p-5 md:p-5 lg:p-6 xl:p-6 2xl:p-8 h-full min-h-[400px] md:min-h-[450px] lg:min-h-[500px] xl:min-h-[550px] 2xl:min-h-[600px] flex flex-col">
            <div className="flex flex-col sm:flex-col md:flex-row lg:flex-row xl:flex-row 2xl:flex-row justify-between items-start md:items-center mb-4 space-y-2 md:space-y-0">
              <h3 className="text-lg sm:text-lg md:text-xl lg:text-xl xl:text-2xl 2xl:text-2xl font-bold text-white">💬 Live Conversations</h3>
              <div className="flex flex-wrap items-center space-x-2 sm:space-x-2 md:space-x-3 lg:space-x-3 xl:space-x-3 2xl:space-x-4">
                <div className={`w-2 h-2 sm:w-2 h-2 md:w-3 h-3 lg:w-3 h-3 xl:w-3 h-3 2xl:w-4 h-4 rounded-full ${isRunning ? 'bg-green-400 animate-pulse' : 'bg-gray-400'}`}></div>
                {autoGenerating && (
                  <div className="w-1.5 h-1.5 sm:w-1.5 h-1.5 md:w-2 h-2 lg:w-2 h-2 xl:w-2 h-2 2xl:w-2 h-2 rounded-full bg-blue-400 animate-ping"></div>
                )}
                <span className="text-white/60 text-xs sm:text-xs md:text-sm lg:text-sm xl:text-sm 2xl:text-base">
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
                    placeholder="Search..."
                    className="w-full px-3 py-1 text-sm bg-white/10 border border-white/20 rounded text-white placeholder-white/40 focus:ring-1 focus:ring-blue-500"
                  />
                  {searchTerm && (
                    <button
                      onClick={() => {
                        setSearchTerm('');
                        setSearchResults([]);
                        setCurrentSearchIndex(0);
                      }}
                      className="absolute right-1 top-1/2 transform -translate-y-1/2 text-white/60 hover:text-white text-xs"
                    >
                      ✕
                    </button>
                  )}
                </div>
                {searchResults.length > 0 && (
                  <div className="flex items-center space-x-1">
                    <span className="text-white/60 text-xs">
                      {currentSearchIndex + 1}/{searchResults.length}
                    </span>
                    <button
                      onClick={() => navigateSearch('prev')}
                      className="px-1 py-1 bg-gray-600 hover:bg-gray-700 text-white text-xs rounded transition-colors"
                    >
                      ↑
                    </button>
                    <button
                      onClick={() => navigateSearch('next')}
                      className="px-1 py-1 bg-gray-600 hover:bg-gray-700 text-white text-xs rounded transition-colors"
                    >
                      ↓
                    </button>
                  </div>
                )}
              </div>
            </div>

            {/* Conversations Display */}
            <div className="flex-1 overflow-y-auto max-h-[300px] md:max-h-[350px] lg:max-h-[400px] xl:max-h-[450px] 2xl:max-h-[500px] space-y-3 mb-4">
              {conversations.length === 0 && observerMessages.length === 0 ? (
                <div className="text-center py-8 space-y-4">
                  <div className="text-4xl">💬</div>
                  <div>
                    <p className="text-white/60 text-sm mb-2">No conversations yet</p>
                    <p className="text-white/40 text-xs">Start simulation to see agent conversations</p>
                  </div>
                </div>
              ) : (
                <>
                  {observerMessages.map((message, messageIndex) => {
                    const isCurrentSearch = searchResults.length > 0 && 
                      searchResults[currentSearchIndex]?.conversationIndex === -1 && 
                      searchResults[currentSearchIndex]?.messageIndex === messageIndex;
                    const isHighlighted = searchResults.some(result => 
                      result.conversationIndex === -1 && result.messageIndex === messageIndex
                    );

                    return (
                      <div
                        key={message.id || messageIndex}
                        ref={isCurrentSearch ? (el) => searchRefs.current[currentSearchIndex] = el : null}
                        className={`rounded-lg p-3 border-l-4 ${
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
                          <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
                            message.agent_name === "Observer (You)"
                              ? 'bg-gradient-to-br from-blue-600 to-blue-800'
                              : 'bg-gradient-to-br from-purple-500 to-pink-500'
                          }`}>
                            <span className="text-white text-xs font-semibold">
                              {message.agent_name === "Observer (You)" ? '👁️' : (message.agent_name?.[0] || '🤖')}
                            </span>
                          </div>
                          <div className="flex-1">
                            <div className="flex items-center space-x-2 mb-1">
                              <span className={`font-medium text-sm ${
                                message.agent_name === "Observer (You)"
                                  ? 'text-blue-300'
                                  : 'text-white'
                              }`}>
                                {message.agent_name}
                                {message.agent_name === "Observer (You)" && (
                                  <span className="ml-1 text-xs bg-blue-600 px-1 py-0.5 rounded">CEO</span>
                                )}
                              </span>
                              <span className="text-white/40 text-xs">
                                {new Date(message.timestamp).toLocaleTimeString()}
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

                  {conversations.map((conversation, conversationIndex) => (
                    <div key={conversationIndex} className="space-y-2">
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
                            className={`rounded-lg p-3 border-l-4 ${
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
                              <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
                                message.agent_name === "Observer (You)"
                                  ? 'bg-gradient-to-br from-blue-600 to-blue-800'
                                  : 'bg-gradient-to-br from-purple-500 to-pink-500'
                              }`}>
                                <span className="text-white text-xs font-semibold">
                                  {message.agent_name === "Observer (You)" ? '👁️' : (message.agent_name?.[0] || '🤖')}
                                </span>
                              </div>
                              <div className="flex-1">
                                <div className="flex items-center space-x-2 mb-1">
                                  <span className={`font-medium text-sm ${
                                    message.agent_name === "Observer (You)"
                                      ? 'text-blue-300'
                                      : 'text-white'
                                  }`}>
                                    {message.agent_name}
                                    {message.agent_name === "Observer (You)" && (
                                      <span className="ml-1 text-xs bg-blue-600 px-1 py-0.5 rounded">CEO</span>
                                    )}
                                  </span>
                                  <span className="text-white/40 text-xs">
                                    {new Date(message.timestamp).toLocaleTimeString()}
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
              <div className="mt-4 p-4 bg-white/5 rounded-lg border border-purple-500/30">
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
                    className="flex-1 bg-white/10 border border-white/20 rounded-lg px-3 py-2 text-white placeholder-white/50 focus:outline-none focus:ring-2 focus:ring-blue-500"
                    onKeyPress={(e) => {
                      if (e.key === 'Enter') {
                        handleSendObserverMessage();
                      }
                    }}
                  />
                  <button
                    onClick={handleSendObserverMessage}
                    disabled={!observerMessage.trim() || isObserverLoading}
                    className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 text-white px-4 py-2 rounded-lg transition-colors duration-200 disabled:cursor-not-allowed"
                  >
                    {isObserverLoading ? 'Sending...' : 'Send'}
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Scenario Setup Section - 25% width on large screens (Right Position) */}
        <div className="lg:col-span-1">
          <div className="bg-white/10 backdrop-blur-lg rounded-xl p-6 h-full">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-bold text-white">📝 Scenario Setup</h3>
              <button
                onClick={() => setShowSetScenario(!showSetScenario)}
                className="flex items-center space-x-2 text-white text-sm font-medium hover:text-blue-300 transition-colors"
              >
                <span className={`transform transition-transform duration-200 ${showSetScenario ? 'rotate-180' : ''}`}>
                  ⬇️
                </span>
              </button>
            </div>
            
            {/* Expandable Scenario Input */}
            {showSetScenario && (
              <div className="bg-white/5 rounded-lg p-4 space-y-3 animate-fadeIn">
                <div className="flex justify-between items-center mb-2">
                  <span className="text-white/60 text-sm">Enter custom scenario or generate random:</span>
                  <button
                    onClick={getRandomScenario}
                    disabled={loading || isRunning}
                    className="px-3 py-1 bg-gray-500 hover:bg-gray-600 text-white text-sm rounded-lg transition-colors disabled:opacity-50"
                  >
                    {loading ? '⏳' : '🎲 Random'}
                  </button>
                </div>
                <div className="relative">
                  <textarea
                    value={customScenario}
                    onChange={(e) => setCustomScenario(e.target.value)}
                    placeholder="Enter your scenario here... (e.g., 'A team of researchers discovers an unexpected signal from deep space')"
                    disabled={loading || isRunning || isRecording}
                    className="w-full px-3 py-2 pr-12 bg-white/10 border border-white/20 rounded-lg text-white placeholder-white/50 focus:ring-2 focus:ring-blue-500 disabled:opacity-50 resize-none"
                    rows="6"
                  />
                  <button
                    onClick={handleVoiceInput}
                    disabled={loading || isRunning}
                    className={`absolute right-2 top-2 p-2 rounded-lg transition-colors disabled:opacity-50 ${
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
                <div className="space-y-2">
                  <input
                    type="text"
                    value={scenarioName}
                    onChange={(e) => setScenarioName(e.target.value)}
                    placeholder="Scenario name (optional)"
                    disabled={loading || isRunning}
                    className="w-full px-3 py-2 bg-white/10 border border-white/20 rounded-lg text-white placeholder-white/50 focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
                  />
                  <button
                    onClick={handleSetScenario}
                    disabled={loading || isRunning || !customScenario.trim()}
                    className="w-full px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 text-white rounded-lg transition-colors disabled:cursor-not-allowed"
                  >
                    {loading ? 'Setting...' : 'Set Scenario'}
                  </button>
                </div>
              </div>
            )}
            
            {/* Current Scenario Display */}
            {!showSetScenario && (simulationState?.scenario || scenario) && (
              <div className="bg-white/5 rounded-lg p-3 animate-fadeIn">
                <h4 className="text-white font-medium text-sm mb-2">Current Scenario:</h4>
                <p className="text-white/80 text-sm mb-3">{simulationState?.scenario_name || scenarioName || 'Custom Scenario'}</p>
                <p className="text-white/60 text-xs mb-3 line-clamp-3">{simulationState?.scenario || scenario}</p>
                <button 
                  onClick={() => setShowSetScenario(true)}
                  className="px-3 py-1 bg-blue-600 hover:bg-blue-700 text-white text-sm rounded transition-colors"
                >
                  Change Scenario
                </button>
              </div>
            )}
            
            {/* No Scenario Set */}
            {!showSetScenario && !simulationState?.scenario && !scenario && (
              <div className="bg-white/5 rounded-lg p-3 text-center animate-fadeIn">
                <p className="text-white/60 text-xs mb-3">Set a scenario to guide your simulation</p>
                <button 
                  onClick={() => setShowSetScenario(true)}
                  className="px-3 py-1 bg-blue-600 hover:bg-blue-700 text-white text-sm rounded transition-colors"
                >
                  Set Scenario
                </button>
              </div>
            )}

            {/* Control Buttons - Icon only at bottom of Live Conversations */}
            <div className="mt-auto pt-4 flex justify-center space-x-3">
              {/* Play/Pause Button */}
              <button
                onClick={playPauseSimulation}
                className={`w-8 h-8 rounded-full transition-all duration-200 flex items-center justify-center ${
                  isRunning && !isPaused
                    ? 'bg-orange-600 hover:bg-orange-700 text-white' 
                    : 'bg-emerald-600 hover:bg-emerald-700 text-white'
                }`}
                title={isRunning && !isPaused ? 'Pause' : 'Play'}
              >
                <span className="text-sm">
                  {isRunning && !isPaused ? '⏸️' : '▶️'}
                </span>
              </button>

              {/* Observer Button */}
              <button
                onClick={() => setShowObserverChat(!showObserverChat)}
                className={`w-8 h-8 rounded-full transition-all duration-200 flex items-center justify-center ${
                  showObserverChat 
                    ? 'bg-blue-600 hover:bg-blue-700 text-white' 
                    : 'bg-gray-600 hover:bg-gray-700 text-white'
                }`}
                title="Observer"
              >
                <span className="text-sm">👁️</span>
              </button>

              {/* Fast Forward Button */}
              <button
                onClick={toggleFastForward}
                disabled={!isRunning || isPaused}
                className={`w-8 h-8 rounded-full transition-all duration-200 flex items-center justify-center ${
                  isRunning && !isPaused
                    ? 'bg-purple-600 hover:bg-purple-700 text-white' 
                    : 'bg-gray-600 cursor-not-allowed text-gray-400'
                }`}
                title="Fast Forward"
              >
                <span className="text-sm">⏩</span>
              </button>

              {/* Start Fresh Button */}
              <button
                onClick={startFreshSimulation}
                className="w-8 h-8 rounded-full bg-red-600 hover:bg-red-700 text-white transition-all duration-200 flex items-center justify-center"
                title="Start Fresh"
              >
                <span className="text-sm">🔄</span>
              </button>
            </div>

            {/* Status Display */}
            <div className="mt-3 text-center">
              <div className="inline-flex items-center space-x-2 bg-white/10 rounded-full px-3 py-1">
                <div className={`w-1.5 h-1.5 rounded-full ${
                  isRunning && !isPaused ? 'bg-green-500 animate-pulse' : 'bg-gray-500'
                }`}></div>
                <span className="text-white text-xs">
                  Status: {isRunning && !isPaused ? 'Running' : isPaused ? 'Paused' : 'Stopped'}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

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