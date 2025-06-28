import React, { useCallback } from 'react';
import { AuthProvider, useAuth } from './AuthContext';
import HomePage from './HomePage';
import AppContent from './AppContent';
import ErrorBoundary from './ErrorBoundary';

// Main App Component
const App = () => {
  const { user, loading, handleExternalAuth } = useAuth();

  console.log('🔍 App: Rendering with user:', !!user, 'loading:', loading);

  // Handler for HomePage authentication
  const handleAuthentication = useCallback((token, userData) => {
    console.log('🔍 App: handleAuthentication called with token:', !!token, 'user:', !!userData);
    const success = handleExternalAuth(token, userData);
    if (success) {
      console.log('✅ App: Authentication successful, state updated');
    } else {
      console.error('❌ App: Authentication failed');
    }
  }, [handleExternalAuth]);

  if (loading) {
    console.log('🔍 App: Showing loading screen');
    return (
      <div className="min-h-screen bg-gradient-to-br from-purple-900 via-blue-900 to-indigo-900 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-white mb-4"></div>
          <p className="text-white/80">Loading...</p>
        </div>
      </div>
    );
  }

  if (!user) {
    console.log('🔍 App: No user, showing HomePage');
    return <HomePage onAuthenticated={handleAuthentication} />;
  }

  console.log('🔍 App: User found, showing AppContent');
  return <AppContent />;
};

// App with Auth Provider and Error Boundary
const AppWithAuth = () => {
  return (
    <ErrorBoundary>
      <AuthProvider>
        <div className="min-h-screen bg-gradient-to-br from-gray-900 via-blue-900 to-purple-900">
          <App />
        </div>
      </AuthProvider>
    </ErrorBoundary>
  );
};

export default AppWithAuth;