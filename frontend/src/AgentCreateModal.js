import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

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
    personality: {
      extroversion: 5,
      optimism: 5,
      curiosity: 5,
      cooperativeness: 5,
      energy: 5
    }
  });

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

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!formData.name.trim() || !formData.goal.trim()) {
      alert('Please fill in at least the name and goal fields.');
      return;
    }
    onCreate(formData);
  };

  const handleClose = () => {
    if (!loading) {
      setFormData({
        name: '',
        archetype: 'scientist',
        goal: '',
        expertise: '',
        background: '',
        avatar_prompt: '',
        personality: {
          extroversion: 5,
          optimism: 5,
          curiosity: 5,
          cooperativeness: 5,
          energy: 5
        }
      });
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
          className="bg-gradient-to-br from-gray-900 to-black rounded-xl p-6 w-full max-w-2xl max-h-[90vh] overflow-y-auto"
          onClick={(e) => e.stopPropagation()}
        >
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-2xl font-bold text-white">🤖 Create New Agent</h2>
            <button
              onClick={handleClose}
              disabled={loading}
              className="text-white/60 hover:text-white transition-colors text-2xl disabled:opacity-50"
            >
              ✕
            </button>
          </div>

          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Basic Information */}
            <div className="space-y-4">
              <h3 className="text-lg font-semibold text-white">Basic Information</h3>
              
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
                  rows="2"
                  required
                />
              </div>
            </div>

            {/* Professional Details */}
            <div className="space-y-4">
              <h3 className="text-lg font-semibold text-white">Professional Details</h3>
              
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
                  rows="3"
                />
              </div>

              <div>
                <label className="block text-white/80 text-sm font-medium mb-2">
                  Avatar Description
                </label>
                <input
                  type="text"
                  value={formData.avatar_prompt}
                  onChange={(e) => handleInputChange('avatar_prompt', e.target.value)}
                  placeholder="e.g., professional medical doctor, lab coat, friendly smile"
                  disabled={loading}
                  className="w-full px-3 py-2 bg-white/10 border border-white/20 rounded-lg text-white placeholder-white/50 focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
                />
              </div>
            </div>

            {/* Personality Traits */}
            <div className="space-y-4">
              <h3 className="text-lg font-semibold text-white">Personality Traits</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {Object.entries(formData.personality).map(([trait, value]) => (
                  <div key={trait}>
                    <label className="block text-white/80 text-sm font-medium mb-2 capitalize">
                      {trait}: {value}/10
                    </label>
                    <input
                      type="range"
                      min="1"
                      max="10"
                      value={value}
                      onChange={(e) => handlePersonalityChange(trait, e.target.value)}
                      disabled={loading}
                      className="w-full h-2 bg-white/20 rounded-lg appearance-none cursor-pointer disabled:opacity-50 slider"
                    />
                  </div>
                ))}
              </div>
            </div>

            {/* Actions */}
            <div className="flex justify-end space-x-3 pt-4 border-t border-white/20">
              <button
                type="button"
                onClick={handleClose}
                disabled={loading}
                className="px-4 py-2 bg-gray-600 hover:bg-gray-700 text-white rounded-lg transition-colors disabled:opacity-50"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={loading || !formData.name.trim() || !formData.goal.trim()}
                className="px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg transition-colors disabled:opacity-50 flex items-center space-x-2"
              >
                {loading ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                    <span>Creating...</span>
                  </>
                ) : (
                  <>
                    <span>➕</span>
                    <span>Create Agent</span>
                  </>
                )}
              </button>
            </div>
          </form>

          <style jsx>{`
            .slider::-webkit-slider-thumb {
              appearance: none;
              height: 20px;
              width: 20px;
              border-radius: 50%;
              background: #10b981;
              cursor: pointer;
              border: 2px solid #ffffff;
            }
            .slider::-moz-range-thumb {
              height: 20px;
              width: 20px;
              border-radius: 50%;
              background: #10b981;
              cursor: pointer;
              border: 2px solid #ffffff;
            }
          `}</style>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
};

export default AgentCreateModal;