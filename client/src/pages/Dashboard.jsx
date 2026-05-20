import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Link } from 'react-router-dom';
import {
  Users,
  Target,
  MessageSquare,
  Star,
  TrendingUp,
  Calendar,
  MapPin,
  Clock,
  CheckCircle,
  AlertCircle,
  X
} from 'lucide-react';

import { useAuth } from '../context/AuthContext';
import LoadingSpinner from '../components/LoadingSpinner';
import SkillBadge from '../components/SkillBadge';
import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL;

const Dashboard = () => {
  const { user, token } = useAuth();

  const [stats, setStats] = useState({
    matches: 0,
    total_swaps: 0,
    pending_swaps: 0,
    active_swaps: 0,
    completed_swaps: 0,
    cancelled_swaps: 0,
    unread_messages: 0,
    unread_notifications: 0,
    profile_views: 0,
    success_rate: 0
  });

  const [recentActivity, setRecentActivity] = useState([]);
  const [matches, setMatches] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let isMounted = true;

    const loadDashboardData = async () => {
      try {
        const authToken = token || localStorage.getItem('authToken');

        if (!authToken) {
          console.error('No auth token found');
          setLoading(false);
          return;
        }

        // Dashboard Stats
        const response = await axios.get(
          `${API_URL}/api/dashboard/stats`,
          {
            headers: {
              Authorization: `Bearer ${authToken}`
            }
          }
        );

        // Recent Activities
        const activitiesResponse = await axios.get(
          `${API_URL}/api/dashboard/activities`,
          {
            headers: {
              Authorization: `Bearer ${authToken}`
            }
          }
        );

        // Top Matches
        const matchesResponse = await axios.get(
          `${API_URL}/api/dashboard/top-matches`,
          {
            headers: {
              Authorization: `Bearer ${authToken}`
            }
          }
        );

        if (!isMounted) return;

        setStats(response.data || {});
        setRecentActivity(activitiesResponse.data || []);
        setMatches(matchesResponse.data || []);

      } catch (error) {
        console.error('Dashboard data loading error:', error);
      } finally {
        if (isMounted) setLoading(false);
      }
    };

    loadDashboardData();

    window.addEventListener('notifications:changed', loadDashboardData);

    const intervalId = setInterval(loadDashboardData, 30000);

    return () => {
      isMounted = false;
      window.removeEventListener(
        'notifications:changed',
        loadDashboardData
      );
      clearInterval(intervalId);
    };
  }, [token]);

  const StatCard = ({ icon: Icon, label, value, color }) => (
    <motion.div
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ delay: 0.1 }}
      className="glass-morphism p-6 rounded-xl border border-gray-700"
    >
      <div className="flex items-center justify-between mb-4">
        <div
          className={`w-12 h-12 rounded-lg flex items-center justify-center ${color}`}
        >
          <Icon className="w-6 h-6 text-white" />
        </div>
      </div>

      <div className="text-2xl font-bold text-white mb-1">
        {value}
      </div>

      <div className="text-gray-400 text-sm">
        {label}
      </div>
    </motion.div>
  );

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <LoadingSpinner size="large" />
      </div>
    );
  }

  return (
    <div className="space-y-8">

      {/* Welcome Section */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="glass-morphism p-8 rounded-2xl border border-gray-700"
      >
        <div className="flex flex-col md:flex-row md:items-center md:justify-between">

          <div>
            <h1 className="text-3xl font-bold text-white mb-2">
              Welcome back, {user?.name}! 👋
            </h1>

            <p className="text-gray-400">
              Ready to continue your skill trading journey?
            </p>
          </div>

          <div className="flex items-center space-x-4 mt-4 md:mt-0">

            <div className="text-right">
              <div className="text-sm text-gray-400">
                Your Rating
              </div>

              <div className="flex items-center space-x-1">
                <Star className="w-5 h-5 text-yellow-400 fill-current" />
                <span className="text-xl font-bold text-white">
                  -
                </span>
              </div>
            </div>

            <div className="text-right">
              <div className="text-sm text-gray-400">
                Location
              </div>

              <div className="flex items-center space-x-1">
                <MapPin className="w-4 h-4 text-gray-400" />
                <span className="text-white">
                  {user?.location?.city || 'Not set'}
                </span>
              </div>
            </div>

          </div>
        </div>
      </motion.div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">

        <StatCard
          icon={Calendar}
          label="Active Swaps"
          value={stats.active_swaps || 0}
          color="bg-primary"
        />

        <StatCard
          icon={CheckCircle}
          label="Completed"
          value={stats.completed_swaps || 0}
          color="bg-green-600"
        />

        <StatCard
          icon={Target}
          label="Pending Requests"
          value={stats.pending_swaps || 0}
          color="bg-yellow-600"
        />

        <StatCard
          icon={TrendingUp}
          label="Success Rate"
          value={`${stats.success_rate || 0}%`}
          color="bg-secondary"
        />

      </div>

    </div>
  );
};

export default Dashboard;