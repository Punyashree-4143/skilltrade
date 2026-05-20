import React, { useEffect, useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { motion } from 'framer-motion';
import axios from 'axios';
import { 
  Home, 
  Users, 
  Target, 
  Calendar, 
  MessageSquare, 
  Bell, 
  User,
  TrendingUp,
  MapPin
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';

const Sidebar = () => {
  const { user, token } = useAuth();
  const location = useLocation();
  const [stats, setStats] = useState({
    matches: 0,
    pending_swaps: 0,
    active_swaps: 0,
    unread_messages: 0,
    unread_notifications: 0,
    profile_views: 0,
    success_rate: 0
  });

  useEffect(() => {
    const loadStats = async () => {
      const authToken = token || localStorage.getItem('authToken');
      if (!authToken) return;

      try {
        const response = await axios.get('http://localhost:8000/api/dashboard/stats', {
          headers: {
            Authorization: `Bearer ${authToken}`
          }
        });
        setStats(response.data || {});
      } catch (error) {
        console.error('Sidebar stats error:', error);
      }
    };

    loadStats();
    window.addEventListener('notifications:changed', loadStats);
    const intervalId = setInterval(loadStats, 30000);

    return () => {
      window.removeEventListener('notifications:changed', loadStats);
      clearInterval(intervalId);
    };
  }, [token]);

  const badgeValue = (value) => {
    const count = Number(value || 0);
    return count > 0 ? String(count) : null;
  };

  const menuItems = [
    { icon: Home, label: 'Dashboard', path: '/app/dashboard', badge: null },
    { icon: Users, label: 'Explore', path: '/app/explore', badge: null },
    { icon: Target, label: 'Matches', path: '/app/matches', badge: badgeValue(stats.matches) },
    { icon: Calendar, label: 'Swaps', path: '/app/swaps', badge: badgeValue((stats.pending_swaps || 0) + (stats.active_swaps || 0)) },
    { icon: MessageSquare, label: 'Messages', path: '/app/messages', badge: badgeValue(stats.unread_messages) },
    { icon: Bell, label: 'Notifications', path: '/app/notifications', badge: badgeValue(stats.unread_notifications) },
  ];

  const quickStats = [
    { label: 'Profile Views', value: String(stats.profile_views || 0), icon: TrendingUp },
    { label: 'Active Swaps', value: String(stats.active_swaps || 0), icon: Calendar },
    { label: 'Success Rate', value: `${stats.success_rate || 0}%`, icon: Target },
    { label: 'Pending Swaps', value: String(stats.pending_swaps || 0), icon: Calendar },
  ];

  return (
    <aside className="hidden lg:block w-64 glass-morphism border-r border-gray-700 min-h-[calc(100vh-4rem)]">
      <div className="p-6">
        <nav className="space-y-2">
          {menuItems.map((item) => {
            const Icon = item.icon;
            const isActive = location.pathname === item.path;
            
            return (
              <Link
                key={item.path}
                to={item.path}
                className="relative"
              >
                <motion.div
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  className={`flex items-center justify-between px-4 py-3 rounded-lg transition-all ${
                    isActive 
                      ? 'bg-gradient-to-r from-primary/20 to-secondary/20 text-white border border-secondary/30' 
                      : 'text-gray-300 hover:text-white hover:bg-gray-800'
                  }`}
                >
                  <div className="flex items-center space-x-3">
                    <Icon className="w-5 h-5" />
                    <span className="font-medium">{item.label}</span>
                  </div>
                  {item.badge && (
                    <span className="bg-secondary text-white text-xs px-2 py-1 rounded-full">
                      {item.badge}
                    </span>
                  )}
                </motion.div>
              </Link>
            );
          })}
        </nav>

        <div className="mt-8 p-4 glass-morphism border border-gray-700 rounded-lg">
          <h3 className="text-white font-semibold mb-3 flex items-center space-x-2">
            <User className="w-4 h-4" />
            <span>Quick Stats</span>
          </h3>
          <div className="space-y-3">
            {quickStats.map((stat, index) => {
              const Icon = stat.icon;
              return (
                <motion.div
                  key={stat.label}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className="flex items-center justify-between"
                >
                  <div className="flex items-center space-x-2">
                    <Icon className="w-4 h-4 text-secondary" />
                    <span className="text-gray-400 text-sm">{stat.label}</span>
                  </div>
                  <span className="text-white font-semibold">{stat.value}</span>
                </motion.div>
              );
            })}
          </div>
        </div>

        <div className="mt-6 p-4 bg-gradient-to-br from-primary/10 to-secondary/10 border border-secondary/20 rounded-lg">
          <div className="flex items-center space-x-2 mb-2">
            <MapPin className="w-4 h-4 text-secondary" />
            <span className="text-white font-medium">Your Location</span>
          </div>
          <p className="text-gray-400 text-sm">
            {user?.location?.city || 'Location not set'}
          </p>
          <p className="text-gray-500 text-xs mt-1">
            {user?.location?.country || ''}
          </p>
        </div>
      </div>
    </aside>
  );
};

export default Sidebar;
