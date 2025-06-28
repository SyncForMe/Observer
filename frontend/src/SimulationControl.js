import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import axios from 'axios';
import { useAuth } from './AuthContext';
import ScenarioCreator from './ScenarioCreator';
import WeeklySummary from './WeeklySummary';

const API = process.env.REACT_APP_BACKEND_URL ? `${process.env.REACT_APP_BACKEND_URL}/api` : 'http://localhost:8001/api';

// Agent Edit Modal Component
const AgentEditModal = ({ isOpen, onClose, agent, onSave }) => {
  const [formData, setFormData] = useState({
    name: '',
    archetype: 'scientist',
    expertise: '',
    background: '',
    goal: '',
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

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    try {
      await onSave(agent.id, formData);
      onClose();
    } catch (error) {
      console.error('Error saving agent:', error);
      alert('Failed to save agent. Please try again.');
    }
    setSaving(false);
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        exit={{ opacity: 0, scale: 0.95 }}
        className="bg-white rounded-xl shadow-2xl max-w-5xl w-full max-h-[90vh] overflow-hidden"
      >
        <div className="bg-gradient-to-r from-purple-600 to-blue-600 text-white p-6">
          <div className="flex justify-between items-center">
            <div>
              <h2 className="text-2xl font-bold">✏️ Edit Agent</h2>
              <p className="text-white/80 mt-1">Customize your agent's personality and expertise</p>
            </div>
            <button
              onClick={onClose}
              className="text-white/70 hover:text-white text-2xl p-2 hover:bg-white/10 rounded-lg transition-colors"
            >
              ✕
            </button>
          </div>
        </div>

        <form onSubmit={handleSubmit} className="p-6 overflow-y-auto max-h-[calc(90vh-140px)]">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Agent Profile */}
            <div>
              <div className="flex items-center space-x-4 mb-6">
                <div className="w-24 h-24 bg-gradient-to-br from-purple-500 to-blue-500 rounded-full flex items-center justify-center">
                  {agent?.avatar_url ? (
                    <img 
                      src={agent.avatar_url} 
                      alt={formData.name}
                      className="w-full h-full rounded-full object-cover"
                    />
                  ) : (
                    <span className="text-white text-2xl font-bold">
                      {formData.name?.[0] || '🤖'}
                    </span>
                  )}
                </div>
                <div className="flex-1">
                  <label className="block text-sm font-medium text-gray-700 mb-2">Agent Name</label>
                  <input
                    type="text"
                    value={formData.name}
                    onChange={(e) => setFormData({...formData, name: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
                    placeholder="Enter agent name"
                    required
                  />
                </div>
              </div>

              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Goal</label>
                  <textarea
                    value={formData.goal}
                    onChange={(e) => setFormData({...formData, goal: e.target.value})}
                    rows={3}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
                    placeholder="What is this agent trying to achieve?"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Expertise</label>
                  <input
                    type="text"
                    value={formData.expertise}
                    onChange={(e) => setFormData({...formData, expertise: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
                    placeholder="Areas of expertise"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Background</label>
                  <textarea
                    value={formData.background}
                    onChange={(e) => setFormData({...formData, background: e.target.value})}
                    rows={3}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
                    placeholder="Professional background and experience"
                  />
                </div>
              </div>
            </div>

            {/* Personality Traits */}
            <div>
              <h3 className="text-lg font-semibold text-gray-800 mb-4">Personality Traits</h3>
              <div className="space-y-4">
                {[
                  { key: 'extroversion', label: 'Extroversion', desc: 'How outgoing and social' },
                  { key: 'optimism', label: 'Optimism', desc: 'How positive and hopeful' },
                  { key: 'curiosity', label: 'Curiosity', desc: 'How inquisitive and exploratory' },
                  { key: 'cooperativeness', label: 'Cooperativeness', desc: 'How collaborative and helpful' },
                  { key: 'energy', label: 'Energy', desc: 'How active and enthusiastic' }
                ].map(trait => (
                  <div key={trait.key}>
                    <div className="flex justify-between items-center mb-2">
                      <div>
                        <span className="text-sm font-medium text-gray-700">{trait.label}</span>
                        <p className="text-xs text-gray-500">{trait.desc}</p>
                      </div>
                      <span className="text-sm font-bold text-purple-600">
                        {formData.personality[trait.key]}/10
                      </span>
                    </div>
                    <input
                      type="range"
                      min="1"
                      max="10"
                      value={formData.personality[trait.key]}
                      onChange={(e) => setFormData({
                        ...formData,
                        personality: {
                          ...formData.personality,
                          [trait.key]: parseInt(e.target.value)
                        }
                      })}
                      className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
                    />
                  </div>
                ))}
              </div>
            </div>
          </div>

          <div className="flex justify-end space-x-3 pt-6 border-t border-gray-200 mt-6">
            <button
              type="button"
              onClick={onClose}
              className="px-6 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={saving}
              className="px-6 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors disabled:opacity-50"
            >
              {saving ? 'Saving...' : 'Save Changes'}
            </button>
          </div>
        </form>
      </motion.div>
    </div>
  );
};

const SimulationControl = ({ setActiveTab, activeTab }) => {
  const [simulationState, setSimulationState] = useState(null);
  const [isRunning, setIsRunning] = useState(false);
  const [isPaused, setIsPaused] = useState(false);
  const [autoMode, setAutoMode] = useState(false);
  const [scenario, setScenario] = useState('');
  const [observerMessages, setObserverMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [fastForwardMode, setFastForwardMode] = useState(false);
  const [agents, setAgents] = useState([]);
  const [agentsLoading, setAgentsLoading] = useState(false);
  const [editingAgent, setEditingAgent] = useState(null);
  const [showEditModal, setShowEditModal] = useState(false);
  const [showWeeklyReport, setShowWeeklyReport] = useState(false);
  const [showObserverChat, setShowObserverChat] = useState(false);
  const [showScenarioCreator, setShowScenarioCreator] = useState(false);
  const [conversations, setConversations] = useState([]);
  const [conversationLoading, setConversationLoading] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [currentSearchIndex, setCurrentSearchIndex] = useState(0);
  const [autoGenerating, setAutoGenerating] = useState(false);
  const [expandedScenario, setExpandedScenario] = useState(false);
  const messagesEndRef = useRef(null);
  const searchRefs = useRef([]);
  const { user, token } = useAuth();

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

  // Search functionality
  const performSearch = (term) => {
    if (!term.trim()) {
      setSearchResults([]);
      setCurrentSearchIndex(0);
      return;
    }

    const results = [];
    conversations.forEach((conversation, convIndex) => {
      conversation.messages?.forEach((message, msgIndex) => {
        const messageText = message.message?.toLowerCase() || '';
        const searchLower = term.toLowerCase();
        
        if (messageText.includes(searchLower)) {
          results.push({
            conversationIndex: convIndex,
            messageIndex: msgIndex,
            conversation: conversation,
            message: message,
            text: message.message
          });
        }
      });
    });

    setSearchResults(results);
    setCurrentSearchIndex(0);
    
    // Scroll to first result
    if (results.length > 0) {
      setTimeout(() => {
        const firstRef = searchRefs.current[0];
        if (firstRef) {
          firstRef.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
      }, 100);
    }
  };

  const navigateSearch = (direction) => {
    if (searchResults.length === 0) return;
    
    let newIndex;
    if (direction === 'prev') {
      newIndex = currentSearchIndex > 0 ? currentSearchIndex - 1 : searchResults.length - 1;
    } else {
      newIndex = currentSearchIndex < searchResults.length - 1 ? currentSearchIndex + 1 : 0;
    }
    
    setCurrentSearchIndex(newIndex);
    
    // Scroll to the result
    setTimeout(() => {
      const ref = searchRefs.current[newIndex];
      if (ref) {
        ref.scrollIntoView({ behavior: 'smooth', block: 'center' });
      }
    }, 100);
  };

  const highlightSearchTerm = (text, term, isCurrentResult = false) => {
    if (!term) return text;
    
    const regex = new RegExp(`(${term})`, 'gi');
    const parts = text.split(regex);
    
    return parts.map((part, index) => 
      regex.test(part) ? (
        <mark 
          key={index} 
          className={isCurrentResult ? 'bg-yellow-400 text-black' : 'bg-blue-400 text-white'}
        >
          {part}
        </mark>
      ) : part
    );
  };

  // Scenarios
  const scenarios = [
    "Medical Research Breakthrough",
    "Space Mission Planning", 
    "Climate Change Solutions",
    "AI Ethics Committee",
    "Startup Pitch Competition",
    "Archaeological Discovery",
    "Cybersecurity Crisis",
    "Educational Reform",
    "Urban Planning",
    "Renewable Energy Project"
  ];

  // Fetch conversations
  const fetchConversations = async () => {
    if (!token) return;
    
    setConversationLoading(true);
    try {
      const response = await axios.get(`${API}/conversations`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setConversations(response.data || []);
    } catch (error) {
      console.error('Failed to fetch conversations:', error);
      setConversations([]);
    }
    setConversationLoading(false);
  };

  // Fetch agents
  const fetchAgents = async () => {
    if (!token) return;
    
    setAgentsLoading(true);
    try {
      const response = await axios.get(`${API}/agents`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setAgents(response.data || []);
    } catch (error) {
      console.error('Failed to fetch agents:', error);
      setAgents([]);
    }
    setAgentsLoading(false);
  };

  // Fetch simulation state
  const fetchSimulationState = async () => {
    if (!token) return;
    
    try {
      const response = await axios.get(`${API}/simulation/state`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setSimulationState(response.data);
      
      // Update running state based on backend response
      const backendIsActive = response.data?.is_active || false;
      setIsRunning(backendIsActive);
      
      // If simulation is not active in backend, it's not paused either
      if (!backendIsActive) {
        setIsPaused(false);
      }
      
    } catch (error) {
      console.error('Failed to fetch simulation state:', error);
    }
  };

  // Clear all agents
  const clearAllAgents = async () => {
    if (!token) return;
    
    if (!confirm(
      `Are you sure you want to remove all ${agents.length} agents from the simulation? This action cannot be undone.`
    )) {
      return;
    }

    setLoading(true);
    try {
      // Remove each agent
      for (const agent of agents) {
        await axios.delete(`${API}/agents/${agent.id}`, {
          headers: { Authorization: `Bearer ${token}` }
        });
      }
      
      console.log('✅ All agents cleared');
      await fetchAgents();
      await fetchSimulationState();
    } catch (error) {
      console.error('Failed to clear agents:', error);
      alert('Failed to clear agents. Please try again.');
    }
    setLoading(false);
  };

  // Start fresh - Clear all data and reset to clean stopped state
  const startFreshSimulation = async () => {
    if (!token) return;
    
    if (!confirm('This will clear all conversations and reset to a clean state. Continue?')) {
      return;
    }

    setLoading(true);
    try {
      // Use simulation start to clear conversations and reset state
      await axios.post(`${API}/simulation/start`, {}, {
        headers: { Authorization: `Bearer ${token}` }
      });

      // Immediately pause the simulation to set it to stopped state
      await axios.post(`${API}/simulation/pause`, {}, {
        headers: { Authorization: `Bearer ${token}` }
      });

      // Refresh data to get current state
      await fetchAgents();
      await fetchConversations();
      await fetchSimulationState();
      
      // Set local state to clean stopped state
      setIsRunning(false);
      setIsPaused(false);
      setAutoMode(false);
      setFastForwardMode(false);
      
      console.log('✅ Fresh state created - conversations cleared, simulation stopped');
    } catch (error) {
      console.error('Failed to create fresh state:', error);
      alert('Failed to create fresh state. Please try again.');
    }
    setLoading(false);
  };

  // Function to display messages with staggered timing for better UX
  const displayMessagesWithDelay = async (conversationData) => {
    if (!conversationData || !conversationData.messages) return;
    
    // Add the conversation structure first (empty messages)
    const emptyConversation = {
      ...conversationData,
      messages: []
    };
    
    setConversations(prevConversations => [...prevConversations, emptyConversation]);
    
    // Then add messages one by one with delay
    for (let i = 0; i < conversationData.messages.length; i++) {
      await new Promise(resolve => setTimeout(resolve, 1000)); // 1 second delay between messages
      
      setConversations(prevConversations => {
        const updatedConversations = [...prevConversations];
        const lastConvIndex = updatedConversations.length - 1;
        const lastConversation = updatedConversations[lastConvIndex];
        
        updatedConversations[lastConvIndex] = {
          ...lastConversation,
          messages: [...(lastConversation.messages || []), conversationData.messages[i]]
        };
        
        return updatedConversations;
      });
      
      // Scroll to bottom as each message appears
      setTimeout(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
      }, 100);
    }
  };

  // Observer message functionality
  const sendObserverMessage = async () => {
    if (!newMessage.trim() || !token) return;
    
    setLoading(true);
    try {
      console.log('🔍 Sending observer message:', newMessage);
      const response = await axios.post(`${API}/observer/send-message`, {
        observer_message: newMessage
      }, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      console.log('✅ Observer message sent successfully:', response.data);
      
      setNewMessage('');
      
      // Add the new observer conversation directly to the existing conversations
      // instead of refreshing everything
      if (response.data && response.data.agent_responses) {
        setConversations(prevConversations => {
          const newConversations = [...prevConversations, response.data.agent_responses];
          return newConversations;
        });
        
        // Display messages one by one with staggered timing
        await displayMessagesWithDelay(response.data.agent_responses);
      }
      
      // Scroll to bottom after new message
      setTimeout(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
      }, 100);
      
    } catch (error) {
      console.error('Failed to send observer message:', error);
      console.error('Error details:', error.response?.data);
      alert('Failed to send message. Please try again.');
    }
    setLoading(false);
  };

  // Remove agent
  const handleRemoveAgent = async (agentId) => {
    if (!token) return;
    
    if (!confirm('Are you sure you want to remove this agent from the simulation?')) {
      return;
    }

    setLoading(true);
    try {
      await axios.delete(`${API}/agents/${agentId}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      console.log('✅ Agent removed successfully');
      await fetchAgents();
      await fetchSimulationState();
    } catch (error) {
      console.error('Failed to remove agent:', error);
      alert('Failed to remove agent. Please try again.');
    }
    setLoading(false);
  };

  // Save agent
  const handleSaveAgent = async (agentId, formData) => {
    if (!token) return;
    
    try {
      await axios.put(`${API}/agents/${agentId}`, formData, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      console.log('✅ Agent updated successfully');
      await fetchAgents();
    } catch (error) {
      console.error('Failed to update agent:', error);
      throw error;
    }
  };

  // Set simulation scenario
  const setSimulationScenario = async (scenarioText) => {
    if (!token) return;
    
    setLoading(true);
    setScenario(scenarioText);
    
    try {
      const response = await axios.post(`${API}/simulation/set-scenario`, {
        scenario: scenarioText,
        scenario_name: scenarioText
      }, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      console.log('✅ Scenario set:', scenarioText);
      await fetchSimulationState();
    } catch (error) {
      console.error('Failed to set scenario:', error);
    }
    setLoading(false);
  };

  // Play/Pause simulation functionality
  const playPauseSimulation = async () => {
    if (!token) return;
    
    setLoading(true);
    try {
      if (!isRunning) {
        // Start the simulation
        const response = await axios.post(`${API}/simulation/start`, {}, {
          headers: { Authorization: `Bearer ${token}` }
        });
        setIsRunning(true);
        setIsPaused(false);
        console.log('✅ Simulation started');
        
      } else if (isPaused) {
        // Resume the simulation
        const response = await axios.post(`${API}/simulation/resume`, {}, {
          headers: { Authorization: `Bearer ${token}` }
        });
        setIsPaused(false);
        console.log('✅ Simulation resumed');
        
      } else {
        // Pause the simulation
        const response = await axios.post(`${API}/simulation/pause`, {}, {
          headers: { Authorization: `Bearer ${token}` }
        });
        setIsPaused(true);
        console.log('✅ Simulation paused');
      }
      
      // Always fetch the latest simulation state after any operation
      setTimeout(() => {
        fetchSimulationState();
      }, 500); // Small delay to ensure backend state is updated
      
    } catch (error) {
      console.error('Failed to control simulation:', error);
      alert('Failed to control simulation. Please try again.');
      
      // Reset local state on error
      await fetchSimulationState();
    }
    setLoading(false);
  };

  // Fast forward simulation functionality
  const toggleFastForward = async () => {
    if (!token) return;
    
    setLoading(true);
    try {
      if (!fastForwardMode) {
        // Start fast forward
        await axios.post(`${API}/simulation/fast-forward`, {
          target_days: 1,
          conversations_per_period: 2
        }, {
          headers: { Authorization: `Bearer ${token}` }
        });
        setFastForwardMode(true);
        console.log('✅ Fast forward activated');
      } else {
        // Fast forward is automatic, no need to toggle off
        setFastForwardMode(false);
        console.log('✅ Fast forward completed');
      }
      
      await fetchSimulationState();
      await fetchConversations();
    } catch (error) {
      console.error('Failed to fast forward:', error);
      alert('Failed to fast forward simulation. Please try again.');
    }
    setLoading(false);
  };

  // Generate conversation manually
  const generateConversation = async () => {
    if (!token) return;
    
    setLoading(true);
    try {
      await axios.post(`${API}/conversation/generate`, {}, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      console.log('✅ Conversation generated');
      
      // Only fetch new conversations instead of all conversations
      await fetchNewConversations();
      
    } catch (error) {
      console.error('Failed to generate conversation:', error);
      if (error.response?.status === 400) {
        // Don't show alert for expected errors (like insufficient agents)
        console.log('Conversation generation skipped:', error.response?.data?.detail);
      } else {
        alert('Failed to generate conversation. Please add more agents or check your simulation setup.');
      }
    }
    setLoading(false);
  };

  // Fetch only new conversations efficiently without causing re-renders
  const fetchNewConversations = async () => {
    if (!token) return;
    
    try {
      const response = await axios.get(`${API}/conversations`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      const allConversations = response.data || [];
      
      // Only update if there are actually new conversations
      if (allConversations.length > conversations.length) {
        // Use functional update to ensure we're working with latest state
        setConversations(prevConversations => {
          // Check if we actually have new conversations to avoid unnecessary updates
          if (allConversations.length > prevConversations.length) {
            // Only add the new conversations, don't replace everything
            const newConversations = allConversations.slice(prevConversations.length);
            const updatedConversations = [...prevConversations, ...newConversations];
            
            // Smooth scroll to new content only if user is near bottom
            setTimeout(() => {
              const conversationContainer = messagesEndRef.current?.parentElement;
              if (conversationContainer) {
                const { scrollTop, scrollHeight, clientHeight } = conversationContainer;
                const isNearBottom = scrollTop + clientHeight >= scrollHeight - 100;
                
                if (isNearBottom) {
                  messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
                }
              }
            }, 100);
            
            return updatedConversations;
          }
          return prevConversations;
        });
      }
    } catch (error) {
      console.error('Failed to fetch new conversations:', error);
    }
  };

  // Get random scenario
  const getRandomScenario = async () => {
    if (!token) return;
    
    setLoading(true);
    try {
      const response = await axios.get(`${API}/simulation/random-scenario`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      const randomScenario = response.data.scenario;
      setScenario(randomScenario);
      
      // Set the scenario
      await axios.post(`${API}/simulation/set-scenario`, {
        scenario: randomScenario,
        scenario_name: randomScenario
      }, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      // Refresh simulation state
      await fetchSimulationState();
    } catch (error) {
      console.error('Failed to get random scenario:', error);
      alert('Failed to get random scenario. Please try again.');
    }
    setLoading(false);
  };

  // Refresh agents when switching to simulation tab
  useEffect(() => {
    if (activeTab === 'simulation') {
      fetchAgents();
      fetchConversations();
      fetchSimulationState();
    }
  }, [activeTab, token]);

  // Auto-generate and refresh conversations (smooth, no flashing)
  useEffect(() => {
    if (isRunning && !isPaused && token && agents.length >= 2) {
      const interval = setInterval(async () => {
        try {
          setAutoGenerating(true);
          
          // Silent generation - don't set loading state to avoid UI flash
          await axios.post(`${API}/conversation/generate`, {}, {
            headers: { Authorization: `Bearer ${token}` }
          });
          
          // Efficiently fetch and update only new conversations
          await fetchNewConversations();
          
        } catch (error) {
          // Silent failure for auto-generation - don't spam console or UI
          if (error.response?.status !== 400) {
            console.error('Auto-generation failed:', error);
          }
        } finally {
          setAutoGenerating(false);
        }
      }, 4000); // Generate every 4 seconds
      return () => clearInterval(interval);
    }
  }, [isRunning, isPaused, token, agents.length, conversations.length]);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white/10 backdrop-blur-lg rounded-xl p-6">
        <div className="flex justify-between items-center">
          <div>
            <h2 className="text-3xl font-bold text-white mb-2">🔭 Observatory</h2>
            <p className="text-white/80">Manage and monitor your AI agent simulations</p>
          </div>
          <div className="flex items-center space-x-2">
            <div className={`w-3 h-3 rounded-full ${isRunning ? 'bg-green-400 animate-pulse' : 'bg-gray-400'}`}></div>
            <span className="text-white text-sm">
              {isRunning ? (isPaused ? 'Paused' : 'Running') : 'Stopped'}
            </span>
          </div>
        </div>

        {/* Scenario Selection */}
        <div className="mb-6">
          <div className="flex justify-between items-center mb-2">
            <label className="block text-white text-sm font-medium">Select or Create Scenario</label>
            <div className="flex space-x-2">
              <button
                onClick={() => setShowScenarioCreator(true)}
                disabled={loading || isRunning}
                className="px-3 py-1 bg-gray-500 hover:bg-gray-600 text-white text-sm rounded-lg transition-colors disabled:opacity-50"
              >
                📝 Create Custom
              </button>
              <button
                onClick={getRandomScenario}
                disabled={loading || isRunning}
                className="px-3 py-1 bg-gray-500 hover:bg-gray-600 text-white text-sm rounded-lg transition-colors disabled:opacity-50"
              >
                {loading ? '⏳' : '🎲 Random'}
              </button>
            </div>
          </div>
          <select
            value={scenario}
            onChange={(e) => setSimulationScenario(e.target.value)}
            disabled={loading || isRunning}
            className="w-full px-3 py-2 bg-white/10 border border-white/20 rounded-lg text-white focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
          >
            <option value="" className="bg-gray-800">Select a predefined scenario...</option>
            {scenarios.map((s) => (
              <option key={s} value={s} className="bg-gray-800">{s}</option>
            ))}
          </select>
        </div>

        {/* Compact Current Scenario Info */}
        {simulationState && (
          <div className="bg-white/5 rounded-lg p-3">
            <div className="flex justify-between items-center">
              <div className="flex items-center space-x-4">
                <h3 className="text-white font-semibold">Current Simulation</h3>
                <div className="flex items-center space-x-4 text-sm">
                  <span className="text-white/60">Agents: <span className="text-white">{agents.length || 0}</span></span>
                  <span className="text-white/60">Messages: <span className="text-white">{simulationState.message_count || 0}</span></span>
                </div>
              </div>
              <button
                onClick={() => setExpandedScenario(!expandedScenario)}
                className="text-white/60 hover:text-white transition-colors"
              >
                {expandedScenario ? '📋 Hide Details' : '📋 View Scenario'}
              </button>
            </div>
            {expandedScenario && (
              <div className="mt-3 pt-3 border-t border-white/10">
                <div className="text-sm">
                  <span className="text-white/60">Current Scenario:</span>
                  <div className="text-white mt-1 p-2 bg-white/5 rounded">
                    {simulationState.scenario || 'No scenario selected'}
                  </div>
                </div>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Combined Active Agents and Live Conversations Section */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Active Agents Section - 25% width on large screens */}
        <div className="lg:col-span-1">
          <div className="bg-white/10 backdrop-blur-lg rounded-xl p-6 h-full">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-bold text-white">🤖 Active Agents</h3>
              <div className="flex items-center space-x-2">
                <span className="text-white/60 text-xs">{agents.length}</span>
                <button
                  onClick={fetchAgents}
                  disabled={agentsLoading || loading}
                  className="px-2 py-1 bg-blue-600 hover:bg-blue-700 text-white text-xs rounded transition-colors disabled:opacity-50"
                >
                  {agentsLoading ? '⏳' : '🔄'}
                </button>
                {agents.length > 0 && (
                  <button
                    onClick={clearAllAgents}
                    disabled={loading || agentsLoading}
                    className="px-2 py-1 bg-red-600 hover:bg-red-700 text-white text-xs rounded transition-colors disabled:opacity-50"
                  >
                    {loading ? '⏳' : '🗑️'}
                  </button>
                )}
              </div>
            </div>

            {agentsLoading ? (
              <div className="text-center py-8">
                <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-white mx-auto mb-2"></div>
                <p className="text-white/60 text-sm">Loading...</p>
              </div>
            ) : agents.length === 0 ? (
              <div className="text-center py-8">
                <div className="text-3xl mb-2">🎭</div>
                <h4 className="text-white font-medium mb-2 text-sm">No Active Agents</h4>
                <p className="text-white/60 text-xs mb-3">Add agents to start simulation</p>
                <button 
                  onClick={() => setActiveTab('agents')}
                  className="px-3 py-1 bg-purple-600 hover:bg-purple-700 text-white text-sm rounded transition-colors"
                >
                  Add Agents
                </button>
              </div>
            ) : (
              <div className="max-h-96 overflow-y-auto space-y-3 scrollbar-thin scrollbar-thumb-white/20 scrollbar-track-transparent">
                {agents.map((agent) => (
                  <motion.div
                    key={agent.id}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="bg-white/5 backdrop-blur-sm rounded-lg p-3 border border-white/10 hover:border-white/20 transition-all duration-200"
                  >
                    {/* Agent Avatar and Basic Info */}
                    <div className="flex items-start space-x-2 mb-2">
                      <div className={`w-8 h-8 rounded-full bg-gradient-to-br ${getArchetypeColor(agent.archetype)} flex items-center justify-center text-white text-xs font-semibold shadow-lg`}>
                        {agent.avatar_url ? (
                          <img 
                            src={agent.avatar_url} 
                            alt={agent.name}
                            className="w-full h-full rounded-full object-cover"
                          />
                        ) : (
                          agent.name?.[0] || '🤖'
                        )}
                      </div>
                      <div className="flex-1 min-w-0">
                        <h4 className="text-white font-medium text-sm truncate">{agent.name}</h4>
                        <p className="text-white/60 text-xs truncate">{agent.archetype}</p>
                      </div>
                    </div>

                    {/* Agent Goal */}
                    <p className="text-white/80 text-xs mb-2 line-clamp-2">{agent.goal}</p>

                    {/* Action Buttons */}
                    <div className="flex space-x-1">
                      <button
                        onClick={() => {
                          setEditingAgent(agent);
                          setShowEditModal(true);
                        }}
                        disabled={loading}
                        className="flex-1 px-2 py-1 bg-blue-600 hover:bg-blue-700 text-white text-xs rounded transition-colors flex items-center justify-center space-x-1 disabled:opacity-50"
                      >
                        <span>✏️</span>
                        <span>Edit</span>
                      </button>
                      <button
                        onClick={() => handleRemoveAgent(agent.id)}
                        disabled={loading}
                        className="flex-1 px-2 py-1 bg-red-600 hover:bg-red-700 text-white text-xs rounded transition-colors flex items-center justify-center space-x-1 disabled:opacity-50"
                      >
                        <span>🗑️</span>
                        <span>Remove</span>
                      </button>
                    </div>
                  </motion.div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Live Conversations Section - 75% width on large screens */}
        <div className="lg:col-span-3">
          <div className="bg-white/10 backdrop-blur-lg rounded-xl p-6 h-full">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-xl font-bold text-white">💬 Live Conversations</h3>
              <div className="flex items-center space-x-3">
                <div className={`w-3 h-3 rounded-full ${isRunning ? 'bg-green-400 animate-pulse' : 'bg-gray-400'}`}></div>
                {autoGenerating && (
                  <div className="w-2 h-2 rounded-full bg-blue-400 animate-ping"></div>
                )}
                <span className="text-white/60 text-sm">
                  {conversations.length} rounds, {observerMessages.length} messages
                </span>
                <button
                  onClick={fetchConversations}
                  disabled={conversationLoading}
                  className="px-3 py-1 bg-blue-600 hover:bg-blue-700 text-white text-sm rounded-lg transition-colors disabled:opacity-50"
                >
                  {conversationLoading ? '⏳' : '🔄 Refresh'}
                </button>
                <button
                  onClick={generateConversation}
                  disabled={loading || agents.length < 2}
                  className="px-3 py-1 bg-green-600 hover:bg-green-700 text-white text-sm rounded-lg transition-colors disabled:opacity-50"
                >
                  {loading ? '⏳' : '💬 Generate'}
                </button>
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

            {/* Conversation Display */}
            <div className="bg-black/20 rounded-lg p-4 h-96 overflow-y-auto space-y-3 scrollbar-thin scrollbar-thumb-white/20 scrollbar-track-transparent">
              {conversationLoading ? (
                <div className="flex items-center justify-center h-full">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-white"></div>
                </div>
              ) : conversations.length === 0 ? (
                <div className="flex items-center justify-center h-full">
                  <div className="text-center">
                    <div className="text-4xl mb-4">💬</div>
                    <p className="text-white/60">No conversations yet</p>
                    <p className="text-white/40 text-sm">Add agents and start simulation to see conversations</p>
                  </div>
                </div>
              ) : (
                <>
                  {conversations.map((conversation, conversationIndex) => (
                    <div key={conversation.id || conversationIndex} className="space-y-2">
                      <div className="flex items-center justify-between">
                        <h4 className="text-white font-medium text-sm">
                          Round {conversation.round_number} - {conversation.time_period}
                        </h4>
                        {conversation.scenario_name && (
                          <span className="text-white/40 text-xs bg-white/5 px-2 py-1 rounded">
                            {conversation.scenario_name}
                          </span>
                        )}
                      </div>
                      
                      {conversation.messages?.map((message, messageIndex) => {
                        const isHighlighted = searchResults.some(result => 
                          result.conversationIndex === conversationIndex && 
                          result.messageIndex === messageIndex
                        );
                        const isCurrentSearch = searchResults[currentSearchIndex]?.conversationIndex === conversationIndex && 
                                              searchResults[currentSearchIndex]?.messageIndex === messageIndex;
                        
                        return (
                          <div
                            key={message.id || messageIndex}
                            ref={isCurrentSearch ? (el) => searchRefs.current[currentSearchIndex] = el : null}
                            className={`rounded-lg p-3 border-l-4 ${
                              message.agent_name === "Observer (You)"
                                ? 'bg-blue-500/20 border-blue-500 shadow-lg' // Special styling for observer messages
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
                                  ? 'bg-gradient-to-br from-blue-600 to-blue-800' // Special blue gradient for observer
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
                                      ? 'text-blue-300' // Special color for observer name
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
                                    ? 'text-blue-100 font-medium' // Special styling for observer text
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
                  <span>👁️</span>
                  <span>Observer Input</span>
                </h4>
                <div className="flex space-x-2">
                  <input
                    type="text"
                    value={newMessage}
                    onChange={(e) => setNewMessage(e.target.value)}
                    placeholder="Send a message to the agents..."
                    className="flex-1 px-3 py-2 bg-white/10 border border-white/20 rounded-lg text-white placeholder-white/40 focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
                    onKeyPress={(e) => {
                      if (e.key === 'Enter' && !e.shiftKey) {
                        e.preventDefault();
                        sendObserverMessage();
                      }
                    }}
                  />
                  <button
                    onClick={sendObserverMessage}
                    disabled={!newMessage.trim() || loading}
                    className="px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg transition-colors disabled:opacity-50"
                  >
                    Send
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Control Buttons - Aligned with Live Conversations Section */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Empty space to match Active Agents column */}
        <div className="lg:col-span-1"></div>
        
        {/* Control Buttons aligned with Live Conversations */}
        <div className="lg:col-span-3 flex justify-center">
          <div className="flex space-x-6">
            {/* Play/Pause Button */}
            <div className="group relative">
              <button
                onClick={playPauseSimulation}
                disabled={loading || agents.length < 2}
                className={`w-12 h-12 rounded-full flex items-center justify-center transition-all duration-200 shadow-lg hover:shadow-xl transform hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed ${
                  !isRunning
                    ? 'bg-green-500 hover:bg-green-600 text-white'
                    : isPaused 
                      ? 'bg-blue-500 hover:bg-blue-600 text-white'
                      : 'bg-yellow-500 hover:bg-yellow-600 text-white'
                }`}
              >
                <span className="text-lg">
                  {loading ? '⏳' : !isRunning ? '▶️' : isPaused ? '▶️' : '⏸️'}
                </span>
              </button>
              <div className="absolute top-14 left-1/2 transform -translate-x-1/2 bg-black text-white text-xs py-1 px-2 rounded opacity-0 group-hover:opacity-100 transition-opacity duration-200 whitespace-nowrap">
                {loading ? 'Loading...' : !isRunning ? 'Start Simulation' : isPaused ? 'Resume Simulation' : 'Pause Simulation'}
              </div>
            </div>

            {/* Observer Button */}
            <div className="group relative">
              <button
                onClick={() => setShowObserverChat(!showObserverChat)}
                className={`w-12 h-12 rounded-full flex items-center justify-center transition-all duration-200 shadow-lg hover:shadow-xl transform hover:scale-105 ${
                  showObserverChat 
                    ? 'bg-purple-500 hover:bg-purple-600 text-white' 
                    : 'bg-gray-600 hover:bg-gray-700 text-white'
                }`}
              >
                <span className="text-lg">👁️</span>
              </button>
              <div className="absolute top-14 left-1/2 transform -translate-x-1/2 bg-black text-white text-xs py-1 px-2 rounded opacity-0 group-hover:opacity-100 transition-opacity duration-200 whitespace-nowrap">
                {showObserverChat ? 'Hide Observer' : 'Show Observer'}
              </div>
            </div>

            {/* Fast Forward Button */}
            <div className="group relative">
              <button
                onClick={toggleFastForward}
                disabled={loading || !isRunning || agents.length < 2}
                className={`w-12 h-12 rounded-full flex items-center justify-center transition-all duration-200 shadow-lg hover:shadow-xl transform hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed ${
                  fastForwardMode
                    ? 'bg-orange-500 hover:bg-orange-600 text-white animate-pulse'
                    : 'bg-indigo-500 hover:bg-indigo-600 text-white'
                }`}
              >
                <span className="text-lg">⏩</span>
              </button>
              <div className="absolute top-14 left-1/2 transform -translate-x-1/2 bg-black text-white text-xs py-1 px-2 rounded opacity-0 group-hover:opacity-100 transition-opacity duration-200 whitespace-nowrap">
                {loading ? 'Processing...' : fastForwardMode ? 'Fast Forward Active' : 'Fast Forward (1 Day)'}
              </div>
            </div>

            {/* Weekly Report Button */}
            <div className="group relative">
              <button
                onClick={() => setShowWeeklyReport(true)}
                disabled={loading}
                className="w-12 h-12 rounded-full bg-emerald-500 hover:bg-emerald-600 text-white flex items-center justify-center transition-all duration-200 shadow-lg hover:shadow-xl transform hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <span className="text-lg">📅</span>
              </button>
              <div className="absolute top-14 left-1/2 transform -translate-x-1/2 bg-black text-white text-xs py-1 px-2 rounded opacity-0 group-hover:opacity-100 transition-opacity duration-200 whitespace-nowrap">
                {loading ? 'Loading...' : 'Weekly Report'}
              </div>
            </div>

            {/* Start Fresh Button */}
            <div className="group relative">
              <button
                onClick={startFreshSimulation}
                disabled={loading}
                className="w-12 h-12 rounded-full bg-red-500 hover:bg-red-600 text-white flex items-center justify-center transition-all duration-200 shadow-lg hover:shadow-xl transform hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <span className="text-lg">🔄</span>
              </button>
              <div className="absolute top-14 left-1/2 transform -translate-x-1/2 bg-black text-white text-xs py-1 px-2 rounded opacity-0 group-hover:opacity-100 transition-opacity duration-200 whitespace-nowrap">
                {loading ? 'Starting Fresh...' : 'Start Fresh'}
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

      {/* Weekly Report Modal */}
      <WeeklySummary
        isOpen={showWeeklyReport}
        onClose={() => setShowWeeklyReport(false)}
      />

      {/* Scenario Creator Modal */}
      <ScenarioCreator
        isOpen={showScenarioCreator}
        onClose={() => setShowScenarioCreator(false)}
        onScenarioCreated={async (scenarioData) => {
          // When a scenario is created, refresh the simulation state
          await fetchSimulationState();
          setShowScenarioCreator(false);
        }}
      />
    </div>
  );
};

export default SimulationControl;