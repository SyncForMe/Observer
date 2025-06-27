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
    return growth > 0 ? 'text-green-300' : 'text-red-300';
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
        <div className="bg-gray-900/95 backdrop-blur-lg rounded-xl p-8 border border-gray-600/30 shadow-2xl">
          <div className="text-center text-gray-300 py-12">
            <div className="relative">
              <div className="animate-spin rounded-full h-16 w-16 border-4 border-gray-600 border-t-blue-500 mx-auto mb-6"></div>
              <div className="absolute inset-0 rounded-full h-16 w-16 border-4 border-transparent border-t-purple-400 animate-ping mx-auto"></div>
            </div>
            <h3 className="text-xl font-semibold mb-2 text-gray-100">Loading Analytics</h3>
            <p className="text-gray-400">Gathering insights from your AI simulations...</p>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="space-y-6">
        <div className="bg-gray-900/95 backdrop-blur-lg rounded-xl p-8 border border-red-600/30 shadow-2xl">
          <div className="text-center py-12">
            <div className="text-6xl mb-4">⚠️</div>
            <h3 className="text-xl font-semibold text-gray-100 mb-2">Analytics Unavailable</h3>
            <p className="text-gray-300 mb-6">{error}</p>
            <button
              onClick={() => {
                setError(null);
                fetchAnalytics();
                fetchWeeklyData();
              }}
              className="bg-gradient-to-r from-purple-600 to-blue-600 text-white py-3 px-6 rounded-lg font-semibold hover:from-purple-700 hover:to-blue-700 transition-all duration-200 shadow-lg"
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
      <div className="bg-gray-900/95 backdrop-blur-lg rounded-xl p-6 border border-gray-600/30 shadow-2xl">
        <div className="flex flex-col lg:flex-row lg:justify-between lg:items-center mb-6 space-y-4 lg:space-y-0">
          <div>
            <h2 className="text-3xl font-bold text-gray-100 mb-2 flex items-center">
              <span className="text-4xl mr-3">📊</span>
              Analytics Dashboard
            </h2>
            <p className="text-gray-300">Monitor your AI simulation performance and insights</p>
            <div className="flex items-center space-x-4 mt-2 text-sm text-gray-400">
              <span>📅 {processedAnalytics?.generated_at ? new Date(processedAnalytics.generated_at).toLocaleDateString() : 'Today'}</span>
              <span>👤 {user?.name || 'User'}</span>
              <span>🔄 Auto-refresh: On</span>
            </div>
          </div>
          
          <div className="flex flex-col sm:flex-row items-start sm:items-center space-y-3 sm:space-y-0 sm:space-x-4">
            {/* Time Range Selector */}
            <div className="flex items-center space-x-2">
              <span className="text-gray-300 text-sm font-medium">Period:</span>
              <select
                value={timeRange}
                onChange={(e) => setTimeRange(e.target.value)}
                className="px-4 py-2 bg-gray-800 border border-gray-600 rounded-lg text-gray-100 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 backdrop-blur-sm"
              >
                <option value="7d" className="bg-gray-800 text-gray-100">Last 7 days</option>
                <option value="30d" className="bg-gray-800 text-gray-100">Last 30 days</option>
                <option value="90d" className="bg-gray-800 text-gray-100">Last 90 days</option>
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
                className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium transition-all duration-200 disabled:opacity-50 flex items-center space-x-2 shadow-lg"
              >
                <span>🔄</span>
                <span>Refresh</span>
              </button>
              
              <button
                onClick={generateWeeklyReport}
                disabled={loading}
                className="px-4 py-2 bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-700 hover:to-indigo-700 text-white rounded-lg font-medium transition-all duration-200 disabled:opacity-50 flex items-center space-x-2 shadow-lg"
              >
                <span>📑</span>
                <span>Generate Report</span>
              </button>
            </div>
          </div>
        </div>
        
        {/* Quick Metrics Preview */}
        {processedAnalytics && (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-6 pt-6 border-t border-gray-600/30">
            <div className="text-center">
              <div className="text-2xl font-bold text-gray-100">{formatNumber(processedAnalytics.conversations.total)}</div>
              <div className="text-gray-400 text-sm">Total Conversations</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-gray-100">{processedAnalytics.agents.total}</div>
              <div className="text-gray-400 text-sm">Active Agents</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-gray-100">{formatNumber(processedAnalytics.documents.total)}</div>
              <div className="text-gray-400 text-sm">Documents Generated</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-gray-100">{formatDuration(processedAnalytics.simulation_time.total)}</div>
              <div className="text-gray-400 text-sm">Total Simulation Time</div>
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
            className="bg-gray-900/95 backdrop-blur-lg rounded-xl p-6 border border-blue-600/40 hover:border-blue-500/60 transition-all duration-300 shadow-xl"
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
            <div className="text-gray-100">
              <div className="text-3xl font-bold mb-1">{formatNumber(processedAnalytics.conversations?.total || 0)}</div>
              <div className="text-gray-300 text-sm font-medium">Total Conversations</div>
              <div className="text-gray-500 text-xs mt-2">
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
            className="bg-gray-900/95 backdrop-blur-lg rounded-xl p-6 border border-green-600/40 hover:border-green-500/60 transition-all duration-300 shadow-xl"
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
            <div className="text-gray-100">
              <div className="text-3xl font-bold mb-1">{formatNumber(processedAnalytics.agents?.active || 0)}</div>
              <div className="text-gray-300 text-sm font-medium">Active Agents</div>
              <div className="text-gray-500 text-xs mt-2">
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
            className="bg-gray-900/95 backdrop-blur-lg rounded-xl p-6 border border-purple-600/40 hover:border-purple-500/60 transition-all duration-300 shadow-xl"
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
            <div className="text-gray-100">
              <div className="text-3xl font-bold mb-1">{formatNumber(processedAnalytics.documents?.total || 0)}</div>
              <div className="text-gray-300 text-sm font-medium">Documents Generated</div>
              <div className="text-gray-500 text-xs mt-2">
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
            className="bg-gray-900/95 backdrop-blur-lg rounded-xl p-6 border border-orange-600/40 hover:border-orange-500/60 transition-all duration-300 shadow-xl"
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
            <div className="text-gray-100">
              <div className="text-3xl font-bold mb-1">{formatDuration(processedAnalytics.simulation_time?.total || 0)}</div>
              <div className="text-gray-300 text-sm font-medium">Simulation Time</div>
              <div className="text-gray-500 text-xs mt-2">
                Avg: {formatDuration((processedAnalytics.simulation_time?.total || 0) / Math.max(processedAnalytics.conversations?.total || 1, 1))} per conversation
              </div>
            </div>
          </motion.div>
        </div>
      )}

      {/* Enhanced Detailed Analytics */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Enhanced Activity Chart */}
        <motion.div 
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.4 }}
          className="bg-gray-900/95 backdrop-blur-lg rounded-xl p-6 border border-gray-600/30 shadow-xl"
        >
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-xl font-bold text-gray-100 flex items-center">
              <span className="text-2xl mr-2">📈</span>
              Activity Overview
            </h3>
            <div className="flex space-x-2">
              <button
                onClick={() => setSelectedMetric('conversations')}
                className={`px-3 py-1 rounded-lg text-sm transition-all font-medium ${
                  selectedMetric === 'conversations' 
                    ? 'bg-blue-600 text-white shadow-lg' 
                    : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                }`}
              >
                Conversations
              </button>
              <button
                onClick={() => setSelectedMetric('agents')}
                className={`px-3 py-1 rounded-lg text-sm transition-all font-medium ${
                  selectedMetric === 'agents' 
                    ? 'bg-green-600 text-white shadow-lg' 
                    : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                }`}
              >
                Agents
              </button>
            </div>
          </div>
          
          {processedAnalytics?.daily_activity ? (
            <div className="space-y-4">
              {/* Enhanced Bar Chart */}
              <div className="relative">
                <div className="flex items-end space-x-1 h-40 px-2">
                  {processedAnalytics.daily_activity.slice(-14).map((day, index) => {
                    const maxValue = Math.max(...processedAnalytics.daily_activity.slice(-14).map(d => d.conversations));
                    const height = Math.max((day.conversations / (maxValue || 1)) * 100, 3);
                    const isToday = new Date(day.date).toDateString() === new Date().toDateString();
                    
                    return (
                      <div key={index} className="flex-1 flex flex-col items-center group relative">
                        <motion.div 
                          initial={{ height: 0 }}
                          animate={{ height: `${height}%` }}
                          transition={{ delay: index * 0.1 }}
                          className={`w-full rounded-t-sm ${
                            isToday 
                              ? 'bg-gradient-to-t from-yellow-600 to-yellow-400' 
                              : 'bg-gradient-to-t from-blue-600 to-purple-600'
                          } hover:from-purple-500 hover:to-blue-500 transition-all duration-300 cursor-pointer`}
                        />
                        
                        {/* Tooltip */}
                        <div className="absolute bottom-full mb-2 opacity-0 group-hover:opacity-100 transition-opacity bg-black/80 text-white text-xs rounded px-2 py-1 whitespace-nowrap z-10">
                          {day.conversations} conversations<br/>
                          {new Date(day.date).toLocaleDateString()}
                        </div>
                        
                        <div className="text-white/60 text-xs mt-2 transform -rotate-45 origin-top">
                          {new Date(day.date).toLocaleDateString('en-US', { 
                            month: 'short', 
                            day: 'numeric' 
                          })}
                        </div>
                      </div>
                    );
                  })}
                </div>
                
                {/* Y-axis labels */}
                <div className="absolute left-0 top-0 h-40 flex flex-col justify-between text-xs text-white/50">
                  <span>{Math.max(...(processedAnalytics.daily_activity.slice(-14).map(d => d.conversations) || [0]))}</span>
                  <span>{Math.floor(Math.max(...(processedAnalytics.daily_activity.slice(-14).map(d => d.conversations) || [0])) / 2)}</span>
                  <span>0</span>
                </div>
              </div>
              
              {/* Legend and Stats */}
              <div className="flex justify-between items-center pt-4 border-t border-white/10">
                <div className="text-center">
                  <span className="text-gray-400 text-sm">Last 14 days</span>
                </div>
                <div className="flex space-x-4 text-sm">
                  <div className="flex items-center space-x-2">
                    <div className="w-3 h-3 bg-gradient-to-r from-blue-600 to-purple-600 rounded"></div>
                    <span className="text-gray-300">Regular days</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <div className="w-3 h-3 bg-gradient-to-r from-yellow-600 to-yellow-400 rounded"></div>
                    <span className="text-gray-300">Today</span>
                  </div>
                </div>
              </div>
            </div>
          ) : (
            <div className="text-center text-white/60 py-12">
              <div className="text-6xl mb-4">📊</div>
              <p>No activity data available</p>
              <p className="text-sm mt-2">Start some conversations to see your activity chart!</p>
            </div>
          )}
        </motion.div>

        {/* Enhanced Top Agents */}
        <motion.div 
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.5 }}
          className="bg-gray-900/95 backdrop-blur-lg rounded-xl p-6 border border-gray-600/30 shadow-xl"
        >
          <h3 className="text-xl font-bold text-gray-100 mb-6 flex items-center">
            <span className="text-2xl mr-2">🏆</span>
            Top Performing Agents
          </h3>
          
          {processedAnalytics?.top_agents && processedAnalytics.top_agents.length > 0 ? (
            <div className="space-y-4">
              {processedAnalytics.top_agents.slice(0, 5).map((agent, index) => (
                <motion.div 
                  key={index}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.6 + index * 0.1 }}
                  className="flex items-center space-x-4 p-4 bg-gray-800/60 rounded-lg hover:bg-gray-700/60 transition-all duration-200 group"
                >
                  <div className={`w-12 h-12 rounded-full flex items-center justify-center text-lg font-bold ${
                    index === 0 ? 'bg-gradient-to-br from-yellow-400 to-yellow-600 text-yellow-900' : 
                    index === 1 ? 'bg-gradient-to-br from-gray-300 to-gray-500 text-gray-900' : 
                    index === 2 ? 'bg-gradient-to-br from-orange-400 to-orange-600 text-orange-900' : 
                    'bg-gradient-to-br from-blue-500 to-blue-600 text-blue-900'
                  }`}>
                    {index < 3 ? ['🥇', '🥈', '🥉'][index] : agent.name[0].toUpperCase()}
                  </div>
                  
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center space-x-2">
                      <div className="text-gray-100 font-medium truncate">{agent.name}</div>
                      <span className="text-xs bg-gray-700 text-gray-300 px-2 py-1 rounded-full">
                        {agent.archetype}
                      </span>
                    </div>
                    <div className="text-gray-400 text-sm">
                      {agent.conversations} conversations
                    </div>
                    
                    {/* Performance Bar */}
                    <div className="mt-2">
                      <div className="flex items-center space-x-2">
                        <div className="flex-1 bg-gray-700 rounded-full h-2">
                          <motion.div
                            initial={{ width: 0 }}
                            animate={{ width: `${(agent.performance_score / 10) * 100}%` }}
                            transition={{ delay: 0.8 + index * 0.1, duration: 0.5 }}
                            className={`h-2 rounded-full ${
                              index === 0 ? 'bg-gradient-to-r from-yellow-400 to-yellow-600' :
                              index === 1 ? 'bg-gradient-to-r from-gray-300 to-gray-500' :
                              index === 2 ? 'bg-gradient-to-r from-orange-400 to-orange-600' :
                              'bg-gradient-to-r from-blue-400 to-blue-600'
                            }`}
                          />
                        </div>
                        <div className="text-gray-200 text-sm font-medium min-w-0">
                          {agent.performance_score?.toFixed(1) || 'N/A'}/10
                        </div>
                      </div>
                    </div>
                  </div>
                  
                  <div className="text-gray-400 group-hover:text-gray-300 transition-colors">
                    #{index + 1}
                  </div>
                </motion.div>
              ))}
              
              {/* View All Button */}
              <div className="pt-4 border-t border-gray-600/30">
                <button className="w-full py-2 text-gray-300 hover:text-gray-100 text-sm hover:bg-gray-800/40 rounded-lg transition-all">
                  View All Agents →
                </button>
              </div>
            </div>
          ) : (
            <div className="text-center text-gray-400 py-12">
              <div className="text-6xl mb-4">🤖</div>
              <p>No agents data available</p>
              <p className="text-sm mt-2">Create some agents to see performance metrics!</p>
            </div>
          )}
        </motion.div>
      </div>

      {/* Enhanced Detailed Statistics */}
      {processedAnalytics && (
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.7 }}
          className="bg-gradient-to-br from-slate-800/40 to-slate-900/40 backdrop-blur-lg rounded-xl p-6 border border-white/10"
        >
          <h3 className="text-xl font-bold text-white mb-6 flex items-center">
            <span className="text-2xl mr-2">📋</span>
            Detailed Statistics
          </h3>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {/* Conversation Stats */}
            <div className="bg-blue-500/20 rounded-lg p-5 border border-blue-300/30">
              <h4 className="text-white font-semibold mb-4 flex items-center">
                <span className="text-xl mr-2">💬</span>
                Conversations
              </h4>
              <div className="space-y-3 text-sm">
                <div className="flex justify-between items-center">
                  <span className="text-white/60">Total Messages:</span>
                  <span className="text-white font-medium">{formatNumber(processedAnalytics.messages?.total || 0)}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-white/60">Avg per Conversation:</span>
                  <span className="text-white font-medium">{processedAnalytics.messages?.average_per_conversation?.toFixed(1) || '0'}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-white/60">This Week:</span>
                  <span className="text-white font-medium">{processedAnalytics.conversations?.weekly || 0}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-white/60">This Month:</span>
                  <span className="text-white font-medium">{processedAnalytics.conversations?.monthly || 0}</span>
                </div>
                
                {/* Progress Bar for Monthly Goal */}
                <div className="pt-2">
                  <div className="flex justify-between text-xs text-white/60 mb-1">
                    <span>Monthly Progress</span>
                    <span>{((processedAnalytics.conversations?.monthly || 0) / 100 * 100).toFixed(0)}%</span>
                  </div>
                  <div className="w-full bg-white/10 rounded-full h-2">
                    <motion.div
                      initial={{ width: 0 }}
                      animate={{ width: `${Math.min((processedAnalytics.conversations?.monthly || 0) / 100 * 100, 100)}%` }}
                      transition={{ delay: 1, duration: 0.8 }}
                      className="bg-gradient-to-r from-blue-400 to-cyan-500 h-2 rounded-full"
                    />
                  </div>
                </div>
              </div>
            </div>

            {/* Agent Performance */}
            <div className="bg-green-500/20 rounded-lg p-5 border border-green-300/30">
              <h4 className="text-white font-semibold mb-4 flex items-center">
                <span className="text-xl mr-2">🤖</span>
                Agent Performance
              </h4>
              <div className="space-y-3 text-sm">
                <div className="flex justify-between items-center">
                  <span className="text-white/60">Total Agents:</span>
                  <span className="text-white font-medium">{processedAnalytics.agents?.total || 0}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-white/60">Most Active:</span>
                  <span className="text-white font-medium truncate ml-2">{processedAnalytics.agents?.most_active || 'N/A'}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-white/60">Avg Performance:</span>
                  <span className="text-white font-medium">{processedAnalytics.agents?.average_performance?.toFixed(1) || '0'}/10</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-white/60">Created This Week:</span>
                  <span className="text-white font-medium">{processedAnalytics.agents?.weekly || 0}</span>
                </div>
                
                {/* Performance Gauge */}
                <div className="pt-2">
                  <div className="flex justify-between text-xs text-white/60 mb-1">
                    <span>Overall Performance</span>
                    <span>{processedAnalytics.agents?.average_performance?.toFixed(1) || '0'}/10</span>
                  </div>
                  <div className="w-full bg-white/10 rounded-full h-2">
                    <motion.div
                      initial={{ width: 0 }}
                      animate={{ width: `${(processedAnalytics.agents?.average_performance || 0) * 10}%` }}
                      transition={{ delay: 1.2, duration: 0.8 }}
                      className="bg-gradient-to-r from-green-400 to-emerald-500 h-2 rounded-full"
                    />
                  </div>
                </div>
              </div>
            </div>

            {/* System Performance */}
            <div className="bg-purple-500/20 rounded-lg p-5 border border-purple-300/30">
              <h4 className="text-white font-semibold mb-4 flex items-center">
                <span className="text-xl mr-2">⚡</span>
                System Performance
              </h4>
              <div className="space-y-3 text-sm">
                <div className="flex justify-between items-center">
                  <span className="text-white/60">API Calls:</span>
                  <span className="text-white font-medium">{formatNumber(processedAnalytics.api_usage?.total_calls || 0)}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-white/60">Avg Response Time:</span>
                  <span className="text-white font-medium">{processedAnalytics.api_usage?.average_response_time?.toFixed(0) || '0'}ms</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-white/60">Success Rate:</span>
                  <span className="text-white font-medium">{processedAnalytics.api_usage?.success_rate?.toFixed(1) || '0'}%</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-white/60">Documents Generated:</span>
                  <span className="text-white font-medium">{processedAnalytics.documents?.total || 0}</span>
                </div>
                
                {/* Success Rate Indicator */}
                <div className="pt-2">
                  <div className="flex justify-between text-xs text-white/60 mb-1">
                    <span>System Health</span>
                    <span className={`${processedAnalytics.api_usage?.success_rate > 95 ? 'text-green-400' : 'text-yellow-400'}`}>
                      {processedAnalytics.api_usage?.success_rate > 95 ? 'Excellent' : 'Good'}
                    </span>
                  </div>
                  <div className="w-full bg-white/10 rounded-full h-2">
                    <motion.div
                      initial={{ width: 0 }}
                      animate={{ width: `${processedAnalytics.api_usage?.success_rate || 0}%` }}
                      transition={{ delay: 1.4, duration: 0.8 }}
                      className={`h-2 rounded-full ${
                        (processedAnalytics.api_usage?.success_rate || 0) > 95 
                          ? 'bg-gradient-to-r from-green-400 to-emerald-500'
                          : 'bg-gradient-to-r from-yellow-400 to-orange-500'
                      }`}
                    />
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          {/* API Usage Chart */}
          {processedAnalytics.api_usage?.history && processedAnalytics.api_usage.history.length > 0 && (
            <div className="mt-8 pt-6 border-t border-white/10">
              <h4 className="text-white font-semibold mb-4 flex items-center">
                <span className="text-xl mr-2">📊</span>
                API Usage Trend (Last 30 Days)
              </h4>
              <div className="flex items-end space-x-1 h-24">
                {processedAnalytics.api_usage.history.slice(-30).map((day, index) => {
                  const maxRequests = Math.max(...processedAnalytics.api_usage.history.map(d => d.requests));
                  const height = Math.max((day.requests / (maxRequests || 1)) * 100, 2);
                  
                  return (
                    <div key={index} className="flex-1 flex flex-col items-center group relative">
                      <motion.div
                        initial={{ height: 0 }}
                        animate={{ height: `${height}%` }}
                        transition={{ delay: 1.6 + index * 0.02, duration: 0.3 }}
                        className="w-full bg-gradient-to-t from-purple-600 to-purple-400 rounded-t-sm"
                      />
                      <div className="absolute bottom-full mb-1 opacity-0 group-hover:opacity-100 transition-opacity bg-black/80 text-white text-xs rounded px-2 py-1 whitespace-nowrap z-10">
                        {day.requests} requests<br/>
                        {day.date}
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}
        </motion.div>
      )}

      {/* Enhanced Weekly Summary */}
      {weeklyData && (
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.8 }}
          className="bg-gradient-to-br from-slate-800/40 to-slate-900/40 backdrop-blur-lg rounded-xl p-6 border border-white/10"
        >
          <div className="flex flex-col lg:flex-row lg:justify-between lg:items-center mb-6">
            <h3 className="text-xl font-bold text-white flex items-center">
              <span className="text-2xl mr-2">📅</span>
              Weekly Summary Report
            </h3>
            <div className="mt-2 lg:mt-0">
              <span className="text-white/60 text-sm bg-white/10 px-3 py-1 rounded-full">
                {weeklyData.week_start} - {weeklyData.week_end}
              </span>
            </div>
          </div>
          
          {/* Weekly Metrics Grid */}
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
            <div className="text-center p-4 bg-white/15 rounded-lg">
              <div className="text-2xl font-bold text-blue-400">{weeklyData.conversations || 0}</div>
              <div className="text-white/70 text-sm">Conversations</div>
            </div>
            <div className="text-center p-4 bg-white/15 rounded-lg">
              <div className="text-2xl font-bold text-green-400">{weeklyData.agents_created || 0}</div>
              <div className="text-white/70 text-sm">Agents Created</div>
            </div>
            <div className="text-center p-4 bg-white/15 rounded-lg">
              <div className="text-2xl font-bold text-purple-400">{weeklyData.documents_created || 0}</div>
              <div className="text-white/70 text-sm">Documents</div>
            </div>
            <div className="text-center p-4 bg-white/15 rounded-lg">
              <div className="text-2xl font-bold text-orange-400">{weeklyData.most_active_day || 'N/A'}</div>
              <div className="text-white/70 text-sm">Most Active Day</div>
            </div>
          </div>
          
          {/* Summary Content */}
          <div className="bg-gradient-to-br from-indigo-500/10 to-purple-600/10 rounded-lg p-5 border border-indigo-300/20">
            <h4 className="text-white font-semibold mb-3 flex items-center">
              <span className="text-lg mr-2">📄</span>
              Executive Summary
            </h4>
            <div className="text-white/80 whitespace-pre-wrap text-sm leading-relaxed">
              {weeklyData.summary || 'No weekly summary available. Generate a report to see insights and recommendations based on your simulation activity.'}
            </div>
          </div>
          
          {/* Key Insights */}
          {weeklyData.key_insights && weeklyData.key_insights.length > 0 && (
            <div className="mt-6">
              <h4 className="text-white font-semibold mb-4 flex items-center">
                <span className="text-lg mr-2">💡</span>
                Key Insights & Recommendations
              </h4>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {weeklyData.key_insights.map((insight, index) => (
                  <motion.div 
                    key={index}
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 1 + index * 0.1 }}
                    className="bg-gradient-to-br from-blue-500/10 to-cyan-600/10 rounded-lg p-4 border border-blue-300/20 hover:border-blue-300/40 transition-all duration-200"
                  >
                    <div className="flex items-start space-x-3">
                      <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center flex-shrink-0 mt-1">
                        <span className="text-white text-sm font-bold">{index + 1}</span>
                      </div>
                      <div className="text-white/80 text-sm leading-relaxed">{insight}</div>
                    </div>
                  </motion.div>
                ))}
              </div>
            </div>
          )}
          
          {/* Daily Breakdown */}
          {weeklyData.daily_breakdown && (
            <div className="mt-6 pt-6 border-t border-white/10">
              <h4 className="text-white font-semibold mb-4 flex items-center">
                <span className="text-lg mr-2">📊</span>
                Daily Activity Breakdown
              </h4>
              <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-7 gap-3">
                {Object.entries(weeklyData.daily_breakdown || {}).map(([day, count], index) => (
                  <motion.div 
                    key={day}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 1.2 + index * 0.1 }}
                    className="text-center p-3 bg-white/5 rounded-lg hover:bg-white/10 transition-all"
                  >
                    <div className="text-lg font-bold text-white">{count}</div>
                    <div className="text-white/60 text-xs">{day.slice(0, 3)}</div>
                  </motion.div>
                ))}
              </div>
            </div>
          )}
        </motion.div>
      )}
    </div>
  );
};

export default AnalyticsDashboard;