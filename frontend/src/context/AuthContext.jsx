import React, { createContext, useContext, useState, useEffect } from 'react';
import { authAPI } from '../api/api';

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem('token') || null);
  const [role, setRole] = useState(localStorage.getItem('role') || 'patient');
  const [loading, setLoading] = useState(true);
  const [toastMessage, setToastMessage] = useState(null);

  const showToast = (msg) => {
    setToastMessage(msg);
    setTimeout(() => {
      setToastMessage(null);
    }, 4000);
  };

  useEffect(() => {
    const fetchUser = async () => {
      if (token) {
        try {
          const profile = await authAPI.getUserProfile();
          setUser(profile);
          if (profile.role) {
            setRole(profile.role);
            localStorage.setItem('role', profile.role);
          }
        } catch (error) {
          console.error('Failed to fetch user profile:', error);
          logout();
        }
      }
      setLoading(false);
    };

    fetchUser();
  }, [token]);

  const login = async (username, password) => {
    try {
      const data = await authAPI.login(username, password);
      localStorage.setItem('token', data.access_token);
      localStorage.setItem('role', data.role);
      setToken(data.access_token);
      setRole(data.role);
      
      const profile = await authAPI.getUserProfile();
      setUser(profile);
      showToast(`Welcome back, ${profile.first_name || profile.username}!`);
      return { success: true, role: data.role };
    } catch (error) {
      console.error('Login error:', error);
      const errMsg = error.response?.data?.detail || 'Invalid username or password';
      showToast(errMsg);
      return { success: false, error: errMsg };
    }
  };

  const register = async (userData) => {
    try {
      const res = await authAPI.register(userData);
      showToast('Registration successful! Please log in.');
      return { success: true, data: res };
    } catch (error) {
      console.error('Register error:', error);
      const errMsg = error.response?.data?.detail || 'Registration failed';
      showToast(errMsg);
      return { success: false, error: errMsg };
    }
  };

  const logout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('role');
    setToken(null);
    setUser(null);
    setRole('patient');
    showToast('Logged out');
  };

  const switchRole = (newRole) => {
    setRole(newRole);
    localStorage.setItem('role', newRole);
    showToast(`Switched view to ${newRole.toUpperCase()}`);
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        role,
        loading,
        login,
        register,
        logout,
        switchRole,
        showToast,
        toastMessage,
      }}
    >
      {children}
      {toastMessage && (
        <div className="toast show">
          <span>✨</span> {toastMessage}
        </div>
      )}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
