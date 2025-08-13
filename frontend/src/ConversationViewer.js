import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import axios from 'axios';
import { useAuth } from './AuthContext';

const API = process.env.REACT_APP_BACKEND_URL ? `${process.env.REACT_APP_BACKEND_URL}/api` : 'http://localhost:8001/api';

// Conversation View Modal Component
const ConversationViewModal = ({ isOpen, onClose, conversation }) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [highlightedMessage, setHighlightedMessage] = useState(null);
  const { token } = useAuth();
  const [agentAvatars, setAgentAvatars] = useState({});
  
  // Fetch agent avatars when modal opens
  useEffect(() => {
    if (isOpen && conversation?.messages) {
      fetchAgentAvatars();
    }
  }, [isOpen, conversation]);

  const fetchAgentAvatars = async () => {
    try {
      // Get unique agent names from conversation
      const agentNames = [...new Set(conversation.messages.map(msg => msg.agent_name).filter(Boolean))];
      
      // Fetch all agents to get their avatars
      const response = await axios.get(`${process.env.REACT_APP_BACKEND_URL}/api/agents`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      const agents = response.data || [];
      const avatarMap = {};
      
      // Create a map of agent names to their avatars
      agentNames.forEach(agentName => {
        const agent = agents.find(a => a.name === agentName);
        if (agent && agent.avatar_url) {
          avatarMap[agentName] = agent.avatar_url;
        }
      });
      
      setAgentAvatars(avatarMap);
    } catch (error) {
      console.error('Failed to fetch agent avatars:', error);
      setAgentAvatars({});
    }
  };

  const getAgentAvatar = (agentName) => {
    return agentAvatars[agentName] || null;
  };
  
  if (!isOpen || !conversation) return null;

  // Filter messages based on search query
  const filteredMessages = conversation.messages?.filter(msg => 
    msg.message.toLowerCase().includes(searchQuery.toLowerCase()) ||
    msg.agent_name.toLowerCase().includes(searchQuery.toLowerCase())
  ) || [];

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-[100] p-4 pt-12">
      <div className="bg-white rounded-lg w-full max-w-4xl max-h-[85vh] overflow-hidden mt-2">
        <div className="bg-gradient-to-r from-blue-600 to-purple-600 text-white p-4">
          <div className="flex justify-between items-center">
            <div>
              <h2 className="text-xl font-bold">{conversation.scenario_name || 'Conversation'}</h2>
              <p className="text-white/80 text-sm">{conversation.messages?.length || 0} messages • Round #{conversation.round_number || 1}</p>
            </div>
            <button
              onClick={onClose}
              className="text-white/70 hover:text-white text-2xl p-2 hover:bg-white/10 rounded-lg transition-colors"
            >
              ✕
            </button>
          </div>
          
          {/* Search Bar */}
          <div className="mt-4">
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search messages or agent names..."
              className="w-full px-3 py-2 bg-white/10 border border-white/20 rounded-lg text-white placeholder-white/50 focus:ring-2 focus:ring-white/30"
            />
            {searchQuery && (
              <p className="text-white/70 text-sm mt-1">
                Found {filteredMessages.length} message{filteredMessages.length !== 1 ? 's' : ''} matching "{searchQuery}"
              </p>
            )}
          </div>
        </div>
        
        <div className="p-4 overflow-y-auto" style={{maxHeight: 'calc(85vh - 140px)'}}>
          {filteredMessages.length === 0 ? (
            <div className="text-center text-gray-500 py-8">
              {searchQuery ? (
                <>
                  <div className="text-4xl mb-2">🔍</div>
                  <p>No messages found matching "{searchQuery}"</p>
                </>
              ) : (
                <>
                  <div className="text-4xl mb-2">💬</div>
                  <p>No messages in this conversation</p>
                </>
              )}
            </div>
          ) : (
            <div className="space-y-4">
              {filteredMessages.map((message, index) => {
                const avatarUrl = getAgentAvatar(message.agent_name);
                return (
                  <div key={index} className="flex space-x-3 p-3 rounded-lg bg-gray-50">
                    <div className="w-10 h-10 rounded-full flex items-center justify-center text-white font-medium overflow-hidden">
                      {avatarUrl ? (
                        <img 
                          src={avatarUrl} 
                          alt={message.agent_name || 'Agent'} 
                          className="w-full h-full object-cover rounded-full"
                          onError={(e) => {
                            // Fallback to gradient background if image fails to load
                            e.target.style.display = 'none';
                            e.target.nextSibling.style.display = 'flex';
                          }}
                        />
                      ) : null}
                      <div 
                        className={`w-full h-full bg-gradient-to-br from-blue-500 to-purple-500 rounded-full flex items-center justify-center ${avatarUrl ? 'hidden' : 'flex'}`}
                      >
                        {message.agent_name?.[0] || '?'}
                      </div>
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center space-x-2 mb-2">
                        <span className="font-semibold text-gray-900">
                          {message.agent_name || 'Unknown Agent'}
                        </span>
                        <span className="text-gray-500 text-sm">
                          {new Date(message.timestamp).toLocaleString()}
                        </span>
                      </div>
                      <div className="text-gray-700 leading-relaxed">
                        {searchQuery ? (
                          <span dangerouslySetInnerHTML={{
                            __html: message.message.replace(
                              new RegExp(`(${searchQuery})`, 'gi'),
                              '<mark class="bg-yellow-200 px-1 rounded">$1</mark>'
                            )
                          }} />
                        ) : (
                          message.message
                        )}
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

// Document/Report View Modal Component
const DocumentModal = ({ isOpen, onClose, document, type = 'document' }) => {
  const { token } = useAuth();
  const [downloading, setDownloading] = useState(false);

  if (!isOpen || !document) return null;

  const downloadPDF = async () => {
    setDownloading(true);
    try {
      const endpoint = type === 'report' 
        ? `/reports/${document.id}/download-pdf`
        : `/documents/${document.id}/download-pdf`;
      
      const response = await axios.get(`${API}${endpoint}`, {
        headers: { Authorization: `Bearer ${token}` },
        responseType: 'blob'
      });

      // Create download link
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `${document.title || 'document'}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Failed to download PDF:', error);
      alert('Failed to download PDF. Please try again.');
    }
    setDownloading(false);
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-[100] p-4">
      <div className="bg-white rounded-lg w-full max-w-4xl max-h-[90vh] overflow-hidden">
        <div className="bg-gradient-to-r from-green-600 to-blue-600 text-white p-4">
          <div className="flex justify-between items-center">
            <div>
              <h2 className="text-xl font-bold">{document.title || `Untitled ${type}`}</h2>
              <p className="text-white/80 text-sm">
                {type === 'document' ? `Created by ${document.creator_agent || 'Unknown'}` : 'Generated Report'} • 
                {new Date(document.created_at).toLocaleDateString()}
              </p>
            </div>
            <div className="flex items-center space-x-2">
              <button
                onClick={downloadPDF}
                disabled={downloading}
                className="px-3 py-1 bg-white/20 hover:bg-white/30 text-white rounded text-sm transition-all duration-200 disabled:opacity-50"
              >
                {downloading ? '⏳ Downloading...' : '📥 Download PDF'}
              </button>
              <button
                onClick={onClose}
                className="text-white/70 hover:text-white text-2xl p-2 hover:bg-white/10 rounded-lg transition-colors"
              >
                ✕
              </button>
            </div>
          </div>
        </div>
        
        <div className="p-6 overflow-y-auto" style={{maxHeight: 'calc(90vh - 100px)'}}>
          <div className="prose max-w-none">
            <div dangerouslySetInnerHTML={{ __html: document.content || 'No content available' }} />
          </div>
        </div>
      </div>
    </div>
  );
};

// Delete Confirmation Modal Component
const DeleteConfirmationModal = ({ isOpen, onClose, onConfirm, conversationTitle, isDeleting }) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-[100] p-4">
      <div className="bg-white rounded-xl shadow-2xl max-w-md w-full mx-4 overflow-hidden">
        {/* Header */}
        <div className="bg-gradient-to-r from-red-500 to-red-600 text-white p-6">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-white/20 rounded-full flex items-center justify-center">
              <span className="text-xl">⚠️</span>
            </div>
            <div>
              <h3 className="text-lg font-bold">Delete Conversation</h3>
              <p className="text-red-100 text-sm">This action cannot be undone</p>
            </div>
          </div>
        </div>

        {/* Content */}
        <div className="p-6">
          <p className="text-gray-700 mb-2">
            Are you sure you want to delete this conversation?
          </p>
          <div className="bg-gray-50 rounded-lg p-3 mb-4">
            <p className="font-medium text-gray-900 text-sm">"{conversationTitle}"</p>
          </div>
          <p className="text-gray-600 text-sm">
            This will permanently remove the conversation and all its messages from your archive.
          </p>
        </div>

        {/* Actions */}
        <div className="bg-gray-50 px-6 py-4 flex justify-end space-x-3">
          <button
            onClick={onClose}
            disabled={isDeleting}
            className="px-4 py-2 text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors duration-200 disabled:opacity-50"
          >
            Cancel
          </button>
          <button
            onClick={onConfirm}
            disabled={isDeleting}
            className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg transition-colors duration-200 disabled:opacity-50 flex items-center space-x-2"
          >
            {isDeleting ? (
              <>
                <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none"/>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"/>
                </svg>
                <span>Deleting...</span>
              </>
            ) : (
              <span>Delete</span>
            )}
          </button>
        </div>
      </div>
    </div>
  );
};

// Enhanced Conversation Viewer Component with Permanent Archive
const ConversationViewer = () => {
  const [conversations, setConversations] = useState([]);
  const [selectedConversation, setSelectedConversation] = useState(null);
  const [conversationReports, setConversationReports] = useState([]);
  const [conversationDocuments, setConversationDocuments] = useState([]);
  const [loading, setLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedConversations, setSelectedConversations] = useState(new Set());
  const [bulkDeleteMode, setBulkDeleteMode] = useState(false);
  const [deleteLoading, setDeleteLoading] = useState(false);
  const [expandedScenario, setExpandedScenario] = useState(null);
  const [showConversationModal, setShowConversationModal] = useState(false);
  const [showDocumentModal, setShowDocumentModal] = useState(false);
  const [selectedDocument, setSelectedDocument] = useState(null);
  const [documentType, setDocumentType] = useState('document');
  const [showDeleteModal, setShowDeleteModal] = useState(false);  // New state for delete modal
  const [conversationToDelete, setConversationToDelete] = useState(null);  // New state for conversation to delete
  const messagesEndRef = useRef(null);
  const { user, token } = useAuth();

  // Fetch conversations on mount
  useEffect(() => {
    fetchConversations();
  }, []);

  // Fetch related data when conversation is selected
  useEffect(() => {
    if (selectedConversation) {
      fetchConversationReports(selectedConversation.id);
      fetchConversationDocuments(selectedConversation.id);
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

  const fetchConversationReports = async (conversationId) => {
    try {
      const response = await axios.get(`${API}/conversations/${conversationId}/reports`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setConversationReports(response.data || []);
    } catch (error) {
      console.error('Failed to fetch conversation reports:', error);
      setConversationReports([]);
    }
  };

  const fetchConversationDocuments = async (conversationId) => {
    try {
      const response = await axios.get(`${API}/conversations/${conversationId}/documents`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setConversationDocuments(response.data || []);
    } catch (error) {
      console.error('Failed to fetch conversation documents:', error);
      setConversationDocuments([]);
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

  // Bulk delete selected conversations with improved modal
  const bulkDeleteConversations = async () => {
    if (selectedConversations.size === 0) {
      alert('Please select conversations to delete');
      return;
    }

    const conversationTitles = Array.from(selectedConversations)
      .map(id => {
        const conv = conversations.find(c => c.id === id);
        return getConversationTitle(conv);
      })
      .slice(0, 3)
      .join(', ');
    
    const titleText = selectedConversations.size > 3 
      ? `${conversationTitles} and ${selectedConversations.size - 3} more`
      : conversationTitles;

    setConversationToDelete({ 
      title: titleText, 
      isBulk: true, 
      count: selectedConversations.size 
    });
    setShowDeleteModal(true);
  };

  // Handle individual conversation delete
  const handleSingleDelete = (conversation) => {
    setConversationToDelete({ 
      title: getConversationTitle(conversation), 
      isBulk: false, 
      conversation 
    });
    setShowDeleteModal(true);
  };

  // Confirm deletion
  const confirmDelete = async () => {
    setDeleteLoading(true);
    
    try {
      if (conversationToDelete.isBulk) {
        // Bulk delete
        const conversationIds = Array.from(selectedConversations);
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
          await fetchConversations();
          setSelectedConversations(new Set());
          setBulkDeleteMode(false);
          
          if (selectedConversation && selectedConversations.has(selectedConversation.id)) {
            setSelectedConversation(null);
          }
        }

        if (failed === 0) {
          // Success - no need for alert as modal provides feedback
        } else {
          alert(`Deleted ${successful} conversation${successful > 1 ? 's' : ''}, failed to delete ${failed}`);
        }
      } else {
        // Single delete
        await axios.delete(`${API}/conversations/${conversationToDelete.conversation.id}`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        await fetchConversations();
        if (selectedConversation?.id === conversationToDelete.conversation.id) {
          setSelectedConversation(null);
        }
      }
    } catch (error) {
      console.error('Delete failed:', error);
      alert('Failed to delete conversation(s). Please try again.');
    }

    setDeleteLoading(false);
    setShowDeleteModal(false);
    setConversationToDelete(null);
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

  const openDocumentModal = (doc, type) => {
    setSelectedDocument(doc);
    setDocumentType(type);
    setShowDocumentModal(true);
  };

  return (
    <div className="space-y-6">
      {/* Header Controls */}
      <div className="bg-white/10 backdrop-blur-lg rounded-xl p-6">
        <div className="flex justify-between items-center mb-6">
          <div>
            <h2 className="text-2xl font-bold text-white mb-2">Conversation Archive</h2>
          </div>
        </div>

        {/* Search and Bulk Actions */}
        <div className="flex flex-wrap gap-4 items-center">
          <div className="flex-1 min-w-64">
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
          <div className="flex justify-between items-center mb-4">
            <h3 className="text-xl font-bold text-white">
              {searchQuery 
                ? `Search Results (${filteredConversations.length})`
                : `List (${conversations.length})`
              }
            </h3>
            <button
              onClick={() => setBulkDeleteMode(!bulkDeleteMode)}
              className={`px-3 py-2 rounded-lg text-sm font-medium transition-all duration-200 ${
                bulkDeleteMode 
                  ? 'bg-red-600 hover:bg-red-700 text-white' 
                  : 'bg-gray-600 hover:bg-gray-700 text-white'
              }`}
            >
              {bulkDeleteMode ? 'Cancel' : 'Delete'}
            </button>
          </div>
          
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
                  <p className="text-sm">Start a simulation to create conversations</p>
                </>
              )}
            </div>
          ) : (
            <div className="space-y-4 max-h-96 overflow-y-hidden hover:overflow-y-auto p-1" style={{scrollbarWidth: 'none', msOverflowStyle: 'none'}}>
              <style jsx>{`
                div::-webkit-scrollbar {
                  display: none;
                }
              `}</style>
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
                  whileHover={{ scale: bulkDeleteMode ? 1.005 : 1.01 }}
                  whileTap={{ scale: 0.99 }}
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
                        <h4 className="text-white font-semibold text-sm">
                          {getConversationTitle(conversation)}
                        </h4>
                        <span className="text-white/40 text-xs">
                          {formatTimestamp(conversation.created_at)}
                        </span>
                      </div>
                      
                      {/* Expandable Scenario Details */}
                      {conversation.scenario && (
                        <div className="mb-2">
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              setExpandedScenario(expandedScenario === conversation.id ? null : conversation.id);
                            }}
                            className="text-white/70 text-xs hover:text-white/90 flex items-center space-x-1"
                          >
                            <span>{expandedScenario === conversation.id ? '🔽' : '▶️'}</span>
                            <span>View Scenario Details</span>
                          </button>
                          {expandedScenario === conversation.id && (
                            <div className="mt-2 p-2 bg-white/5 rounded text-white/80 text-xs">
                              {conversation.scenario}
                            </div>
                          )}
                        </div>
                      )}
                      
                      <div className="flex justify-between items-center">
                        <span className="text-white/60 text-xs">
                          {conversation.messages?.length || 0} messages • {conversation.time_period || 'Unknown time'}
                        </span>
                      </div>
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>
          )}
        </div>

        {/* Enhanced Conversation Details Panel */}
        <div className="bg-white/10 backdrop-blur-lg rounded-xl p-6">
          <div className="flex justify-between items-center mb-4">
            <h3 className="text-xl font-bold text-white">Details</h3>
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
                <div className="space-y-3">
                  {/* Scenario and Metrics Row */}
                  <div className="flex items-start justify-between">
                    <div>
                      <span className="text-white/60 text-sm">Scenario:</span>
                      <div className="text-white font-medium">{selectedConversation.scenario_name || 'General'}</div>
                    </div>
                    
                    {/* Right Side Metrics */}
                    <div className="text-right">
                      <div className="text-white/40 text-xs mb-1">
                        {new Date(selectedConversation.created_at).toLocaleDateString()}
                      </div>
                      <div className="flex items-center space-x-4">
                        <div className="text-center">
                          <div className="text-white font-bold text-lg">{selectedConversation.round_number || 1}</div>
                          <div className="text-white/60 text-xs">Days</div>
                        </div>
                        <div className="text-center">
                          <div className="text-white font-bold text-lg">{selectedConversation.messages?.length || 0}</div>
                          <div className="text-white/60 text-xs">Messages</div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              {/* View Conversation Button */}
              <div className="bg-white/5 rounded-lg p-4">
                <button
                  onClick={() => setShowConversationModal(true)}
                  className="w-full px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium transition-all duration-200"
                >
                  View Full Conversation
                </button>
              </div>

              {/* Reports Section */}
              <div className="bg-white/5 rounded-lg p-4">
                <h4 className="text-white font-medium mb-3">📊 Generated Reports ({conversationReports.length})</h4>
                {conversationReports.length === 0 ? (
                  <p className="text-white/60 text-sm">No reports generated for this conversation</p>
                ) : (
                  <div className="space-y-2">
                    {conversationReports.map((report, index) => (
                      <div
                        key={index}
                        onClick={() => openDocumentModal(report, 'report')}
                        className="flex items-center justify-between p-2 bg-white/5 rounded cursor-pointer hover:bg-white/10 transition-colors"
                      >
                        <div>
                          <div className="text-white text-sm font-medium">{report.title}</div>
                          <div className="text-white/60 text-xs">
                            {new Date(report.created_at).toLocaleDateString()} • {report.type}
                          </div>
                        </div>
                        <div className="text-white/40 text-xs">Click to view</div>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              {/* Documents Section */}
              <div className="bg-white/5 rounded-lg p-4">
                <h4 className="text-white font-medium mb-3">📄 Agent Documents ({conversationDocuments.length})</h4>
                {conversationDocuments.length === 0 ? (
                  <p className="text-white/60 text-sm">No documents created by agents for this conversation</p>
                ) : (
                  <div className="space-y-2">
                    {conversationDocuments.map((document, index) => (
                      <div
                        key={index}
                        onClick={() => openDocumentModal(document, 'document')}
                        className="flex items-center justify-between p-2 bg-white/5 rounded cursor-pointer hover:bg-white/10 transition-colors"
                      >
                        <div>
                          <div className="text-white text-sm font-medium">{document.title}</div>
                          <div className="text-white/60 text-xs">
                            Created by {document.creator_agent} • {new Date(document.created_at).toLocaleDateString()} • {document.document_type}
                          </div>
                        </div>
                        <div className="text-white/40 text-xs">Click to view</div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Modals */}
      <ConversationViewModal
        isOpen={showConversationModal}
        onClose={() => setShowConversationModal(false)}
        conversation={selectedConversation}
      />

      <DocumentModal
        isOpen={showDocumentModal}
        onClose={() => setShowDocumentModal(false)}
        document={selectedDocument}
        type={documentType}
      />

      <DeleteConfirmationModal
        isOpen={showDeleteModal}
        onClose={() => {
          setShowDeleteModal(false);
          setConversationToDelete(null);
        }}
        onConfirm={confirmDelete}
        conversationTitle={conversationToDelete?.title || ''}
        isDeleting={deleteLoading}
      />
    </div>
  );
};

export default ConversationViewer;