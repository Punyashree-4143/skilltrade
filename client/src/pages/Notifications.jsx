import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Bell, Users, MessageSquare, CheckCircle, Eye, Star, UserPlus, Award, X } from 'lucide-react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import LoadingSpinner from '../components/LoadingSpinner';

const API_BASE_URL = 'http://localhost:8000';

const notificationTypes = {
  new_match: { icon: Users, color: 'text-green-400', bgColor: 'bg-green-900', actionUrl: '/app/matches' },
  new_message: { icon: MessageSquare, color: 'text-blue-400', bgColor: 'bg-blue-900', actionUrl: '/app/messages' },
  swap_accepted: { icon: CheckCircle, color: 'text-green-400', bgColor: 'bg-green-900', actionUrl: '/app/swaps' },
  swap_rejected: { icon: X, color: 'text-red-400', bgColor: 'bg-red-900', actionUrl: '/app/swaps' },
  swap_request: { icon: UserPlus, color: 'text-blue-400', bgColor: 'bg-blue-900', actionUrl: '/app/swaps' },
  profile_viewed: { icon: Eye, color: 'text-purple-400', bgColor: 'bg-purple-900', actionUrl: '/app/profile' },
  review_received: { icon: Star, color: 'text-yellow-400', bgColor: 'bg-yellow-900', actionUrl: '/app/profile' },
  swap_completed: { icon: Award, color: 'text-green-400', bgColor: 'bg-green-900', actionUrl: '/app/swaps' }
};

const Notifications = () => {
  const { token, logout } = useAuth();
  const navigate = useNavigate();
  const [notifications, setNotifications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all');
  const [error, setError] = useState('');

  const notifyBadgeChanged = () => {
    window.dispatchEvent(new Event('notifications:changed'));
  };

  const authHeaders = () => ({
    Authorization: `Bearer ${token || localStorage.getItem('authToken')}`
  });

  const normalizeNotification = (notification) => ({
    id: notification.id,
    type: notification.type,
    title: notification.title,
    message: notification.message,
    relatedUserId: notification.related_user_id,
    relatedSwapId: notification.related_swap_id,
    isRead: Boolean(notification.is_read),
    timestamp: notification.created_at,
    actionUrl: notificationTypes[notification.type]?.actionUrl
  });

  const handleRequestError = (err, fallbackMessage) => {
    if (err.response?.status === 401) {
      setError('Your session has expired. Please log in again.');
      logout();
      return;
    }

    setError(err.response?.data?.message || err.response?.data?.detail || fallbackMessage);
  };

  const loadNotifications = async () => {
    if (!token && !localStorage.getItem('authToken')) {
      setLoading(false);
      return;
    }

    try {
      setLoading(true);
      const response = await axios.get(`${API_BASE_URL}/api/notifications`, {
        headers: authHeaders()
      });

      const nextNotifications = Array.isArray(response.data)
        ? response.data.map(normalizeNotification)
        : [];

      setNotifications(nextNotifications);
      setError('');
    } catch (err) {
      handleRequestError(err, 'Failed to load notifications');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadNotifications();
  }, [token]);

  const filteredNotifications = notifications.filter(notif => 
    filter === 'all' ? true : 
    filter === 'unread' ? !notif.isRead : 
    notif.isRead
  );

  const handleMarkAsRead = async (notifId) => {
    try {
      await axios.put(`${API_BASE_URL}/api/notifications/read/${notifId}`, {}, {
        headers: authHeaders()
      });

      setNotifications(prev => prev.map(notif =>
        notif.id === notifId ? { ...notif, isRead: true } : notif
      ));
      notifyBadgeChanged();
      setError('');
    } catch (err) {
      handleRequestError(err, 'Failed to mark notification as read');
    }
  };

  const handleMarkAllAsRead = async () => {
    try {
      await axios.put(`${API_BASE_URL}/api/notifications/read-all`, {}, {
        headers: authHeaders()
      });

      setNotifications(prev => prev.map(notif => ({ ...notif, isRead: true })));
      notifyBadgeChanged();
      setError('');
    } catch (err) {
      handleRequestError(err, 'Failed to mark notifications as read');
    }
  };

  const handleClearNotification = async (notifId) => {
    try {
      await axios.delete(`${API_BASE_URL}/api/notifications/${notifId}`, {
        headers: authHeaders()
      });

      setNotifications(prev => prev.filter(notif => notif.id !== notifId));
      notifyBadgeChanged();
      setError('');
    } catch (err) {
      handleRequestError(err, 'Failed to delete notification');
    }
  };

  const handleClearAll = async () => {
    try {
      await axios.delete(`${API_BASE_URL}/api/notifications/clear-all`, {
        headers: authHeaders()
      });

      setNotifications([]);
      notifyBadgeChanged();
      setError('');
    } catch (err) {
      handleRequestError(err, 'Failed to clear notifications');
    }
  };

  const getNotificationIcon = (type) => {
    const IconComponent = notificationTypes[type]?.icon || Bell;
    return <IconComponent className="w-5 h-5" />;
  };

  const getNotificationColor = (type) => {
    return notificationTypes[type]?.color || 'text-gray-400';
  };

  const getNotificationBg = (type) => {
    return notificationTypes[type]?.bgColor || 'bg-gray-900';
  };

  const formatTime = (timestamp) => {
    if (!timestamp) return '';

    const date = new Date(timestamp);
    if (Number.isNaN(date.getTime())) return '';

    const now = new Date();
    const diff = now - date;
    
    if (diff < 60000) { // Less than 1 minute
      return 'Just now';
    } else if (diff < 3600000) { // Less than 1 hour
      return `${Math.floor(diff / 60000)} minutes ago`;
    } else if (diff < 86400000) { // Less than 1 day
      return `${Math.floor(diff / 3600000)} hours ago`;
    } else {
      return date.toLocaleDateString();
    }
  };

  const NotificationCard = ({ notification }) => (
    <motion.div
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      whileHover={{ scale: 1.02 }}
      className={`glass-morphism p-4 rounded-xl border transition-all cursor-pointer ${
        notification.isRead 
          ? 'border-gray-700 opacity-70' 
          : 'border-primary hover:border-primary/80'
      }`}
    >
      <div className="flex items-start space-x-3">
        <div className={`p-2 rounded-lg ${getNotificationBg(notification.type)}`}>
          <div className={getNotificationColor(notification.type)}>
            {getNotificationIcon(notification.type)}
          </div>
        </div>
        
        <div className="flex-1 min-w-0">
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-sm font-semibold text-white">{notification.title}</h3>
            <div className="flex items-center space-x-2">
              {!notification.isRead && (
                <div className="w-2 h-2 bg-blue-400 rounded-full" />
              )}
              <span className="text-xs text-gray-500">
                {formatTime(notification.timestamp)}
              </span>
            </div>
          </div>
          
          <p className="text-sm text-gray-300 mb-3">{notification.message}</p>
          
          {notification.userName && (
            <div className="flex items-center space-x-2 mb-3">
              <img
                src={notification.userAvatar}
                alt={notification.userName}
                className="w-6 h-6 rounded-full object-cover"
              />
              <span className="text-xs text-gray-400">{notification.userName}</span>
            </div>
          )}
          
          {notification.actionUrl && (
            <div className="flex items-center space-x-2">
              <button
                onClick={() => navigate(notification.actionUrl)}
                className="text-sm text-primary hover:text-secondary transition-colors"
              >
                View Details
              </button>
              
              {!notification.isRead && (
                <button
                  onClick={() => handleMarkAsRead(notification.id)}
                  className="text-sm text-gray-400 hover:text-white transition-colors"
                >
                  Mark as Read
                </button>
              )}
              
              <button
                onClick={() => handleClearNotification(notification.id)}
                className="text-sm text-red-400 hover:text-red-300 transition-colors"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
          )}
        </div>
      </div>
    </motion.div>
  );

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-primary">
        <LoadingSpinner size="large" />
      </div>
    );
  }

  const unreadCount = notifications.filter(n => !n.isRead).length;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-8 p-6"
    >
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold text-white mb-2">Notifications</h1>
          <p className="text-gray-400">
            {unreadCount > 0 ? `${unreadCount} unread notifications` : 'All caught up!'}
          </p>
          {error && (
            <p className="text-sm text-red-400 mt-2">{error}</p>
          )}
        </div>
        
        {unreadCount > 0 && (
          <button
            onClick={handleMarkAllAsRead}
            className="bg-primary hover:bg-primary/80 text-white px-4 py-2 rounded-lg transition-colors"
          >
            Mark All as Read
          </button>
        )}
      </div>

      {/* Filter Tabs */}
      <div className="glass-morphism p-2 rounded-xl border border-gray-700 mb-8">
        <div className="flex space-x-1">
          {['all', 'unread', 'read'].map(tab => (
            <button
              key={tab}
              onClick={() => setFilter(tab)}
              className={`px-6 py-3 rounded-lg font-medium transition-colors ${
                filter === tab
                  ? 'bg-primary text-white'
                  : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
              }`}
            >
              {tab === 'all' ? 'All' : tab === 'unread' ? 'Unread' : 'Read'} 
              ({tab === 'all' ? notifications.length : 
                tab === 'unread' ? unreadCount : 
                notifications.length - unreadCount})
            </button>
          ))}
        </div>
      </div>

      {/* Clear All Button */}
      {notifications.length > 0 && (
        <div className="flex justify-end mb-6">
          <button
            onClick={handleClearAll}
            className="text-sm text-red-400 hover:text-red-300 transition-colors"
          >
            Clear All Notifications
          </button>
        </div>
      )}

      {/* Notifications List */}
      {filteredNotifications.length === 0 ? (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="text-center py-12"
        >
          <Bell className="w-12 h-12 text-gray-500 mx-auto mb-4" />
          <p className="text-gray-400 text-lg">
            {filter === 'unread' ? 'No unread notifications' : 
             filter === 'read' ? 'No read notifications' : 
             'No notifications'}
          </p>
          <p className="text-gray-500">
            {filter === 'unread' ? 'You\'re all caught up!' : 
             filter === 'read' ? 'No read notifications yet' : 
             'Stay tuned for updates'}
          </p>
        </motion.div>
      ) : (
        <div className="space-y-4">
          {filteredNotifications.map((notification, idx) => (
            <motion.div
              key={notification.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: idx * 0.1 }}
            >
              <NotificationCard notification={notification} />
            </motion.div>
          ))}
        </div>
      )}
    </motion.div>
  );
};

export default Notifications;
