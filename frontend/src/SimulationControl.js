import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import axios from 'axios';
import { useAuth } from './App';

const API = process.env.REACT_APP_BACKEND_URL ? `${process.env.REACT_APP_BACKEND_URL}/api` : 'http://localhost:8001/api';

// Simulation Control Panel Component
const SimulationControl = () => {
  const [simulationState, setSimulationState] = useState(null);
  const [isRunning, setIsRunning] = useState(false);
  const [isPaused, setIsPaused] = useState(false);
  const [autoMode, setAutoMode] = useState(false);
  const [scenario, setScenario] = useState('');
  const [observerMessages, setObserverMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [fastForwardMode, setFastForwardMode] = useState(false);
  const messagesEndRef = useRef(null);
  const { user, token } = useAuth();

  // Fetch simulation state on mount
  useEffect(() => {
    fetchSimulationState();
    fetchObserverMessages();
    // Set up polling for real-time updates
    const interval = setInterval(() => {
      if (isRunning) {
        fetchObserverMessages();
        fetchSimulationState();
      }
    }, 2000);
    return () => clearInterval(interval);
  }, [isRunning]);

  // Auto-scroll to bottom of messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [observerMessages]);

  const fetchSimulationState = async () => {
    try {
      const response = await axios.get(`${API}/simulation/state`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (response.data) {
        setSimulationState(response.data);
        setIsRunning(response.data.is_running || false);
        setIsPaused(response.data.is_paused || false);
        setScenario(response.data.scenario || '');
      }
    } catch (error) {
      console.error('Failed to fetch simulation state:', error);
    }
  };

  const fetchObserverMessages = async () => {
    try {
      const response = await axios.get(`${API}/observer/messages`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (response.data && response.data.messages) {
        setObserverMessages(response.data.messages);
      }
    } catch (error) {
      console.error('Failed to fetch observer messages:', error);
    }
  };

  const startSimulation = async () => {
    setLoading(true);
    try {
      const response = await axios.post(`${API}/simulation/start`, {}, {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (response.data.success) {
        setIsRunning(true);
        setIsPaused(false);
        await fetchSimulationState();
      }
    } catch (error) {
      console.error('Failed to start simulation:', error);
      alert('Failed to start simulation. Please try again.');
    }
    setLoading(false);
  };

  const pauseSimulation = async () => {
    setLoading(true);
    try {
      const response = await axios.post(`${API}/simulation/pause`, {}, {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (response.data.success) {
        setIsPaused(true);
        await fetchSimulationState();
      }
    } catch (error) {
      console.error('Failed to pause simulation:', error);
    }
    setLoading(false);
  };

  const resumeSimulation = async () => {
    setLoading(true);
    try {
      const response = await axios.post(`${API}/simulation/resume`, {}, {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (response.data.success) {
        setIsPaused(false);
        await fetchSimulationState();
      }
    } catch (error) {
      console.error('Failed to resume simulation:', error);
    }
    setLoading(false);
  };

  const toggleFastForward = async () => {
    setLoading(true);
    try {
      const response = await axios.post(`${API}/simulation/fast-forward`, {
        enabled: !fastForwardMode
      }, {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (response.data.success) {
        setFastForwardMode(!fastForwardMode);
      }
    } catch (error) {
      console.error('Failed to toggle fast forward:', error);
    }
    setLoading(false);
  };

  const toggleAutoMode = async () => {
    setLoading(true);
    try {
      const response = await axios.post(`${API}/simulation/toggle-auto-mode`, {}, {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (response.data.success) {
        setAutoMode(response.data.auto_mode_enabled);
      }
    } catch (error) {
      console.error('Failed to toggle auto mode:', error);
    }
    setLoading(false);
  };

  const setSimulationScenario = async (scenarioName) => {
    setLoading(true);
    try {
      const response = await axios.post(`${API}/simulation/set-scenario`, {
        scenario: scenarioName,
        scenario_name: scenarioName
      }, {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (response.data.success) {
        setScenario(scenarioName);
        await fetchSimulationState();
      }
    } catch (error) {
      console.error('Failed to set scenario:', error);
    }
    setLoading(false);
  };

  const sendObserverMessage = async () => {
    if (!newMessage.trim()) return;
    
    setLoading(true);
    try {
      const response = await axios.post(`${API}/observer/send-message`, {
        message: newMessage.trim()
      }, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      if (response.data.success) {
        setNewMessage('');
        // Refresh messages
        await fetchObserverMessages();
      }
    } catch (error) {
      console.error('Failed to send observer message:', error);
      alert('Failed to send message. Please try again.');
    }
    setLoading(false);
  };

  const generateSummary = async () => {
    setLoading(true);
    try {
      const response = await axios.post(`${API}/simulation/generate-summary`, {}, {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (response.data.success) {
        alert('Summary generated successfully!');
      }
    } catch (error) {
      console.error('Failed to generate summary:', error);
      alert('Failed to generate summary. Please try again.');
    }
    setLoading(false);
  };

  const scenarios = [
    'Research Station',
    'Corporate Board Meeting', 
    'Medical Conference',
    'Tech Startup Pitch',
    'Scientific Collaboration',
    'Emergency Response Team',
    'Educational Workshop',
    'Creative Brainstorming'
  ];

  return (
    <div className="space-y-6">
      {/* Simulation Control Header */}
      <div className="bg-white/10 backdrop-blur-lg rounded-xl p-6">
        <div className="flex justify-between items-center mb-6">
          <div>
            <h2 className="text-2xl font-bold text-white mb-2">🎮 Simulation Control</h2>
            <p className="text-white/80">Manage and monitor your AI agent simulations</p>
          </div>
          <div className="flex items-center space-x-2">
            <div className={`w-3 h-3 rounded-full ${isRunning ? 'bg-green-400 animate-pulse' : 'bg-gray-400'}`}></div>
            <span className="text-white text-sm">
              {isRunning ? (isPaused ? 'Paused' : 'Running') : 'Stopped'}
            </span>
          </div>
        </div>

        {/* Control Buttons */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
          <button
            onClick={isRunning ? (isPaused ? resumeSimulation : pauseSimulation) : startSimulation}
            disabled={loading}
            className={`px-4 py-3 rounded-lg font-semibold transition-all duration-200 ${
              isRunning 
                ? (isPaused 
                    ? 'bg-green-600 hover:bg-green-700 text-white' 
                    : 'bg-yellow-600 hover:bg-yellow-700 text-white')
                : 'bg-blue-600 hover:bg-blue-700 text-white'
            } disabled:opacity-50`}
          >
            {loading ? '⏳' : isRunning ? (isPaused ? '▶️ Resume' : '⏸️ Pause') : '🚀 Start'}
          </button>

          <button
            onClick={toggleFastForward}
            disabled={loading || !isRunning}
            className={`px-4 py-3 rounded-lg font-semibold transition-all duration-200 ${
              fastForwardMode 
                ? 'bg-purple-600 hover:bg-purple-700 text-white' 
                : 'bg-gray-600 hover:bg-gray-700 text-white'
            } disabled:opacity-50`}
          >
            ⚡ Fast Forward
          </button>

          <button
            onClick={toggleAutoMode}
            disabled={loading}
            className={`px-4 py-3 rounded-lg font-semibold transition-all duration-200 ${
              autoMode 
                ? 'bg-orange-600 hover:bg-orange-700 text-white' 
                : 'bg-gray-600 hover:bg-gray-700 text-white'
            } disabled:opacity-50`}
          >
            🤖 Auto Mode
          </button>

          <button
            onClick={generateSummary}
            disabled={loading || !isRunning}
            className="px-4 py-3 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg font-semibold transition-all duration-200 disabled:opacity-50"
          >
            📋 Summary
          </button>
        </div>

        {/* Scenario Selection */}
        <div className="mb-6">
          <label className="block text-white text-sm font-medium mb-2">Select Scenario</label>
          <select
            value={scenario}
            onChange={(e) => setSimulationScenario(e.target.value)}
            disabled={loading || isRunning}
            className="w-full px-3 py-2 bg-white/10 border border-white/20 rounded-lg text-white focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
          >
            <option value="" className="bg-gray-800">Select a scenario...</option>
            {scenarios.map((s) => (
              <option key={s} value={s} className="bg-gray-800">{s}</option>
            ))}
          </select>
        </div>

        {/* Current Scenario Info */}
        {simulationState && (
          <div className="bg-white/5 rounded-lg p-4">
            <h3 className="text-white font-semibold mb-2">Current Simulation</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
              <div>
                <span className="text-white/60">Scenario:</span>
                <div className="text-white">{simulationState.scenario || 'None'}</div>
              </div>
              <div>
                <span className="text-white/60">Agents:</span>
                <div className="text-white">{simulationState.agent_count || 0}</div>
              </div>
              <div>
                <span className="text-white/60">Messages:</span>
                <div className="text-white">{simulationState.message_count || 0}</div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Observer Chat */}
      <div className="bg-white/10 backdrop-blur-lg rounded-xl p-6">
        <h3 className="text-xl font-bold text-white mb-4">💬 Observer Chat</h3>
        
        {/* Messages Display */}
        <div className="bg-white/5 rounded-lg p-4 h-64 overflow-y-auto mb-4">
          {observerMessages.length === 0 ? (
            <div className="text-center text-white/60 mt-8">
              <div className="text-4xl mb-2">👁️</div>
              <p>No messages yet. Start observing the simulation!</p>
            </div>
          ) : (
            <div className="space-y-3">
              {observerMessages.map((msg, index) => (
                <div key={index} className="flex space-x-3">
                  <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm ${
                    msg.type === 'observer' 
                      ? 'bg-blue-600' 
                      : msg.type === 'system' 
                        ? 'bg-gray-600' 
                        : 'bg-green-600'
                  }`}>
                    {msg.type === 'observer' ? '👁️' : msg.type === 'system' ? '⚙️' : '🤖'}
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center space-x-2 mb-1">
                      <span className="text-white font-medium">
                        {msg.agent_name || msg.type || 'Observer'}
                      </span>
                      <span className="text-white/40 text-xs">
                        {new Date(msg.timestamp).toLocaleTimeString()}
                      </span>
                    </div>
                    <div className="text-white/80 text-sm">{msg.message}</div>
                  </div>
                </div>
              ))}
              <div ref={messagesEndRef} />
            </div>
          )}
        </div>

        {/* Message Input */}
        <div className="flex space-x-3">
          <input
            type="text"
            value={newMessage}
            onChange={(e) => setNewMessage(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && sendObserverMessage()}
            placeholder="Type your observer message..."
            disabled={loading || !isRunning}
            className="flex-1 px-4 py-2 bg-white/10 border border-white/20 rounded-lg text-white placeholder-white/40 focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
          />
          <button
            onClick={sendObserverMessage}
            disabled={loading || !newMessage.trim() || !isRunning}
            className="px-6 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-semibold transition-all duration-200 disabled:opacity-50"
          >
            Send
          </button>
        </div>
      </div>
    </div>
  );
};

export default SimulationControl;