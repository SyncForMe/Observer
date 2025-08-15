import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useAuth } from './AuthContext';

const SetupFlow = ({ onComplete, onCancel, existingAgents = [], onAddAgent }) => {
  const { token } = useAuth(); // Get token from auth context
  const [currentStep, setCurrentStep] = useState('category'); // category, scenario, agents, review
  const [selectedCategory, setSelectedCategory] = useState(null);
  const [selectedTrack, setSelectedTrack] = useState(null);
  const [scenario, setScenario] = useState('');
  const [scenarioInput, setScenarioInput] = useState('');
  const [isListening, setIsListening] = useState(false);
  const [agentCreationQueue, setAgentCreationQueue] = useState([]);
  const [agentInput, setAgentInput] = useState('');
  const [showTooltip, setShowTooltip] = useState(null);

  const recognition = useRef(null);

  // Create speech recognition instance
  const createSpeechRecognition = () => {
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      const newRecognition = new SpeechRecognition();
      newRecognition.continuous = true;
      newRecognition.interimResults = true;
      newRecognition.lang = 'en-US';

      newRecognition.onresult = (event) => {
        let finalTranscript = '';
        let interimTranscript = '';
        
        for (let i = event.resultIndex; i < event.results.length; i++) {
          const transcript = event.results[i][0].transcript;
          if (event.results[i].isFinal) {
            finalTranscript += transcript;
          } else {
            interimTranscript += transcript;
          }
        }
        
        console.log('🎤 Final transcript:', finalTranscript);
        console.log('🎤 Interim transcript:', interimTranscript);
        
        // Add final transcript to the input field
        if (finalTranscript) {
          if (currentStep === 'scenario') {
            setScenarioInput(prev => (prev + ' ' + finalTranscript).trim());
          } else if (currentStep === 'agents') {
            setAgentInput(prev => (prev + ' ' + finalTranscript).trim());
          }
          console.log('✅ Text added to input field');
        }
      };

      newRecognition.onerror = (event) => {
        console.error('Voice recognition error:', event.error);
        setIsListening(false);
      };

      newRecognition.onend = () => {
        console.log('🎤 Recognition ended');
        setIsListening(false);
      };

      return newRecognition;
    }
    return null;
  };

  // Voice recognition setup
  useEffect(() => {
    recognition.current = createSpeechRecognition();
  }, [currentStep]);

  const startVoiceRecognition = () => {
    if (!isListening) {
      // Create fresh recognition instance every time
      recognition.current = createSpeechRecognition();
      
      if (recognition.current) {
        setIsListening(true);
        try {
          recognition.current.start();
          console.log('🎤 Voice recognition started');
        } catch (error) {
          console.error('Error starting voice recognition:', error);
          setIsListening(false);
        }
      }
    }
  };

  const stopVoiceRecognition = () => {
    if (recognition.current && isListening) {
      setIsListening(false);
      recognition.current.stop();
      recognition.current = null; // Clear the reference
      console.log('🎤 Voice recognition stopped');
    }
  };

  const categories = {
    business: {
      title: 'Business & Professional',
      icon: '🏢',
      description: 'For business owners, entrepreneurs, and professionals',
      color: 'from-blue-500 to-indigo-600',
      tracks: {
        fast: {
          name: 'Fast Track',
          description: 'Rapid decision-making, immediate solutions, ROI-focused conversations with minimal discussion.',
          icon: '⚡'
        },
        research: {
          name: 'Research Track', 
          description: 'Data-driven analysis with real-time market research and competitive insights using AI research tools.',
          icon: '📊'
        },
        strategic: {
          name: 'Strategic Track',
          description: 'Long-term planning with comprehensive strategy development and detailed analysis.',
          icon: '🎯'
        }
      }
    },
    entertainment: {
      title: 'Entertainment & Personal',
      icon: '🎭',
      description: 'For fun conversations and personal problem-solving',
      color: 'from-purple-500 to-pink-600',
      tracks: {
        fun: {
          name: 'Fun Track',
          description: 'Fictional characters, celebrity conversations, and entertaining scenarios for pure enjoyment.',
          icon: '🎪'
        },
        personal: {
          name: 'Personal Track',
          description: 'Real-life problems, advice from diverse expert agents, and personal development coaching.',
          icon: '💭'
        },
        creative: {
          name: 'Creative Track',
          description: 'Storytelling, imaginative scenarios, and collaborative creative projects.',
          icon: '🎨'
        }
      }
    },
    research: {
      title: 'Social Studies & Research',
      icon: '🌍',
      description: 'For researchers, sociologists, and world-builders',
      color: 'from-green-500 to-emerald-600',
      tracks: {
        society: {
          name: 'Society Track',
          description: 'Social dynamics, community behavior, and group psychology experiments.',
          icon: '👥'
        },
        worldbuilding: {
          name: 'World Building Track',
          description: 'Fictional societies with governance systems, economies, religions, and cultures.',
          icon: '🏛️'
        },
        academic: {
          name: 'Academic Track',
          description: 'Controlled experiments, behavioral analysis, and structured research studies.',
          icon: '📚'
        }
      }
    }
  };

  const handleCategorySelect = (categoryId) => {
    setSelectedCategory(categoryId);
  };

  const handleTrackSelect = (trackId) => {
    setSelectedTrack(trackId);
    setCurrentStep('scenario');
  };

  const handleScenarioSubmit = () => {
    if (scenarioInput.trim()) {
      setScenario(scenarioInput.trim());
      setCurrentStep('agents');
    }
  };

  const handleAgentSubmit = async () => {
    if (agentInput.trim()) {
      const newAgentRequest = {
        id: Date.now(),
        prompt: agentInput.trim(),
        status: 'creating',
        progress: 0,
        agent: null // Will store the actual generated agent
      };
      
      setAgentCreationQueue(prev => [...prev, newAgentRequest]);
      setAgentInput('');
      
      try {
        // Check if we have a valid token
        if (!token) {
          console.error('❌ No authentication token available');
          setAgentCreationQueue(prev => 
            prev.map(agent => 
              agent.id === newAgentRequest.id 
                ? { ...agent, status: 'failed', progress: 0 }
                : agent
            )
          );
          return;
        }

        console.log('🚀 Starting AI agent generation for:', agentInput.trim());
        console.log('🔑 Token available:', !!token);
        
        // Start progress simulation
        const progressInterval = setInterval(() => {
          setAgentCreationQueue(prev => 
            prev.map(agent => 
              agent.id === newAgentRequest.id && agent.status === 'creating'
                ? { ...agent, progress: Math.min(agent.progress + Math.random() * 15, 90) }
                : agent
            )
          );
        }, 500);

        // Call the AI-powered agent generation API
        const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/agents/ai-generate`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
          },
          body: JSON.stringify({
            description: agentInput.trim()
          })
        });

        clearInterval(progressInterval); // Stop progress simulation

        console.log('🔄 API Response status:', response.status);

        if (response.ok) {
          const generatedAgent = await response.json();
          console.log('✅ Agent generated successfully:', generatedAgent.name);
          
          // Update the agent creation queue with the generated agent
          setAgentCreationQueue(prev => 
            prev.map(agent => 
              agent.id === newAgentRequest.id 
                ? { 
                    ...agent, 
                    progress: 100, 
                    status: 'completed',
                    agent: generatedAgent,
                    name: generatedAgent.name
                  }
                : agent
            )
          );

          console.log(`✅ AI-generated agent created: ${generatedAgent.name}`);
        } else {
          // Handle API error
          const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }));
          console.error('❌ Agent generation failed:', response.status, errorData.detail);
          
          setAgentCreationQueue(prev => 
            prev.map(agent => 
              agent.id === newAgentRequest.id 
                ? { ...agent, status: 'failed', progress: 0 }
                : agent
            )
          );
        }
      } catch (error) {
        console.error('❌ Agent generation error:', error);
        
        setAgentCreationQueue(prev => 
          prev.map(agent => 
            agent.id === newAgentRequest.id 
              ? { ...agent, status: 'failed', progress: 0 }
              : agent
          )
        );
      }
    }
  };

  const handleComplete = () => {
    const completedAgents = agentCreationQueue
      .filter(a => a.status === 'completed' && a.agent)
      .map(a => a.agent); // Extract the actual generated agent objects
    
    onComplete({
      category: selectedCategory,
      track: selectedTrack,
      scenario: scenario,
      agents: completedAgents // Pass the generated agent objects
    });
  };

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <motion.div 
        initial={{ scale: 0.9, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        exit={{ scale: 0.9, opacity: 0 }}
        className="bg-white rounded-2xl shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-hidden"
      >
        {/* Header */}
        <div className="bg-gradient-to-r from-indigo-600 to-purple-600 p-6 text-white">
          <div className="flex justify-between items-center">
            <div>
              <h2 className="text-2xl font-bold">AI Simulation Setup</h2>
              <p className="opacity-90">Create your perfect AI conversation experience</p>
            </div>
            <button 
              onClick={onCancel}
              className="text-white/80 hover:text-white transition-colors"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
          
          {/* Progress Steps */}
          <div className="flex mt-6 space-x-4">
            {['category', 'scenario', 'agents', 'review'].map((step, index) => (
              <div key={step} className="flex items-center">
                <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium ${
                  currentStep === step ? 'bg-white text-indigo-600' : 
                  ['category', 'scenario', 'agents'].indexOf(currentStep) > ['category', 'scenario', 'agents'].indexOf(step) ? 'bg-white/30 text-white' : 'bg-white/10 text-white/60'
                }`}>
                  {index + 1}
                </div>
                {index < 3 && <div className="w-8 h-0.5 bg-white/30 ml-2"></div>}
              </div>
            ))}
          </div>
        </div>

        {/* Content */}
        <div className="p-6 max-h-[60vh] overflow-y-auto">
          <AnimatePresence mode="wait">
            {currentStep === 'category' && (
              <motion.div
                key="category"
                initial={{ x: 300, opacity: 0 }}
                animate={{ x: 0, opacity: 1 }}
                exit={{ x: -300, opacity: 0 }}
              >
                <h3 className="text-xl font-semibold mb-6">Choose Your Simulation Type</h3>
                
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  {Object.entries(categories).map(([key, category]) => (
                    <motion.div
                      key={key}
                      whileHover={{ scale: 1.02 }}
                      whileTap={{ scale: 0.98 }}
                      onClick={() => handleCategorySelect(key)}
                      className={`p-6 rounded-xl cursor-pointer border-2 transition-all ${
                        selectedCategory === key 
                          ? 'border-indigo-500 bg-indigo-50' 
                          : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
                      }`}
                    >
                      <div className="text-4xl mb-3">{category.icon}</div>
                      <h4 className="font-semibold text-lg mb-2">{category.title}</h4>
                      <p className="text-gray-600 text-sm">{category.description}</p>
                    </motion.div>
                  ))}
                </div>

                {/* Track Selection */}
                {selectedCategory && (
                  <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="mt-8"
                  >
                    <h4 className="text-lg font-semibold mb-4">Select Your Track</h4>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                      {Object.entries(categories[selectedCategory].tracks).map(([trackKey, track]) => (
                        <motion.div
                          key={trackKey}
                          whileHover={{ scale: 1.02 }}
                          onClick={() => handleTrackSelect(trackKey)}
                          onMouseEnter={() => setShowTooltip(trackKey)}
                          onMouseLeave={() => setShowTooltip(null)}
                          className="relative p-4 rounded-lg border-2 border-gray-200 hover:border-indigo-300 cursor-pointer transition-all"
                        >
                          <div className="flex items-center space-x-3">
                            <span className="text-2xl">{track.icon}</span>
                            <span className="font-medium">{track.name}</span>
                          </div>
                          
                          {showTooltip === trackKey && (
                            <motion.div
                              initial={{ opacity: 0, y: 10 }}
                              animate={{ opacity: 1, y: 0 }}
                              className="absolute z-10 top-full left-0 right-0 mt-2 p-3 bg-gray-900 text-white text-sm rounded-lg shadow-lg"
                            >
                              {track.description}
                            </motion.div>
                          )}
                        </motion.div>
                      ))}
                    </div>
                  </motion.div>
                )}
              </motion.div>
            )}

            {currentStep === 'scenario' && (
              <motion.div
                key="scenario"
                initial={{ x: 300, opacity: 0 }}
                animate={{ x: 0, opacity: 1 }}
                exit={{ x: -300, opacity: 0 }}
              >
                <h3 className="text-xl font-semibold mb-6">Describe Your Scenario</h3>
                
                <div className="space-y-4">
                  <div className="bg-gray-50 rounded-lg p-4">
                    <div className="flex items-center space-x-3 mb-3">
                      <div className="w-8 h-8 bg-indigo-100 rounded-full flex items-center justify-center">
                        <span className="text-indigo-600 text-sm">🤖</span>
                      </div>
                      <span className="font-medium text-gray-700">AI Assistant</span>
                    </div>
                    <p className="text-gray-600">
                      Tell me about the scenario you'd like to simulate. What situation, challenge, or topic would you like the agents to discuss? 
                      You can use your voice for easier input!
                    </p>
                  </div>

                  <div className="relative">
                    <textarea
                      value={scenarioInput}
                      onChange={(e) => setScenarioInput(e.target.value)}
                      placeholder="Describe your scenario here... (e.g., 'A startup team needs to decide on their go-to-market strategy')"
                      className="w-full h-32 p-4 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent resize-none"
                    />
                    
                    <button
                      onClick={isListening ? stopVoiceRecognition : startVoiceRecognition}
                      className={`absolute bottom-3 right-3 p-2 rounded-full transition-all ${
                        isListening 
                          ? 'bg-red-500 text-white animate-pulse' 
                          : 'bg-indigo-500 text-white hover:bg-indigo-600'
                      }`}
                      title={isListening ? 'Stop voice input' : 'Start voice input'}
                    >
                      {isListening ? (
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 10a1 1 0 011-1h4a1 1 0 011 1v4a1 1 0 01-1 1h-4a1 1 0 01-1-1v-4z" />
                        </svg>
                      ) : (
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
                        </svg>
                      )}
                    </button>
                  </div>

                  <div className="flex space-x-3">
                    <button
                      onClick={() => setCurrentStep('category')}
                      className="px-6 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
                    >
                      Back
                    </button>
                    <button
                      onClick={handleScenarioSubmit}
                      disabled={!scenarioInput.trim()}
                      className="flex-1 px-6 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                    >
                      Continue to Agents
                    </button>
                  </div>
                </div>
              </motion.div>
            )}

            {currentStep === 'agents' && (
              <motion.div
                key="agents"
                initial={{ x: 300, opacity: 0 }}
                animate={{ x: 0, opacity: 1 }}
                exit={{ x: -300, opacity: 0 }}
              >
                <h3 className="text-xl font-semibold mb-6">Add Your Agents</h3>
                
                <div className="space-y-6">
                  {/* AI Guide */}
                  <div className="bg-gray-50 rounded-lg p-4">
                    <div className="flex items-center space-x-3 mb-3">
                      <div className="w-8 h-8 bg-indigo-100 rounded-full flex items-center justify-center">
                        <span className="text-indigo-600 text-sm">🤖</span>
                      </div>
                      <span className="font-medium text-gray-700">AI Assistant</span>
                    </div>
                    <p className="text-gray-600">
                      Describe what kind of agent you want. Tell me about their role, expertise, background, and personality. 
                      For example: "A senior marketing director with 10 years of B2B experience, analytical mindset, and expertise in digital campaigns."
                    </p>
                  </div>

                  {/* Agent Input */}
                  <div className="relative">
                    <div className="flex space-x-3">
                      <textarea
                        value={agentInput}
                        onChange={(e) => setAgentInput(e.target.value)}
                        placeholder="Describe your agent here..."
                        className="flex-1 h-20 p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent resize-none"
                      />
                      <button
                        onClick={isListening ? stopVoiceRecognition : startVoiceRecognition}
                        className={`p-3 rounded-lg transition-all ${
                          isListening 
                            ? 'bg-red-500 text-white animate-pulse' 
                            : 'bg-indigo-500 text-white hover:bg-indigo-600'
                        }`}
                        title={isListening ? 'Stop voice input' : 'Start voice input'}
                      >
                        {isListening ? (
                          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 10a1 1 0 011-1h4a1 1 0 011 1v4a1 1 0 01-1 1h-4a1 1 0 01-1-1v-4z" />
                          </svg>
                        ) : (
                          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
                          </svg>
                        )}
                      </button>
                      <button
                        onClick={handleAgentSubmit}
                        disabled={!agentInput.trim()}
                        className="px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                      >
                        Add Agent
                      </button>
                    </div>
                  </div>

                  {/* Agent Creation Queue */}
                  {agentCreationQueue.length > 0 && (
                    <div className="space-y-3">
                      <h4 className="font-medium text-gray-700">Creating Agents...</h4>
                      {agentCreationQueue.map((agent) => (
                        <motion.div
                          key={agent.id}
                          initial={{ opacity: 0, y: 20 }}
                          animate={{ opacity: 1, y: 0 }}
                          className="p-4 border border-gray-200 rounded-lg"
                        >
                          <div className="flex items-center justify-between mb-2">
                            <span className="font-medium text-sm">
                              {agent.status === 'completed' && agent.name 
                                ? `${agent.name} (from: "${agent.prompt.substring(0, 30)}${agent.prompt.length > 30 ? '...' : ''}")`
                                : `Creating: ${agent.prompt.substring(0, 50)}${agent.prompt.length > 50 ? '...' : ''}`
                              }
                            </span>
                            <span className={`text-xs px-2 py-1 rounded-full ${
                              agent.status === 'creating' ? 'bg-yellow-100 text-yellow-800' : 
                              agent.status === 'completed' ? 'bg-green-100 text-green-800' :
                              'bg-red-100 text-red-800'
                            }`}>
                              {agent.status === 'creating' ? 'Generating...' : 
                               agent.status === 'completed' ? 'Ready' : 
                               'Failed'}
                            </span>
                          </div>
                          
                          {/* Progress bar */}
                          <div className="w-full bg-gray-200 rounded-full h-2">
                            <div 
                              className={`h-2 rounded-full transition-all duration-300 ${
                                agent.status === 'failed' ? 'bg-red-500' : 'bg-blue-500'
                              }`}
                              style={{ width: `${agent.progress}%` }}
                            />
                          </div>
                          
                          {/* Show generated agent details if completed */}
                          {agent.status === 'completed' && agent.agent && (
                            <div className="mt-2 p-2 bg-green-50 rounded text-xs">
                              <div className="flex items-center space-x-2 mb-1">
                                {agent.agent.avatar_url && (
                                  <img 
                                    src={agent.agent.avatar_url} 
                                    alt={agent.name}
                                    className="w-6 h-6 rounded-full"
                                  />
                                )}
                                <span className="font-medium text-green-800">{agent.agent.archetype} • {agent.agent.goal.substring(0, 50)}...</span>
                              </div>
                            </div>
                          )}
                          
                          {/* Show error message if failed */}
                          {agent.status === 'failed' && (
                            <div className="mt-2 text-xs text-red-600">
                              Failed to generate agent. Please try again.
                            </div>
                          )}
                        </motion.div>
                      ))}
                    </div>
                  )}

                  {/* Continue Button */}
                  <div className="flex space-x-3">
                    <button
                      onClick={() => setCurrentStep('scenario')}
                      className="px-6 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
                    >
                      Back
                    </button>
                    <button
                      onClick={handleComplete}
                      disabled={agentCreationQueue.filter(a => a.status === 'completed').length < 2}
                      className="flex-1 px-6 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                    >
                      Start Simulation ({agentCreationQueue.filter(a => a.status === 'completed').length} agents ready)
                    </button>
                  </div>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </motion.div>
    </div>
  );
};

export default SetupFlow;