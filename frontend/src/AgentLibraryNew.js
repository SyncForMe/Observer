import React, { useState, useEffect, useRef } from 'react';
import { useAuth } from './App';
import axios from 'axios';

const API = process.env.REACT_APP_BACKEND_URL ? `${process.env.REACT_APP_BACKEND_URL}/api` : 'http://localhost:8001/api';

// Healthcare Categories with full agent data
const healthcareCategories = {
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
        background: "Harvard-trained physician-scientist with 15 years in oncology research. Led breakthrough studies on BRCA mutations at Dana-Farber Cancer Institute.",
        expertise: "Precision Oncology, Genomic Medicine, Clinical Trials, Biomarkers, Pharmacogenomics",
        memories: "Witnessed first successful CRISPR gene therapy trial. Lost mentor to pancreatic cancer, driving obsession with early detection.",
        knowledge: "https://www.cancer.gov/, https://www.genome.gov/, https://clinicaltrials.gov/",
        avatar: "https://v3.fal.media/files/zebra/4WDHNe8Ifcyy64zQkIXiE.png"
      },
      {
        id: 2,
        name: "Dr. Marcus Rodriguez",
        archetype: "leader",
        archetypeDisplay: "The Leader",
        title: "Emergency Medicine Physician",
        goal: "To advance global health equity through innovative healthcare delivery models.",
        background: "Emergency medicine physician and global health advocate. Founded medical nonprofit serving rural communities.",
        expertise: "Emergency Medicine, Global Health, Telemedicine, Disaster Medicine, Healthcare Equity",
        memories: "Established telemedicine network serving 50,000 patients. Led medical response to Hurricane Maria.",
        knowledge: "https://www.who.int/, https://www.msf.org/, https://www.acep.org/",
        avatar: "https://v3.fal.media/files/kangaroo/Fs0Hk6n-gu_fG33Lhj7JC.png"
      },
      {
        id: 3,
        name: "Dr. Katherine Vale",
        archetype: "mediator",
        archetypeDisplay: "The Mediator",
        title: "Family Medicine Physician",
        goal: "To bridge the gap between specialist and primary care through collaborative medicine.",
        background: "Family medicine physician specializing in care coordination. Developed innovative patient-centered medical home model.",
        expertise: "Family Medicine, Care Coordination, Chronic Disease Management, Patient-Centered Care",
        memories: "Coordinated care for diabetic patient with 8 specialists achieving 70% improvement.",
        knowledge: "https://www.aafp.org/, https://www.pcpcc.org/, https://www.cms.gov/",
        avatar: "https://v3.fal.media/files/panda/A4RzV6yZUDiO4IVKkqKlz.png"
      },
      {
        id: 4,
        name: "Dr. Ahmed Hassan",
        archetype: "optimist",
        archetypeDisplay: "The Optimist",
        title: "Internal Medicine Specialist",
        goal: "To revolutionize preventive care through innovative screening and early intervention programs.",
        background: "Internal medicine specialist with focus on preventive care. Developed population health initiatives that reduced chronic disease rates by 40%.",
        expertise: "Internal Medicine, Preventive Care, Population Health, Chronic Disease Prevention, Health Screening",
        memories: "Created community health program that prevented 200+ diabetes cases. Pioneered early detection protocol for heart disease.",
        knowledge: "https://www.acponline.org/, https://www.ahrq.gov/, https://www.uspreventiveservicestaskforce.org/",
        avatar: "https://v3.fal.media/files/zebra/DgQjI5zc64wjP8S9jg475.png"
      }
    ]
  },
  pharmaceutical: {
    name: "Pharmaceutical",
    icon: "💊",
    agents: [
      {
        id: 121,
        name: "Dr. Elena Petrov",
        archetype: "scientist",
        archetypeDisplay: "The Scientist",
        title: "Pharmaceutical Research Director",
        goal: "To accelerate drug discovery through innovative molecular design and clinical trials.",
        background: "PhD in Pharmaceutical Sciences from MIT. Led development of 3 FDA-approved drugs. Expert in computational drug design and clinical trial optimization.",
        expertise: "Drug Discovery, Clinical Trials, Molecular Design, Pharmacokinetics, Regulatory Affairs",
        memories: "Developed breakthrough Alzheimer's drug that passed Phase II trials. Created AI-powered drug screening platform reducing discovery time by 60%.",
        knowledge: "https://www.fda.gov/, https://clinicaltrials.gov/, https://www.ema.europa.eu/",
        avatar: "https://v3.fal.media/files/rabbit/XGsVyTlCp9yX8-EO7FGOD.png"
      },
      {
        id: 122,
        name: "Dr. James Park",
        archetype: "optimist",
        archetypeDisplay: "The Optimist",
        title: "Clinical Pharmacist",
        goal: "To optimize patient outcomes through personalized medication management and education.",
        background: "PharmD with specialized training in clinical pharmacy. Developed medication therapy management programs that improved patient adherence by 85%.",
        expertise: "Clinical Pharmacy, Medication Therapy Management, Pharmacogenomics, Patient Education, Drug Safety",
        memories: "Prevented 500+ adverse drug events through comprehensive medication reviews. Established pharmaceutical care model adopted by 20 hospitals.",
        knowledge: "https://www.accp.com/, https://www.ashp.org/, https://www.pharmacogenomics.org/",
        avatar: "https://v3.fal.media/files/elephant/j_PzMAW0YvGLO3ZOEMxD2.png"
      },
      {
        id: 123,
        name: "Dr. Maria Santos",
        archetype: "leader",
        archetypeDisplay: "The Leader",
        title: "Regulatory Affairs Director",
        goal: "To streamline drug approval processes while maintaining the highest safety standards.",
        background: "Former FDA reviewer turned industry leader. Led regulatory strategy for 15+ successful drug approvals. Expert in global regulatory harmonization.",
        expertise: "Regulatory Affairs, FDA Approval Process, Global Drug Registration, Quality Assurance, Compliance",
        memories: "Negotiated breakthrough therapy designation for rare disease drug. Led international regulatory team through complex approval process across 30 countries.",
        knowledge: "https://www.fda.gov/, https://www.ich.org/, https://www.raps.org/",
        avatar: "https://v3.fal.media/files/tiger/H8P4Xf2WwYKJAOpcV8sIh.png"
      }
    ]
  },
  biotechnology: {
    name: "Biotechnology",
    icon: "🧬",
    agents: [
      {
        id: 161,
        name: "Dr. Lisa Wang",
        archetype: "scientist",
        archetypeDisplay: "The Scientist",
        title: "Biotech Research Scientist",
        goal: "To develop revolutionary gene therapies for previously incurable genetic diseases.",
        background: "PhD in Molecular Biology from Stanford. Pioneered CRISPR applications in genetic disease treatment. Published 50+ papers in top-tier journals.",
        expertise: "Gene Therapy, CRISPR Technology, Molecular Biology, Genetic Engineering, Cell Biology",
        memories: "Developed first successful gene therapy for inherited blindness. Created viral vector delivery system with 95% efficiency.",
        knowledge: "https://www.nature.com/, https://www.cell.com/, https://www.biotech.org/",
        avatar: "https://v3.fal.media/files/lion/mNlCUOdUdRJxODNVWJgXR.png"
      },
      {
        id: 162,
        name: "Dr. Robert Kim",
        archetype: "adventurer",
        archetypeDisplay: "The Adventurer",
        title: "Biotech Innovation Leader",
        goal: "To push the boundaries of biotechnology through disruptive innovation and strategic risk-taking.",
        background: "Serial biotech entrepreneur with 3 successful exits. Founded companies focused on synthetic biology and personalized medicine. Angel investor in 20+ biotech startups.",
        expertise: "Biotech Innovation, Synthetic Biology, Personalized Medicine, Venture Capital, Strategic Partnerships",
        memories: "Led team that created first synthetic organism for drug production. Raised $200M for breakthrough platform technology.",
        knowledge: "https://www.nature.com/nbt/, https://www.bio.org/, https://www.xconomy.com/",
        avatar: "https://v3.fal.media/files/dolphin/Q4aWJM3FKjTJfkl1F9gNV.png"
      }
    ]
  }
};

// Finance Categories with full agent data
const financeCategories = {
  investmentBanking: {
    name: "Investment Banking",
    icon: "🏦",
    agents: [
      {
        id: 301,
        name: "Marcus Goldman",
        archetype: "leader",
        archetypeDisplay: "The Leader",
        title: "Managing Director - M&A",
        goal: "To lead complex mergers and acquisitions that create substantial value for clients and stakeholders.",
        background: "Managing Director with 20+ years in investment banking. Led transactions worth over $100B. Expert in cross-border M&A and strategic advisory.",
        expertise: "Mergers & Acquisitions, Corporate Finance, Deal Structuring, Strategic Advisory, Capital Markets",
        memories: "Led $50B mega-merger between two Fortune 500 companies. Structured innovative financing for tech unicorn IPO.",
        knowledge: "https://www.sec.gov/, https://www.federalreserve.gov/, https://www.bloomberg.com/",
        avatar: "https://v3.fal.media/files/zebra/jaob551emeN1UGNivcsat.png"
      },
      {
        id: 302,
        name: "Alexandra Chen",
        archetype: "optimist",
        archetypeDisplay: "The Optimist",
        title: "VP - Equity Capital Markets",
        goal: "To democratize access to capital markets and help innovative companies grow through strategic public offerings.",
        background: "Equity capital markets expert with track record of successful IPOs. Helped 50+ companies go public raising over $20B in total.",
        expertise: "IPO Strategy, Equity Capital Markets, Valuation, Investor Relations, Public Company Readiness",
        memories: "Led record-breaking biotech IPO that raised $2B. Developed innovative direct listing structure adopted industry-wide.",
        knowledge: "https://www.nasdaq.com/, https://www.nyse.com/, https://www.sec.gov/",
        avatar: "https://v3.fal.media/files/panda/X9kT3mVzP0oL4bWqJ2fNc.png"
      }
    ]
  },
  riskManagement: {
    name: "Risk Management",
    icon: "⚖️",
    agents: [
      {
        id: 341,
        name: "Dr. Sarah Mitchell",
        archetype: "skeptic",
        archetypeDisplay: "The Skeptic",
        title: "Chief Risk Officer",
        goal: "To protect organizational assets while enabling calculated growth through comprehensive risk assessment.",
        background: "PhD in Financial Mathematics from Oxford. Former regulatory examiner turned Chief Risk Officer. Expert in systemic risk and stress testing.",
        expertise: "Risk Assessment, Stress Testing, Regulatory Compliance, Financial Mathematics, Systemic Risk",
        memories: "Identified and prevented major trading loss that could have bankrupted the firm. Developed risk model that predicted 2008 subprime crisis.",
        knowledge: "https://www.bis.org/, https://www.federalreserve.gov/, https://www.risk.net/",
        avatar: "https://v3.fal.media/files/elephant/X7gP9mVzQ4aL5wWqJ3nN8.png"
      }
    ]
  }
};

// Technology Categories with full agent data
const technologyCategories = {
  softwareEngineering: {
    name: "Software Engineering",
    icon: "💻",
    agents: [
      {
        id: 501,
        name: "Dr. Aisha Muhammad",
        archetype: "scientist",
        archetypeDisplay: "The Scientist",
        title: "AI Ethics Researcher",
        goal: "To develop ethical AI systems that enhance human capabilities while preserving privacy and autonomy.",
        background: "Computer scientist with PhD in AI from MIT. Former tech lead at major AI company. Published extensively on AI safety and ethics.",
        expertise: "Machine Learning, AI Safety, Natural Language Processing, Computer Vision, Ethics in AI",
        memories: "Witnessed GPT-3's first outputs at OpenAI in 2020. Developed fairness framework adopted by major tech companies.",
        knowledge: "Expert understanding of machine learning including deep neural networks, transformers, and reinforcement learning.",
        avatar: "https://v3.fal.media/files/penguin/pESE1pNcl0pyoMBUKWKnW.png"
      },
      {
        id: 502,
        name: "Alex Thompson",
        archetype: "optimist",
        archetypeDisplay: "The Optimist",
        title: "Full Stack Developer",
        goal: "To create innovative software solutions that improve people's daily lives and democratize access to technology.",
        background: "Self-taught programmer turned tech lead. Built multiple successful web applications serving millions of users. Open source contributor.",
        expertise: "Full Stack Development, Web Applications, React, Node.js, Database Design, Cloud Architecture",
        memories: "Created viral productivity app with 10M+ downloads. Led development of real-time collaboration platform used by Fortune 500 companies.",
        knowledge: "https://developer.mozilla.org/, https://react.dev/, https://nodejs.org/",
        avatar: "https://v3.fal.media/files/lion/K2mX7qVzQ8aL4wWqJ5nR9.png"
      }
    ]
  },
  aiMachineLearning: {
    name: "AI & Machine Learning",
    icon: "🤖",
    agents: [
      {
        id: 521,
        name: "Dr. Chen Li",
        archetype: "researcher",
        archetypeDisplay: "The Researcher",
        title: "Machine Learning Research Scientist",
        goal: "To advance the frontiers of artificial intelligence through groundbreaking research and applications.",
        background: "PhD in Computer Science from Stanford. Research scientist at top AI lab. Expert in deep learning and neural architecture search.",
        expertise: "Deep Learning, Neural Networks, Computer Vision, Natural Language Processing, Reinforcement Learning",
        memories: "Developed breakthrough architecture that achieved state-of-the-art results on ImageNet. Published seminal paper on attention mechanisms.",
        knowledge: "https://arxiv.org/, https://papers.nips.cc/, https://icml.cc/",
        avatar: "https://v3.fal.media/files/dolphin/M8kT2qVzP7aL9wWqJ6nS0.png"
      }
    ]
  }
};

// Define sectors with categories
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

// Quick Team Builders
const quickTeams = {
  research: {
    name: "Research Team",
    icon: "🔬",
    description: "Scientist, Optimist, Leader",
    agents: [
      healthcareCategories.medical.agents[0], // Dr. Sarah Chen - Scientist
      financeCategories.investmentBanking.agents[1], // Alexandra Chen - Optimist
      healthcareCategories.medical.agents[1] // Dr. Marcus Rodriguez - Leader
    ]
  },
  business: {
    name: "Business Team", 
    icon: "💼",
    description: "Strategist, Consultant, Innovator",
    agents: [
      technologyCategories.softwareEngineering.agents[0], // Dr. Aisha Muhammad - Tech leader
      financeCategories.investmentBanking.agents[0], // Marcus Goldman - Business strategist
      technologyCategories.aiMachineLearning.agents[0] // Dr. Chen Li - Innovation researcher
    ]
  },
  crypto: {
    name: "Crypto Team",
    icon: "₿", 
    description: "Blockchain Expert, DeFi Specialist, Crypto Analyst",
    agents: [
      financeCategories.investmentBanking.agents[0], // Marcus Goldman - Finance expert
      technologyCategories.softwareEngineering.agents[1], // Alex Thompson - Tech expert
      financeCategories.riskManagement.agents[0] // Dr. Sarah Mitchell - Risk expert
    ]
  }
};

const AgentLibrary = ({ onAddAgent, onRemoveAgent }) => {
  const { token } = useAuth();
  const [selectedSector, setSelectedSector] = useState(null);
  const [selectedCategory, setSelectedCategory] = useState(null);
  const [selectedAgentDetails, setSelectedAgentDetails] = useState(null);
  const [selectedQuickTeam, setSelectedQuickTeam] = useState(null);
  const [addingAgents, setAddingAgents] = useState(new Set());
  const [addedAgents, setAddedAgents] = useState(new Set());
  const [isSectorsExpanded, setIsSectorsExpanded] = useState(true);
  const [isMyAgentsExpanded, setIsMyAgentsExpanded] = useState(false);
  const [isTeamBuildersExpanded, setIsTeamBuildersExpanded] = useState(false);
  const [savedAgents, setSavedAgents] = useState([]);
  const [loadingSavedAgents, setLoadingSavedAgents] = useState(false);

  // Fetch saved agents on mount
  useEffect(() => {
    if (token) {
      fetchSavedAgents();
    }
  }, [token]);

  const fetchSavedAgents = async () => {
    if (!token) return;
    setLoadingSavedAgents(true);
    try {
      const response = await axios.get(`${API}/saved-agents`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setSavedAgents(response.data || []);
    } catch (error) {
      console.error('Failed to fetch saved agents:', error);
      setSavedAgents([]);
    }
    setLoadingSavedAgents(false);
  };

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

  const handleQuickTeamAdd = async (teamKey) => {
    const team = quickTeams[teamKey];
    if (!team || !team.agents) return;

    for (const agent of team.agents) {
      await handleAddAgent(agent);
    }
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
            {/* MY AGENTS header with expandable button */}
            <div 
              className="flex justify-between items-center cursor-pointer hover:bg-gray-100 p-2 rounded-lg transition-colors mb-4"
              onClick={() => setIsMyAgentsExpanded(!isMyAgentsExpanded)}
            >
              <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wide">MY AGENTS</h3>
              <button
                type="button"
                className="text-gray-500 hover:text-gray-700 transition-transform duration-200"
                style={{ transform: isMyAgentsExpanded ? 'rotate(180deg)' : 'rotate(0deg)' }}
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </svg>
              </button>
            </div>
            
            {/* My Agents list - conditionally rendered */}
            {isMyAgentsExpanded && (
              <div className="space-y-2 mb-6 max-h-48 overflow-y-auto">
                {loadingSavedAgents ? (
                  <div className="text-center py-4 text-gray-500">Loading your agents...</div>
                ) : savedAgents.length === 0 ? (
                  <div className="text-center py-4 text-gray-500 text-sm">
                    No saved agents yet.<br/>
                    Create and save agents to see them here.
                  </div>
                ) : (
                  savedAgents.map((agent) => (
                    <div
                      key={agent.id}
                      className="w-full text-left p-3 rounded-lg transition-colors text-gray-700 hover:bg-gray-100 border cursor-pointer"
                    >
                      <div className="font-medium">{agent.name}</div>
                      <div className="text-xs text-gray-500 capitalize">{agent.archetype}</div>
                    </div>
                  ))
                )}
              </div>
            )}
            
            {/* QUICK TEAM BUILDERS header with expandable button */}
            <div 
              className="flex justify-between items-center cursor-pointer hover:bg-gray-100 p-2 rounded-lg transition-colors mb-4"
              onClick={() => setIsTeamBuildersExpanded(!isTeamBuildersExpanded)}
            >
              <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wide">QUICK TEAM BUILDERS</h3>
              <button
                type="button"
                className="text-gray-500 hover:text-gray-700 transition-transform duration-200"
                style={{ transform: isTeamBuildersExpanded ? 'rotate(180deg)' : 'rotate(0deg)' }}
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </svg>
              </button>
            </div>
            
            {/* Team Builders list - conditionally rendered */}
            {isTeamBuildersExpanded && (
              <div className="space-y-2 mb-6">
                {Object.entries(quickTeams).map(([key, team]) => (
                  <button
                    key={key}
                    onClick={() => {
                      setSelectedQuickTeam(key);
                      setSelectedSector(null);
                      setSelectedCategory(null);
                    }}
                    className={`w-full text-left p-3 rounded-lg transition-colors ${
                      selectedQuickTeam === key
                        ? 'bg-purple-100 text-purple-800 border-l-4 border-purple-600'
                        : 'text-gray-700 hover:bg-gray-100'
                    }`}
                  >
                    <div className="flex items-center space-x-2">
                      <span className="text-lg">{team.icon}</span>
                      <div>
                        <div className="font-medium text-sm">{team.name}</div>
                        <div className="text-xs text-gray-500">{team.description}</div>
                      </div>
                    </div>
                  </button>
                ))}
              </div>
            )}
            
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
                      setSelectedQuickTeam(null);
                    }}
                    className={`w-full text-left p-3 rounded-lg transition-colors ${
                      selectedSector === key
                        ? 'bg-purple-100 text-purple-800 border-l-4 border-purple-600'
                        : 'text-gray-700 hover:bg-gray-100'
                    }`}
                  >
                    <div className="flex items-center space-x-2">
                      <span className="text-lg">{sector.icon}</span>
                      <div>
                        <div className="font-medium text-sm">{sector.name}</div>
                        <div className="text-xs text-gray-500">
                          {Object.keys(sector.categories).length} categories
                        </div>
                      </div>
                    </div>
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
                <div className="flex items-center mb-6">
                  <button
                    onClick={() => setSelectedQuickTeam(null)}
                    className="text-purple-600 hover:text-purple-800 font-medium mr-4 flex items-center"
                  >
                    ← Back to Teams
                  </button>
                  <h3 className="text-xl font-bold text-gray-800">
                    {quickTeams[selectedQuickTeam].icon} {quickTeams[selectedQuickTeam].name}
                  </h3>
                </div>

                <div className="mb-6">
                  <button
                    onClick={() => handleQuickTeamAdd(selectedQuickTeam)}
                    className="bg-purple-600 text-white px-6 py-3 rounded-lg hover:bg-purple-700 font-medium"
                  >
                    Add Entire Team
                  </button>
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-4">
                  {quickTeams[selectedQuickTeam].agents.map((agent) => (
                    <div key={agent.id} className="bg-white border border-gray-200 rounded-lg hover:shadow-md transition-shadow">
                      <div className="p-4">
                        <div className="flex items-start space-x-3">
                          <img
                            src={agent.avatar}
                            alt={agent.name}
                            className="w-12 h-12 rounded-full object-cover"
                          />
                          <div className="flex-1">
                            <h4 className="font-semibold text-gray-800">{agent.name}</h4>
                            <p className="text-sm text-gray-600">{agent.title}</p>
                            <p className="text-xs text-purple-600 mt-1">{agent.archetypeDisplay}</p>
                          </div>
                        </div>
                        <div className="mt-3 space-y-2">
                          <button
                            onClick={() => setSelectedAgentDetails(agent)}
                            className="w-full bg-gray-100 text-gray-700 py-2 px-3 rounded text-sm hover:bg-gray-200 transition-colors"
                          >
                            View Details
                          </button>
                          <button
                            onClick={() => handleAddAgent(agent)}
                            disabled={addingAgents.has(agent.id)}
                            className={`w-full py-2 px-3 rounded text-sm font-medium transition-colors ${
                              addedAgents.has(agent.id)
                                ? 'bg-green-100 text-green-800'
                                : addingAgents.has(agent.id)
                                ? 'bg-gray-300 text-gray-500'
                                : 'bg-purple-600 text-white hover:bg-purple-700'
                            }`}
                          >
                            {addedAgents.has(agent.id) 
                              ? '✅ Added' 
                              : addingAgents.has(agent.id) 
                              ? 'Adding...' 
                              : 'Add Agent'
                            }
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
                    onClick={() => setSelectedSector(null)}
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

                {sectors[selectedSector].categories[selectedCategory].agents.length > 0 ? (
                  <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-4">
                    {sectors[selectedSector].categories[selectedCategory].agents.map((agent) => (
                      <div key={agent.id} className="bg-white border border-gray-200 rounded-lg hover:shadow-md transition-shadow">
                        <div className="p-4">
                          <div className="flex items-start space-x-3">
                            <img
                              src={agent.avatar}
                              alt={agent.name}
                              className="w-12 h-12 rounded-full object-cover"
                            />
                            <div className="flex-1">
                              <h4 className="font-semibold text-gray-800">{agent.name}</h4>
                              <p className="text-sm text-gray-600">{agent.title}</p>
                              <p className="text-xs text-purple-600 mt-1">{agent.archetypeDisplay}</p>
                            </div>
                          </div>
                          <div className="mt-3 space-y-2">
                            <button
                              onClick={() => setSelectedAgentDetails(agent)}
                              className="w-full bg-gray-100 text-gray-700 py-2 px-3 rounded text-sm hover:bg-gray-200 transition-colors"
                            >
                              View Details
                            </button>
                            <button
                              onClick={() => handleAddAgent(agent)}
                              disabled={addingAgents.has(agent.id)}
                              className={`w-full py-2 px-3 rounded text-sm font-medium transition-colors ${
                                addedAgents.has(agent.id)
                                  ? 'bg-green-100 text-green-800'
                                  : addingAgents.has(agent.id)
                                  ? 'bg-gray-300 text-gray-500'
                                  : 'bg-purple-600 text-white hover:bg-purple-700'
                              }`}
                            >
                              {addedAgents.has(agent.id) 
                                ? '✅ Added' 
                                : addingAgents.has(agent.id) 
                                ? 'Adding...' 
                                : 'Add Agent'
                              }
                            </button>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-8">
                    <div className="text-4xl mb-4">🔍</div>
                    <h4 className="text-lg font-semibold text-gray-800 mb-2">No agents found</h4>
                    <p className="text-gray-600">This category is currently empty.</p>
                  </div>
                )}
              </div>
            ) : (
              // Default Empty State
              <div className="text-center py-20">
                <div className="text-6xl mb-6">🏛️</div>
                <h3 className="text-2xl font-bold text-gray-800 mb-4">Welcome to Agent Library</h3>
                <p className="text-gray-600 max-w-lg mx-auto mb-6">
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
              <div className="flex items-start space-x-4">
                <img
                  src={selectedAgentDetails.avatar}
                  alt={selectedAgentDetails.name}
                  className="w-16 h-16 rounded-full object-cover border-2 border-white"
                />
                <div>
                  <h3 className="text-xl font-bold">{selectedAgentDetails.name}</h3>
                  <p className="text-blue-100">{selectedAgentDetails.title}</p>
                  <p className="text-blue-200 text-sm">{selectedAgentDetails.archetypeDisplay}</p>
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
                  <span className="mr-2">🏆</span>
                  Expertise
                </h4>
                <p className="text-gray-700 leading-relaxed">{selectedAgentDetails.expertise}</p>
              </div>

              <div>
                <h4 className="font-bold text-gray-800 mb-3 flex items-center">
                  <span className="mr-2">📚</span>
                  Background
                </h4>
                <p className="text-gray-700 leading-relaxed">{selectedAgentDetails.background}</p>
              </div>

              <div>
                <h4 className="font-bold text-gray-800 mb-3 flex items-center">
                  <span className="mr-2">🧠</span>
                  Key Memories & Knowledge
                </h4>
                <p className="text-gray-700 leading-relaxed mb-3">{selectedAgentDetails.memories}</p>
                <p className="text-sm text-blue-600 break-words">{selectedAgentDetails.knowledge}</p>
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