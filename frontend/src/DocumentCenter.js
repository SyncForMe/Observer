import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import axios from 'axios';
import { useAuth } from './App';

const API = process.env.REACT_APP_BACKEND_URL ? `${process.env.REACT_APP_BACKEND_URL}/api` : 'http://localhost:8001/api';

// Document Generation and Management Center
const DocumentCenter = () => {
  const [documents, setDocuments] = useState([]);
  const [categories, setCategories] = useState([]);
  const [selectedCategory, setSelectedCategory] = useState('');
  const [selectedDocument, setSelectedDocument] = useState(null);
  const [loading, setLoading] = useState(false);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showGenerateModal, setShowGenerateModal] = useState(false);
  const [selectedDocuments, setSelectedDocuments] = useState(new Set());
  const [newDocument, setNewDocument] = useState({
    title: '',
    category: '',
    content: '',
    description: ''
  });
  const [generateOptions, setGenerateOptions] = useState({
    type: 'summary',
    scenario: '',
    conversation_id: '',
    template: 'protocol'
  });

  // Get auth data safely
  let user, token;
  try {
    const auth = useAuth();
    user = auth?.user;
    token = auth?.token;
  } catch (error) {
    console.error('Auth error in DocumentCenter:', error);
    user = null;
    token = null;
  }

  // Document types for generation
  const documentTypes = [
    { value: 'summary', label: '📋 Conversation Summary' },
    { value: 'report', label: '📊 Analysis Report' },
    { value: 'protocol', label: '📝 Meeting Protocol' },
    { value: 'action_items', label: '✅ Action Items' },
    { value: 'decisions', label: '🎯 Decisions Made' },
    { value: 'insights', label: '💡 Key Insights' }
  ];

  const templates = [
    { value: 'protocol', label: 'Meeting Protocol' },
    { value: 'research', label: 'Research Report' },
    { value: 'executive', label: 'Executive Summary' },
    { value: 'technical', label: 'Technical Documentation' },
    { value: 'creative', label: 'Creative Brief' }
  ];

  // Fetch documents and categories on mount
  useEffect(() => {
    if (token) {
      fetchDocuments();
      fetchCategories();
    }
  }, [token]);

  // Fetch documents when category filter changes
  useEffect(() => {
    if (token) {
      fetchDocuments();
    }
  }, [selectedCategory, token]);

  const fetchDocuments = async () => {
    if (!token) return;
    
    setLoading(true);
    try {
      const url = selectedCategory 
        ? `${API}/documents?category=${selectedCategory}`
        : `${API}/documents`;
      
      const response = await axios.get(url, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      if (response.data) {
        setDocuments(Array.isArray(response.data) ? response.data : []);
      }
    } catch (error) {
      console.error('Failed to fetch documents:', error);
      setDocuments([]);
    }
    setLoading(false);
  };

  const fetchCategories = async () => {
    if (!token) return;
    
    try {
      const response = await axios.get(`${API}/documents/categories`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (response.data) {
        setCategories(Array.isArray(response.data) ? response.data : []);
      }
    } catch (error) {
      console.error('Failed to fetch categories:', error);
      setCategories([]);
    }
  };

  const createDocument = async () => {
    if (!newDocument.title || !newDocument.content || !token) {
      alert('Please fill in title and content');
      return;
    }

    setLoading(true);
    try {
      const response = await axios.post(`${API}/documents/create`, newDocument, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      if (response.data?.success) {
        setShowCreateModal(false);
        setNewDocument({ title: '', category: '', content: '', description: '' });
        await fetchDocuments();
      }
    } catch (error) {
      console.error('Failed to create document:', error);
      alert('Failed to create document. Please try again.');
    }
    setLoading(false);
  };

  const generateDocument = async () => {
    if (!generateOptions.type || !token) {
      alert('Please select a document type');
      return;
    }

    setLoading(true);
    try {
      const response = await axios.post(`${API}/documents/generate`, generateOptions, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      if (response.data?.success) {
        setShowGenerateModal(false);
        setGenerateOptions({ type: 'summary', scenario: '', conversation_id: '', template: 'protocol' });
        await fetchDocuments();
        alert('Document generated successfully!');
      }
    } catch (error) {
      console.error('Failed to generate document:', error);
      alert('Failed to generate document. Please try again.');
    }
    setLoading(false);
  };

  const analyzeConversation = async () => {
    if (!token) return;
    
    setLoading(true);
    try {
      const response = await axios.post(`${API}/documents/analyze-conversation`, {}, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      if (response.data?.success) {
        await fetchDocuments();
        alert('Conversation analysis completed!');
      }
    } catch (error) {
      console.error('Failed to analyze conversation:', error);
      alert('Failed to analyze conversation. Please try again.');
    }
    setLoading(false);
  };

  const deleteDocument = async (documentId) => {
    if (!window.confirm('Are you sure you want to delete this document?') || !token) return;

    setLoading(true);
    try {
      const response = await axios.delete(`${API}/documents/${documentId}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      if (response.data?.success) {
        await fetchDocuments();
        if (selectedDocument?.id === documentId) {
          setSelectedDocument(null);
        }
      }
    } catch (error) {
      console.error('Failed to delete document:', error);
      alert('Failed to delete document. Please try again.');
    }
    setLoading(false);
  };

  const bulkDeleteDocuments = async () => {
    if (selectedDocuments.size === 0 || !token) {
      alert('Please select documents to delete');
      return;
    }

    if (!window.confirm(`Are you sure you want to delete ${selectedDocuments.size} documents?`)) return;

    setLoading(true);
    try {
      const response = await axios.post(`${API}/documents/bulk-delete`, {
        document_ids: Array.from(selectedDocuments)
      }, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      if (response.data?.success) {
        setSelectedDocuments(new Set());
        await fetchDocuments();
        alert(`Successfully deleted ${response.data.deleted_count} documents`);
      }
    } catch (error) {
      console.error('Failed to bulk delete documents:', error);
      alert('Failed to delete documents. Please try again.');
    }
    setLoading(false);
  };

  const toggleDocumentSelection = (documentId) => {
    const newSelected = new Set(selectedDocuments);
    if (newSelected.has(documentId)) {
      newSelected.delete(documentId);
    } else {
      newSelected.add(documentId);
    }
    setSelectedDocuments(newSelected);
  };

  const selectAllDocuments = () => {
    if (selectedDocuments.size === documents.length) {
      setSelectedDocuments(new Set());
    } else {
      setSelectedDocuments(new Set(documents.map(doc => doc.id)));
    }
  };

  const formatDate = (dateString) => {
    try {
      return new Date(dateString).toLocaleDateString();
    } catch (error) {
      return 'Invalid Date';
    }
  };

  const getDocumentIcon = (category) => {
    const icons = {
      'summary': '📋',
      'report': '📊',
      'protocol': '📝',
      'analysis': '🔍',
      'insights': '💡',
      'decisions': '🎯',
      'action_items': '✅'
    };
    return icons[category] || '📄';
  };

  const getCategoryColor = (category) => {
    const colors = {
      'summary': 'bg-blue-500',
      'report': 'bg-green-500',
      'protocol': 'bg-purple-500',
      'analysis': 'bg-orange-500',
      'insights': 'bg-yellow-500',
      'decisions': 'bg-red-500',
      'action_items': 'bg-indigo-500'
    };
    return colors[category] || 'bg-gray-500';
  };

  // Show authentication error if no user/token
  if (!user || !token) {
    return (
      <div className="space-y-6">
        <div className="bg-white/10 backdrop-blur-lg rounded-xl p-6">
          <div className="text-center text-white/60 py-12">
            <div className="text-4xl mb-2">🔐</div>
            <h3 className="text-xl font-semibold text-white mb-2">Authentication Required</h3>
            <p>Please log in to access the Document Center</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header and Controls */}
      <div className="bg-white/10 backdrop-blur-lg rounded-xl p-6">
        <div className="flex justify-between items-center mb-6">
          <div>
            <h2 className="text-2xl font-bold text-white mb-2">📄 Document Center</h2>
            <p className="text-white/80">Generate, manage, and analyze documents from AI conversations</p>
          </div>
          <div className="flex items-center space-x-3">
            <button
              onClick={() => setShowGenerateModal(true)}
              className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-semibold transition-all duration-200"
            >
              🤖 Generate
            </button>
            <button
              onClick={() => setShowCreateModal(true)}
              className="px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg font-semibold transition-all duration-200"
            >
              ➕ Create
            </button>
            <button
              onClick={analyzeConversation}
              disabled={loading}
              className="px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg font-semibold transition-all duration-200 disabled:opacity-50"
            >
              🔍 Analyze
            </button>
          </div>
        </div>

        {/* Filters and Bulk Actions */}
        <div className="flex flex-wrap gap-4 items-center">
          <div>
            <label className="block text-white text-sm font-medium mb-2">Filter by Category</label>
            <select
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              className="px-3 py-2 bg-white/10 border border-white/20 rounded-lg text-white focus:ring-2 focus:ring-blue-500"
            >
              <option value="" className="bg-gray-800">All Categories</option>
              {categories.map(category => (
                <option key={category} value={category} className="bg-gray-800">
                  {category.charAt(0).toUpperCase() + category.slice(1)}
                </option>
              ))}
            </select>
          </div>

          {selectedDocuments.size > 0 && (
            <div className="flex items-center space-x-3">
              <span className="text-white text-sm">
                {selectedDocuments.size} selected
              </span>
              <button
                onClick={bulkDeleteDocuments}
                disabled={loading}
                className="px-3 py-1 bg-red-600 hover:bg-red-700 text-white rounded text-sm transition-all duration-200 disabled:opacity-50"
              >
                🗑️ Delete Selected
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Documents Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Document List */}
        <div className="bg-white/10 backdrop-blur-lg rounded-xl p-6">
          <div className="flex justify-between items-center mb-4">
            <h3 className="text-xl font-bold text-white">Documents</h3>
            {documents.length > 0 && (
              <button
                onClick={selectAllDocuments}
                className="text-white/70 hover:text-white text-sm transition-colors"
              >
                {selectedDocuments.size === documents.length ? 'Deselect All' : 'Select All'}
              </button>
            )}
          </div>

          {loading ? (
            <div className="text-center text-white/60 py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-white mx-auto mb-2"></div>
              <p>Loading documents...</p>
            </div>
          ) : documents.length === 0 ? (
            <div className="text-center text-white/60 py-8">
              <div className="text-4xl mb-2">📄</div>
              <p>No documents yet</p>
              <p className="text-sm">Create or generate a document to get started</p>
            </div>
          ) : (
            <div className="space-y-3 max-h-96 overflow-y-auto">
              {documents.map((document) => (
                <motion.div
                  key={document.id}
                  className={`p-4 rounded-lg cursor-pointer transition-all duration-200 border ${
                    selectedDocument?.id === document.id
                      ? 'bg-blue-600/30 border-blue-400/50'
                      : 'bg-white/5 hover:bg-white/10 border-white/10'
                  }`}
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                >
                  <div className="flex items-start space-x-3">
                    <input
                      type="checkbox"
                      checked={selectedDocuments.has(document.id)}
                      onChange={() => toggleDocumentSelection(document.id)}
                      onClick={(e) => e.stopPropagation()}
                      className="mt-1"
                    />
                    
                    <div
                      className="flex-1"
                      onClick={() => setSelectedDocument(document)}
                    >
                      <div className="flex justify-between items-start mb-2">
                        <h4 className="text-white font-semibold flex items-center space-x-2">
                          <span>{getDocumentIcon(document.category)}</span>
                          <span>{document.title}</span>
                        </h4>
                        <span className="text-white/40 text-xs">
                          {formatDate(document.created_at)}
                        </span>
                      </div>
                      
                      <div className="flex items-center space-x-2 mb-2">
                        <span className={`px-2 py-1 ${getCategoryColor(document.category)} text-white text-xs rounded-full`}>
                          {document.category}
                        </span>
                        {document.scenario && (
                          <span className="px-2 py-1 bg-gray-600 text-white text-xs rounded-full">
                            {document.scenario}
                          </span>
                        )}
                      </div>
                      
                      <p className="text-white/70 text-sm line-clamp-2">
                        {document.description || document.preview || 'No description available'}
                      </p>
                    </div>
                    
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        deleteDocument(document.id);
                      }}
                      className="text-red-400 hover:text-red-300 transition-colors"
                    >
                      🗑️
                    </button>
                  </div>
                </motion.div>
              ))}
            </div>
          )}
        </div>

        {/* Document Viewer */}
        <div className="bg-white/10 backdrop-blur-lg rounded-xl p-6">
          <h3 className="text-xl font-bold text-white mb-4">Document Preview</h3>
          
          {!selectedDocument ? (
            <div className="text-center text-white/60 py-12">
              <div className="text-4xl mb-2">👆</div>
              <p>Select a document to view its content</p>
            </div>
          ) : (
            <div className="space-y-4">
              {/* Document Header */}
              <div className="bg-white/5 rounded-lg p-4">
                <h4 className="text-white font-bold text-lg mb-2">
                  {getDocumentIcon(selectedDocument.category)} {selectedDocument.title}
                </h4>
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="text-white/60">Category:</span>
                    <div className="text-white">{selectedDocument.category}</div>
                  </div>
                  <div>
                    <span className="text-white/60">Created:</span>
                    <div className="text-white">{formatDate(selectedDocument.created_at)}</div>
                  </div>
                  {selectedDocument.scenario && (
                    <div>
                      <span className="text-white/60">Scenario:</span>
                      <div className="text-white">{selectedDocument.scenario}</div>
                    </div>
                  )}
                  <div>
                    <span className="text-white/60">Size:</span>
                    <div className="text-white">{selectedDocument.content?.length || 0} characters</div>
                  </div>
                </div>
              </div>

              {/* Document Content */}
              <div className="bg-white/5 rounded-lg p-4 h-64 overflow-y-auto">
                <div className="text-white/80 whitespace-pre-wrap text-sm">
                  {selectedDocument.content || selectedDocument.preview || 'No content available'}
                </div>
              </div>

              {/* Document Actions */}
              <div className="flex space-x-3">
                <button
                  onClick={() => {
                    navigator.clipboard.writeText(selectedDocument.content || '');
                    alert('Content copied to clipboard!');
                  }}
                  className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-sm transition-all duration-200"
                >
                  📋 Copy
                </button>
                <button
                  onClick={() => {
                    const blob = new Blob([selectedDocument.content || ''], { type: 'text/plain' });
                    const url = URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = `${selectedDocument.title}.txt`;
                    a.click();
                    URL.revokeObjectURL(url);
                  }}
                  className="px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg text-sm transition-all duration-200"
                >
                  💾 Download
                </button>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Create Document Modal */}
      <AnimatePresence>
        {showCreateModal && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4"
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              className="bg-white rounded-lg w-full max-w-2xl max-h-[90vh] overflow-hidden"
            >
              <div className="bg-gradient-to-r from-green-600 to-blue-600 text-white p-6">
                <div className="flex justify-between items-center">
                  <h3 className="text-2xl font-bold">➕ Create Document</h3>
                  <button
                    onClick={() => setShowCreateModal(false)}
                    className="text-white/70 hover:text-white text-2xl"
                  >
                    ✕
                  </button>
                </div>
              </div>
              
              <div className="p-6 space-y-4">
                <div>
                  <label className="block text-gray-700 font-medium mb-2">Title</label>
                  <input
                    type="text"
                    value={newDocument.title}
                    onChange={(e) => setNewDocument({...newDocument, title: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                    placeholder="Enter document title..."
                  />
                </div>
                
                <div>
                  <label className="block text-gray-700 font-medium mb-2">Category</label>
                  <select
                    value={newDocument.category}
                    onChange={(e) => setNewDocument({...newDocument, category: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="">Select category...</option>
                    {categories.map(category => (
                      <option key={category} value={category}>{category}</option>
                    ))}
                  </select>
                </div>
                
                <div>
                  <label className="block text-gray-700 font-medium mb-2">Description</label>
                  <input
                    type="text"
                    value={newDocument.description}
                    onChange={(e) => setNewDocument({...newDocument, description: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                    placeholder="Brief description..."
                  />
                </div>
                
                <div>
                  <label className="block text-gray-700 font-medium mb-2">Content</label>
                  <textarea
                    value={newDocument.content}
                    onChange={(e) => setNewDocument({...newDocument, content: e.target.value})}
                    rows={8}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                    placeholder="Enter document content..."
                  />
                </div>
                
                <div className="flex justify-end space-x-3 pt-4">
                  <button
                    onClick={() => setShowCreateModal(false)}
                    className="px-6 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
                  >
                    Cancel
                  </button>
                  <button
                    onClick={createDocument}
                    disabled={loading}
                    className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
                  >
                    {loading ? 'Creating...' : 'Create'}
                  </button>
                </div>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Generate Document Modal */}
      <AnimatePresence>
        {showGenerateModal && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4"
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              className="bg-white rounded-lg w-full max-w-2xl max-h-[90vh] overflow-hidden"
            >
              <div className="bg-gradient-to-r from-blue-600 to-purple-600 text-white p-6">
                <div className="flex justify-between items-center">
                  <h3 className="text-2xl font-bold">🤖 Generate Document</h3>
                  <button
                    onClick={() => setShowGenerateModal(false)}
                    className="text-white/70 hover:text-white text-2xl"
                  >
                    ✕
                  </button>
                </div>
              </div>
              
              <div className="p-6 space-y-4">
                <div>
                  <label className="block text-gray-700 font-medium mb-2">Document Type</label>
                  <select
                    value={generateOptions.type}
                    onChange={(e) => setGenerateOptions({...generateOptions, type: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  >
                    {documentTypes.map(type => (
                      <option key={type.value} value={type.value}>{type.label}</option>
                    ))}
                  </select>
                </div>
                
                <div>
                  <label className="block text-gray-700 font-medium mb-2">Template</label>
                  <select
                    value={generateOptions.template}
                    onChange={(e) => setGenerateOptions({...generateOptions, template: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  >
                    {templates.map(template => (
                      <option key={template.value} value={template.value}>{template.label}</option>
                    ))}
                  </select>
                </div>
                
                <div>
                  <label className="block text-gray-700 font-medium mb-2">Scenario (Optional)</label>
                  <input
                    type="text"
                    value={generateOptions.scenario}
                    onChange={(e) => setGenerateOptions({...generateOptions, scenario: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                    placeholder="Specific scenario to analyze..."
                  />
                </div>
                
                <div className="flex justify-end space-x-3 pt-4">
                  <button
                    onClick={() => setShowGenerateModal(false)}
                    className="px-6 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
                  >
                    Cancel
                  </button>
                  <button
                    onClick={generateDocument}
                    disabled={loading}
                    className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
                  >
                    {loading ? 'Generating...' : 'Generate'}
                  </button>
                </div>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default DocumentCenter;