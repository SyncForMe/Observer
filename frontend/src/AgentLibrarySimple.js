import React, { useState } from 'react';
import { useAuth } from './App';

// Healthcare Categories
const healthcareCategories = {
  medical: { name: "Medical", icon: "🩺", agents: Array(4).fill({}) },
  pharmaceutical: { name: "Pharmaceutical", icon: "💊", agents: Array(3).fill({}) },
  biotechnology: { name: "Biotechnology", icon: "🧬", agents: Array(3).fill({}) },
  nursing: { name: "Nursing", icon: "👩‍⚕️", agents: Array(3).fill({}) },
  publicHealth: { name: "Public Health", icon: "🏥", agents: Array(3).fill({}) },
  nutrition: { name: "Nutrition & Dietetics", icon: "🥗", agents: Array(2).fill({}) },
  physicalTherapy: { name: "Physical Therapy", icon: "🏃‍♂️", agents: Array(2).fill({}) },
  veterinary: { name: "Veterinary", icon: "🐕", agents: Array(2).fill({}) },
  medicalResearch: { name: "Medical Research", icon: "🔬", agents: Array(2).fill({}) },
  epidemiology: { name: "Epidemiology", icon: "📊", agents: Array(2).fill({}) }
};

// Finance Categories
const financeCategories = {
  investmentBanking: { name: "Investment Banking", icon: "🏦", agents: Array(3).fill({}) },
  ventureCapital: { name: "Venture Capital", icon: "🚀", agents: Array(2).fill({}) },
  privateEquity: { name: "Private Equity", icon: "💼", agents: Array(2).fill({}) },
  insurance: { name: "Insurance", icon: "🛡️", agents: Array(2).fill({}) },
  accounting: { name: "Accounting", icon: "📊", agents: Array(2).fill({}) },
  auditing: { name: "Auditing", icon: "🔍", agents: Array(2).fill({}) },
  taxAdvisory: { name: "Tax Advisory", icon: "📋", agents: Array(2).fill({}) },
  realEstate: { name: "Real Estate", icon: "🏢", agents: Array(2).fill({}) },
  banking: { name: "Banking", icon: "🏛️", agents: Array(2).fill({}) },
  trading: { name: "Trading", icon: "📈", agents: Array(2).fill({}) },
  riskManagement: { name: "Risk Management", icon: "⚖️", agents: Array(2).fill({}) },
  actuarialScience: { name: "Actuarial Science", icon: "📐", agents: Array(2).fill({}) }
};

// Technology Categories
const technologyCategories = {
  softwareEngineering: { name: "Software Engineering", icon: "💻", agents: Array(3).fill({}) },
  dataScience: { name: "Data Science", icon: "📊", agents: Array(3).fill({}) },
  cybersecurity: { name: "Cybersecurity", icon: "🔒", agents: Array(3).fill({}) },
  aiMachineLearning: { name: "AI & Machine Learning", icon: "🧠", agents: Array(3).fill({}) },
  devOps: { name: "DevOps", icon: "⚙️", agents: Array(3).fill({}) },
  cloudArchitecture: { name: "Cloud Architecture", icon: "☁️", agents: Array(3).fill({}) },
  blockchain: { name: "Blockchain", icon: "🔗", agents: Array(3).fill({}) },
  civilEngineering: { name: "Civil Engineering", icon: "🏗️", agents: Array(3).fill({}) },
  mechanicalEngineering: { name: "Mechanical Engineering", icon: "⚙️", agents: Array(3).fill({}) },
  electricalEngineering: { name: "Electrical Engineering", icon: "⚡", agents: Array(3).fill({}) },
  chemicalEngineering: { name: "Chemical Engineering", icon: "🧪", agents: Array(3).fill({}) },
  aerospaceEngineering: { name: "Aerospace Engineering", icon: "🚀", agents: Array(3).fill({}) },
  biomedicalEngineering: { name: "Biomedical Engineering", icon: "🩺", agents: Array(3).fill({}) }
};

// Define sectors
const sectors = {
  healthcare: {
    name: "Healthcare & Life Sciences",
    icon: "🏥",
    categories: healthcareCategories
  },
  finance: {
    name: "Finance & Business",
    icon: "💰",
    categories: financeCategories
  },
  technology: {
    name: "Technology & Engineering",
    icon: "🔧",
    categories: technologyCategories
  }
};

// Quick Teams
const quickTeams = {
  research: {
    name: "Research Team",
    icon: "🔬",
    description: "Scientist, Optimist, Leader",
    agents: Array(3).fill({})
  },
  business: {
    name: "Business Team", 
    icon: "💼",
    description: "Strategist, Consultant, Innovator",
    agents: Array(3).fill({})
  },
  crypto: {
    name: "Crypto Team",
    icon: "₿", 
    description: "Blockchain Expert, DeFi Specialist, Crypto Analyst",
    agents: Array(3).fill({})
  }
};

const AgentLibrary = ({ onAddAgent, onRemoveAgent }) => {
  const { user, token } = useAuth();
  const [selectedSector, setSelectedSector] = useState(null);
  const [selectedCategory, setSelectedCategory] = useState(null);
  const [selectedAgentDetails, setSelectedAgentDetails] = useState(null);
  const [selectedQuickTeam, setSelectedQuickTeam] = useState(null);
  const [isSectorsExpanded, setIsSectorsExpanded] = useState(true);
  const [isQuickTeamBuildersExpanded, setIsQuickTeamBuildersExpanded] = useState(false);
  
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
            {/* QUICK TEAM BUILDERS header with expandable button */}
            <div 
              className="flex justify-between items-center cursor-pointer hover:bg-gray-100 p-2 rounded-lg transition-colors mb-4"
              onClick={() => {
                setIsQuickTeamBuildersExpanded(!isQuickTeamBuildersExpanded);
                setSelectedSector(null);
                setSelectedCategory(null);
              }}
            >
              <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wide">QUICK TEAM BUILDERS</h3>
              <button
                type="button"
                className="text-gray-500 hover:text-gray-700 transition-transform duration-200"
                style={{ transform: isQuickTeamBuildersExpanded ? 'rotate(180deg)' : 'rotate(0deg)' }}
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </svg>
              </button>
            </div>
            
            {/* Quick Team Builders list - conditionally rendered */}
            {isQuickTeamBuildersExpanded && (
              <div className="space-y-2 mb-6">
                <button
                  onClick={() => {
                    setSelectedQuickTeam('research');
                    setSelectedSector(null);
                    setSelectedCategory(null);
                  }}
                  className="w-full text-left p-3 rounded-lg transition-colors text-gray-700 hover:bg-gray-100"
                >
                  <span className="text-lg mr-2">🔬</span>
                  Research Team
                </button>
                
                <button
                  onClick={() => {
                    setSelectedQuickTeam('business');
                    setSelectedSector(null);
                    setSelectedCategory(null);
                  }}
                  className="w-full text-left p-3 rounded-lg transition-colors text-gray-700 hover:bg-gray-100"
                >
                  <span className="text-lg mr-2">💼</span>
                  Business Team
                </button>
                
                <button
                  onClick={() => {
                    setSelectedQuickTeam('crypto');
                    setSelectedSector(null);
                    setSelectedCategory(null);
                  }}
                  className="w-full text-left p-3 rounded-lg transition-colors text-gray-700 hover:bg-gray-100"
                >
                  <span className="text-lg mr-2">₿</span>
                  Crypto Team
                </button>
              </div>
            )}

            {/* SECTORS header with expandable button */}
            <div 
              className="flex justify-between items-center cursor-pointer hover:bg-gray-100 p-2 rounded-lg transition-colors mb-4"
              onClick={() => {
                setIsSectorsExpanded(!isSectorsExpanded);
                setSelectedQuickTeam(null);
              }}
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
                      setSelectedQuickTeam(null);
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
            {selectedQuickTeam ? (
              // Quick Team View
              <div>
                {/* Back Button */}
                <div className="mb-4">
                  <button
                    onClick={() => {
                      setSelectedQuickTeam(null);
                      setIsQuickTeamBuildersExpanded(true);
                    }}
                    className="flex items-center space-x-2 text-purple-600 hover:text-purple-700 transition-colors"
                  >
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                    </svg>
                    <span>Back to Quick Teams</span>
                  </button>
                </div>
                
                <div className="flex justify-between items-center mb-6">
                  <h3 className="text-xl font-bold text-gray-800">
                    {quickTeams[selectedQuickTeam].icon} {quickTeams[selectedQuickTeam].name}
                  </h3>
                  <button
                    className="bg-purple-600 text-white px-4 py-2 rounded-lg hover:bg-purple-700 font-medium"
                  >
                    Add Entire Team
                  </button>
                </div>
                
                <p className="text-gray-600 mb-6">{quickTeams[selectedQuickTeam].description}</p>
                
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 agent-grid">
                  {Array(3).fill(0).map((_, index) => (
                    <div key={index} className="bg-white border border-gray-200 rounded-lg hover:shadow-md transition-shadow">
                      <div className="p-4">
                        <div className="flex items-start space-x-3">
                          <div className="w-12 h-12 rounded-full bg-purple-100 flex items-center justify-center">
                            <span className="text-purple-600 text-lg font-bold">A</span>
                          </div>
                          <div>
                            <h4 className="font-semibold text-gray-800">Agent Name</h4>
                            <p className="text-sm text-gray-500">Archetype</p>
                          </div>
                        </div>
                        
                        <div className="mt-3">
                          <p className="text-sm text-gray-600">Agent Title</p>
                        </div>
                        
                        <div className="mt-4 flex space-x-2">
                          <button
                            onClick={() => setSelectedAgentDetails({})}
                            className="text-purple-600 hover:text-purple-800 text-sm font-medium"
                          >
                            View Details
                          </button>
                          <button
                            className="bg-purple-600 text-white px-3 py-1 rounded hover:bg-purple-700 text-sm"
                          >
                            Add Agent
                          </button>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ) : selectedSector && !selectedCategory ? (
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

                <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-4 agent-grid">
                  {Array(sectors[selectedSector].categories[selectedCategory].agents.length).fill(0).map((_, index) => (
                    <div key={index} className="bg-white border border-gray-200 rounded-lg hover:shadow-md transition-shadow">
                      <div className="p-4">
                        <div className="flex items-start space-x-3">
                          <div className="w-12 h-12 rounded-full bg-purple-100 flex items-center justify-center">
                            <span className="text-purple-600 text-lg font-bold">A</span>
                          </div>
                          <div>
                            <h4 className="font-semibold text-gray-800">Agent Name</h4>
                            <p className="text-sm text-gray-500">Archetype</p>
                          </div>
                        </div>
                        
                        <div className="mt-3">
                          <p className="text-sm text-gray-600">Agent Title</p>
                        </div>
                        
                        <div className="mt-4 flex space-x-2">
                          <button
                            onClick={() => setSelectedAgentDetails({})}
                            className="text-purple-600 hover:text-purple-800 text-sm font-medium"
                          >
                            View Details
                          </button>
                          <button
                            className="bg-purple-600 text-white px-3 py-1 rounded hover:bg-purple-700 text-sm"
                          >
                            Add Agent
                          </button>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ) : (
              // Welcome View (Default)
              <div className="text-center py-12">
                <div className="text-6xl mb-4">👋</div>
                <h3 className="text-xl font-semibold text-gray-800 mb-2">Welcome to the Agent Library</h3>
                <p className="text-gray-600 max-w-lg mx-auto mb-8">
                  Select a team from <strong>Quick Team Builders</strong> to see pre-configured agent teams, 
                  or choose a sector from <strong>Sectors</strong> to browse agents by industry.
                </p>
                <div className="space-y-2 text-sm text-gray-500">
                  <p>🔬 Quick Team Builders: Pre-made teams for instant setup</p>
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
            {/* Header */}
            <div className="bg-blue-500 text-white p-6 rounded-t-lg relative">
              <button
                onClick={() => setSelectedAgentDetails(null)}
                className="absolute top-4 right-4 text-white hover:text-gray-200 text-xl font-bold w-8 h-8 flex items-center justify-center rounded-full hover:bg-blue-600 transition-colors"
              >
                ×
              </button>
              
              <div className="flex items-center space-x-4">
                <div className="w-16 h-16 rounded-full bg-blue-400 flex items-center justify-center">
                  <span className="text-white text-xl">👤</span>
                </div>
                <div>
                  <h3 className="text-xl font-bold">Agent Name</h3>
                  <p className="text-blue-100">Professional</p>
                  <p className="text-blue-200 text-sm mt-1">Archetype</p>
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
                <p className="text-gray-700 leading-relaxed">Agent goal description</p>
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
                className="flex-1 py-3 px-4 rounded-lg font-medium transition-colors bg-purple-600 text-white hover:bg-purple-700"
              >
                Add Agent
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AgentLibrary;