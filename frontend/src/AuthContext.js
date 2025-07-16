import React, { createContext, useContext, useState, useEffect } from 'react';
import axios from 'axios';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [token, setToken] = useState(null);

  const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
  const API = `${BACKEND_URL}/api`;

  useEffect(() => {
    // Initialize token from localStorage
    const savedToken = localStorage.getItem('auth_token');
    if (savedToken) {
      setToken(savedToken);
      checkAuthStatus(savedToken);
    } else {
      setLoading(false);
    }
  }, []);

  const checkAuthStatus = async (authToken) => {
    try {
      const response = await axios.get(`${API}/auth/me`, {
        headers: { Authorization: `Bearer ${authToken}` }
      });
      
      if (response.data && response.data.id) {
        setUser(response.data);
        setToken(authToken);
      } else {
        localStorage.removeItem('auth_token');
        setToken(null);
        setUser(null);
      }
    } catch (error) {
      console.error('Auth check failed:', error);
      localStorage.removeItem('auth_token');
      setToken(null);
      setUser(null);
    } finally {
      setLoading(false);
    }
  };

  const login = async (email, password) => {
    try {
      const response = await axios.post(`${API}/auth/login`, { email, password });
      
      if (response.data && response.data.access_token) {
        const newToken = response.data.access_token;
        localStorage.setItem('auth_token', newToken);
        setToken(newToken);
        setUser(response.data.user);
        return { success: true };
      }
      return { success: false, error: response.data?.error || 'Login failed' };
    } catch (error) {
      return { success: false, error: error.response?.data?.error || 'Login failed' };
    }
  };

  const logout = () => {
    localStorage.removeItem('auth_token');
    setToken(null);
    setUser(null);
  };

  const testLogin = async () => {
    try {
      console.log('🔍 AuthContext: Starting testLogin');
      const response = await axios.post(`${API}/auth/test-login`);
      console.log('🔍 AuthContext: testLogin response:', response.data);
      
      if (response.data && response.data.access_token) {
        const newToken = response.data.access_token;
        localStorage.setItem('auth_token', newToken);
        setToken(newToken);
        setUser(response.data.user);
        console.log('🔍 AuthContext: testLogin successful, user set:', response.data.user);
        return { success: true };
      }
      console.log('🔍 AuthContext: testLogin failed - no access_token');
      return { success: false, error: 'Test login failed' };
    } catch (error) {
      console.error('🔍 AuthContext: testLogin error:', error);
      return { success: false, error: error.response?.data?.error || 'Test login failed' };
    }
  };

  return (
    <AuthContext.Provider value={{ 
      user, 
      token, 
      login, 
      logout, 
      testLogin,
      loading,
      isAuthenticated: !!token && !!user 
    }}>
      {children}
    </AuthContext.Provider>
  );
};