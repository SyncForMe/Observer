import React from 'react';
import { motion } from 'framer-motion';

const StartButton = ({ onClick }) => {
  return (
    <div className="bg-gradient-to-br from-indigo-500/20 via-purple-500/20 to-pink-500/20 backdrop-blur-lg rounded-xl border border-white/20 p-8 h-[600px] flex flex-col items-center justify-center text-center relative overflow-hidden">
      {/* Background Animation */}
      <div className="absolute inset-0 bg-gradient-to-br from-blue-600/10 via-purple-600/10 to-pink-600/10 animate-pulse"></div>
      
      {/* Floating Elements */}
      <div className="absolute top-10 left-10 w-4 h-4 bg-blue-400/30 rounded-full animate-bounce"></div>
      <div className="absolute top-20 right-16 w-3 h-3 bg-purple-400/30 rounded-full animate-bounce delay-300"></div>
      <div className="absolute bottom-20 left-20 w-5 h-5 bg-pink-400/30 rounded-full animate-bounce delay-700"></div>
      
      <div className="relative z-10 max-w-md">
        {/* AI Icon */}
        <motion.div
          animate={{ 
            scale: [1, 1.1, 1],
            rotate: [0, 5, -5, 0]
          }}
          transition={{ 
            duration: 4, 
            repeat: Infinity,
            ease: "easeInOut"
          }}
          className="w-24 h-24 mx-auto mb-6 bg-gradient-to-br from-indigo-400 to-purple-500 rounded-2xl flex items-center justify-center shadow-2xl"
        >
          <span className="text-4xl">🤖</span>
        </motion.div>
        
        {/* Title */}
        <motion.h2
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="text-3xl font-bold text-white mb-4 bg-gradient-to-r from-blue-200 via-purple-200 to-pink-200 bg-clip-text text-transparent"
        >
          Ready to Begin?
        </motion.h2>
        
        {/* Description */}
        <motion.p
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="text-white/70 mb-8 leading-relaxed"
        >
          Create your perfect AI simulation in minutes. Choose your type, describe your scenario, and watch intelligent agents collaborate in real-time.
        </motion.p>
        
        {/* Start Button */}
        <motion.button
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.6 }}
          whileHover={{ 
            scale: 1.05,
            boxShadow: "0 20px 40px rgba(99, 102, 241, 0.4)"
          }}
          whileTap={{ scale: 0.98 }}
          onClick={onClick}
          className="bg-gradient-to-r from-indigo-500 to-purple-600 hover:from-indigo-600 hover:to-purple-700 text-white font-semibold px-8 py-4 rounded-2xl shadow-lg transition-all duration-300 flex items-center space-x-3 mx-auto"
        >
          <span className="text-2xl">✨</span>
          <span className="text-lg">Start New Simulation</span>
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
          </svg>
        </motion.button>
        
        {/* Features */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 1 }}
          className="mt-8 grid grid-cols-3 gap-4 text-center"
        >
          <div className="text-white/60">
            <div className="text-lg mb-1">🎯</div>
            <div className="text-xs">Smart Setup</div>
          </div>
          <div className="text-white/60">
            <div className="text-lg mb-1">🎙️</div>
            <div className="text-xs">Voice Input</div>
          </div>
          <div className="text-white/60">
            <div className="text-lg mb-1">⚡</div>
            <div className="text-xs">Fast Track</div>
          </div>
        </motion.div>
      </div>
    </div>
  );
};

export default StartButton;