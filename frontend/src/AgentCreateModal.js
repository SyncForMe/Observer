import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import axios from 'axios';

const API = process.env.REACT_APP_BACKEND_URL ? `${process.env.REACT_APP_BACKEND_URL}/api` : 'http://localhost:8001/api';

const AGENT_ARCHETYPES = {
  "scientist": {
    "name": "The Scientist",
    "description": "Logical, curious, methodical",
    "default_traits": {"extroversion": 4, "optimism": 6, "curiosity": 9, "cooperativeness": 7, "energy": 6}
  },
  "artist": {
    "name": "The Artist", 
    "description": "Creative, emotional, expressive",
    "default_traits": {"extroversion": 6, "optimism": 7, "curiosity": 8, "cooperativeness": 6, "energy": 7}
  },
  "leader": {
    "name": "The Leader",
    "description": "Confident, decisive, social", 
    "default_traits": {"extroversion": 9, "optimism": 8, "curiosity": 6, "cooperativeness": 8, "energy": 8}
  },
  "skeptic": {
    "name": "The Skeptic",
    "description": "Questioning, cautious, analytical",
    "default_traits": {"extroversion": 4, "optimism": 3, "curiosity": 7, "cooperativeness": 5, "energy": 5}
  },
  "optimist": {
    "name": "The Optimist", 
    "description": "Positive, encouraging, hopeful",
    "default_traits": {"extroversion": 8, "optimism": 10, "curiosity": 6, "cooperativeness": 9, "energy": 8}
  },
  "introvert": {
    "name": "The Introvert",
    "description": "Quiet, thoughtful, observant",
    "default_traits": {"extroversion": 2, "optimism": 5, "curiosity": 7, "cooperativeness": 6, "energy": 4}
  },
  "adventurer": {
    "name": "The Adventurer",
    "description": "Bold, spontaneous, energetic", 
    "default_traits": {"extroversion": 8, "optimism": 8, "curiosity": 9, "cooperativeness": 6, "energy": 9}
  },
  "mediator": {
    "name": "The Mediator",
    "description": "Peaceful, diplomatic, empathetic",
    "default_traits": {"extroversion": 6, "optimism": 7, "curiosity": 6, "cooperativeness": 10, "energy": 6}
  },
  "researcher": {
    "name": "The Researcher",
    "description": "Investigative, detail-oriented, systematic",
    "default_traits": {"extroversion": 3, "optimism": 6, "curiosity": 9, "cooperativeness": 7, "energy": 5}
  }
};

const AgentCreateModal = ({ isOpen, onClose, onCreate, loading }) => {
  const [formData, setFormData] = useState({
    name: '',
    archetype: 'scientist',
    goal: '',
    expertise: '',
    background: '',
    avatar_prompt: '',
    avatar_url: '',
    personality: {
      extroversion: 5,
      optimism: 5,
      curiosity: 5,
      cooperativeness: 5,
      energy: 5
    }
  });

  const [avatarGenerating, setAvatarGenerating] = useState(false);
  const [avatarError, setAvatarError] = useState('');

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

  const handleArchetypeChange = (archetype) => {
    const defaultTraits = AGENT_ARCHETYPES[archetype]?.default_traits || {};
    setFormData(prev => ({
      ...prev,
      archetype,
      personality: {
        extroversion: defaultTraits.extroversion || 5,
        optimism: defaultTraits.optimism || 5,
        curiosity: defaultTraits.curiosity || 5,
        cooperativeness: defaultTraits.cooperativeness || 5,
        energy: defaultTraits.energy || 5
      }
    }));
  };

  const generateAvatar = async () => {
    if (!formData.avatar_prompt.trim()) {
      setAvatarError('Please enter an avatar description first');
      return;
    }

    setAvatarGenerating(true);
    setAvatarError('');
    
    try {
      const token = localStorage.getItem('token');
      const response = await axios.post(`${API}/avatars/generate`, {
        prompt: formData.avatar_prompt
      }, {
        headers: { Authorization: `Bearer ${token}` }
      });

      if (response.data.success && response.data.image_url) {
        setFormData(prev => ({
          ...prev,
          avatar_url: response.data.image_url
        }));
      } else {
        setAvatarError(response.data.error || 'Failed to generate avatar');
      }
    } catch (error) {
      console.error('Avatar generation failed:', error);
      setAvatarError(error.response?.data?.detail || 'Failed to generate avatar. Please try again.');
    }
    
    setAvatarGenerating(false);
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!formData.name.trim() || !formData.goal.trim()) {
      alert('Please fill in at least the name and goal fields.');
      return;
    }
    onCreate(formData);
  };

  const handleClose = () => {
    if (!loading && !avatarGenerating) {
      setFormData({
        name: '',
        archetype: 'scientist',
        goal: '',
        expertise: '',
        background: '',
        avatar_prompt: '',
        avatar_url: '',
        personality: {
          extroversion: 5,
          optimism: 5,
          curiosity: 5,
          cooperativeness: 5,
          energy: 5
        }
      });
      setAvatarError('');
      onClose();
    }
  };

  if (!isOpen) return null;

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4"
        onClick={handleClose}
      >
        <motion.div
          initial={{ scale: 0.9, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          exit={{ scale: 0.9, opacity: 0 }}
          className="bg-gradient-to-br from-gray-900 to-black rounded-xl p-6 w-full max-w-7xl h-[90vh] overflow-y-auto"
          onClick={(e) => e.stopPropagation()}
        >
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-3xl font-bold text-white">🤖 Create New Agent</h2>
            <button
              onClick={handleClose}
              disabled={loading || avatarGenerating}
              className="text-white/60 hover:text-white transition-colors text-2xl disabled:opacity-50"
            >
              ✕
            </button>
          </div>

          <form onSubmit={handleSubmit} className="h-full">
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 h-full">
              
              {/* Left Column - Basic Info & Professional Details */}
              <div className="space-y-6">
                <div className="space-y-4">
                  <h3 className="text-xl font-semibold text-white border-b border-white/20 pb-2">Basic Information</h3>
                  
                  <div>
                    <label className="block text-white/80 text-sm font-medium mb-2">
                      Agent Name *
                    </label>
                    <input
                      type="text"
                      value={formData.name}
                      onChange={(e) => handleInputChange('name', e.target.value)}
                      placeholder="e.g., Dr. Sarah Chen"
                      disabled={loading}
                      className="w-full px-3 py-2 bg-white/10 border border-white/20 rounded-lg text-white placeholder-white/50 focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
                      required
                    />
                  </div>

                  <div>
                    <label className="block text-white/80 text-sm font-medium mb-2">
                      Archetype
                    </label>
                    <select
                      value={formData.archetype}
                      onChange={(e) => handleArchetypeChange(e.target.value)}
                      disabled={loading}
                      className="w-full px-3 py-2 bg-white/10 border border-white/20 rounded-lg text-white focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
                    >
                      {Object.entries(AGENT_ARCHETYPES).map(([key, archetype]) => (
                        <option key={key} value={key} className="bg-gray-800">
                          {archetype.name} - {archetype.description}
                        </option>
                      ))}
                    </select>
                  </div>

                  <div>
                    <label className="block text-white/80 text-sm font-medium mb-2">
                      Primary Goal *
                    </label>
                    <textarea
                      value={formData.goal}
                      onChange={(e) => handleInputChange('goal', e.target.value)}
                      placeholder="e.g., To advance medical research through innovative treatments"
                      disabled={loading}
                      className="w-full px-3 py-2 bg-white/10 border border-white/20 rounded-lg text-white placeholder-white/50 focus:ring-2 focus:ring-blue-500 disabled:opacity-50 resize-none"
                      rows="3"
                      required
                    />
                  </div>
                </div>

                <div className="space-y-4">
                  <h3 className="text-xl font-semibold text-white border-b border-white/20 pb-2">Professional Details</h3>
                  
                  <div>
                    <label className="block text-white/80 text-sm font-medium mb-2">
                      Expertise
                    </label>
                    <input
                      type="text"
                      value={formData.expertise}
                      onChange={(e) => handleInputChange('expertise', e.target.value)}
                      placeholder="e.g., Oncology, Drug Development, Clinical Trials"
                      disabled={loading}
                      className="w-full px-3 py-2 bg-white/10 border border-white/20 rounded-lg text-white placeholder-white/50 focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
                    />
                  </div>

                  <div>
                    <label className="block text-white/80 text-sm font-medium mb-2">
                      Background
                    </label>
                    <textarea
                      value={formData.background}
                      onChange={(e) => handleInputChange('background', e.target.value)}
                      placeholder="e.g., 15 years experience in pharmaceutical research, former head of oncology at major hospital"
                      disabled={loading}
                      className="w-full px-3 py-2 bg-white/10 border border-white/20 rounded-lg text-white placeholder-white/50 focus:ring-2 focus:ring-blue-500 disabled:opacity-50 resize-none"
                      rows="4"
                    />
                  </div>
                </div>
              </div>

              {/* Middle Column - Avatar Generation */}
              <div className="space-y-6">
                <div className="space-y-4">
                  <h3 className="text-xl font-semibold text-white border-b border-white/20 pb-2">Avatar Generation</h3>
                  
                  <div>
                    <label className="block text-white/80 text-sm font-medium mb-2">
                      Avatar Description
                    </label>
                    <textarea
                      value={formData.avatar_prompt}
                      onChange={(e) => handleInputChange('avatar_prompt', e.target.value)}
                      placeholder="e.g., professional medical doctor, lab coat, friendly smile, middle-aged Asian woman"
                      disabled={loading || avatarGenerating}
                      className="w-full px-3 py-2 bg-white/10 border border-white/20 rounded-lg text-white placeholder-white/50 focus:ring-2 focus:ring-blue-500 disabled:opacity-50 resize-none"
                      rows="3"
                    />
                  </div>

                  <button
                    type="button"
                    onClick={generateAvatar}
                    disabled={loading || avatarGenerating || !formData.avatar_prompt.trim()}
                    className="w-full px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg transition-colors disabled:opacity-50 flex items-center justify-center space-x-2"
                  >
                    {avatarGenerating ? (
                      <>
                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                        <span>Generating Avatar...</span>
                      </>
                    ) : (
                      <>
                        <span>🎨</span>
                        <span>Generate Avatar</span>
                      </>
                    )}
                  </button>

                  {avatarError && (
                    <p className="text-red-400 text-sm">{avatarError}</p>
                  )}

                  {/* Avatar Preview */}
                  <div className="bg-white/5 rounded-lg p-4 min-h-[300px] flex items-center justify-center">
                    {formData.avatar_url ? (
                      <div className="text-center">
                        <img
                          src={formData.avatar_url}
                          alt="Generated Avatar"
                          className="w-48 h-48 object-cover rounded-lg border-2 border-white/20 mx-auto mb-2"
                          onError={(e) => {
                            e.target.style.display = 'none';
                            setAvatarError('Failed to load generated avatar');
                          }}
                        />
                        <p className="text-white/60 text-sm">Avatar Preview</p>
                      </div>
                    ) : (
                      <div className="text-center text-white/40">
                        <div className="w-48 h-48 bg-white/10 rounded-lg border-2 border-dashed border-white/20 flex items-center justify-center mx-auto mb-2">
                          <span className="text-4xl">👤</span>
                        </div>
                        <p className="text-sm">Avatar will appear here after generation</p>
                      </div>
                    )}
                  </div>
                </div>
              </div>

              {/* Right Column - Personality Traits */}
              <div className="space-y-6">
                <div className="space-y-4">
                  <h3 className="text-xl font-semibold text-white border-b border-white/20 pb-2">Personality Traits</h3>
                  <p className="text-white/60 text-sm">Adjust the sliders to customize your agent's personality</p>
                  
                  <div className="space-y-6">
                    {Object.entries(formData.personality).map(([trait, value]) => (
                      <div key={trait} className="space-y-2">
                        <div className="flex justify-between items-center">
                          <label className="text-white/80 text-sm font-medium capitalize">
                            {trait}
                          </label>
                          <span className="text-white text-sm font-semibold bg-white/10 px-2 py-1 rounded">
                            {value}/10
                          </span>
                        </div>
                        <input
                          type="range"
                          min="1"
                          max="10"
                          value={value}
                          onChange={(e) => handlePersonalityChange(trait, e.target.value)}
                          disabled={loading}
                          className="w-full h-3 bg-white/20 rounded-lg appearance-none cursor-pointer disabled:opacity-50 slider"
                        />
                        <div className="flex justify-between text-xs text-white/40">
                          <span>Low</span>
                          <span>High</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Actions at bottom of right column */}
                <div className="flex flex-col space-y-3 pt-4 border-t border-white/20">
                  <button
                    type="submit"
                    disabled={loading || avatarGenerating || !formData.name.trim() || !formData.goal.trim()}
                    className="w-full px-4 py-3 bg-green-600 hover:bg-green-700 text-white rounded-lg transition-colors disabled:opacity-50 flex items-center justify-center space-x-2"
                  >
                    {loading ? (
                      <>
                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                        <span>Creating Agent...</span>
                      </>
                    ) : (
                      <>
                        <span>➕</span>
                        <span>Create Agent</span>
                      </>
                    )}
                  </button>
                  
                  <button
                    type="button"
                    onClick={handleClose}
                    disabled={loading || avatarGenerating}
                    className="w-full px-4 py-2 bg-gray-600 hover:bg-gray-700 text-white rounded-lg transition-colors disabled:opacity-50"
                  >
                    Cancel
                  </button>
                </div>
              </div>
            </div>
          </form>

          <style jsx>{`
            .slider::-webkit-slider-thumb {
              appearance: none;
              height: 24px;
              width: 24px;
              border-radius: 50%;
              background: #10b981;
              cursor: pointer;
              border: 3px solid #ffffff;
              box-shadow: 0 2px 6px rgba(0,0,0,0.3);
            }
            .slider::-moz-range-thumb {
              height: 24px;
              width: 24px;
              border-radius: 50%;
              background: #10b981;
              cursor: pointer;
              border: 3px solid #ffffff;
              box-shadow: 0 2px 6px rgba(0,0,0,0.3);
            }
            .slider::-webkit-slider-track {
              height: 12px;
              border-radius: 6px;
              background: rgba(255,255,255,0.2);
            }
            .slider::-moz-range-track {
              height: 12px;
              border-radius: 6px;
              background: rgba(255,255,255,0.2);
            }
          `}</style>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
};

export default AgentCreateModal;