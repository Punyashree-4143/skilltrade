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

const Dashboard = () => {
  const { user } = useAuth();
  const [stats, setStats] = useState({
    totalSwaps: 0,
    completedSwaps: 0,
    pendingRequests: 0,
    unreadMessages: 0,
    averageRating: 0
  });
  const [recentActivity, setRecentActivity] = useState([]);
  const [matches, setMatches] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Simulate API calls - in real app these would be actual API calls
    const loadDashboardData = async () => {
      try {
        // Mock data - replace with actual API calls
        setStats({
          totalSwaps: 12,
          completedSwaps: 8,
          pendingRequests: 3,
          unreadMessages: 5,
          averageRating: 4.7
        });

        setRecentActivity([
          {
            id: 1,
            type: 'swap_request',
            message: 'Sarah Chen wants to learn React from you',
            time: '2 hours ago',
            avatar: '/api/placeholder/40/40'
          },
          {
            id: 2,
            type: 'message',
            message: 'New message from Mike Rodriguez',
            time: '5 hours ago',
            avatar: '/api/placeholder/40/40'
          },
          {
            id: 3,
            type: 'swap_completed',
            message: 'You completed a skill swap with Emma Thompson',
            time: '1 day ago',
            avatar: '/api/placeholder/40/40'
          }
        ]);

        setMatches([
          {
            id: 1,
            name: 'Alex Johnson',
            avatar: '/api/placeholder/60/60',
            matchScore: 95,
            offeredSkills: ['Guitar', 'Music Theory'],
            wantedSkills: ['Web Development'],
            distance: '2.5 km'
          },
          {
            id: 2,
            name: 'Maria Garcia',
            avatar: '/api/placeholder/60/60',
            matchScore: 88,
            offeredSkills: ['Spanish', 'Translation'],
            wantedSkills: ['English Conversation'],
            distance: '5.1 km'
          }
        ]);
      } catch (error) {
        console.error('Dashboard data loading error:', error);
      } finally {
        setLoading(false);
      }
    };

    loadDashboardData();
  }, []);

  const StatCard = ({ icon: Icon, label, value, color, change }) => (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="glass-morphism p-6 rounded-xl border border-gray-700"
    >
      <div className="flex items-center justify-between mb-4">
        <div className={`w-12 h-12 rounded-lg flex items-center justify-center ${color}`}>
          <Icon className="w-6 h-6 text-white" />
        </div>
        {change && (
          <span className={`text-sm font-medium ${
            change > 0 ? 'text-green-400' : 'text-red-400'
          }`}>
            {change > 0 ? '+' : ''}{change}%
          </span>
        )}
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
                <span className="text-xl font-bold text-white">{stats.averageRating}</span>
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
          label="Total Swaps"
          value={stats.totalSwaps}
          color="bg-primary"
          change={12}
        />
        <StatCard
          icon={CheckCircle}
          label="Completed"
          value={stats.completedSwaps}
          color="bg-green-600"
          change={8}
        />
        <StatCard
          icon={Target}
          label="Pending Requests"
          value={stats.pendingRequests}
          color="bg-yellow-600"
          change={-5}
        />
        <StatCard
          icon={MessageSquare}
          label="Unread Messages"
          value={stats.unreadMessages}
          color="bg-secondary"
          change={15}
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
                  key={activity.id}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className="flex items-start space-x-4 p-4 rounded-lg hover:bg-gray-800/50 transition-colors cursor-pointer"
                >
                  <img
                    src={activity.avatar}
                    alt="User"
                    className="w-10 h-10 rounded-full"
                  />
                  <div className="flex-1">
                    <p className="text-white text-sm">{activity.message}</p>
                    <div className="flex items-center space-x-2 mt-1">
                      <Clock className="w-3 h-3 text-gray-500" />
                      <span className="text-gray-500 text-xs">{activity.time}</span>
                    </div>
                  </div>
                  {activity.type === 'swap_request' && (
                    <AlertCircle className="w-5 h-5 text-yellow-400" />
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
                      src={match.avatar}
                      alt={match.name}
                      className="w-12 h-12 rounded-full"
                    />
                    <div className="flex-1">
                      <div className="flex items-center space-x-2">
                        <h3 className="font-medium text-white">{match.name}</h3>
                        <span className="text-xs bg-primary/20 text-primary px-2 py-1 rounded-full">
                          {match.matchScore}% match
                        </span>
                      </div>
                      <div className="flex items-center space-x-1 text-gray-400 text-xs">
                        <MapPin className="w-3 h-3" />
                        <span>{match.distance}</span>
                      </div>
                    </div>
                  </div>
                  
                  <div className="space-y-2">
                    <div className="flex flex-wrap gap-1">
                      {match.offeredSkills.slice(0, 2).map((skill, i) => (
                        <SkillBadge key={i} skill={skill} variant="offered" size="sm" />
                      ))}
                    </div>
                    <div className="flex flex-wrap gap-1">
                      {match.wantedSkills.slice(0, 2).map((skill, i) => (
                        <SkillBadge key={i} skill={skill} variant="wanted" size="sm" />
                      ))}
                    </div>
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
