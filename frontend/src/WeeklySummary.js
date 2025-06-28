import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import axios from 'axios';
import { useAuth } from './AuthContext';

const API = process.env.REACT_APP_BACKEND_URL ? `${process.env.REACT_APP_BACKEND_URL}/api` : 'http://localhost:8001/api';

// Weekly Summary Component
const WeeklySummary = ({ isOpen, onClose }) => {
  const [weeklyData, setWeeklyData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [selectedWeek, setSelectedWeek] = useState('current');
  const [generating, setGenerating] = useState(false);
  const { user, token } = useAuth();

  useEffect(() => {
    if (isOpen) {
      fetchWeeklySummary();
    }
  }, [isOpen, selectedWeek]);

  const fetchWeeklySummary = async () => {
    if (!token) return;
    
    setLoading(true);
    try {
      const response = await axios.get(`${API}/analytics/weekly-summary?week=${selectedWeek}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (response.data) {
        setWeeklyData(response.data);
      }
    } catch (error) {
      console.error('Failed to fetch weekly summary:', error);
    }
    setLoading(false);
  };

  const generateWeeklyReport = async () => {
    if (!token) return;
    
    setGenerating(true);
    try {
      const response = await axios.post(`${API}/simulation/auto-weekly-report`, {}, {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (response.data?.success) {
        await fetchWeeklySummary();
        alert('Weekly report generated successfully!');
      }
    } catch (error) {
      console.error('Failed to generate weekly report:', error);
      alert('Failed to generate weekly report. Please try again.');
    }
    setGenerating(false);
  };

  const formatDate = (dateString) => {
    try {
      return new Date(dateString).toLocaleDateString('en-US', { 
        year: 'numeric', 
        month: 'long', 
        day: 'numeric' 
      });
    } catch (error) {
      return dateString;
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
          <div className="bg-gradient-to-r from-indigo-600 to-purple-600 text-white p-6">
            <div className="flex justify-between items-center">
              <div>
                <h2 className="text-2xl font-bold">📅 Weekly Summary</h2>
                <p className="text-white/80 mt-1">AI-powered insights and analytics from your simulations</p>
              </div>
              <div className="flex items-center space-x-4">
                <select
                  value={selectedWeek}
                  onChange={(e) => setSelectedWeek(e.target.value)}
                  className="px-3 py-2 bg-white/10 border border-white/20 rounded-lg text-white"
                >
                  <option value="current" className="bg-gray-800">This Week</option>
                  <option value="last" className="bg-gray-800">Last Week</option>
                  <option value="two_weeks" className="bg-gray-800">2 Weeks Ago</option>
                  <option value="month" className="bg-gray-800">This Month</option>
                </select>
                <button
                  onClick={generateWeeklyReport}
                  disabled={generating}
                  className="px-4 py-2 bg-white/20 hover:bg-white/30 text-white rounded-lg transition-all duration-200 disabled:opacity-50"
                >
                  {generating ? '⏳ Generating...' : '🔄 Generate Report'}
                </button>
                <button
                  onClick={onClose}
                  className="text-white/70 hover:text-white text-2xl p-2 hover:bg-white/10 rounded-lg transition-colors"
                >
                  ✕
                </button>
              </div>
            </div>
          </div>

          {/* Content */}
          <div className="p-6 overflow-y-auto max-h-[calc(90vh-120px)]">
            {loading ? (
              <div className="text-center py-12">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto mb-4"></div>
                <p className="text-gray-600">Loading weekly summary...</p>
              </div>
            ) : !weeklyData ? (
              <div className="text-center py-12">
                <div className="text-6xl mb-4">📊</div>
                <h3 className="text-xl font-semibold text-gray-800 mb-2">No Weekly Data Available</h3>
                <p className="text-gray-600 mb-6">Generate a weekly report to see comprehensive insights</p>
                <button
                  onClick={generateWeeklyReport}
                  disabled={generating}
                  className="px-6 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-all duration-200 disabled:opacity-50"
                >
                  {generating ? 'Generating...' : 'Generate Weekly Report'}
                </button>
              </div>
            ) : (
              <div className="space-y-6">
                {/* Week Overview */}
                <div className="bg-gradient-to-r from-indigo-50 to-purple-50 rounded-lg p-6">
                  <div className="flex justify-between items-center mb-4">
                    <div>
                      <h3 className="text-xl font-bold text-gray-800">
                        Week of {formatDate(weeklyData.week_start)} - {formatDate(weeklyData.week_end)}
                      </h3>
                      <p className="text-gray-600">Generated: {formatDate(weeklyData.generated_at)}</p>
                    </div>
                    <div className="text-right">
                      <div className="text-2xl font-bold text-indigo-600">{weeklyData.total_conversations || 0}</div>
                      <div className="text-sm text-gray-600">Total Conversations</div>
                    </div>
                  </div>
                </div>

                {/* Key Metrics */}
                <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                  <div className="bg-blue-50 rounded-lg p-4 text-center">
                    <div className="text-2xl font-bold text-blue-600">{weeklyData.metrics?.agents_used || 0}</div>
                    <div className="text-sm text-blue-600">Agents Used</div>
                  </div>
                  <div className="bg-green-50 rounded-lg p-4 text-center">
                    <div className="text-2xl font-bold text-green-600">{weeklyData.metrics?.documents_generated || 0}</div>
                    <div className="text-sm text-green-600">Documents Generated</div>
                  </div>
                  <div className="bg-orange-50 rounded-lg p-4 text-center">
                    <div className="text-2xl font-bold text-orange-600">{weeklyData.metrics?.simulation_hours || 0}h</div>
                    <div className="text-sm text-orange-600">Simulation Time</div>
                  </div>
                  <div className="bg-purple-50 rounded-lg p-4 text-center">
                    <div className="text-2xl font-bold text-purple-600">{weeklyData.metrics?.scenarios_explored || 0}</div>
                    <div className="text-sm text-purple-600">Scenarios Explored</div>
                  </div>
                </div>

                {/* Executive Summary */}
                {weeklyData.summary && (
                  <div className="bg-white border border-gray-200 rounded-lg p-6">
                    <h4 className="text-lg font-semibold text-gray-800 mb-3">📋 Executive Summary</h4>
                    <div className="prose max-w-none">
                      <div className="text-gray-700 whitespace-pre-wrap leading-relaxed">
                        {weeklyData.summary}
                      </div>
                    </div>
                  </div>
                )}

                {/* Key Insights */}
                {weeklyData.key_insights && weeklyData.key_insights.length > 0 && (
                  <div className="bg-white border border-gray-200 rounded-lg p-6">
                    <h4 className="text-lg font-semibold text-gray-800 mb-4">💡 Key Insights</h4>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      {weeklyData.key_insights.map((insight, index) => (
                        <div key={index} className="bg-yellow-50 border-l-4 border-yellow-400 p-4 rounded-r-lg">
                          <div className="text-gray-800">{insight}</div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Top Performing Agents */}
                {weeklyData.top_agents && weeklyData.top_agents.length > 0 && (
                  <div className="bg-white border border-gray-200 rounded-lg p-6">
                    <h4 className="text-lg font-semibold text-gray-800 mb-4">🏆 Top Performing Agents</h4>
                    <div className="space-y-3">
                      {weeklyData.top_agents.slice(0, 5).map((agent, index) => (
                        <div key={index} className="flex items-center space-x-4 p-3 bg-gray-50 rounded-lg">
                          <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold ${
                            index === 0 ? 'bg-yellow-400 text-yellow-900' : 
                            index === 1 ? 'bg-gray-300 text-gray-700' : 
                            index === 2 ? 'bg-orange-400 text-orange-900' : 'bg-blue-100 text-blue-800'
                          }`}>
                            {index < 3 ? ['🥇', '🥈', '🥉'][index] : index + 1}
                          </div>
                          <div className="flex-1">
                            <div className="font-semibold text-gray-800">{agent.name}</div>
                            <div className="text-sm text-gray-600">{agent.conversations} conversations</div>
                          </div>
                          <div className="text-right">
                            <div className="font-semibold text-gray-800">{agent.performance_score?.toFixed(1) || 'N/A'}</div>
                            <div className="text-xs text-gray-500">Performance</div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Activity Timeline */}
                {weeklyData.daily_activity && weeklyData.daily_activity.length > 0 && (
                  <div className="bg-white border border-gray-200 rounded-lg p-6">
                    <h4 className="text-lg font-semibold text-gray-800 mb-4">📈 Daily Activity</h4>
                    <div className="flex items-end space-x-2 h-32">
                      {weeklyData.daily_activity.map((day, index) => (
                        <div key={index} className="flex-1 flex flex-col items-center">
                          <div 
                            className="w-full bg-gradient-to-t from-indigo-600 to-purple-600 rounded-t"
                            style={{ 
                              height: `${Math.max((day.conversations / Math.max(...weeklyData.daily_activity.map(d => d.conversations))) * 100, 5)}%` 
                            }}
                            title={`${day.conversations} conversations`}
                          ></div>
                          <div className="text-xs text-gray-600 mt-2">
                            {new Date(day.date).toLocaleDateString('en-US', { weekday: 'short' })}
                          </div>
                          <div className="text-xs text-gray-500">{day.conversations}</div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Recommendations */}
                {weeklyData.recommendations && weeklyData.recommendations.length > 0 && (
                  <div className="bg-white border border-gray-200 rounded-lg p-6">
                    <h4 className="text-lg font-semibold text-gray-800 mb-4">🎯 Recommendations</h4>
                    <div className="space-y-3">
                      {weeklyData.recommendations.map((rec, index) => (
                        <div key={index} className="flex items-start space-x-3 p-3 bg-blue-50 rounded-lg">
                          <div className="w-6 h-6 bg-blue-600 rounded-full flex items-center justify-center text-white text-sm font-bold">
                            {index + 1}
                          </div>
                          <div className="flex-1 text-gray-800">{rec}</div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Export Actions */}
                <div className="bg-gray-50 rounded-lg p-4">
                  <div className="flex justify-between items-center">
                    <div>
                      <h5 className="font-semibold text-gray-800">Export Report</h5>
                      <p className="text-sm text-gray-600">Save this weekly summary for your records</p>
                    </div>
                    <div className="flex space-x-3">
                      <button
                        onClick={() => {
                          const content = JSON.stringify(weeklyData, null, 2);
                          const blob = new Blob([content], { type: 'application/json' });
                          const url = URL.createObjectURL(blob);
                          const a = document.createElement('a');
                          a.href = url;
                          a.download = `weekly-summary-${weeklyData.week_start}.json`;
                          a.click();
                          URL.revokeObjectURL(url);
                        }}
                        className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-all duration-200"
                      >
                        📄 JSON
                      </button>
                      <button
                        onClick={() => {
                          const printContent = `
Weekly Summary: ${formatDate(weeklyData.week_start)} - ${formatDate(weeklyData.week_end)}

Executive Summary:
${weeklyData.summary || 'No summary available'}

Key Metrics:
- Total Conversations: ${weeklyData.total_conversations || 0}
- Agents Used: ${weeklyData.metrics?.agents_used || 0}
- Documents Generated: ${weeklyData.metrics?.documents_generated || 0}
- Simulation Hours: ${weeklyData.metrics?.simulation_hours || 0}

Key Insights:
${weeklyData.key_insights?.map((insight, i) => `${i + 1}. ${insight}`).join('\n') || 'No insights available'}
                          `;
                          const blob = new Blob([printContent], { type: 'text/plain' });
                          const url = URL.createObjectURL(blob);
                          const a = document.createElement('a');
                          a.href = url;
                          a.download = `weekly-summary-${weeklyData.week_start}.txt`;
                          a.click();
                          URL.revokeObjectURL(url);
                        }}
                        className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-all duration-200"
                      >
                        📝 Text
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
};

export default WeeklySummary;