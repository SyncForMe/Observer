import React, { useState, useEffect } from 'react';
import { useAuth } from './App';
import axios from 'axios';

const API = process.env.REACT_APP_BACKEND_URL ? `${process.env.REACT_APP_BACKEND_URL}/api` : 'http://localhost:8001/api';

// Define sectors
const sectors = {
  healthcare: {
    name: "Healthcare",
    icon: "🏥",
    categories: {
      medical: {
        name: "Medical",
        icon: "🩺",
        agents: [
          {
            id: 1,
            name: "Dr. Sarah Chen",
            archetype: "scientist",
            archetypeDisplay: "The Scientist",
            title: "Precision Medicine Oncologist",
            goal: "To advance personalized medicine through genomic research and clinical application.",
            background: "Harvard-trained physician-scientist with 15 years in oncology research.",
            expertise: "Precision Oncology, Genomic Medicine, Clinical Trials",
            memories: "Witnessed first successful CRISPR gene therapy trial.",
            knowledge: "https://www.cancer.gov/, https://www.genome.gov/",
            avatar: "https://v3.fal.media/files/zebra/4WDHNe8Ifcyy64zQkIXiE.png"
          }
        ]
      }
    }
  },
  finance: {
    name: "Finance",
    icon: "💰",
    categories: {
      investmentBanking: {
        name: "Investment Banking",
        icon: "🏦",
        agents: [
          {
            id: 101,
            name: "Marcus Goldman",
            archetype: "leader",
            archetypeDisplay: "The Leader",
            title: "Managing Director - M&A",
            goal: "To lead complex mergers and acquisitions that create substantial value for clients and stakeholders.",
            background: "Managing Director with 20+ years in investment banking.",
            expertise: "Mergers & Acquisitions, Corporate Finance, Deal Structuring",
            memories: "Led $50B mega-merger between two Fortune 500 companies.",
            knowledge: "https://www.sec.gov/, https://www.federalreserve.gov/",
            avatar: "https://v3.fal.media/files/zebra/jaob551emeN1UGNivcsat.png"
          }
        ]
      }
    }
  },
  technology: {
    name: "Technology",
    icon: "💻",
    categories: {
      softwareEngineering: {
        name: "Software Engineering",
        icon: "💻",
        agents: [
          {
            id: 301,
            name: "Dr. Aisha Muhammad",
            archetype: "scientist",
            archetypeDisplay: "The Scientist",
            title: "AI Ethics Researcher",
            goal: "To develop ethical AI systems that enhance human capabilities while preserving privacy and autonomy.",
            background: "Computer scientist with PhD in AI from MIT.",
            expertise: "Machine Learning, AI Safety, Natural Language Processing",
            memories: "Witnessed GPT-3's first outputs at OpenAI in 2020.",
            knowledge: "Expert understanding of machine learning including deep neural networks.",
            avatar: "https://v3.fal.media/files/penguin/pESE1pNcl0pyoMBUKWKnW.png"
          }
        ]
      }
    }
  }
};

const AgentLibrary = ({ onAddAgent, onRemoveAgent }) => {
  const { token } = useAuth();
  const [selectedSector, setSelectedSector] = useState(null);
  const [selectedCategory, setSelectedCategory] = useState(null);
  const [selectedAgentDetails, setSelectedAgentDetails] = useState(null);
  const [addingAgents, setAddingAgents] = useState(new Set());
  const [addedAgents, setAddedAgents] = useState(new Set());
  const [isSectorsExpanded, setIsSectorsExpanded] = useState(true);

  const handleAddAgent = async (agent) => {
    if (!onAddAgent) return;
    
    setAddingAgents(prev => new Set(prev).add(agent.id));
    
    try {
      const agentData = {
        name: agent.name,
        archetype: agent.archetype,
        goal: agent.goal,
        background: agent.background,
        expertise: agent.expertise,
        memory_summary: `${agent.memories} Knowledge Sources: ${agent.knowledge}`,
        avatar_url: agent.avatar,
      };
      
      const result = await onAddAgent(agentData);
      
      if (result && result.success) {
        setAddedAgents(prev => new Set(prev).add(agent.id));
        console.log('Agent added successfully:', result.message);
      } else {
        console.error('Failed to add agent:', result?.message || 'Unknown error');
      }
      
    } catch (error) {
      console.error('Failed to add agent:', error);
    }
    
    setAddingAgents(prev => {
      const newSet = new Set(prev);
      newSet.delete(agent.id);
      return newSet;
    });
  };

  const currentSector = sectors[selectedSector];
  const currentCategory = selectedCategory ? currentSector?.categories[selectedCategory] : null;

  return (
    <div className="space-y-6">
      {/* Agent Library Header */}
      <div className="bg-white/10 backdrop-blur-lg rounded-xl p-6">
        <div className="flex justify-between items-center mb-2">
          <div>
            <h2 className="text-2xl font-bold text-white mb-2">🤖 Agent Library</h2>
            <p className="text-white/80">Choose from professionally crafted agent profiles</p>
          </div>
        </div>
      </div>

      {/* Main Agent Library Content */}
      <div className="bg-white/10 backdrop-blur-lg rounded-xl overflow-hidden">
        <div className="flex h-[600px]">
          {/* Sidebar */}
          <div className="w-64 bg-gray-50 border-r p-4">
            {/* SECTORS header with expandable button */}
            <div 
              className="flex justify-between items-center cursor-pointer hover:bg-gray-100 p-2 rounded-lg transition-colors mb-4"
              onClick={() => setIsSectorsExpanded(!isSectorsExpanded)}
            >
              <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wide">SECTORS</h3>
              <button
                type="button"
                className="text-gray-500 hover:text-gray-700 transition-transform duration-200"
                style={{ transform: isSectorsExpanded ? 'rotate(180deg)' : 'rotate(0deg)' }}
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </svg>
              </button>
            </div>
            
            {/* Sectors list - conditionally rendered */}
            {isSectorsExpanded && (
              <div className="space-y-2">
                {Object.entries(sectors).map(([key, sector]) => (
                  <button
                    key={key}
                    onClick={() => {
                      setSelectedSector(key);
                      setSelectedCategory(null);
                    }}
                    className={`w-full text-left p-3 rounded-lg transition-colors ${
                      selectedSector === key
                        ? 'bg-purple-100 text-purple-800 border-l-4 border-purple-600'
                        : 'text-gray-700 hover:bg-gray-100'
                    }`}
                  >
                    <span className="text-lg mr-2">{sector.icon}</span>
                    {sector.name}
                  </button>
                ))}
              </div>
            )}
          </div>

          {/* Main Content */}
          <div className="flex-1 p-6 overflow-y-auto">
            {selectedSector && !selectedCategory ? (
              // Sector Categories View  
              <div>
                {/* Back Button */}
                <div className="flex items-center mb-6">
                  <button
                    onClick={() => {
                      setSelectedSector(null);
                    }}
                    className="text-purple-600 hover:text-purple-800 font-medium mr-4 flex items-center"
                  >
                    ← Back to Sectors
                  </button>
                  <h3 className="text-xl font-bold text-gray-800">
                    {sectors[selectedSector].icon} {sectors[selectedSector].name}
                  </h3>
                </div>
                <div className="grid grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
                  {Object.entries(sectors[selectedSector].categories).map(([key, category]) => (
                    <button
                      key={key}
                      onClick={() => setSelectedCategory(key)}
                      className="bg-white border-2 border-gray-200 rounded-lg p-4 hover:border-purple-300 hover:shadow-md transition-all text-center group"
                    >
                      <div className="text-3xl mb-2 group-hover:scale-110 transition-transform">
                        {category.icon}
                      </div>
                      <div className="text-sm font-medium text-gray-800">
                        {category.name}
                      </div>
                      <div className="text-xs text-gray-500 mt-1">
                        {category.agents.length} agents
                      </div>
                    </button>
                  ))}
                </div>
              </div>
            ) : selectedCategory ? (
              // Agents View
              <div>
                <div className="flex items-center mb-6">
                  <button
                    onClick={() => setSelectedCategory(null)}
                    className="text-purple-600 hover:text-purple-800 font-medium mr-4 flex items-center"
                  >
                    ← Back
                  </button>
                  <h3 className="text-xl font-bold text-gray-800">
                    {sectors[selectedSector].categories[selectedCategory].icon} {sectors[selectedSector].categories[selectedCategory].name}
                  </h3>
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-4">
                  {sectors[selectedSector].categories[selectedCategory].agents.map((agent) => (
                    <div key={agent.id} className="bg-white border border-gray-200 rounded-lg hover:shadow-md transition-shadow relative">
                      {addedAgents.has(agent.id) && (
                        <div className="absolute top-2 right-2 z-10 flex items-center space-x-1">
                          <div className="bg-transparent border border-green-500 text-green-600 text-xs font-medium px-2 py-1 rounded-full">
                            added
                          </div>
                        </div>
                      )}
                      <div className="p-4">
                        <div className="flex items-start space-x-3">
                          <img
                            src={agent.avatar}
                            alt={agent.name}
                            className="w-12 h-12 rounded-full object-cover"
                          />
                          <div className="flex-1 min-w-0">
                            <h4 className="font-semibold text-gray-900 text-sm">{agent.name}</h4>
                            <p className="text-xs text-gray-600 mt-1">{agent.archetypeDisplay || agent.archetype}</p>
                          </div>
                        </div>
                        
                        <div className="mt-3">
                          <div className="mb-2">
                            <span className="text-xs font-medium text-gray-700 uppercase tracking-wide">ARCHETYPE</span>
                            <p className="text-xs text-gray-600 mt-1">{agent.archetypeDisplay || agent.archetype}</p>
                          </div>
                          
                          <div className="mb-2">
                            <span className="text-xs font-medium text-gray-700 uppercase tracking-wide">GOAL</span>
                            <p className="text-xs text-gray-600 mt-1">{agent.goal}</p>
                          </div>
                          
                          <div className="mb-3">
                            <span className="text-xs font-medium text-gray-700 uppercase tracking-wide">EXPERTISE</span>
                            <p className="text-xs text-gray-600 mt-1">{agent.expertise}</p>
                          </div>
                        </div>
                      </div>
                      
                      <div className="px-4 pb-4 space-y-2">
                        <button
                          onClick={() => setSelectedAgentDetails(agent)}
                          className="w-full border border-blue-500 text-blue-600 py-2 px-3 rounded text-xs font-medium hover:bg-blue-50 transition-colors"
                        >
                          🔍 View Full Details
                        </button>
                        <button
                          onClick={() => handleAddAgent(agent)}
                          disabled={addingAgents.has(agent.id)}
                          className={`w-full py-2 px-3 rounded text-xs font-medium transition-colors ${
                            addingAgents.has(agent.id)
                              ? 'bg-gray-300 text-gray-500'
                              : 'bg-purple-600 text-white hover:bg-purple-700'
                          }`}
                        >
                          {addingAgents.has(agent.id) 
                            ? 'Adding...'
                            : addedAgents.has(agent.id) 
                            ? 'Add Again' 
                            : 'Add Agent'
                          }
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ) : (
              // Default Empty State
              <div className="text-center py-20">
                <div className="text-6xl mb-6">🏛️</div>
                <h3 className="text-2xl font-bold text-gray-800 mb-4">Welcome to Agent Library</h3>
                <p className="text-gray-600 max-w-lg mx-auto mb-6">
                  Choose a sector from <strong>Sectors</strong> to browse agents by industry.
                </p>
                <div className="space-y-2 text-sm text-gray-500">
                  <p>🏭 Sectors: Browse agents by healthcare, finance, and technology</p>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Agent Details Modal */}
      {selectedAgentDetails && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-[100] p-4">
          <div className="bg-white rounded-lg w-full max-w-2xl max-h-[90vh] overflow-y-auto relative">
            {/* Blue Header with Agent Info */}
            <div className="bg-blue-500 text-white p-6 rounded-t-lg relative">
              <button
                onClick={() => setSelectedAgentDetails(null)}
                className="absolute top-4 right-4 text-white hover:text-gray-200 text-xl font-bold w-8 h-8 flex items-center justify-center rounded-full hover:bg-blue-600 transition-colors"
              >
                ×
              </button>
              
              <div className="flex items-center space-x-4">
                <img
                  src={selectedAgentDetails.avatar}
                  alt={selectedAgentDetails.name}
                  className="w-16 h-16 rounded-full object-cover border-2 border-white"
                />
                <div>
                  <h3 className="text-xl font-bold">{selectedAgentDetails.name}</h3>
                  <p className="text-blue-100">{selectedAgentDetails.title || "Professional"}</p>
                  <p className="text-blue-200 text-sm mt-1">{selectedAgentDetails.archetypeDisplay || selectedAgentDetails.archetype}</p>
                </div>
              </div>
            </div>

            {/* Content */}
            <div className="p-6 space-y-6">
              <div>
                <h4 className="font-bold text-gray-800 mb-3 flex items-center">
                  <span className="mr-2">🎯</span>
                  Goal
                </h4>
                <p className="text-gray-700 leading-relaxed">{selectedAgentDetails.goal}</p>
              </div>

              <div>
                <h4 className="font-bold text-gray-800 mb-3 flex items-center">
                  <span className="mr-2">🧠</span>
                  Expertise
                </h4>
                <p className="text-gray-700 leading-relaxed">{selectedAgentDetails.expertise}</p>
              </div>

              <div>
                <h4 className="font-bold text-gray-800 mb-3 flex items-center">
                  <span className="mr-2">📋</span>
                  Background
                </h4>
                <p className="text-gray-700 leading-relaxed">{selectedAgentDetails.background}</p>
              </div>
            </div>

            {/* Bottom Buttons */}
            <div className="px-6 pb-6 flex space-x-3">
              <button
                onClick={() => setSelectedAgentDetails(null)}
                className="flex-1 bg-white border border-gray-300 text-gray-700 py-3 px-4 rounded-lg font-medium hover:bg-gray-50 transition-colors"
              >
                Close
              </button>
              <button
                onClick={() => handleAddAgent(selectedAgentDetails)}
                disabled={addingAgents.has(selectedAgentDetails.id)}
                className={`flex-1 py-3 px-4 rounded-lg font-medium transition-colors ${
                  addedAgents.has(selectedAgentDetails.id)
                    ? 'bg-green-100 text-green-800'
                    : addingAgents.has(selectedAgentDetails.id)
                    ? 'bg-gray-300 text-gray-500'
                    : 'bg-purple-600 text-white hover:bg-purple-700'
                }`}
              >
                {addedAgents.has(selectedAgentDetails.id) 
                  ? '✅ Added' 
                  : addingAgents.has(selectedAgentDetails.id) 
                  ? 'Adding...' 
                  : 'Add Agent'
                }
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AgentLibrary;