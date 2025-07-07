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
  const [recordingField, setRecordingField] = useState(null); // Track which field is being recorded

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

  // Voice input functionality (reused from SimulationControl)
  const handleVoiceInput = async (fieldName) => {
    const token = localStorage.getItem('auth_token');
    if (!token) {
      alert('Please login to use voice input functionality.');
      return;
    }

    if (recordingField === fieldName) {
      // Stop recording immediately when clicked again
      console.log('🛑 User requested to stop recording');
      setRecordingField(null);
      if (window.currentMediaRecorder && window.currentMediaRecorder.state === 'recording') {
        window.currentMediaRecorder.stop();
      }
      return;
    }

    if (recordingField) {
      alert('Another field is currently being recorded. Please wait or stop the current recording.');
      return;
    }

    try {
      console.log(`🎤 Starting voice input for ${fieldName}...`);
      setRecordingField(fieldName);

      const stream = await navigator.mediaDevices.getUserMedia({ 
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true,
          sampleRate: 44100
        } 
      });

      console.log('🎵 Microphone access granted, audio stream obtained');

      const mediaRecorder = new MediaRecorder(stream, {
        mimeType: 'audio/webm;codecs=opus'
      });
      window.currentMediaRecorder = mediaRecorder;

      const audioChunks = [];

      mediaRecorder.ondataavailable = (event) => {
        console.log('🎵 Audio data chunk received:', event.data.size, 'bytes');
        if (event.data.size > 0) {
          audioChunks.push(event.data);
        }
      };

      mediaRecorder.onstop = async () => {
        console.log('🛑 MediaRecorder stopped, processing audio...');
        
        if (audioChunks.length === 0) {
          console.log('⚠️ No audio data recorded');
          alert('No audio was recorded. Please try again.');
          setRecordingField(null);
          return;
        }

        const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
        console.log(`📦 Audio blob created: ${audioBlob.size} bytes, type: ${audioBlob.type}`);

        const formData = new FormData();
        const fileName = `voice_input_${fieldName}_${Date.now()}.webm`;
        formData.append('file', audioBlob, fileName);

        try {
          console.log('🚀 Sending transcription request...');
          const response = await axios.post(`${API}/speech/transcribe-scenario`, formData, {
            headers: {
              'Content-Type': 'multipart/form-data',
              'Authorization': `Bearer ${token}`
            },
            timeout: 30000
          });

          console.log('✅ Transcription response received:', response);
          
          if (response.data && response.data.text) {
            console.log(`📝 Setting transcribed text for ${fieldName}:`, response.data.text);
            handleInputChange(fieldName, response.data.text);
            console.log('✅ Text successfully set in input field');
          } else {
            console.log('❌ No text in transcription response:', response.data);
            alert('No speech was detected in the recording. Please speak clearly and try again.');
          }
        } catch (error) {
          console.error('❌ Failed to transcribe audio:', error);
          
          if (error.response?.status === 401) {
            alert('Authentication failed. Please refresh the page and try again.');
          } else if (error.response?.status === 400) {
            const errorMsg = error.response.data?.detail || 'Invalid audio format';
            alert(`Invalid request: ${errorMsg}. Try a different browser or check microphone settings.`);
          } else if (error.code === 'ECONNABORTED') {
            alert('Request timeout. Please try with a shorter recording.');
          } else {
            alert(`Failed to transcribe audio: ${error.response?.data?.detail || error.message}. Please check the console for details.`);
          }
        }

        // Stop all tracks to release microphone
        stream.getTracks().forEach(track => {
          track.stop();
          console.log('🔇 Microphone track stopped');
        });
        setRecordingField(null);
      };

      mediaRecorder.onerror = (event) => {
        console.error('❌ MediaRecorder error:', event.error);
        alert('Recording error occurred. Please try again.');
        window.currentMediaRecorder = null;
        setRecordingField(null);
      };

      console.log('🎬 Starting MediaRecorder...');
      console.log('💡 Click the microphone button again to stop recording');
      mediaRecorder.start(1000);

      // Backup auto-stop after 60 seconds
      setTimeout(() => {
        if (mediaRecorder.state === 'recording') {
          console.log('⏰ Safety auto-stop after 60 seconds');
          mediaRecorder.stop();
        }
      }, 60000);

    } catch (error) {
      console.error('❌ Failed to start recording:', error);
      setRecordingField(null);
      window.currentMediaRecorder = null;
      
      if (error.name === 'NotAllowedError') {
        alert('Microphone access denied. Please allow microphone access and try again.');
      } else if (error.name === 'NotFoundError') {
        alert('No microphone found. Please connect a microphone and try again.');
      } else if (error.name === 'NotSupportedError') {
        alert('Voice recording is not supported in this browser. Please use Chrome, Firefox, or Safari.');
      } else {
        alert(`Failed to access microphone: ${error.message}. Please check your browser settings and try again.`);
      }
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!formData.name.trim() || !formData.goal.trim()) {
      alert('Please fill in at least the name and goal fields.');
      return;
    }
    if (recordingField) {
      alert('Please wait for voice recording to complete before creating the agent.');
      return;
    }
    onCreate(formData);
  };

  const handleClose = () => {
    if (!loading && !avatarGenerating && !recordingField) {
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
      setRecordingField(null);
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
        className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
        onClick={handleClose}
      >
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          exit={{ opacity: 0, scale: 0.95 }}
          className="bg-white rounded-xl shadow-2xl w-full h-[90vh] overflow-hidden flex flex-col"
          onClick={(e) => e.stopPropagation()}
        >
          {/* Header */}
          <div className="bg-gradient-to-r from-purple-600 to-blue-600 text-white p-6">
            <div className="flex justify-between items-center">
              <div>
                <h2 className="text-2xl font-bold">🤖 Create New Agent</h2>
                <p className="text-white/80 mt-1">Design your agent's personality, expertise, and appearance</p>
              </div>
              <button
                onClick={handleClose}
                disabled={loading || avatarGenerating || recordingField}
                className="text-white/70 hover:text-white text-2xl p-2 hover:bg-white/10 rounded-lg transition-colors disabled:opacity-50"
              >
                ✕
              </button>
            </div>
          </div>

          {/* Content - Fixed height to fit screen */}
          <form onSubmit={handleSubmit} className="flex-1 p-6 overflow-hidden">
            <div className="grid grid-cols-12 gap-4 h-full">
              
              {/* Left Column - Basic Info (15%) */}
              <div className="col-span-2 space-y-3">
                <div className="bg-gray-50 rounded-lg p-3 h-full">
                  <h3 className="text-sm font-semibold text-gray-800 mb-3 border-b border-gray-200 pb-2">Basic Info</h3>
                  
                  <div className="space-y-3">
                    <div>
                      <label className="block text-xs font-medium text-gray-700 mb-1">
                        Agent Name *
                      </label>
                      <input
                        type="text"
                        value={formData.name}
                        onChange={(e) => handleInputChange('name', e.target.value)}
                        placeholder="Dr. Sarah Chen"
                        disabled={loading}
                        className="w-full px-2 py-1 text-sm border border-gray-300 rounded focus:ring-1 focus:ring-purple-500 disabled:opacity-50"
                        required
                      />
                    </div>

                    <div>
                      <label className="block text-xs font-medium text-gray-700 mb-1">
                        Archetype
                      </label>
                      <select
                        value={formData.archetype}
                        onChange={(e) => handleArchetypeChange(e.target.value)}
                        disabled={loading}
                        className="w-full px-2 py-1 text-sm border border-gray-300 rounded focus:ring-1 focus:ring-purple-500 disabled:opacity-50"
                      >
                        {Object.entries(AGENT_ARCHETYPES).map(([key, archetype]) => (
                          <option key={key} value={key}>
                            {archetype.name}
                          </option>
                        ))}
                      </select>
                    </div>

                    <div>
                      <label className="block text-xs font-medium text-gray-700 mb-1">
                        Primary Goal *
                      </label>
                      <div className="relative">
                        <textarea
                          value={formData.goal}
                          onChange={(e) => handleInputChange('goal', e.target.value)}
                          placeholder="What is this agent trying to achieve?"
                          disabled={loading || recordingField === 'goal'}
                          className="w-full px-2 py-1 pr-8 text-sm border border-gray-300 rounded focus:ring-1 focus:ring-purple-500 disabled:opacity-50 resize-none"
                          rows="3"
                          required
                        />
                        <button
                          type="button"
                          onClick={() => handleVoiceInput('goal')}
                          disabled={loading || recordingField}
                          className={`absolute right-1 top-1 p-1 rounded transition-colors disabled:opacity-50 ${
                            recordingField === 'goal' 
                              ? 'bg-red-500/20 text-red-500 animate-pulse' 
                              : 'text-gray-400 hover:text-purple-600 hover:bg-purple-50'
                          }`}
                          title={recordingField === 'goal' ? 'Recording... Click to stop' : 'Click to record with voice'}
                        >
                          <svg width="12" height="12" viewBox="0 0 24 24" fill="currentColor">
                            <path d="M12 1c-1.6 0-3 1.4-3 3v8c0 1.6 1.4 3 3 3s3-1.4 3-3V4c0-1.6-1.4-3-3-3zm0 18c-3.3 0-6-2.7-6-6h-2c0 4.4 3.6 8 8 8s8-3.6 8-8h-2c0 3.3-2.7 6-6 6zm1-6V4c0-.6-.4-1-1-1s-1 .4-1 1v9c0 .6.4 1 1 1s1-.4 1-1z"/>
                            <rect x="10" y="20" width="4" height="2" rx="1"/>
                          </svg>
                        </button>
                      </div>
                    </div>

                    {/* Avatar Generation Section */}
                    <div className="border-t border-gray-200 pt-3 mt-3">
                      <h4 className="text-xs font-semibold text-gray-800 mb-2">Avatar Generation</h4>
                      
                      <div className="space-y-2">
                        <div>
                          <label className="block text-xs font-medium text-gray-700 mb-1">
                            Avatar Description
                          </label>
                          <textarea
                            value={formData.avatar_prompt}
                            onChange={(e) => handleInputChange('avatar_prompt', e.target.value)}
                            placeholder="professional doctor, lab coat, friendly"
                            disabled={loading || avatarGenerating}
                            className="w-full px-2 py-1 text-xs border border-gray-300 rounded focus:ring-1 focus:ring-purple-500 disabled:opacity-50 resize-none"
                            rows="2"
                          />
                        </div>

                        <button
                          type="button"
                          onClick={generateAvatar}
                          disabled={loading || avatarGenerating || !formData.avatar_prompt.trim()}
                          className="w-full px-2 py-1 text-xs bg-purple-600 hover:bg-purple-700 text-white rounded transition-colors disabled:opacity-50 flex items-center justify-center space-x-1"
                        >
                          {avatarGenerating ? (
                            <>
                              <div className="animate-spin rounded-full h-2 w-2 border-b border-white"></div>
                              <span>Generating...</span>
                            </>
                          ) : (
                            <>
                              <span>🎨</span>
                              <span>Generate Avatar</span>
                            </>
                          )}
                        </button>

                        {avatarError && (
                          <p className="text-red-600 text-xs">{avatarError}</p>
                        )}

                        {/* Avatar Preview */}
                        <div className="bg-white border border-gray-200 rounded p-1 flex items-center justify-center h-16">
                          {formData.avatar_url ? (
                            <img
                              src={formData.avatar_url}
                              alt="Generated Avatar"
                              className="w-12 h-12 object-cover rounded"
                              onError={(e) => {
                                e.target.style.display = 'none';
                                setAvatarError('Failed to load avatar');
                              }}
                            />
                          ) : (
                            <div className="text-center text-gray-400">
                              <div className="w-12 h-12 bg-gray-100 rounded border border-dashed border-gray-300 flex items-center justify-center">
                                <span className="text-lg">👤</span>
                              </div>
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Center Column - Professional Details (65%) - DOMINANT SECTION */}
              <div className="col-span-7 space-y-3">
                <div className="bg-gradient-to-br from-blue-50 to-purple-50 rounded-lg p-4 h-full border-2 border-blue-200">
                  <h3 className="text-lg font-bold text-purple-800 mb-4 border-b-2 border-purple-300 pb-2 text-center">
                    🎓 Professional Details - The Core of Your Agent
                  </h3>
                  
                  <div className="space-y-4 h-full">
                    
                    <div>
                      <label className="block text-sm font-semibold text-gray-800 mb-2 flex items-center space-x-2">
                        <span>💼 Areas of Expertise</span>
                      </label>
                      <div className="relative">
                        <textarea
                          value={formData.expertise}
                          onChange={(e) => handleInputChange('expertise', e.target.value)}
                          placeholder="e.g., Oncology, Drug Development, Clinical Trials, Biomarker Research, Precision Medicine..."
                          disabled={loading || recordingField === 'expertise'}
                          className="w-full px-3 py-2 pr-10 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 disabled:opacity-50 resize-none"
                          rows="4"
                        />
                        <button
                          type="button"
                          onClick={() => handleVoiceInput('expertise')}
                          disabled={loading || recordingField}
                          className={`absolute right-2 top-2 p-1 rounded transition-colors disabled:opacity-50 ${
                            recordingField === 'expertise' 
                              ? 'bg-red-500/20 text-red-500 animate-pulse' 
                              : 'text-gray-400 hover:text-purple-600 hover:bg-purple-50'
                          }`}
                          title={recordingField === 'expertise' ? 'Recording... Click to stop' : 'Click to record with voice'}
                        >
                          <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor">
                            <path d="M12 1c-1.6 0-3 1.4-3 3v8c0 1.6 1.4 3 3 3s3-1.4 3-3V4c0-1.6-1.4-3-3-3zm0 18c-3.3 0-6-2.7-6-6h-2c0 4.4 3.6 8 8 8s8-3.6 8-8h-2c0 3.3-2.7 6-6 6zm1-6V4c0-.6-.4-1-1-1s-1 .4-1 1v9c0 .6.4 1 1 1s1-.4 1-1z"/>
                            <rect x="10" y="20" width="4" height="2" rx="1"/>
                          </svg>
                        </button>
                      </div>
                    </div>

                    <div>
                      <label className="block text-sm font-semibold text-gray-800 mb-2 flex items-center space-x-2">
                        <span>📚 Professional Background</span>
                      </label>
                      <div className="relative">
                        <textarea
                          value={formData.background}
                          onChange={(e) => handleInputChange('background', e.target.value)}
                          placeholder="e.g., 15 years experience in pharmaceutical research, former head of oncology at major hospital, published 50+ research papers..."
                          disabled={loading || recordingField === 'background'}
                          className="w-full px-3 py-2 pr-10 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 disabled:opacity-50 resize-none"
                          rows="6"
                        />
                        <button
                          type="button"
                          onClick={() => handleVoiceInput('background')}
                          disabled={loading || recordingField}
                          className={`absolute right-2 top-2 p-1 rounded transition-colors disabled:opacity-50 ${
                            recordingField === 'background' 
                              ? 'bg-red-500/20 text-red-500 animate-pulse' 
                              : 'text-gray-400 hover:text-purple-600 hover:bg-purple-50'
                          }`}
                          title={recordingField === 'background' ? 'Recording... Click to stop' : 'Click to record with voice'}
                        >
                          <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor">
                            <path d="M12 1c-1.6 0-3 1.4-3 3v8c0 1.6 1.4 3 3 3s3-1.4 3-3V4c0-1.6-1.4-3-3-3zm0 18c-3.3 0-6-2.7-6-6h-2c0 4.4 3.6 8 8 8s8-3.6 8-8h-2c0 3.3-2.7 6-6 6zm1-6V4c0-.6-.4-1-1-1s-1 .4-1 1v9c0 .6.4 1 1 1s1-.4 1-1z"/>
                            <rect x="10" y="20" width="4" height="2" rx="1"/>
                          </svg>
                        </button>
                      </div>
                    </div>

                  </div>
                </div>
              </div>

              {/* Right Column - Personality Traits (15%) */}
              <div className="col-span-3 space-y-3">
                {/* Personality Traits with Sliders */}
                <div className="bg-gray-50 rounded-lg p-3 h-full">
                  <h3 className="text-sm font-semibold text-gray-800 mb-3 border-b border-gray-200 pb-2">Personality Traits</h3>
                  
                  <div className="space-y-4">
                    {Object.entries(formData.personality).map(([trait, value]) => (
                      <div key={trait} className="space-y-2">
                        <div className="flex justify-between items-center">
                          <label className="text-gray-700 text-sm font-medium capitalize">
                            {trait}
                          </label>
                          <span className="text-gray-600 text-sm font-semibold bg-purple-100 px-2 py-1 rounded">
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
                          className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer disabled:opacity-50 slider-custom"
                          style={{
                            background: `linear-gradient(to right, #8b5cf6 0%, #8b5cf6 ${(value-1)*11.11}%, #e5e7eb ${(value-1)*11.11}%, #e5e7eb 100%)`
                          }}
                        />
                        <div className="flex justify-between text-xs text-gray-400 px-1">
                          <span>Low</span>
                          <span>High</span>
                        </div>
                      </div>
                    ))}
                  </div>

                  {/* Action Buttons */}
                  <div className="flex flex-col space-y-3 pt-4 border-t border-gray-200 mt-4">
                    <button
                      type="submit"
                      disabled={loading || avatarGenerating || recordingField || !formData.name.trim() || !formData.goal.trim()}
                      className="w-full px-3 py-3 bg-green-600 hover:bg-green-700 text-white rounded-lg transition-colors disabled:opacity-50 flex items-center justify-center space-x-2 text-sm font-semibold"
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
                    
                    <button
                      type="button"
                      onClick={handleClose}
                      disabled={loading || avatarGenerating || recordingField}
                      className="w-full px-3 py-2 bg-gray-600 hover:bg-gray-700 text-white rounded-lg transition-colors disabled:opacity-50 text-sm"
                    >
                      Cancel
                    </button>
                  </div>
                </div>
              </div>
            </div>
            
            {/* Recording Status */}
            {recordingField && (
              <div className="fixed bottom-4 right-4 bg-red-500 text-white px-4 py-2 rounded-lg shadow-lg animate-pulse">
                🎤 Recording {recordingField}... Click microphone to stop
              </div>
            )}
          </form>

          <style jsx>{`
            .slider-custom::-webkit-slider-thumb {
              appearance: none;
              height: 20px;
              width: 20px;
              border-radius: 50%;
              background: #8b5cf6;
              cursor: pointer;
              border: 2px solid #ffffff;
              box-shadow: 0 2px 6px rgba(0,0,0,0.3);
            }
            .slider-custom::-moz-range-thumb {
              height: 20px;
              width: 20px;
              border-radius: 50%;
              background: #8b5cf6;
              cursor: pointer;
              border: 2px solid #ffffff;
              box-shadow: 0 2px 6px rgba(0,0,0,0.3);
              border: none;
            }
            .slider-custom::-webkit-slider-track {
              height: 8px;
              border-radius: 4px;
              background: transparent;
            }
            .slider-custom::-moz-range-track {
              height: 8px;
              border-radius: 4px;
              background: transparent;
              border: none;
            }
          `}</style>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
};

export default AgentCreateModal;