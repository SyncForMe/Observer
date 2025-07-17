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
    const savedUser = localStorage.getItem('auth_user');
    
    if (savedToken) {
      setToken(savedToken);
      
      // If we have cached user data, set it immediately for instant loading
      if (savedUser) {
        try {
          const userData = JSON.parse(savedUser);
          setUser(userData);
          console.log('🔍 AuthContext: Loaded cached user data for instant display');
        } catch (error) {
          console.error('Error parsing cached user data:', error);
          localStorage.removeItem('auth_user');
        }
      }
      
      // Always fetch fresh data from backend (but user sees cached data immediately)
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
        
        // Cache user data in localStorage for instant loading on next page load
        localStorage.setItem('auth_user', JSON.stringify(response.data));
        console.log('🔍 AuthContext: Cached fresh user data from backend');
      } else {
        localStorage.removeItem('auth_token');
        localStorage.removeItem('auth_user');
        setToken(null);
        setUser(null);
      }
    } catch (error) {
      console.error('Auth check failed:', error);
      localStorage.removeItem('auth_token');
      localStorage.removeItem('auth_user');
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
    localStorage.removeItem('auth_user');
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
        const userData = response.data.user;
        
        localStorage.setItem('auth_token', newToken);
        localStorage.setItem('auth_user', JSON.stringify(userData));
        
        setToken(newToken);
        setUser(userData);
        
        console.log('🔍 AuthContext: testLogin successful, user set and cached:', userData);
        return { success: true };
      }
      console.log('🔍 AuthContext: testLogin failed - no access_token');
      return { success: false, error: 'Test login failed' };
    } catch (error) {
      console.error('🔍 AuthContext: testLogin error:', error);
      return { success: false, error: error.response?.data?.error || 'Test login failed' };
    }
  };

  const updateUser = (updatedUserData) => {
    console.log('🔍 AuthContext: Updating user data:', updatedUserData);
    const newUserData = {
      ...user,
      ...updatedUserData
    };
    setUser(newUserData);
    
    // Cache the updated user data in localStorage
    localStorage.setItem('auth_user', JSON.stringify(newUserData));
    console.log('🔍 AuthContext: Cached updated user data to localStorage');
  };

  return (
    <AuthContext.Provider value={{ 
      user, 
      token, 
      login, 
      logout, 
      testLogin,
      updateUser,
      loading,
      isAuthenticated: !!token && !!user 
    }}>
      {children}
    </AuthContext.Provider>
  );
};