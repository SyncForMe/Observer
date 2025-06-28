import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import axios from 'axios';
import { useAuth } from './AuthContext';

const API = process.env.REACT_APP_BACKEND_URL ? `${process.env.REACT_APP_BACKEND_URL}/api` : 'http://localhost:8001/api';

// Custom Scenario Creator Component
const ScenarioCreator = ({ isOpen, onClose, onScenarioCreated }) => {
  const [scenarios, setScenarios] = useState([]);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('create');
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [newScenario, setNewScenario] = useState({
    name: '',
    description: '',
    context: '',
    objectives: '',
    setting: '',
    participants: '',
    constraints: '',
    success_criteria: ''
  });
  const [selectedFile, setSelectedFile] = useState(null);
  const [uploadProgress, setUploadProgress] = useState(0);
  const { user, token } = useAuth();

  // Predefined scenario templates
  const scenarioTemplates = [
    {
      name: 'Business Board Meeting',
      description: 'Strategic decision-making session for corporate leadership',
      context: 'The board of directors is meeting to discuss quarterly performance and strategic initiatives for the upcoming year.',
      objectives: 'Make key strategic decisions, review financial performance, approve budgets, discuss market opportunities',
      setting: 'Corporate boardroom with senior executives and key stakeholders',
      participants: 'CEO, CFO, COO, Board Members, Strategic Advisors',
      constraints: 'Limited time (2 hours), must reach consensus on major decisions, budget limitations',
      success_criteria: 'Clear decisions on strategic initiatives, approved budgets, defined action items with owners'
    },
    {
      name: 'Medical Emergency Response',
      description: 'Critical care team responding to complex medical emergency',
      context: 'Emergency department receiving multiple trauma patients requiring immediate coordinated care.',
      objectives: 'Stabilize patients, coordinate care teams, make rapid clinical decisions, optimize resource allocation',
      setting: 'Hospital emergency department with multiple trauma bays and specialized equipment',
      participants: 'Emergency Physicians, Trauma Surgeons, Nurses, Specialists, Technicians',
      constraints: 'Time-critical decisions, limited resources, multiple competing priorities',
      success_criteria: 'Patient stabilization, efficient care coordination, optimal outcomes, clear communication'
    },
    {
      name: 'Research Collaboration',
      description: 'Interdisciplinary research team working on breakthrough project',
      context: 'Scientists from different disciplines collaborating on innovative research with potential major impact.',
      objectives: 'Share expertise, develop hypotheses, design experiments, plan research methodology',
      setting: 'Research facility with access to specialized equipment and data',
      participants: 'Research Scientists, Graduate Students, Lab Technicians, Subject Matter Experts',
      constraints: 'Funding limitations, timeline pressures, technical challenges, publication deadlines',
      success_criteria: 'Clear research plan, defined methodologies, resource allocation, timeline agreement'
    },
    {
      name: 'Crisis Management',
      description: 'Emergency response team managing organizational crisis',
      context: 'Organization facing significant crisis requiring immediate coordinated response and strategic communication.',
      objectives: 'Assess situation, implement crisis response plan, coordinate communications, minimize impact',
      setting: 'Crisis command center with communication systems and decision-making tools',
      participants: 'Crisis Manager, Communications Lead, Legal Counsel, Operations Director, Key Stakeholders',
      constraints: 'Public scrutiny, limited information, time pressure, potential legal implications',
      success_criteria: 'Effective crisis response, clear communication, stakeholder alignment, reputation protection'
    }
  ];

  useEffect(() => {
    if (isOpen) {
      fetchUploadedFiles();
      fetchRandomScenario();
    }
  }, [isOpen]);

  const fetchUploadedFiles = async () => {
    if (!token) return;
    
    try {
      const response = await axios.get(`${API}/scenario/uploads`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (response.data) {
        setUploadedFiles(response.data);
      }
    } catch (error) {
      console.error('Failed to fetch uploaded files:', error);
    }
  };

  const fetchRandomScenario = async () => {
    try {
      const response = await axios.get(`${API}/simulation/random-scenario`);
      if (response.data) {
        // This could be used to show inspiration or random scenario suggestions
        console.log('Random scenario suggestion:', response.data);
      }
    } catch (error) {
      console.error('Failed to fetch random scenario:', error);
    }
  };

  const applyTemplate = (template) => {
    setNewScenario(template);
  };

  const createScenario = async () => {
    if (!newScenario.name || !newScenario.description || !token) {
      alert('Please fill in at least the name and description');
      return;
    }

    setLoading(true);
    try {
      const response = await axios.post(`${API}/simulation/set-scenario`, {
        scenario: newScenario.context || newScenario.description,
        scenario_name: newScenario.name,
        ...newScenario
      }, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      if (response.data?.success) {
        alert('Scenario created and set successfully!');
        if (onScenarioCreated) {
          onScenarioCreated(newScenario);
        }
        setNewScenario({
          name: '',
          description: '',
          context: '',
          objectives: '',
          setting: '',
          participants: '',
          constraints: '',
          success_criteria: ''
        });
        onClose();
      }
    } catch (error) {
      console.error('Failed to create scenario:', error);
      alert('Failed to create scenario. Please try again.');
    }
    setLoading(false);
  };

  const uploadScenarioFile = async () => {
    if (!selectedFile || !token) {
      alert('Please select a file to upload');
      return;
    }

    const formData = new FormData();
    formData.append('file', selectedFile);
    formData.append('description', `Scenario content from ${selectedFile.name}`);

    setLoading(true);
    setUploadProgress(0);

    try {
      const response = await axios.post(`${API}/scenario/upload-content`, formData, {
        headers: { 
          Authorization: `Bearer ${token}`,
          'Content-Type': 'multipart/form-data'
        },
        onUploadProgress: (progressEvent) => {
          const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          setUploadProgress(progress);
        }
      });
      
      if (response.data?.success) {
        alert('Scenario file uploaded successfully!');
        setSelectedFile(null);
        setUploadProgress(0);
        await fetchUploadedFiles();
      }
    } catch (error) {
      console.error('Failed to upload scenario file:', error);
      alert('Failed to upload file. Please try again.');
    }
    setLoading(false);
  };

  const downloadFile = async (fileId, filename) => {
    if (!token) return;

    try {
      const response = await axios.get(`${API}/scenario/uploads/${fileId}`, {
        headers: { Authorization: `Bearer ${token}` },
        responseType: 'blob'
      });
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', filename);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Failed to download file:', error);
      alert('Failed to download file.');
    }
  };

  if (!isOpen) return null;

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 bg-black/50 flex items-center justify-center z-[100] p-4"
      >
        <motion.div
          initial={{ scale: 0.9, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          exit={{ scale: 0.9, opacity: 0 }}
          className="bg-white rounded-lg w-full max-w-6xl max-h-[90vh] overflow-hidden"
        >
          {/* Header */}
          <div className="bg-gradient-to-r from-emerald-600 to-teal-600 text-white p-6">
            <div className="flex justify-between items-center">
              <div>
                <h2 className="text-2xl font-bold">🎭 Custom Scenario Creator</h2>
                <p className="text-white/80 mt-1">Design and create custom simulation scenarios</p>
              </div>
              <button
                onClick={onClose}
                className="text-white/70 hover:text-white text-2xl p-2 hover:bg-white/10 rounded-lg transition-colors"
              >
                ✕
              </button>
            </div>
          </div>

          {/* Tab Navigation */}
          <div className="bg-gray-50 border-b">
            <div className="flex">
              <button
                onClick={() => setActiveTab('create')}
                className={`px-6 py-3 font-medium ${
                  activeTab === 'create' 
                    ? 'text-emerald-600 border-b-2 border-emerald-600 bg-white' 
                    : 'text-gray-500 hover:text-gray-700'
                }`}
              >
                ✏️ Create Scenario
              </button>
              <button
                onClick={() => setActiveTab('templates')}
                className={`px-6 py-3 font-medium ${
                  activeTab === 'templates' 
                    ? 'text-emerald-600 border-b-2 border-emerald-600 bg-white' 
                    : 'text-gray-500 hover:text-gray-700'
                }`}
              >
                📋 Templates
              </button>
              <button
                onClick={() => setActiveTab('upload')}
                className={`px-6 py-3 font-medium ${
                  activeTab === 'upload' 
                    ? 'text-emerald-600 border-b-2 border-emerald-600 bg-white' 
                    : 'text-gray-500 hover:text-gray-700'
                }`}
              >
                📁 Upload Content
              </button>
            </div>
          </div>

          {/* Content */}
          <div className="p-6 overflow-y-auto max-h-[calc(90vh-180px)]">
            {activeTab === 'create' && (
              <div className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {/* Basic Information */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Scenario Name *</label>
                    <input
                      type="text"
                      value={newScenario.name}
                      onChange={(e) => setNewScenario({...newScenario, name: e.target.value})}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
                      placeholder="Enter scenario name..."
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Setting</label>
                    <input
                      type="text"
                      value={newScenario.setting}
                      onChange={(e) => setNewScenario({...newScenario, setting: e.target.value})}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
                      placeholder="Where does this scenario take place?"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Description *</label>
                  <textarea
                    value={newScenario.description}
                    onChange={(e) => setNewScenario({...newScenario, description: e.target.value})}
                    rows={3}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
                    placeholder="Brief description of the scenario..."
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Context & Background</label>
                  <textarea
                    value={newScenario.context}
                    onChange={(e) => setNewScenario({...newScenario, context: e.target.value})}
                    rows={4}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
                    placeholder="Detailed context and background information..."
                  />
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Objectives</label>
                    <textarea
                      value={newScenario.objectives}
                      onChange={(e) => setNewScenario({...newScenario, objectives: e.target.value})}
                      rows={3}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
                      placeholder="What should participants achieve?"
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Participants</label>
                    <textarea
                      value={newScenario.participants}
                      onChange={(e) => setNewScenario({...newScenario, participants: e.target.value})}
                      rows={3}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
                      placeholder="Who is involved in this scenario?"
                    />
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Constraints</label>
                    <textarea
                      value={newScenario.constraints}
                      onChange={(e) => setNewScenario({...newScenario, constraints: e.target.value})}
                      rows={3}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
                      placeholder="What limitations or challenges exist?"
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Success Criteria</label>
                    <textarea
                      value={newScenario.success_criteria}
                      onChange={(e) => setNewScenario({...newScenario, success_criteria: e.target.value})}
                      rows={3}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
                      placeholder="How will success be measured?"
                    />
                  </div>
                </div>

                <div className="flex justify-end space-x-3 pt-4 border-t">
                  <button
                    onClick={onClose}
                    className="px-6 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
                  >
                    Cancel
                  </button>
                  <button
                    onClick={createScenario}
                    disabled={loading}
                    className="px-6 py-2 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 transition-colors disabled:opacity-50"
                  >
                    {loading ? 'Creating...' : 'Create & Set Scenario'}
                  </button>
                </div>
              </div>
            )}

            {activeTab === 'templates' && (
              <div className="space-y-6">
                <div className="text-center mb-6">
                  <h3 className="text-xl font-semibold text-gray-800 mb-2">Scenario Templates</h3>
                  <p className="text-gray-600">Choose a template to get started quickly</p>
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {scenarioTemplates.map((template, index) => (
                    <motion.div
                      key={index}
                      className="border border-gray-200 rounded-lg p-6 hover:shadow-lg transition-shadow cursor-pointer"
                      whileHover={{ scale: 1.02 }}
                      onClick={() => {
                        applyTemplate(template);
                        setActiveTab('create');
                      }}
                    >
                      <h4 className="text-lg font-semibold text-gray-800 mb-2">{template.name}</h4>
                      <p className="text-gray-600 text-sm mb-4">{template.description}</p>
                      <div className="text-sm text-gray-500 space-y-1">
                        <div><strong>Setting:</strong> {template.setting.substring(0, 60)}...</div>
                        <div><strong>Participants:</strong> {template.participants}</div>
                      </div>
                      <div className="mt-4 flex justify-end">
                        <span className="px-3 py-1 bg-emerald-100 text-emerald-700 rounded-full text-sm">
                          Use Template
                        </span>
                      </div>
                    </motion.div>
                  ))}
                </div>
              </div>
            )}

            {activeTab === 'upload' && (
              <div className="space-y-6">
                <div className="text-center mb-6">
                  <h3 className="text-xl font-semibold text-gray-800 mb-2">Upload Scenario Content</h3>
                  <p className="text-gray-600">Upload documents, scripts, or other content to enhance your scenarios</p>
                </div>

                {/* File Upload */}
                <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center">
                  <div className="mb-4">
                    <svg className="mx-auto h-12 w-12 text-gray-400" stroke="currentColor" fill="none" viewBox="0 0 48 48">
                      <path d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" />
                    </svg>
                  </div>
                  <div className="mb-4">
                    <label htmlFor="file-upload" className="cursor-pointer">
                      <span className="text-sm font-medium text-gray-600">
                        Click to upload or drag and drop
                      </span>
                      <input
                        id="file-upload"
                        type="file"
                        className="sr-only"
                        accept=".txt,.pdf,.docx,.md"
                        onChange={(e) => setSelectedFile(e.target.files[0])}
                      />
                    </label>
                  </div>
                  <p className="text-xs text-gray-500">
                    Supports: TXT, PDF, DOCX, MD files up to 10MB
                  </p>
                </div>

                {selectedFile && (
                  <div className="bg-gray-50 rounded-lg p-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="font-medium text-gray-800">{selectedFile.name}</p>
                        <p className="text-sm text-gray-600">{(selectedFile.size / 1024 / 1024).toFixed(2)} MB</p>
                      </div>
                      <button
                        onClick={uploadScenarioFile}
                        disabled={loading}
                        className="px-4 py-2 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 transition-colors disabled:opacity-50"
                      >
                        {loading ? 'Uploading...' : 'Upload'}
                      </button>
                    </div>
                    {uploadProgress > 0 && (
                      <div className="mt-2">
                        <div className="bg-gray-200 rounded-full h-2">
                          <div 
                            className="bg-emerald-600 h-2 rounded-full transition-all duration-300"
                            style={{ width: `${uploadProgress}%` }}
                          ></div>
                        </div>
                        <p className="text-sm text-gray-600 mt-1">{uploadProgress}% uploaded</p>
                      </div>
                    )}
                  </div>
                )}

                {/* Uploaded Files */}
                {uploadedFiles.length > 0 && (
                  <div>
                    <h4 className="text-lg font-semibold text-gray-800 mb-4">Uploaded Files</h4>
                    <div className="space-y-3">
                      {uploadedFiles.map((file, index) => (
                        <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                          <div>
                            <p className="font-medium text-gray-800">{file.filename}</p>
                            <p className="text-sm text-gray-600">{file.description}</p>
                            <p className="text-xs text-gray-500">Uploaded: {new Date(file.uploaded_at).toLocaleDateString()}</p>
                          </div>
                          <button
                            onClick={() => downloadFile(file.id, file.filename)}
                            className="px-3 py-1 bg-gray-600 text-white rounded hover:bg-gray-700 transition-colors"
                          >
                            📥 Download
                          </button>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
};

export default ScenarioCreator;