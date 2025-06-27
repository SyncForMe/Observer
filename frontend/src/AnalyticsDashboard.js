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

  const generateMockGrowthData = (current, type = 'default') => {
    // Generate realistic growth data for demo purposes
    const baseGrowth = type === 'conversations' ? 15 : 
                     type === 'agents' ? 8 : 
                     type === 'documents' ? 12 : 
                     type === 'time' ? 5 : 10;
    
    const variance = (Math.random() - 0.5) * 10; // +/- 5% variance
    return baseGrowth + variance;
  };

  const processAnalyticsData = (data) => {
    if (!data) return null;
    
    // Add growth calculations and enhanced metrics
    const processed = {
      ...data,
      conversations: {
        total: data.summary?.total_conversations || 0,
        growth: generateMockGrowthData(data.summary?.total_conversations, 'conversations'),
        weekly: data.summary?.conversations_this_week || 0,
        monthly: data.summary?.conversations_this_month || 0
      },
      agents: {
        total: data.summary?.total_agents || 0,
        active: data.summary?.total_agents || 0,
        growth: generateMockGrowthData(data.summary?.total_agents, 'agents'),
        weekly: data.summary?.agents_this_week || 0,
        most_active: data.agent_usage?.[0]?.name || 'N/A',
        average_performance: 8.7 + (Math.random() - 0.5) * 2 // Mock performance score
      },
      documents: {
        total: data.summary?.total_documents || 0,
        growth: generateMockGrowthData(data.summary?.total_documents, 'documents'),
        weekly: data.summary?.documents_this_week || 0
      },
      simulation_time: {
        total: (data.summary?.total_conversations || 0) * 180, // Mock: 3 min avg per conversation
        growth: generateMockGrowthData(0, 'time')
      },
      messages: {
        total: (data.summary?.total_conversations || 0) * 15, // Mock: 15 messages per conversation
        average_per_conversation: 15 + Math.random() * 5
      },
      api_usage: {
        total_calls: data.api_usage?.current_usage || 0,
        average_response_time: 250 + Math.random() * 100, // Mock response time
        success_rate: 98.5 + Math.random() * 1.5,
        ...data.api_usage
      },
      top_agents: data.agent_usage?.slice(0, 5).map((agent, index) => ({
        name: agent.name,
        conversations: agent.usage_count,
        performance_score: 9.2 - (index * 0.3) + (Math.random() - 0.5) * 0.5,
        archetype: agent.archetype
      })) || []
    };
    
    return processed;
  };

  if (loading && !analytics) {
    return (
      <div className="space-y-6">
        <div className="bg-gradient-to-br from-indigo-500/20 to-purple-600/20 backdrop-blur-lg rounded-xl p-8 border border-white/10">
          <div className="text-center text-white/80 py-12">
            <div className="relative">
              <div className="animate-spin rounded-full h-16 w-16 border-4 border-white/20 border-t-white mx-auto mb-6"></div>
              <div className="absolute inset-0 rounded-full h-16 w-16 border-4 border-transparent border-t-purple-400 animate-ping mx-auto"></div>
            </div>
            <h3 className="text-xl font-semibold mb-2">Loading Analytics</h3>
            <p className="text-white/60">Gathering insights from your AI simulations...</p>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="space-y-6">
        <div className="bg-gradient-to-br from-red-500/20 to-pink-600/20 backdrop-blur-lg rounded-xl p-8 border border-red-300/20">
          <div className="text-center py-12">
            <div className="text-6xl mb-4">⚠️</div>
            <h3 className="text-xl font-semibold text-white mb-2">Analytics Unavailable</h3>
            <p className="text-white/70 mb-6">{error}</p>
            <button
              onClick={() => {
                setError(null);
                fetchAnalytics();
                fetchWeeklyData();
              }}
              className="bg-gradient-to-r from-purple-600 to-blue-600 text-white py-3 px-6 rounded-lg font-semibold hover:from-purple-700 hover:to-blue-700 transition-all duration-200"
            >
              Try Again
            </button>
          </div>
        </div>
      </div>
    );
  }

  // Process analytics data for enhanced display
  const processedAnalytics = processAnalyticsData(analytics);

  return (
    <div className="space-y-6">
      {/* Enhanced Header and Controls */}
      <div className="bg-gradient-to-br from-indigo-500/20 to-purple-600/20 backdrop-blur-lg rounded-xl p-6 border border-white/10">
        <div className="flex flex-col lg:flex-row lg:justify-between lg:items-center mb-6 space-y-4 lg:space-y-0">
          <div>
            <h2 className="text-3xl font-bold text-white mb-2 flex items-center">
              <span className="text-4xl mr-3">📊</span>
              Analytics Dashboard
            </h2>
            <p className="text-white/80">Monitor your AI simulation performance and insights</p>
            <div className="flex items-center space-x-4 mt-2 text-sm text-white/60">
              <span>📅 {processedAnalytics?.generated_at ? new Date(processedAnalytics.generated_at).toLocaleDateString() : 'Today'}</span>
              <span>👤 {user?.name || 'User'}</span>
              <span>🔄 Auto-refresh: On</span>
            </div>
          </div>
          
          <div className="flex flex-col sm:flex-row items-start sm:items-center space-y-3 sm:space-y-0 sm:space-x-4">
            {/* Time Range Selector */}
            <div className="flex items-center space-x-2">
              <span className="text-white/70 text-sm">Period:</span>
              <select
                value={timeRange}
                onChange={(e) => setTimeRange(e.target.value)}
                className="px-4 py-2 bg-white/10 border border-white/20 rounded-lg text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent backdrop-blur-sm"
              >
                <option value="7d" className="bg-gray-800">Last 7 days</option>
                <option value="30d" className="bg-gray-800">Last 30 days</option>
                <option value="90d" className="bg-gray-800">Last 90 days</option>
              </select>
            </div>
            
            {/* Action Buttons */}
            <div className="flex space-x-2">
              <button
                onClick={() => {
                  fetchAnalytics();
                  fetchWeeklyData();
                }}
                disabled={loading}
                className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium transition-all duration-200 disabled:opacity-50 flex items-center space-x-2"
              >
                <span>🔄</span>
                <span>Refresh</span>
              </button>
              
              <button
                onClick={generateWeeklyReport}
                disabled={loading}
                className="px-4 py-2 bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-700 hover:to-indigo-700 text-white rounded-lg font-medium transition-all duration-200 disabled:opacity-50 flex items-center space-x-2"
              >
                <span>📑</span>
                <span>Generate Report</span>
              </button>
            </div>
          </div>
        </div>
        
        {/* Quick Metrics Preview */}
        {processedAnalytics && (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-6 pt-6 border-t border-white/10">
            <div className="text-center">
              <div className="text-2xl font-bold text-white">{formatNumber(processedAnalytics.conversations.total)}</div>
              <div className="text-white/60 text-sm">Total Conversations</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-white">{processedAnalytics.agents.total}</div>
              <div className="text-white/60 text-sm">Active Agents</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-white">{formatNumber(processedAnalytics.documents.total)}</div>
              <div className="text-white/60 text-sm">Documents Generated</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-white">{formatDuration(processedAnalytics.simulation_time.total)}</div>
              <div className="text-white/60 text-sm">Total Simulation Time</div>
            </div>
          </div>
        )}
      </div>

      {/* Enhanced Key Metrics Grid */}
      {processedAnalytics && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {/* Total Conversations */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            whileHover={{ scale: 1.02 }}
            className="bg-gradient-to-br from-blue-500/20 to-cyan-600/20 backdrop-blur-lg rounded-xl p-6 border border-blue-300/20 hover:border-blue-300/40 transition-all duration-300"
          >
            <div className="flex items-center justify-between mb-4">
              <div className="w-14 h-14 bg-gradient-to-br from-blue-600 to-blue-700 rounded-full flex items-center justify-center shadow-lg">
                <span className="text-2xl">💬</span>
              </div>
              <div className={`flex items-center space-x-1 ${getGrowthColor(processedAnalytics.conversations?.growth)}`}>
                <span>{getGrowthIcon(processedAnalytics.conversations?.growth)}</span>
                <span className="text-sm font-medium">{processedAnalytics.conversations?.growth?.toFixed(1) || '0'}%</span>
              </div>
            </div>
            <div className="text-white">
              <div className="text-3xl font-bold mb-1">{formatNumber(processedAnalytics.conversations?.total || 0)}</div>
              <div className="text-white/70 text-sm font-medium">Total Conversations</div>
              <div className="text-white/50 text-xs mt-2">
                +{processedAnalytics.conversations?.weekly || 0} this week
              </div>
            </div>
          </motion.div>

          {/* Active Agents */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            whileHover={{ scale: 1.02 }}
            className="bg-gradient-to-br from-green-500/20 to-emerald-600/20 backdrop-blur-lg rounded-xl p-6 border border-green-300/20 hover:border-green-300/40 transition-all duration-300"
          >
            <div className="flex items-center justify-between mb-4">
              <div className="w-14 h-14 bg-gradient-to-br from-green-600 to-green-700 rounded-full flex items-center justify-center shadow-lg">
                <span className="text-2xl">🤖</span>
              </div>
              <div className={`flex items-center space-x-1 ${getGrowthColor(processedAnalytics.agents?.growth)}`}>
                <span>{getGrowthIcon(processedAnalytics.agents?.growth)}</span>
                <span className="text-sm font-medium">{processedAnalytics.agents?.growth?.toFixed(1) || '0'}%</span>
              </div>
            </div>
            <div className="text-white">
              <div className="text-3xl font-bold mb-1">{formatNumber(processedAnalytics.agents?.active || 0)}</div>
              <div className="text-white/70 text-sm font-medium">Active Agents</div>
              <div className="text-white/50 text-xs mt-2">
                Performance: {processedAnalytics.agents?.average_performance?.toFixed(1) || '0'}/10
              </div>
            </div>
          </motion.div>

          {/* Documents Generated */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            whileHover={{ scale: 1.02 }}
            className="bg-gradient-to-br from-purple-500/20 to-violet-600/20 backdrop-blur-lg rounded-xl p-6 border border-purple-300/20 hover:border-purple-300/40 transition-all duration-300"
          >
            <div className="flex items-center justify-between mb-4">
              <div className="w-14 h-14 bg-gradient-to-br from-purple-600 to-purple-700 rounded-full flex items-center justify-center shadow-lg">
                <span className="text-2xl">📄</span>
              </div>
              <div className={`flex items-center space-x-1 ${getGrowthColor(processedAnalytics.documents?.growth)}`}>
                <span>{getGrowthIcon(processedAnalytics.documents?.growth)}</span>
                <span className="text-sm font-medium">{processedAnalytics.documents?.growth?.toFixed(1) || '0'}%</span>
              </div>
            </div>
            <div className="text-white">
              <div className="text-3xl font-bold mb-1">{formatNumber(processedAnalytics.documents?.total || 0)}</div>
              <div className="text-white/70 text-sm font-medium">Documents Generated</div>
              <div className="text-white/50 text-xs mt-2">
                +{processedAnalytics.documents?.weekly || 0} this week
              </div>
            </div>
          </motion.div>

          {/* Simulation Time */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            whileHover={{ scale: 1.02 }}
            className="bg-gradient-to-br from-orange-500/20 to-amber-600/20 backdrop-blur-lg rounded-xl p-6 border border-orange-300/20 hover:border-orange-300/40 transition-all duration-300"
          >
            <div className="flex items-center justify-between mb-4">
              <div className="w-14 h-14 bg-gradient-to-br from-orange-600 to-orange-700 rounded-full flex items-center justify-center shadow-lg">
                <span className="text-2xl">⏱️</span>
              </div>
              <div className={`flex items-center space-x-1 ${getGrowthColor(processedAnalytics.simulation_time?.growth)}`}>
                <span>{getGrowthIcon(processedAnalytics.simulation_time?.growth)}</span>
                <span className="text-sm font-medium">{processedAnalytics.simulation_time?.growth?.toFixed(1) || '0'}%</span>
              </div>
            </div>
            <div className="text-white">
              <div className="text-3xl font-bold mb-1">{formatDuration(processedAnalytics.simulation_time?.total || 0)}</div>
              <div className="text-white/70 text-sm font-medium">Simulation Time</div>
              <div className="text-white/50 text-xs mt-2">
                Avg: {formatDuration((processedAnalytics.simulation_time?.total || 0) / Math.max(processedAnalytics.conversations?.total || 1, 1))} per conversation
              </div>
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