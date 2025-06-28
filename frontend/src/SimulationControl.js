import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import axios from 'axios';
import { useAuth } from './AuthContext';

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
      if (!confirm('Failed to save agent. Would you like to try again?')) {
        setSaving(false);
        return;
      }
      // Retry the operation
      await handleSubmit(e);
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
  const [showObserverChat, setShowObserverChat] = useState(false);
  const [showSetScenario, setShowSetScenario] = useState(false);
  const [customScenario, setCustomScenario] = useState('');
  const [isRecording, setIsRecording] = useState(false);
  const [conversations, setConversations] = useState([]);
  const [conversationLoading, setConversationLoading] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [currentSearchIndex, setCurrentSearchIndex] = useState(0);
  const [autoGenerating, setAutoGenerating] = useState(false);

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
      if (!confirm('Failed to clear agents. Would you like to try again?')) {
        return;
      }
      // Retry the operation
      await clearAllAgents();
    }
    setLoading(false);
  };

  // Start fresh - Clear all data and reset to clean stopped state
  const startFreshSimulation = async () => {
    if (!token) return;
    
    if (!confirm('This will clear all conversations, remove all agents, and pause the simulation. Continue?')) {
      return;
    }

    setLoading(true);
    try {
      console.log('🔄 Starting fresh simulation...');
      
      // Step 1: Pause simulation first if it's running
      if (isRunning && !isPaused) {
        console.log('⏸️ Pausing simulation...');
        await axios.post(`${API}/simulation/pause`, {}, {
          headers: { Authorization: `Bearer ${token}` }
        });
      }
      
      // Step 2: Clear all agents
      if (agents.length > 0) {
        console.log(`🗑️ Clearing ${agents.length} agents...`);
        const agentIds = agents.map(agent => agent.id);
        await axios.post(`${API}/agents/bulk-delete`, agentIds, {
          headers: { Authorization: `Bearer ${token}` }
        });
      }
      
      // Step 3: Start fresh simulation to clear conversations
      console.log('🆕 Starting fresh simulation state...');
      await axios.post(`${API}/simulation/start`, {}, {
        headers: { Authorization: `Bearer ${token}` }
      });

      // Step 4: Immediately pause the simulation to set it to stopped state
      console.log('⏸️ Pausing fresh simulation...');
      await axios.post(`${API}/simulation/pause`, {}, {
        headers: { Authorization: `Bearer ${token}` }
      });

      // Step 5: Clear local state immediately
      setAgents([]);
      setConversations([]);
      setObserverMessages([]);
      setScenario('');
      setNewMessage('');
      
      // Set simulation state to clean stopped state
      setIsRunning(false);
      setIsPaused(false);
      setAutoMode(false);
      setFastForwardMode(false);
      
      // Step 6: Refresh data to confirm clean state
      await fetchAgents();
      await fetchConversations();
      await fetchSimulationState();
      
      console.log('✅ Fresh state created - all conversations cleared, all agents removed, simulation paused');
    } catch (error) {
      console.error('Failed to create fresh state:', error);
      if (!confirm('Failed to create fresh state. Would you like to try again?')) {
        return;
      }
      // Retry the operation
      await startFreshSimulation();
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
        
        // Reset loading state immediately after sending, before displaying messages
        setLoading(false);
        
        // Display messages one by one with staggered timing (async, non-blocking)
        displayMessagesWithDelay(response.data.agent_responses);
      } else {
        setLoading(false);
      }
      
      // Scroll to bottom after new message
      setTimeout(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
      }, 100);
      
    } catch (error) {
      console.error('Failed to send observer message:', error);
      console.error('Error details:', error.response?.data);
      if (!confirm('Failed to send message. Would you like to try again?')) {
        setLoading(false);
        return;
      }
      // Retry the operation
      await sendObserverMessage();
    }
  };

  // Remove agent
  const handleRemoveAgent = async (agentId) => {
    if (!token) return;

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
      if (!confirm('Failed to remove agent. Would you like to try again?')) {
        setLoading(false);
        return;
      }
      // Retry the operation
      await handleRemoveAgent(agentId);
      return;
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

  // Voice recording for scenario input
  const handleVoiceInput = async () => {
    if (!token) return;

    if (isRecording) {
      // Stop recording
      setIsRecording(false);
      return;
    }

    try {
      setIsRecording(true);
      
      // Request microphone access
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      const audioChunks = [];

      mediaRecorder.ondataavailable = (event) => {
        audioChunks.push(event.data);
      };

      mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
        const formData = new FormData();
        formData.append('audio', audioBlob, 'scenario.webm');

        try {
          console.log('🎤 Sending audio for transcription...');
          const response = await axios.post(`${API}/speech/transcribe-scenario`, formData, {
            headers: {
              Authorization: `Bearer ${token}`,
              'Content-Type': 'multipart/form-data'
            }
          });

          console.log('📝 Transcription response:', response.data);
          
          if (response.data && response.data.text) {
            console.log('✅ Setting transcribed text:', response.data.text);
            setCustomScenario(response.data.text);
          } else {
            console.log('❌ No text in transcription response');
            if (!confirm('No speech was detected. Would you like to try recording again?')) {
              return;
            }
            await handleVoiceInput();
          }
        } catch (error) {
          console.error('Failed to transcribe audio:', error);
          console.error('Error details:', error.response?.data);
          if (!confirm('Failed to transcribe audio. Would you like to try again?')) {
            return;
          }
          await handleVoiceInput();
        }

        // Stop all tracks to release microphone
        stream.getTracks().forEach(track => track.stop());
        setIsRecording(false);
      };

      mediaRecorder.start();

      // Auto-stop after 30 seconds
      setTimeout(() => {
        if (mediaRecorder.state === 'recording') {
          mediaRecorder.stop();
        }
      }, 30000);

    } catch (error) {
      console.error('Failed to access microphone:', error);
      if (!confirm('Failed to access microphone. Please check permissions and try again.')) {
        setIsRecording(false);
        return;
      }
      setIsRecording(false);
    }
  };

  // Set custom scenario
  const handleSetScenario = async () => {
    if (!token || !customScenario.trim()) return;

    setLoading(true);
    try {
      await axios.post(`${API}/simulation/set-scenario`, {
        scenario: customScenario.trim(),
        scenario_name: customScenario.trim().substring(0, 50) + (customScenario.length > 50 ? '...' : '')
      }, {
        headers: { Authorization: `Bearer ${token}` }
      });

      console.log('✅ Custom scenario set');
      setShowSetScenario(false);
      setCustomScenario('');
      await fetchSimulationState();
    } catch (error) {
      console.error('Failed to set scenario:', error);
      if (!confirm('Failed to set scenario. Would you like to try again?')) {
        setLoading(false);
        return;
      }
      await handleSetScenario();
      return;
    }
    setLoading(false);
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
      if (!confirm('Failed to control simulation. Would you like to try again?')) {
        // Reset local state on error
        await fetchSimulationState();
        setLoading(false);
        return;
      }
      // Retry the operation
      await playPauseSimulation();
      return;
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
      if (!confirm('Failed to fast forward simulation. Would you like to try again?')) {
        setLoading(false);
        return;
      }
      // Retry the operation
      await toggleFastForward();
      return;
    }
    setLoading(false);
  };

  // Generate conversation manually
  const generateConversation = async () => {
    if (!token) return;
    
    setLoading(true);
    try {
      const response = await axios.post(`${API}/conversation/generate`, {}, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      console.log('✅ Conversation generated:', response.data);
      
      // Use staggered display for regular conversations too
      if (response.data) {
        await displayMessagesWithDelay(response.data);
      }
      
    } catch (error) {
      console.error('Failed to generate conversation:', error);
      if (error.response?.status === 400) {
        // Don't show alert for expected errors (like insufficient agents)
        console.log('Conversation generation skipped:', error.response?.data?.detail);
      } else {
        if (!confirm('Failed to generate conversation. Please add more agents or check your simulation setup. Would you like to try again?')) {
          setLoading(false);
          return;
        }
        // Retry the operation
        await generateConversation();
        return;
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
      
      // Set the scenario in the text box for editing instead of directly applying
      setCustomScenario(randomScenario);
      setShowSetScenario(true); // Expand the set scenario section
      
    } catch (error) {
      console.error('Failed to get random scenario:', error);
      if (!confirm('Failed to get random scenario. Would you like to try again?')) {
        setLoading(false);
        return;
      }
      // Retry the operation
      await getRandomScenario();
      return;
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
          const response = await axios.post(`${API}/conversation/generate`, {}, {
            headers: { Authorization: `Bearer ${token}` }
          });
          
          // Use staggered display for auto-generated conversations
          if (response.data) {
            await displayMessagesWithDelay(response.data);
          }
          
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
  }, [isRunning, isPaused, token, agents.length]);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white/10 backdrop-blur-lg rounded-xl p-3">
        <div className="flex justify-between items-center">
          <div className="flex items-center space-x-3">
            <h2 className="text-lg font-semibold text-white">🔭 Observatory</h2>
            <div className="flex items-center space-x-2">
              <div className={`w-2 h-2 rounded-full ${isRunning ? 'bg-green-400 animate-pulse' : 'bg-gray-400'}`}></div>
              <span className="text-white/80 text-xs">
                {isRunning ? (isPaused ? 'Paused' : 'Running') : 'Stopped'}
              </span>
            </div>
          </div>
        </div>

        {/* Set Scenario */}
        <div className="mt-3 mb-3">
          <div className="flex justify-between items-center mb-2">
            <button
              onClick={() => setShowSetScenario(!showSetScenario)}
              className="flex items-center space-x-2 text-white text-sm font-medium hover:text-blue-300 transition-colors"
            >
              <span>Set Scenario</span>
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
                  rows="3"
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
                    className="w-4 h-4"
                  >
                    <path d="M12 1c-1.6 0-3 1.4-3 3v8c0 1.6 1.4 3 3 3s3-1.4 3-3V4c0-1.6-1.4-3-3-3zm0 18c-3.3 0-6-2.7-6-6h-2c0 4.4 3.6 8 8 8s8-3.6 8-8h-2c0 3.3-2.7 6-6 6zm1-6V4c0-.6-.4-1-1-1s-1 .4-1 1v9c0 .6.4 1 1 1s1-.4 1-1z"/>
                    <rect x="10" y="20" width="4" height="2" rx="1"/>
                  </svg>
                </button>
              </div>
              <div className="flex justify-end space-x-2">
                <button
                  onClick={() => {
                    setShowSetScenario(false);
                    setCustomScenario('');
                  }}
                  disabled={loading || isRecording}
                  className="px-3 py-1 bg-gray-600 hover:bg-gray-700 text-white text-sm rounded-lg transition-colors disabled:opacity-50"
                >
                  Cancel
                </button>
                <button
                  onClick={handleSetScenario}
                  disabled={loading || isRunning || !customScenario.trim() || isRecording}
                  className="px-3 py-1 bg-blue-600 hover:bg-blue-700 text-white text-sm rounded-lg transition-colors disabled:opacity-50"
                >
                  Set Scenario
                </button>
              </div>
              {isRecording && (
                <p className="text-yellow-300 text-xs">
                  🎤 Recording... Speak clearly. Recording will auto-stop after 30 seconds.
                </p>
              )}
            </div>
          )}
        </div>

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
      
      <style jsx>{`
        @keyframes fadeIn {
          from { opacity: 0; transform: translateY(-10px); }
          to { opacity: 1; transform: translateY(0); }
        }
        .animate-fadeIn {
          animation: fadeIn 0.3s ease-out;
        }
      `}</style>
    </div>
  );
};

export default SimulationControl;