import React, { useState } from 'react';
import { useAuth } from './App';

const AgentLibrary = ({ onAddAgent, onRemoveAgent }) => {
  const [selectedAgentDetails, setSelectedAgentDetails] = useState(null);
  
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
            {/* SECTORS header */}
            <div className="flex justify-between items-center cursor-pointer hover:bg-gray-100 p-2 rounded-lg transition-colors mb-4">
              <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wide">SECTORS</h3>
              <button
                type="button"
                className="text-gray-500 hover:text-gray-700 transition-transform duration-200"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </svg>
              </button>
            </div>
            
            {/* Sectors list */}
            <div className="space-y-2">
              <button className="w-full text-left p-3 rounded-lg transition-colors text-gray-700 hover:bg-gray-100">
                <span className="text-lg mr-2">🏥</span>
                Healthcare
              </button>
              <button className="w-full text-left p-3 rounded-lg transition-colors text-gray-700 hover:bg-gray-100">
                <span className="text-lg mr-2">💰</span>
                Finance
              </button>
              <button className="w-full text-left p-3 rounded-lg transition-colors text-gray-700 hover:bg-gray-100">
                <span className="text-lg mr-2">💻</span>
                Technology
              </button>
            </div>
          </div>

          {/* Main Content */}
          <div className="flex-1 p-6 overflow-y-auto">
            {/* Default Empty State */}
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