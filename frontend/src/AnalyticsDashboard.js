import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import axios from 'axios';
import { useAuth } from './App';

const API = process.env.REACT_APP_BACKEND_URL ? `${process.env.REACT_APP_BACKEND_URL}/api` : 'http://localhost:8001/api';

// Enhanced Analytics Dashboard with Beautiful Visualizations
const AnalyticsDashboard = () => {
  const [analytics, setAnalytics] = useState(null);
  const [weeklyData, setWeeklyData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [timeRange, setTimeRange] = useState('30d');
  const [summaryPeriod, setSummaryPeriod] = useState('weekly');
  const [selectedMetric, setSelectedMetric] = useState('conversations');
  const { user, token } = useAuth();

  useEffect(() => {
    fetchAnalytics();
    fetchWeeklyData();
  }, [timeRange, summaryPeriod]);

  const fetchAnalytics = async () => {
    setLoading(true);
    setError(null);
    try {
      console.log('🔍 Fetching analytics with token:', !!token);
      const response = await axios.get(`${API}/analytics/comprehensive?period=${timeRange}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      console.log('✅ Analytics response:', response.data);
      if (response.data) {
        setAnalytics(response.data);
      }
    } catch (error) {
      console.error('❌ Failed to fetch analytics:', error);
      setError('Failed to load analytics data. Please try again.');
    }
    setLoading(false);
  };

  const fetchWeeklyData = async () => {
    try {
      console.log('🔍 Fetching weekly data with token:', !!token);
      const response = await axios.get(`${API}/analytics/weekly-summary`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      console.log('✅ Weekly data response:', response.data);
      if (response.data) {
        setWeeklyData(response.data);
      }
    } catch (error) {
      console.error('❌ Failed to fetch weekly data:', error.response?.data || error.message);
    }
  };

  const generateWeeklyReport = async () => {
    setLoading(true);
    try {
      const response = await axios.post(`${API}/simulation/auto-weekly-report`, {}, {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (response.data.success) {
        alert('Weekly report generated successfully!');
        await fetchWeeklyData();
      }
    } catch (error) {
      console.error('Failed to generate weekly report:', error);
      alert('Failed to generate weekly report. Please try again.');
    }
    setLoading(false);
  };

  const formatNumber = (num) => {
    if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M';
    if (num >= 1000) return (num / 1000).toFixed(1) + 'K';
    return num?.toString() || '0';
  };

  const formatDuration = (seconds) => {
    if (!seconds) return '0m';
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    if (hours > 0) return `${hours}h ${minutes}m`;
    return `${minutes}m`;
  };

  const getGrowthColor = (growth) => {
    if (!growth) return 'text-gray-400';
    return growth > 0 ? 'text-green-400' : 'text-red-400';
  };

  const getGrowthIcon = (growth) => {
    if (!growth) return '—';
    return growth > 0 ? '📈' : '📉';
  };

  if (loading && !analytics) {
    return (
      <div className="space-y-6">
        <div className="bg-white/10 backdrop-blur-lg rounded-xl p-6">
          <div className="text-center text-white/60 py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-white mx-auto mb-4"></div>
            <p>Loading analytics...</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header and Controls */}
      <div className="bg-white/10 backdrop-blur-lg rounded-xl p-6">
        <div className="flex justify-between items-center mb-6">
          <div>
            <h2 className="text-2xl font-bold text-white mb-2">📊 Analytics Dashboard</h2>
            <p className="text-white/80">Monitor your AI simulation performance and insights</p>
          </div>
          <div className="flex items-center space-x-4">
            <select
              value={timeRange}
              onChange={(e) => setTimeRange(e.target.value)}
              className="px-3 py-2 bg-white/10 border border-white/20 rounded-lg text-white focus:ring-2 focus:ring-blue-500"
            >
              <option value="1d" className="bg-gray-800">Last 24 hours</option>
              <option value="7d" className="bg-gray-800">Last 7 days</option>
              <option value="30d" className="bg-gray-800">Last 30 days</option>
              <option value="90d" className="bg-gray-800">Last 90 days</option>
            </select>
            <button
              onClick={generateWeeklyReport}
              disabled={loading}
              className="px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg font-semibold transition-all duration-200 disabled:opacity-50"
            >
              📑 Generate Report
            </button>
          </div>
        </div>
      </div>

      {/* Key Metrics Grid */}
      {analytics && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {/* Total Conversations */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-white/10 backdrop-blur-lg rounded-xl p-6"
          >
            <div className="flex items-center justify-between mb-4">
              <div className="w-12 h-12 bg-blue-600 rounded-full flex items-center justify-center">
                💬
              </div>
              <div className={`flex items-center space-x-1 ${getGrowthColor(analytics.conversations?.growth)}`}>
                <span>{getGrowthIcon(analytics.conversations?.growth)}</span>
                <span className="text-sm">{analytics.conversations?.growth?.toFixed(1) || '0'}%</span>
              </div>
            </div>
            <div className="text-white">
              <div className="text-2xl font-bold">{formatNumber(analytics.conversations?.total || 0)}</div>
              <div className="text-white/60 text-sm">Total Conversations</div>
            </div>
          </motion.div>

          {/* Active Agents */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="bg-white/10 backdrop-blur-lg rounded-xl p-6"
          >
            <div className="flex items-center justify-between mb-4">
              <div className="w-12 h-12 bg-green-600 rounded-full flex items-center justify-center">
                🤖
              </div>
              <div className={`flex items-center space-x-1 ${getGrowthColor(analytics.agents?.growth)}`}>
                <span>{getGrowthIcon(analytics.agents?.growth)}</span>
                <span className="text-sm">{analytics.agents?.growth?.toFixed(1) || '0'}%</span>
              </div>
            </div>
            <div className="text-white">
              <div className="text-2xl font-bold">{formatNumber(analytics.agents?.active || 0)}</div>
              <div className="text-white/60 text-sm">Active Agents</div>
            </div>
          </motion.div>

          {/* Documents Generated */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="bg-white/10 backdrop-blur-lg rounded-xl p-6"
          >
            <div className="flex items-center justify-between mb-4">
              <div className="w-12 h-12 bg-purple-600 rounded-full flex items-center justify-center">
                📄
              </div>
              <div className={`flex items-center space-x-1 ${getGrowthColor(analytics.documents?.growth)}`}>
                <span>{getGrowthIcon(analytics.documents?.growth)}</span>
                <span className="text-sm">{analytics.documents?.growth?.toFixed(1) || '0'}%</span>
              </div>
            </div>
            <div className="text-white">
              <div className="text-2xl font-bold">{formatNumber(analytics.documents?.total || 0)}</div>
              <div className="text-white/60 text-sm">Documents Generated</div>
            </div>
          </motion.div>

          {/* Simulation Time */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="bg-white/10 backdrop-blur-lg rounded-xl p-6"
          >
            <div className="flex items-center justify-between mb-4">
              <div className="w-12 h-12 bg-orange-600 rounded-full flex items-center justify-center">
                ⏱️
              </div>
              <div className={`flex items-center space-x-1 ${getGrowthColor(analytics.simulation_time?.growth)}`}>
                <span>{getGrowthIcon(analytics.simulation_time?.growth)}</span>
                <span className="text-sm">{analytics.simulation_time?.growth?.toFixed(1) || '0'}%</span>
              </div>
            </div>
            <div className="text-white">
              <div className="text-2xl font-bold">{formatDuration(analytics.simulation_time?.total || 0)}</div>
              <div className="text-white/60 text-sm">Simulation Time</div>
            </div>
          </motion.div>
        </div>
      )}

      {/* Detailed Analytics */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Activity Chart */}
        <div className="bg-white/10 backdrop-blur-lg rounded-xl p-6">
          <h3 className="text-xl font-bold text-white mb-4">📈 Activity Overview</h3>
          
          {analytics?.daily_activity ? (
            <div className="space-y-4">
              {/* Simple Bar Chart */}
              <div className="flex items-end space-x-2 h-32">
                {analytics.daily_activity.slice(-7).map((day, index) => (
                  <div key={index} className="flex-1 flex flex-col items-center">
                    <div 
                      className="w-full bg-gradient-to-t from-blue-600 to-purple-600 rounded-t"
                      style={{ 
                        height: `${Math.max((day.conversations / Math.max(...analytics.daily_activity.map(d => d.conversations))) * 100, 5)}%` 
                      }}
                    ></div>
                    <div className="text-white/60 text-xs mt-2">
                      {new Date(day.date).toLocaleDateString('en-US', { weekday: 'short' })}
                    </div>
                  </div>
                ))}
              </div>
              
              {/* Legend */}
              <div className="text-center">
                <span className="text-white/60 text-sm">Daily Conversations (Last 7 days)</span>
              </div>
            </div>
          ) : (
            <div className="text-center text-white/60 py-8">
              <div className="text-4xl mb-2">📊</div>
              <p>No activity data available</p>
            </div>
          )}
        </div>

        {/* Top Agents */}
        <div className="bg-white/10 backdrop-blur-lg rounded-xl p-6">
          <h3 className="text-xl font-bold text-white mb-4">🏆 Top Performing Agents</h3>
          
          {analytics?.top_agents ? (
            <div className="space-y-3">
              {analytics.top_agents.slice(0, 5).map((agent, index) => (
                <div key={index} className="flex items-center space-x-3 p-3 bg-white/5 rounded-lg">
                  <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm ${
                    index === 0 ? 'bg-yellow-500' : 
                    index === 1 ? 'bg-gray-400' : 
                    index === 2 ? 'bg-orange-500' : 'bg-blue-500'
                  }`}>
                    {index < 3 ? ['🥇', '🥈', '🥉'][index] : agent.name[0]}
                  </div>
                  <div className="flex-1">
                    <div className="text-white font-medium">{agent.name}</div>
                    <div className="text-white/60 text-sm">{agent.conversations} conversations</div>
                  </div>
                  <div className="text-white/80">
                    {agent.performance_score?.toFixed(1) || 'N/A'}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center text-white/60 py-8">
              <div className="text-4xl mb-2">🤖</div>
              <p>No agent data available</p>
            </div>
          )}
        </div>
      </div>

      {/* Detailed Statistics */}
      {analytics && (
        <div className="bg-white/10 backdrop-blur-lg rounded-xl p-6">
          <h3 className="text-xl font-bold text-white mb-4">📋 Detailed Statistics</h3>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {/* Conversation Stats */}
            <div className="bg-white/5 rounded-lg p-4">
              <h4 className="text-white font-semibold mb-3">💬 Conversations</h4>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-white/60">Total Messages:</span>
                  <span className="text-white">{formatNumber(analytics.messages?.total || 0)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-white/60">Avg per Conversation:</span>
                  <span className="text-white">{analytics.messages?.average_per_conversation?.toFixed(1) || '0'}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-white/60">Longest Conversation:</span>
                  <span className="text-white">{analytics.conversations?.longest_duration || '0m'}</span>
                </div>
              </div>
            </div>

            {/* Agent Performance */}
            <div className="bg-white/5 rounded-lg p-4">
              <h4 className="text-white font-semibold mb-3">🤖 Agent Performance</h4>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-white/60">Total Agents:</span>
                  <span className="text-white">{analytics.agents?.total || 0}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-white/60">Most Active:</span>
                  <span className="text-white">{analytics.agents?.most_active || 'N/A'}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-white/60">Avg Performance:</span>
                  <span className="text-white">{analytics.agents?.average_performance?.toFixed(1) || '0'}/10</span>
                </div>
              </div>
            </div>

            {/* System Performance */}
            <div className="bg-white/5 rounded-lg p-4">
              <h4 className="text-white font-semibold mb-3">⚡ System Performance</h4>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-white/60">API Calls:</span>
                  <span className="text-white">{formatNumber(analytics.api_usage?.total_calls || 0)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-white/60">Avg Response Time:</span>
                  <span className="text-white">{analytics.api_usage?.average_response_time || '0'}ms</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-white/60">Success Rate:</span>
                  <span className="text-white">{analytics.api_usage?.success_rate?.toFixed(1) || '0'}%</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Weekly Summary */}
      {weeklyData && (
        <div className="bg-white/10 backdrop-blur-lg rounded-xl p-6">
          <div className="flex justify-between items-center mb-4">
            <h3 className="text-xl font-bold text-white">📅 Weekly Summary</h3>
            <span className="text-white/60 text-sm">
              {weeklyData.week_start} - {weeklyData.week_end}
            </span>
          </div>
          
          <div className="bg-white/5 rounded-lg p-4">
            <div className="text-white/80 whitespace-pre-wrap text-sm">
              {weeklyData.summary || 'No weekly summary available. Generate a report to see insights.'}
            </div>
          </div>
          
          {weeklyData.key_insights && (
            <div className="mt-4">
              <h4 className="text-white font-semibold mb-2">💡 Key Insights</h4>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {weeklyData.key_insights.map((insight, index) => (
                  <div key={index} className="bg-white/5 rounded-lg p-3">
                    <div className="text-white/80 text-sm">{insight}</div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default AnalyticsDashboard;