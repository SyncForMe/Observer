import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import axios from 'axios';
import { useAuth } from './App';

const API = process.env.REACT_APP_BACKEND_URL ? `${process.env.REACT_APP_BACKEND_URL}/api` : 'http://localhost:8001/api';

// Real-time Conversation Viewer Component
const ConversationViewer = () => {
  const [conversations, setConversations] = useState([]);
  const [selectedConversation, setSelectedConversation] = useState(null);
  const [loading, setLoading] = useState(false);
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [translationLanguage, setTranslationLanguage] = useState('en');
  const [translatedMessages, setTranslatedMessages] = useState({});
  const [relationships, setRelationships] = useState([]);
  const [filterAgent, setFilterAgent] = useState('');
  const messagesEndRef = useRef(null);
  const { user, token } = useAuth();

  // Available languages for translation
  const languages = [
    { code: 'en', name: 'English' },
    { code: 'es', name: 'Spanish' },
    { code: 'fr', name: 'French' },
    { code: 'de', name: 'German' },
    { code: 'it', name: 'Italian' },
    { code: 'pt', name: 'Portuguese' },
    { code: 'ru', name: 'Russian' },
    { code: 'ja', name: 'Japanese' },
    { code: 'ko', name: 'Korean' },
    { code: 'zh', name: 'Chinese' }
  ];

  // Fetch conversations on mount and set up auto-refresh
  useEffect(() => {
    fetchConversations();
    fetchRelationships();
    
    let interval;
    if (autoRefresh) {
      interval = setInterval(fetchConversations, 3000);
    }
    
    return () => {
      if (interval) clearInterval(interval);
    };
  }, [autoRefresh]);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    if (selectedConversation) {
      messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }
  }, [selectedConversation]);

  const fetchConversations = async () => {
    try {
      const response = await axios.get(`${API}/conversations`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (response.data) {
        setConversations(response.data);
        
        // Update selected conversation if it exists
        if (selectedConversation) {
          const updated = response.data.find(c => c.id === selectedConversation.id);
          if (updated) {
            setSelectedConversation(updated);
          }
        }
      }
    } catch (error) {
      console.error('Failed to fetch conversations:', error);
    }
  };

  const fetchRelationships = async () => {
    try {
      const response = await axios.get(`${API}/relationships`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (response.data) {
        setRelationships(response.data);
      }
    } catch (error) {
      console.error('Failed to fetch relationships:', error);
    }
  };

  const fetchRelationships = async () => {

  const translateConversation = async (conversationId) => {
    if (translationLanguage === 'en') return;
    
    setLoading(true);
    try {
      const response = await axios.post(`${API}/conversations/translate`, {
        conversation_id: conversationId,
        target_language: translationLanguage
      }, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      if (response.data.success && response.data.translated_messages) {
        setTranslatedMessages(prev => ({
          ...prev,
          [conversationId]: response.data.translated_messages
        }));
      }
    } catch (error) {
      console.error('Failed to translate conversation:', error);
      alert('Translation failed. Please try again.');
    }
    setLoading(false);
  };

  const getUniqueAgents = () => {
    const agents = new Set();
    conversations.forEach(conv => {
      conv.messages?.forEach(msg => {
        if (msg.agent_name) agents.add(msg.agent_name);
      });
    });
    return Array.from(agents).sort();
  };

  const filteredConversations = conversations.filter(conv => {
    if (!filterAgent) return true;
    return conv.messages?.some(msg => msg.agent_name === filterAgent);
  });

  const getRelationshipInfo = (agent1, agent2) => {
    return relationships.find(rel => 
      (rel.agent1 === agent1 && rel.agent2 === agent2) ||
      (rel.agent1 === agent2 && rel.agent2 === agent1)
    );
  };

  const getMessageTranslation = (conversationId, messageIndex) => {
    return translatedMessages[conversationId]?.[messageIndex];
  };

  const formatTimestamp = (timestamp) => {
    return new Date(timestamp).toLocaleString();
  };

  return (
    <div className="space-y-6">
      {/* Header Controls */}
      <div className="bg-white/10 backdrop-blur-lg rounded-xl p-6">
        <div className="flex justify-between items-center mb-6">
          <div>
            <h2 className="text-2xl font-bold text-white mb-2">💬 Live Conversations</h2>
            <p className="text-white/80">Monitor real-time agent interactions and relationships</p>
          </div>
          <div className="flex items-center space-x-4">
            <button
              onClick={() => setAutoRefresh(!autoRefresh)}
              className={`px-4 py-2 rounded-lg font-semibold transition-all duration-200 ${
                autoRefresh 
                  ? 'bg-green-600 hover:bg-green-700 text-white' 
                  : 'bg-gray-600 hover:bg-gray-700 text-white'
              }`}
            >
              {autoRefresh ? '🔄 Auto Refresh' : '⏸️ Paused'}
            </button>
            <button
              onClick={generateConversation}
              disabled={loading}
              className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-semibold transition-all duration-200 disabled:opacity-50"
            >
              {loading ? '⏳' : '🎭 Generate'}
            </button>
          </div>
        </div>

        {/* Filters and Translation */}
        <div className="flex flex-wrap gap-4">
          <div>
            <label className="block text-white text-sm font-medium mb-2">Filter by Agent</label>
            <select
              value={filterAgent}
              onChange={(e) => setFilterAgent(e.target.value)}
              className="px-3 py-2 bg-white/10 border border-white/20 rounded-lg text-white focus:ring-2 focus:ring-blue-500"
            >
              <option value="" className="bg-gray-800">All Agents</option>
              {getUniqueAgents().map(agent => (
                <option key={agent} value={agent} className="bg-gray-800">{agent}</option>
              ))}
            </select>
          </div>
          
          <div>
            <label className="block text-white text-sm font-medium mb-2">Translation Language</label>
            <select
              value={translationLanguage}
              onChange={(e) => setTranslationLanguage(e.target.value)}
              className="px-3 py-2 bg-white/10 border border-white/20 rounded-lg text-white focus:ring-2 focus:ring-blue-500"
            >
              {languages.map(lang => (
                <option key={lang.code} value={lang.code} className="bg-gray-800">
                  {lang.name}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Conversations Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Conversation List */}
        <div className="bg-white/10 backdrop-blur-lg rounded-xl p-6">
          <h3 className="text-xl font-bold text-white mb-4">Recent Conversations</h3>
          
          {filteredConversations.length === 0 ? (
            <div className="text-center text-white/60 py-8">
              <div className="text-4xl mb-2">💭</div>
              <p>No conversations yet</p>
              <p className="text-sm">Generate a conversation to get started</p>
            </div>
          ) : (
            <div className="space-y-3 max-h-96 overflow-y-auto">
              {filteredConversations.map((conversation) => (
                <motion.div
                  key={conversation.id}
                  onClick={() => setSelectedConversation(conversation)}
                  className={`p-4 rounded-lg cursor-pointer transition-all duration-200 ${
                    selectedConversation?.id === conversation.id
                      ? 'bg-blue-600/30 border border-blue-400/50'
                      : 'bg-white/5 hover:bg-white/10 border border-white/10'
                  }`}
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                >
                  <div className="flex justify-between items-start mb-2">
                    <h4 className="text-white font-semibold">
                      {conversation.title || `Conversation ${conversation.id.slice(0, 8)}`}
                    </h4>
                    <span className="text-white/40 text-xs">
                      {formatTimestamp(conversation.created_at)}
                    </span>
                  </div>
                  
                  <div className="text-white/70 text-sm mb-2">
                    {conversation.scenario || 'General Discussion'}
                  </div>
                  
                  <div className="flex justify-between items-center">
                    <span className="text-white/60 text-xs">
                      {conversation.messages?.length || 0} messages
                    </span>
                    <div className="flex space-x-1">
                      {conversation.agents?.slice(0, 3).map((agent, idx) => (
                        <div
                          key={idx}
                          className="w-6 h-6 bg-gradient-to-br from-purple-500 to-blue-500 rounded-full flex items-center justify-center text-xs text-white"
                          title={agent}
                        >
                          {agent[0]}
                        </div>
                      ))}
                      {conversation.agents?.length > 3 && (
                        <div className="w-6 h-6 bg-gray-600 rounded-full flex items-center justify-center text-xs text-white">
                          +{conversation.agents.length - 3}
                        </div>
                      )}
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>
          )}
        </div>

        {/* Selected Conversation Details */}
        <div className="bg-white/10 backdrop-blur-lg rounded-xl p-6">
          <div className="flex justify-between items-center mb-4">
            <h3 className="text-xl font-bold text-white">Conversation Details</h3>
            {selectedConversation && translationLanguage !== 'en' && (
              <button
                onClick={() => translateConversation(selectedConversation.id)}
                disabled={loading}
                className="px-3 py-1 bg-purple-600 hover:bg-purple-700 text-white rounded text-sm transition-all duration-200 disabled:opacity-50"
              >
                🌐 Translate
              </button>
            )}
          </div>
          
          {!selectedConversation ? (
            <div className="text-center text-white/60 py-12">
              <div className="text-4xl mb-2">👆</div>
              <p>Select a conversation to view details</p>
            </div>
          ) : (
            <div className="space-y-4">
              {/* Conversation Info */}
              <div className="bg-white/5 rounded-lg p-4">
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="text-white/60">Scenario:</span>
                    <div className="text-white">{selectedConversation.scenario || 'General'}</div>
                  </div>
                  <div>
                    <span className="text-white/60">Duration:</span>
                    <div className="text-white">{selectedConversation.duration || 'Ongoing'}</div>
                  </div>
                </div>
              </div>

              {/* Messages */}
              <div className="bg-white/5 rounded-lg p-4 h-64 overflow-y-auto">
                {selectedConversation.messages?.length === 0 ? (
                  <div className="text-center text-white/60 mt-8">
                    <p>No messages in this conversation yet</p>
                  </div>
                ) : (
                  <div className="space-y-3">
                    {selectedConversation.messages?.map((message, index) => {
                      const translation = getMessageTranslation(selectedConversation.id, index);
                      const relationship = index > 0 ? getRelationshipInfo(
                        message.agent_name,
                        selectedConversation.messages[index - 1].agent_name
                      ) : null;
                      
                      return (
                        <div key={index} className="space-y-2">
                          {relationship && (
                            <div className="text-center">
                              <span className="inline-block px-3 py-1 bg-purple-600/30 rounded-full text-xs text-white/80">
                                Relationship: {relationship.relationship_type} (Trust: {relationship.trust_level}/10)
                              </span>
                            </div>
                          )}
                          
                          <div className="flex space-x-3">
                            <div className="w-8 h-8 bg-gradient-to-br from-green-500 to-blue-500 rounded-full flex items-center justify-center text-sm text-white">
                              {message.agent_name?.[0] || '?'}
                            </div>
                            <div className="flex-1">
                              <div className="flex items-center space-x-2 mb-1">
                                <span className="text-white font-medium">
                                  {message.agent_name || 'Unknown'}
                                </span>
                                <span className="text-white/40 text-xs">
                                  {formatTimestamp(message.timestamp)}
                                </span>
                              </div>
                              <div className="text-white/80 text-sm">
                                {translation || message.message}
                              </div>
                              {translation && (
                                <div className="text-white/50 text-xs mt-1 italic">
                                  Original: {message.message}
                                </div>
                              )}
                            </div>
                          </div>
                        </div>
                      );
                    })}
                    <div ref={messagesEndRef} />
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Relationships Overview */}
      {relationships.length > 0 && (
        <div className="bg-white/10 backdrop-blur-lg rounded-xl p-6">
          <h3 className="text-xl font-bold text-white mb-4">🤝 Agent Relationships</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {relationships.map((rel, index) => (
              <div key={index} className="bg-white/5 rounded-lg p-4">
                <div className="flex justify-between items-center mb-2">
                  <div className="flex items-center space-x-2">
                    <div className="w-6 h-6 bg-blue-500 rounded-full flex items-center justify-center text-xs text-white">
                      {rel.agent1[0]}
                    </div>
                    <span className="text-white text-sm">↔️</span>
                    <div className="w-6 h-6 bg-green-500 rounded-full flex items-center justify-center text-xs text-white">
                      {rel.agent2[0]}
                    </div>
                  </div>
                  <div className="text-white/60 text-xs">
                    Trust: {rel.trust_level}/10
                  </div>
                </div>
                <div className="text-white font-medium text-sm">{rel.agent1} & {rel.agent2}</div>
                <div className="text-white/70 text-xs">{rel.relationship_type}</div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default ConversationViewer;