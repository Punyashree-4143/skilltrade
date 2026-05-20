import React, { useEffect, useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import axios from 'axios';
import { 
  Search, 
  Bell, 
  MessageSquare, 
  Settings, 
  User, 
  LogOut,
  Menu,
  X,
  Home,
  Users,
  Target,
  Calendar
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import NotificationBadge from './NotificationBadge';

const Navbar = () => {
  const { user, token, logout } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [showUserMenu, setShowUserMenu] = useState(false);
  const [unreadNotifications, setUnreadNotifications] = useState(0);

  const isAppRoute = location.pathname.startsWith('/app');

  useEffect(() => {
    const loadNotificationCount = async () => {
      const authToken = token || localStorage.getItem('authToken');
      if (!authToken || !isAppRoute) {
        setUnreadNotifications(0);
        return;
      }

      try {
  const response = await axios.get(
    `${import.meta.env.VITE_API_URL}/api/notifications`,
    {
      headers: {
        Authorization: `Bearer ${authToken}`
      }
    }
  );

        const notifications = Array.isArray(response.data) ? response.data : [];
        setUnreadNotifications(
          notifications.filter(notification => !notification.is_read).length
        );
      } catch (error) {
        console.error('Notification count error:', error);
        setUnreadNotifications(0);
      }
    };

    loadNotificationCount();
    window.addEventListener('notifications:changed', loadNotificationCount);
    const intervalId = setInterval(loadNotificationCount, 30000);

    return () => {
      window.removeEventListener('notifications:changed', loadNotificationCount);
      clearInterval(intervalId);
    };
  }, [token, isAppRoute, location.pathname]);

  const handleLogout = async () => {
    await logout();
    navigate('/');
  };

  const navItems = [
    { icon: Home, label: 'Dashboard', path: '/app/dashboard' },
    { icon: Users, label: 'Explore', path: '/app/explore' },
    { icon: Target, label: 'Matches', path: '/app/matches' },
    { icon: Calendar, label: 'Swaps', path: '/app/swaps' },
  ];

  if (!isAppRoute) {
    return (
      <nav className="glass-morphism border-b border-gray-700 sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <Link to="/" className="flex items-center space-x-2">
              <div className="w-8 h-8 bg-gradient-to-r from-primary to-secondary rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-lg">ST</span>
              </div>
              <span className="text-xl font-bold gradient-text">SkillTrade</span>
            </Link>

            <div className="hidden md:flex items-center space-x-6">
              <Link to="/about" className="text-gray-300 hover:text-white transition-colors">
                About
              </Link>
              <Link 
                to="/login" 
                className="bg-gradient-to-r from-primary to-secondary text-white px-4 py-2 rounded-lg hover:shadow-lg transition-all"
              >
                Sign In
              </Link>
            </div>

            <button
              onClick={() => setIsMenuOpen(!isMenuOpen)}
              className="md:hidden text-gray-300 hover:text-white"
            >
              {isMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>
          </div>

          {isMenuOpen && (
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              className="md:hidden py-4 border-t border-gray-700"
            >
              <div className="flex flex-col space-y-3">
                <Link to="/about" className="text-gray-300 hover:text-white transition-colors">
                  About
                </Link>
                <Link 
                  to="/login" 
                  className="bg-gradient-to-r from-primary to-secondary text-white px-4 py-2 rounded-lg text-center"
                >
                  Sign In
                </Link>
              </div>
            </motion.div>
          )}
        </div>
      </nav>
    );
  }

  return (
    <nav className="glass-morphism border-b border-gray-700 sticky top-0 z-40">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          <Link to="/app/dashboard" className="flex items-center space-x-2">
            <div className="w-8 h-8 bg-gradient-to-r from-primary to-secondary rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-lg">ST</span>
            </div>
            <span className="text-xl font-bold gradient-text">SkillTrade</span>
          </Link>

          <div className="hidden lg:flex items-center space-x-6">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = location.pathname === item.path;
              
              return (
                <Link
                  key={item.path}
                  to={item.path}
                  className={`flex items-center space-x-2 px-3 py-2 rounded-lg transition-all ${
                    isActive 
                      ? 'bg-secondary text-white' 
                      : 'text-gray-300 hover:text-white hover:bg-gray-800'
                  }`}
                >
                  <Icon className="w-4 h-4" />
                  <span>{item.label}</span>
                </Link>
              );
            })}
          </div>

          <div className="flex items-center space-x-4">
            <button className="text-gray-300 hover:text-white transition-colors">
              <Search className="w-5 h-5" />
            </button>

            <Link to="/app/notifications" className="relative">
              <Bell className="w-5 h-5 text-gray-300 hover:text-white transition-colors" />
              <NotificationBadge count={unreadNotifications} />
            </Link>

            <Link to="/app/messages" className="relative">
              <MessageSquare className="w-5 h-5 text-gray-300 hover:text-white transition-colors" />
              <NotificationBadge />
            </Link>

            <div className="relative">
              <button
                onClick={() => setShowUserMenu(!showUserMenu)}
                className="flex items-center space-x-2 text-gray-300 hover:text-white transition-colors"
              >
                <div className="w-8 h-8 bg-gray-600 rounded-full flex items-center justify-center">
                  {user?.avatar ? (
                    <img src={user.avatar} alt={user.name} className="w-full h-full rounded-full object-cover" />
                  ) : (
                    <User className="w-4 h-4" />
                  )}
                </div>
                <span className="hidden md:block">{user?.name}</span>
              </button>

              {showUserMenu && (
                <motion.div
                  initial={{ opacity: 0, y: -10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="absolute right-0 mt-2 w-48 glass-morphism border border-gray-700 rounded-lg shadow-lg"
                >
                  <Link
                    to="/app/profile"
                    className="flex items-center space-x-2 px-4 py-3 text-gray-300 hover:text-white hover:bg-gray-800 transition-colors"
                  >
                    <User className="w-4 h-4" />
                    <span>Profile</span>
                  </Link>
                  <Link
                    to="/app/profile/edit"
                    className="flex items-center space-x-2 px-4 py-3 text-gray-300 hover:text-white hover:bg-gray-800 transition-colors"
                  >
                    <Settings className="w-4 h-4" />
                    <span>Settings</span>
                  </Link>
                  <button
                    onClick={handleLogout}
                    className="flex items-center space-x-2 w-full px-4 py-3 text-gray-300 hover:text-white hover:bg-gray-800 transition-colors text-left"
                  >
                    <LogOut className="w-4 h-4" />
                    <span>Logout</span>
                  </button>
                </motion.div>
              )}
            </div>

            <button
              onClick={() => setIsMenuOpen(!isMenuOpen)}
              className="lg:hidden text-gray-300 hover:text-white"
            >
              {isMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>
          </div>
        </div>

        {isMenuOpen && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            className="lg:hidden py-4 border-t border-gray-700"
          >
            <div className="flex flex-col space-y-3">
              {navItems.map((item) => {
                const Icon = item.icon;
                const isActive = location.pathname === item.path;
                
                return (
                  <Link
                    key={item.path}
                    to={item.path}
                    className={`flex items-center space-x-2 px-3 py-2 rounded-lg transition-all ${
                      isActive 
                        ? 'bg-secondary text-white' 
                        : 'text-gray-300 hover:text-white hover:bg-gray-800'
                    }`}
                  >
                    <Icon className="w-4 h-4" />
                    <span>{item.label}</span>
                  </Link>
                );
              })}
            </div>
          </motion.div>
        )}
      </div>
    </nav>
  );
};

export default Navbar;
