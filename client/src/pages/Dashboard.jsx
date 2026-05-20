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
  AlertCircle
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import LoadingSpinner from '../components/LoadingSpinner';
import SkillBadge from '../components/SkillBadge';
import axios from 'axios';

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

        const response = await axios.get('http://localhost:8000/api/dashboard/stats', {
          headers: {
            Authorization: `Bearer ${authToken}`
          }
        });

        const activitiesResponse = await axios.get('http://localhost:8000/api/dashboard/activities', {
          headers: {
            Authorization: `Bearer ${authToken}`
          }
        });

        const matchesResponse = await axios.get('http://localhost:8000/api/dashboard/top-matches', {
          headers: {
            Authorization: `Bearer ${authToken}`
          }
        });

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
      window.removeEventListener('notifications:changed', loadDashboardData);
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
        <div className={`w-12 h-12 rounded-lg flex items-center justify-center ${color}`}>
          <Icon className="w-6 h-6 text-white" />
        </div>
      </div>
      <div className="text-2xl font-bold text-white mb-1">{value}</div>
      <div className="text-gray-400 text-sm">{label}</div>
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
              <div className="text-sm text-gray-400">Your Rating</div>
              <div className="flex items-center space-x-1">
                <Star className="w-5 h-5 text-yellow-400 fill-current" />
                <span className="text-xl font-bold text-white">-</span>
              </div>
            </div>
            <div className="text-right">
              <div className="text-sm text-gray-400">Location</div>
              <div className="flex items-center space-x-1">
                <MapPin className="w-4 h-4 text-gray-400" />
                <span className="text-white">{user?.location?.city || 'Not set'}</span>
              </div>
            </div>
          </div>
        </div>
      </motion.div>

      {/* Stats Grid */}
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

      <div className="grid lg:grid-cols-3 gap-8">
        {/* Recent Activity */}
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.1 }}
          className="lg:col-span-2"
        >
          <div className="glass-morphism p-6 rounded-xl border border-gray-700">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-semibold text-white">Recent Activity</h2>
              <Link
                to="/app/notifications"
                className="text-primary hover:text-secondary transition-colors text-sm"
              >
                View all
              </Link>
            </div>
            
            <div className="space-y-4">
              {recentActivity.map((activity, index) => (
                <motion.div
                  key={activity.swap_id || index}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className="flex items-start space-x-4 p-4 rounded-lg hover:bg-gray-800/50 transition-colors cursor-pointer"
                >
                  <img
                    src={activity.other_user?.avatar || `https://ui-avatars.com/api/?name=${encodeURIComponent(activity.other_user?.name || 'User')}&background=6366f1&color=fff&size=40`}
                    alt={activity.other_user?.name || 'User'}
                    className="w-10 h-10 rounded-full"
                  />
                  <div className="flex-1">
                    <p className="text-white text-sm">{activity.message}</p>
                    <div className="flex items-center space-x-2 mt-1">
                      <Clock className="w-3 h-3 text-gray-500" />
                      <span className="text-gray-500 text-xs">
                        {new Date(activity.timestamp).toLocaleString()}
                      </span>
                    </div>
                  </div>
                  {activity.type.includes('swap_sent') && (
                    <AlertCircle className="w-5 h-5 text-blue-400" />
                  )}
                  {activity.type.includes('swap_received') && (
                    <AlertCircle className="w-5 h-5 text-yellow-400" />
                  )}
                  {activity.type.includes('accepted') && (
                    <CheckCircle className="w-5 h-5 text-green-400" />
                  )}
                  {activity.type.includes('completed') && (
                    <CheckCircle className="w-5 h-5 text-blue-400" />
                  )}
                  {activity.type.includes('cancelled') && (
                    <X className="w-5 h-5 text-red-400" />
                  )}
                </motion.div>
              ))}
            </div>
          </div>
        </motion.div>

        {/* Top Matches */}
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.2 }}
        >
          <div className="glass-morphism p-6 rounded-xl border border-gray-700">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-semibold text-white">Top Matches</h2>
              <Link
                to="/app/matches"
                className="text-primary hover:text-secondary transition-colors text-sm"
              >
                See all
              </Link>
            </div>
            
            <div className="space-y-4">
              {matches.map((match, index) => (
                <motion.div
                  key={match.id}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className="p-4 rounded-lg border border-gray-700 hover:border-primary/50 transition-all cursor-pointer"
                >
                  <div className="flex items-center space-x-3 mb-3">
                    <img
                      src={match.avatar || `https://ui-avatars.com/api/?name=${encodeURIComponent(match.name)}&background=6366f1&color=fff&size=60`}
                      alt={match.name}
                      className="w-12 h-12 rounded-full"
                    />
                    <div className="flex-1">
                      <div className="flex items-center space-x-2">
                        <h3 className="font-medium text-white">{match.name}</h3>
                        <span className="text-xs bg-primary/20 text-primary px-2 py-1 rounded-full">
                          {match.match_score}% match
                        </span>
                      </div>
                      <div className="flex items-center space-x-1 text-gray-400 text-xs">
                        <MapPin className="w-3 h-3" />
                        <span>{match.location?.city || 'Location not set'}</span>
                      </div>
                    </div>
                  </div>
                  
                  <div className="space-y-2">
                    <div className="flex flex-wrap gap-1">
                      {match.skills_offered?.slice(0, 2).map((skill, i) => (
                        <SkillBadge key={i} skill={skill} variant="offered" size="sm" />
                      ))}
                    </div>
                    <div className="flex flex-wrap gap-1">
                      {match.skills_wanted?.slice(0, 2).map((skill, i) => (
                        <SkillBadge key={i} skill={skill} variant="wanted" size="sm" />
                      ))}
                    </div>
                    {match.matching_skills && match.matching_skills.length > 0 && (
                      <div className="text-xs text-green-400">
                        Matching skills: {match.matching_skills.join(', ')}
                      </div>
                    )}
                  </div>
                </motion.div>
              ))}
            </div>
          </div>
        </motion.div>
      </div>

      {/* Quick Actions */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
        className="glass-morphism p-6 rounded-xl border border-gray-700"
      >
        <h2 className="text-xl font-semibold text-white mb-6">Quick Actions</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <Link
            to="/app/explore"
            className="p-4 bg-gradient-to-br from-primary/10 to-primary/20 border border-primary/30 rounded-lg hover:from-primary/20 hover:to-primary/30 transition-all text-center group"
          >
            <Users className="w-8 h-8 text-primary mx-auto mb-2 group-hover:scale-110 transition-transform" />
            <span className="text-white text-sm">Explore Users</span>
          </Link>
          <Link
            to="/app/matches"
            className="p-4 bg-gradient-to-br from-secondary/10 to-secondary/20 border border-secondary/30 rounded-lg hover:from-secondary/20 hover:to-secondary/30 transition-all text-center group"
          >
            <Target className="w-8 h-8 text-secondary mx-auto mb-2 group-hover:scale-110 transition-transform" />
            <span className="text-white text-sm">Find Matches</span>
          </Link>
          <Link
            to="/app/swaps"
            className="p-4 bg-gradient-to-br from-green-600/10 to-green-600/20 border border-green-600/30 rounded-lg hover:from-green-600/20 hover:to-green-600/30 transition-all text-center group"
          >
            <Calendar className="w-8 h-8 text-green-400 mx-auto mb-2 group-hover:scale-110 transition-transform" />
            <span className="text-white text-sm">My Swaps</span>
          </Link>
          <Link
            to="/app/messages"
            className="p-4 bg-gradient-to-br from-blue-600/10 to-blue-600/20 border border-blue-600/30 rounded-lg hover:from-blue-600/20 hover:to-blue-600/30 transition-all text-center group"
          >
            <MessageSquare className="w-8 h-8 text-blue-400 mx-auto mb-2 group-hover:scale-110 transition-transform" />
            <span className="text-white text-sm">Messages</span>
          </Link>
        </div>
      </motion.div>
    </div>
  );
};

export default Dashboard;
