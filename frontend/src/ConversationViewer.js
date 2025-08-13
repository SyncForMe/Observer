import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import axios from 'axios';
import { useAuth } from './AuthContext';

const API = process.env.REACT_APP_BACKEND_URL ? `${process.env.REACT_APP_BACKEND_URL}/api` : 'http://localhost:8001/api';

// Enhanced Conversation Viewer Component with Search and Bulk Delete
const ConversationViewer = () => {
  const [conversations, setConversations] = useState([]);
  const [selectedConversation, setSelectedConversation] = useState(null);
  const [loading, setLoading] = useState(false);
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedConversations, setSelectedConversations] = useState(new Set());
  const [bulkDeleteMode, setBulkDeleteMode] = useState(false);
  const [deleteLoading, setDeleteLoading] = useState(false);
  const messagesEndRef = useRef(null);
  const { user, token } = useAuth();

  // Fetch conversations on mount and set up auto-refresh
  useEffect(() => {
    fetchConversations();
    
    let interval;
    if (autoRefresh) {
      interval = setInterval(fetchConversations, 5000); // Increased to 5 seconds for better performance
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
        // Sort by created_at in descending order (newest first)
        const sortedConversations = response.data.sort((a, b) => 
          new Date(b.created_at) - new Date(a.created_at)
        );
        setConversations(sortedConversations);
        
        // Update selected conversation if it exists
        if (selectedConversation) {
          const updated = sortedConversations.find(c => c.id === selectedConversation.id);
          if (updated) {
            setSelectedConversation(updated);
          }
        }
      }
    } catch (error) {
      console.error('Failed to fetch conversations:', error);
    }
  };

  // Filter conversations based on search query
  const filteredConversations = conversations.filter(conv => {
    if (!searchQuery.trim()) return true;
    
    const query = searchQuery.toLowerCase();
    const scenarioName = (conv.scenario_name || '').toLowerCase();
    const scenario = (conv.scenario || '').toLowerCase();
    const timeperiod = (conv.time_period || '').toLowerCase();
    
    return scenarioName.includes(query) || 
           scenario.includes(query) || 
           timeperiod.includes(query);
  });

  // Handle conversation selection for bulk delete
  const toggleConversationSelection = (conversationId) => {
    const newSelected = new Set(selectedConversations);
    if (newSelected.has(conversationId)) {
      newSelected.delete(conversationId);
    } else {
      newSelected.add(conversationId);
    }
    setSelectedConversations(newSelected);
  };

  // Select all filtered conversations
  const selectAllConversations = () => {
    const allIds = new Set(filteredConversations.map(conv => conv.id));
    setSelectedConversations(allIds);
  };

  // Clear all selections
  const clearAllSelections = () => {
    setSelectedConversations(new Set());
  };

  // Bulk delete selected conversations
  const bulkDeleteConversations = async () => {
    if (selectedConversations.size === 0) {
      alert('Please select conversations to delete');
      return;
    }

    const confirmMessage = `Are you sure you want to delete ${selectedConversations.size} conversation${selectedConversations.size > 1 ? 's' : ''}? This action cannot be undone.`;
    if (!window.confirm(confirmMessage)) {
      return;
    }

    setDeleteLoading(true);
    const conversationIds = Array.from(selectedConversations);
    
    try {
      // Delete conversations one by one (backend doesn't have bulk delete endpoint yet)
      const deletePromises = conversationIds.map(async (conversationId) => {
        try {
          await axios.delete(`${API}/conversations/${conversationId}`, {
            headers: { Authorization: `Bearer ${token}` }
          });
          return { id: conversationId, success: true };
        } catch (error) {
          console.error(`Failed to delete conversation ${conversationId}:`, error);
          return { id: conversationId, success: false, error };
        }
      });

      const results = await Promise.all(deletePromises);
      const successful = results.filter(r => r.success).length;
      const failed = results.filter(r => !r.success).length;

      if (successful > 0) {
        // Refresh conversations list
        await fetchConversations();
        
        // Clear selections
        setSelectedConversations(new Set());
        
        // Clear selected conversation if it was deleted
        if (selectedConversation && selectedConversations.has(selectedConversation.id)) {
          setSelectedConversation(null);
        }
      }

      // Show result message
      if (failed === 0) {
        alert(`Successfully deleted ${successful} conversation${successful > 1 ? 's' : ''}`);
      } else {
        alert(`Deleted ${successful} conversation${successful > 1 ? 's' : ''}, failed to delete ${failed}`);
      }

    } catch (error) {
      console.error('Bulk delete failed:', error);
      alert('Failed to delete conversations. Please try again.');
    }

    setDeleteLoading(false);
  };

  const formatTimestamp = (timestamp) => {
    return new Date(timestamp).toLocaleString();
  };

  const getConversationTitle = (conversation) => {
    // Use scenario_name as title if available, otherwise fallback to generic title
    if (conversation.scenario_name && conversation.scenario_name.trim()) {
      return conversation.scenario_name;
    }
    return `Conversation ${conversation.id.slice(0, 8)}`;
  };

  return (
    <div className="space-y-6">
      {/* Header Controls */}
      <div className="bg-white/10 backdrop-blur-lg rounded-xl p-6">
        <div className="flex justify-between items-center mb-6">
          <div>
            <h2 className="text-2xl font-bold text-white mb-2">💬 My Conversations</h2>
            <p className="text-white/80">View and manage your conversation history</p>
          </div>
          <div className="flex items-center space-x-4">
            <button
              onClick={() => setBulkDeleteMode(!bulkDeleteMode)}
              className={`px-4 py-2 rounded-lg font-semibold transition-all duration-200 ${
                bulkDeleteMode 
                  ? 'bg-red-600 hover:bg-red-700 text-white' 
                  : 'bg-gray-600 hover:bg-gray-700 text-white'
              }`}
            >
              {bulkDeleteMode ? '📝 Select Mode' : '🗑️ Delete Mode'}
            </button>
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
          </div>
        </div>

        {/* Search and Bulk Actions */}
        <div className="flex flex-wrap gap-4 items-center">
          <div className="flex-1 min-w-64">
            <label className="block text-white text-sm font-medium mb-2">🔍 Search Conversations</label>
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search by scenario name or description..."
              className="w-full px-3 py-2 bg-white/10 border border-white/20 rounded-lg text-white placeholder-white/50 focus:ring-2 focus:ring-blue-500"
            />
          </div>
          
          {bulkDeleteMode && (
            <div className="flex items-center space-x-2">
              <button
                onClick={selectAllConversations}
                className="px-3 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-sm transition-all duration-200"
              >
                Select All ({filteredConversations.length})
              </button>
              <button
                onClick={clearAllSelections}
                className="px-3 py-2 bg-gray-600 hover:bg-gray-700 text-white rounded-lg text-sm transition-all duration-200"
              >
                Clear Selection
              </button>
              <button
                onClick={bulkDeleteConversations}
                disabled={deleteLoading || selectedConversations.size === 0}
                className="px-3 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg text-sm transition-all duration-200 disabled:opacity-50"
              >
                {deleteLoading ? '⏳ Deleting...' : `Delete (${selectedConversations.size})`}
              </button>
            </div>
          )}
        </div>

        {/* Search Results Counter */}
        {searchQuery && (
          <div className="mt-4 text-white/70 text-sm">
            Found {filteredConversations.length} conversation{filteredConversations.length !== 1 ? 's' : ''} matching "{searchQuery}"
          </div>
        )}
      </div>

      {/* Conversations Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Conversation List */}
        <div className="bg-white/10 backdrop-blur-lg rounded-xl p-6">
          <h3 className="text-xl font-bold text-white mb-4">
            {searchQuery 
              ? `Search Results (${filteredConversations.length})`
              : `My Conversations (${conversations.length})`
            }
          </h3>
          
          {filteredConversations.length === 0 ? (
            <div className="text-center text-white/60 py-8">
              <div className="text-4xl mb-2">💭</div>
              {searchQuery ? (
                <>
                  <p>No conversations found matching "{searchQuery}"</p>
                  <p className="text-sm">Try a different search term</p>
                </>
              ) : (
                <>
                  <p>No conversations yet</p>
                  <p className="text-sm">Generate a conversation to get started</p>
                </>
              )}
            </div>
          ) : (
            <div className="space-y-3 max-h-96 overflow-y-auto">
              {filteredConversations.map((conversation) => (
                <motion.div
                  key={conversation.id}
                  onClick={() => !bulkDeleteMode && setSelectedConversation(conversation)}
                  className={`p-4 rounded-lg transition-all duration-200 ${
                    bulkDeleteMode 
                      ? 'cursor-pointer border-2' + (selectedConversations.has(conversation.id) 
                          ? ' border-red-400 bg-red-600/20' 
                          : ' border-white/20 hover:border-red-300 bg-white/5')
                      : 'cursor-pointer' + (selectedConversation?.id === conversation.id
                          ? ' bg-blue-600/30 border border-blue-400/50'
                          : ' bg-white/5 hover:bg-white/10 border border-white/10')
                  }`}
                  whileHover={{ scale: bulkDeleteMode ? 1.01 : 1.02 }}
                  whileTap={{ scale: 0.98 }}
                >
                  <div className="flex items-start space-x-3">
                    {bulkDeleteMode && (
                      <div 
                        className="mt-1"
                        onClick={(e) => {
                          e.stopPropagation();
                          toggleConversationSelection(conversation.id);
                        }}
                      >
                        <input
                          type="checkbox"
                          checked={selectedConversations.has(conversation.id)}
                          onChange={() => toggleConversationSelection(conversation.id)}
                          className="w-4 h-4 text-red-600 bg-gray-100 border-gray-300 rounded focus:ring-red-500"
                        />
                      </div>
                    )}
                    
                    <div className="flex-1">
                      <div className="flex justify-between items-start mb-2">
                        <h4 className="text-white font-semibold">
                          {getConversationTitle(conversation)}
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
                          {conversation.messages?.length || 0} messages • {conversation.time_period || 'Unknown time'}
                        </span>
                        {conversation.agents && conversation.agents.length > 0 && (
                          <div className="flex space-x-1">
                            {conversation.agents.slice(0, 3).map((agent, idx) => (
                              <div
                                key={idx}
                                className="w-6 h-6 bg-gradient-to-br from-purple-500 to-blue-500 rounded-full flex items-center justify-center text-xs text-white"
                                title={agent}
                              >
                                {agent[0]}
                              </div>
                            ))}
                            {conversation.agents.length > 3 && (
                              <div className="w-6 h-6 bg-gray-600 rounded-full flex items-center justify-center text-xs text-white">
                                +{conversation.agents.length - 3}
                              </div>
                            )}
                          </div>
                        )}
                      </div>
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
          </div>
          
          {!selectedConversation ? (
            <div className="text-center text-white/60 py-12">
              <div className="text-4xl mb-2">👆</div>
              <p>Select a conversation to view details</p>
              {bulkDeleteMode && (
                <p className="text-sm mt-2">Exit delete mode to view conversations</p>
              )}
            </div>
          ) : (
            <div className="space-y-4">
              {/* Conversation Info */}
              <div className="bg-white/5 rounded-lg p-4">
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="text-white/60">Scenario:</span>
                    <div className="text-white">{selectedConversation.scenario_name || 'General'}</div>
                  </div>
                  <div>
                    <span className="text-white/60">Time Period:</span>
                    <div className="text-white">{selectedConversation.time_period || 'Unknown'}</div>
                  </div>
                  <div>
                    <span className="text-white/60">Round:</span>
                    <div className="text-white">#{selectedConversation.round_number || 1}</div>
                  </div>
                  <div>
                    <span className="text-white/60">Messages:</span>
                    <div className="text-white">{selectedConversation.messages?.length || 0}</div>
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
                      return (
                        <div key={index} className="space-y-2">
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
                                {message.message}
                              </div>
                            </div>
                          </div>
                        </div>
                      );
                    })}
                    <div ref={messagesEndRef} />
                  </div>
                )}
              </div>
              
              {/* Individual Delete Button */}
              <div className="flex justify-end">
                <button  
                  onClick={async () => {
                    if (window.confirm('Are you sure you want to delete this conversation? This action cannot be undone.')) {
                      setDeleteLoading(true);
                      try {
                        await axios.delete(`${API}/conversations/${selectedConversation.id}`, {
                          headers: { Authorization: `Bearer ${token}` }
                        });
                        await fetchConversations();
                        setSelectedConversation(null);
                        alert('Conversation deleted successfully');
                      } catch (error) {
                        console.error('Failed to delete conversation:', error);
                        alert('Failed to delete conversation. Please try again.');
                      }
                      setDeleteLoading(false);
                    }
                  }}
                  disabled={deleteLoading}
                  className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg text-sm transition-all duration-200 disabled:opacity-50"
                >
                  {deleteLoading ? '⏳ Deleting...' : '🗑️ Delete This Conversation'}
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ConversationViewer;