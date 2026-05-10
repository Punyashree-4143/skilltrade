import React, { useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { AuthProvider, useAuth } from './context/AuthContext';
import ProtectedRoute from './components/ProtectedRoute';
import Layout from './components/Layout';
import Navbar from './components/Navbar';

// Pages
import Landing from './pages/Landing';
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import Profile from './pages/Profile';
import EditProfile from './pages/EditProfile';
import Explore from './pages/Explore';
import Matches from './pages/Matches';
import SwapRequests from './pages/SwapRequests';
import Chat from './pages/Chat';
import Messages from './pages/Messages';
import Notifications from './pages/Notifications';
import UserProfile from './pages/UserProfile';
import About from './pages/About';

// Components
import LoadingSpinner from './components/LoadingSpinner';
import ToastContainer from './components/ToastContainer';

const AppContent = () => {
  const { loading, isAuthenticated } = useAuth();

  useEffect(() => {
    const handleBeforeUnload = () => {
      localStorage.setItem('lastPage', window.location.pathname);
    };
    
    window.addEventListener('beforeunload', handleBeforeUnload);
    return () => window.removeEventListener('beforeunload', handleBeforeUnload);
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-primary">
        <LoadingSpinner size="large" />
      </div>
    );
  }

  return (
    <Router>
      <div className="min-h-screen bg-primary">
        <Routes>
          {/* Public Routes */}
          <Route path="/" element={<Landing />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/about" element={<About />} />
          
          {/* Protected Routes */}
          <Route
            path="/app/*"
            element={
              <ProtectedRoute>
                <Layout>
                  <Routes>
                    <Route path="dashboard" element={<Dashboard />} />
                    <Route path="profile" element={<Profile />} />
                    <Route path="profile/edit" element={<EditProfile />} />
                    <Route path="explore" element={<Explore />} />
                    <Route path="matches" element={<Matches />} />
                    <Route path="swaps" element={<SwapRequests />} />
                    <Route path="chat" element={<Chat />} />
                    <Route path="chat/:userId" element={<Chat />} />
                    <Route path="messages" element={<Messages />} />
                    <Route path="notifications" element={<Notifications />} />
                    <Route path="user/:userId" element={<UserProfile />} />
                    <Route path="" element={<Navigate to="/app/dashboard" replace />} />
                  </Routes>
                </Layout>
              </ProtectedRoute>
            }
          />
          
          {/* Fallback Routes */}
          <Route 
            path="*" 
            element={
              isAuthenticated ? (
                <Navigate to="/app/dashboard" replace />
              ) : (
                <Navigate to="/" replace />
              )
            } 
          />
        </Routes>
        
        <ToastContainer />
      </div>
    </Router>
  );
};

const App = () => {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
};

export default App;
