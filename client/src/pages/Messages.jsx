import React, { useState, useEffect, useRef } from 'react';
import { motion } from 'framer-motion';
import { Send, Search, MoreVertical, CheckCheck } from 'lucide-react';
import axios from 'axios';
import LoadingSpinner from '../components/LoadingSpinner';
import { useAuth } from '../context/AuthContext';

const API_BASE_URL = import.meta.env.VITE_API_URL;

const avatarFallback = (name, size = 'large') => {
  const sizeClass = size === 'small' ? 'w-8 h-8 text-xs' : 'w-10 h-10 text-sm';

  return (
    <div className={`${sizeClass} rounded-full bg-gray-700 flex items-center justify-center text-white font-semibold`}>
      {(name || '?').charAt(0).toUpperCase()}
    </div>
  );
};

const ConversationView = ({
  conversation,
  messagesLoading,
  isTyping,
  newMessage,
  setNewMessage,
  handleKeyPress,
  handleSendMessage,
  sending,
  inputRef,
  messagesEndRef,
  formatTime
}) => (
  <motion.div
    initial={{ opacity: 0, x: 20 }}
    animate={{ opacity: 1, x: 0 }}
    className="h-full flex flex-col"
  >
    {/* Header */}
    <div className="glass-morphism border-b border-gray-700 p-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          {conversation.userAvatar ? (
            <img
              src={conversation.userAvatar}
              alt={conversation.userName}
              className="w-10 h-10 rounded-full object-cover"
            />
          ) : avatarFallback(conversation.userName)}
          <div>
            <h3 className="text-lg font-semibold text-white">{conversation.userName}</h3>
            <div className="flex items-center space-x-2">
              <div className={`w-2 h-2 rounded-full ${conversation.isOnline ? 'bg-green-400' : 'bg-gray-500'}`} />
              <span className="text-sm text-gray-400">
                {conversation.isOnline ? 'Online' : 'Offline'}
              </span>
            </div>
          </div>
        </div>
        <div className="text-sm text-gray-400">
          Last seen: {formatTime(conversation.lastMessageTime) || 'Unknown'}
        </div>
      </div>
    </div>

    {/* Messages */}
    <div className="flex-1 overflow-y-auto p-4 space-y-4">
      {messagesLoading ? (
        <div className="h-full flex items-center justify-center">
          <LoadingSpinner size="medium" />
        </div>
      ) : conversation.messages.length === 0 ? (
        <div className="h-full flex items-center justify-center text-gray-500">
          <p>No messages yet</p>
        </div>
      ) : conversation.messages.map((message, idx) => (
        <motion.div
          key={message.id}
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: idx * 0.05 }}
          className={`flex ${message.isOwn ? 'justify-end' : 'justify-start'} mb-4`}
        >
          {!message.isOwn && idx === 0 && (
            <div className="text-xs text-gray-500 mb-2">
              Started conversation with {conversation.userName}
            </div>
          )}

          <div className={`max-w-xs lg:max-w-md px-4 py-2 rounded-2xl ${
            message.isOwn
              ? 'bg-primary text-white'
              : 'bg-gray-800 text-gray-100'
          }`}>
            <div className="text-sm">{message.content}</div>
            <div className={`text-xs text-gray-500 mt-1 ${
              message.isOwn ? 'text-right' : 'text-left'
            }`}>
              {formatTime(message.created_at)}
            </div>
          </div>
        </motion.div>
      ))}
      <div ref={messagesEndRef} />
    </div>

    {/* Message Input */}
    <div className="glass-morphism border-t border-gray-700 p-4">
      {isTyping && (
        <div className="text-xs text-gray-500 mb-2">You are typing...</div>
      )}
      <div className="flex items-center space-x-2">
        <input
          ref={inputRef}
          type="text"
          value={newMessage}
          onChange={(e) => setNewMessage(e.target.value)}
          onKeyDown={handleKeyPress}
          placeholder="Type a message..."
          className="flex-1 px-4 py-2 bg-gray-800 border border-gray-600 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
        />
        <button
          onClick={handleSendMessage}
          disabled={!newMessage.trim() || sending}
          className="bg-primary hover:bg-primary/80 text-white p-2 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <Send className="w-4 h-4" />
        </button>
      </div>
    </div>
  </motion.div>
);

const Messages = () => {
  const { user, token, logout } = useAuth();
  const [conversations, setConversations] = useState([]);
  const [selectedConversation, setSelectedConversation] = useState(null);
  const [loading, setLoading] = useState(true);
  const [messagesLoading, setMessagesLoading] = useState(false);
  const [sending, setSending] = useState(false);
  const [error, setError] = useState('');
  const [searchTerm, setSearchTerm] = useState('');
  const [newMessage, setNewMessage] = useState('');
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);
  const activeConversationIdRef = useRef(null);

  const authHeaders = () => ({
    Authorization: `Bearer ${token || localStorage.getItem('authToken')}`
  });

  const currentUserId = user?.id || user?._id;

  const normalizeConversation = (conversation) => {
    const participant = conversation.other_participant || conversation.otherParticipant || {};
    const name = participant.name || 'Unknown user';

    return {
      id: conversation.conversation_id,
      conversation_id: conversation.conversation_id,
      receiverId: participant.id,
      userName: name,
      userAvatar: participant.avatar,
      isOnline: Boolean(participant.is_online),
      lastMessage: conversation.last_message || '',
      lastMessageTime: conversation.updated_at,
      unreadCount: conversation.unread_count || 0,
      messages: []
    };
  };

  const normalizeMessage = (message) => ({
    id: message.id,
    senderId: message.sender_id,
    receiverId: message.receiver_id,
    content: message.message || message.content || '',
    created_at: message.created_at,
    isOwn: String(message.sender_id) === String(currentUserId),
    isRead: Boolean(message.is_read)
  });

  const parseUtcTimestamp = (timestamp) => {
    if (!timestamp) return null;

    if (timestamp instanceof Date) {
      return timestamp;
    }

    if (typeof timestamp === 'string') {
      const hasTimezone = /(?:Z|[+-]\d{2}:?\d{2})$/i.test(timestamp);
      return new Date(hasTimezone ? timestamp : `${timestamp}Z`);
    }

    return new Date(timestamp);
  };

  const handleRequestError = (err, fallbackMessage) => {
    if (err.response?.status === 401) {
      setError('Your session has expired. Please log in again.');
      logout();
      return;
    }

    setError(err.response?.data?.message || err.response?.data?.detail || fallbackMessage);
  };

  useEffect(() => {
    activeConversationIdRef.current = selectedConversation?.id || null;
  }, [selectedConversation?.id]);

  const fetchConversations = async ({ showLoader = false } = {}) => {
    if (!token && !localStorage.getItem('authToken')) {
      if (showLoader) setLoading(false);
      return;
    }

    try {
      if (showLoader) setLoading(true);
      const response = await axios.get(`${API_BASE_URL}/api/messages/conversations`, {
        headers: authHeaders()
      });

      const nextConversations = Array.isArray(response.data)
        ? response.data.map(normalizeConversation)
        : [];

      setConversations(prev => {
        const messagesByConversation = new Map(prev.map(conv => [conv.id, conv.messages || []]));
        return nextConversations.map(conv => ({
          ...conv,
          messages: messagesByConversation.get(conv.id) || []
        }));
      });

      setError('');
    } catch (err) {
      handleRequestError(err, 'Failed to load conversations');
    } finally {
      if (showLoader) setLoading(false);
    }
  };

  const fetchMessages = async (conversationId, { showLoader = false } = {}) => {
    if (!conversationId || (!token && !localStorage.getItem('authToken'))) return;

    try {
      if (showLoader) setMessagesLoading(true);
      const response = await axios.get(`${API_BASE_URL}/api/messages/${conversationId}`, {
        headers: authHeaders()
      });

      const nextMessages = Array.isArray(response.data)
        ? response.data.map(normalizeMessage).sort((a, b) => parseUtcTimestamp(a.created_at) - parseUtcTimestamp(b.created_at))
        : [];

      const unreadReceivedMessages = nextMessages.filter(message => !message.isOwn && !message.isRead);
      if (unreadReceivedMessages.length > 0) {
        await Promise.all(unreadReceivedMessages.map(message =>
          axios.put(`${API_BASE_URL}/api/messages/read/${message.id}`, {}, {
            headers: authHeaders()
          })
        ));
      }

      const displayMessages = nextMessages.map(message => (
        message.isOwn ? message : { ...message, isRead: true }
      ));

      setConversations(prev => prev.map(conv =>
        conv.id === conversationId ? { ...conv, messages: displayMessages, unreadCount: 0 } : conv
      ));

      setSelectedConversation(prev =>
        prev?.id === conversationId ? { ...prev, messages: displayMessages, unreadCount: 0 } : prev
      );

      setError('');
    } catch (err) {
      handleRequestError(err, 'Failed to load messages');
    } finally {
      if (showLoader) setMessagesLoading(false);
    }
  };

  useEffect(() => {
    fetchConversations({ showLoader: true });
  }, [token]);

  useEffect(() => {
    const intervalId = setInterval(() => {
      fetchConversations();
      if (activeConversationIdRef.current) {
        fetchMessages(activeConversationIdRef.current);
      }
    }, 5000);

    return () => clearInterval(intervalId);
  }, [token, currentUserId]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [selectedConversation?.messages]);

  const filteredConversations = conversations.filter(conv =>
    conv.userName.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const handleSendMessage = async () => {
    const text = newMessage.trim();
    if (!text || !selectedConversation || sending) return;

    try {
      setSending(true);
      await axios.post(`${API_BASE_URL}/api/messages/send`, {
        receiver_id: selectedConversation.receiverId,
        message: text
      }, {
        headers: authHeaders()
      });

      setNewMessage('');
      await fetchMessages(selectedConversation.id);
      await fetchConversations();
      setError('');
    } catch (err) {
      handleRequestError(err, 'Failed to send message');
    } finally {
      setSending(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const formatTime = (timestamp) => {
    if (!timestamp) return '';

    const date = parseUtcTimestamp(timestamp);
    if (Number.isNaN(date.getTime())) return '';

    const now = new Date();
    const diff = Math.max(0, now - date);
    
    if (diff < 60000) { // Less than 1 minute
      return 'Just now';
    } else if (diff < 3600000) { // Less than 1 hour
      const minutes = Math.floor(diff / 60000);
      return `${minutes} ${minutes === 1 ? 'min' : 'mins'} ago`;
    } else if (diff < 86400000) { // Less than 1 day
      const hours = Math.floor(diff / 3600000);
      return `${hours} ${hours === 1 ? 'hour' : 'hours'} ago`;
    } else {
      return date.toLocaleDateString();
    }
  };

  const selectConversation = (conversation) => {
    setSelectedConversation(conversation);
    fetchMessages(conversation.id, { showLoader: true });
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-primary">
        <LoadingSpinner size="large" />
      </div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="h-full flex"
    >
      {/* Conversations Sidebar */}
      <div className="w-80 glass-morphism border-r border-gray-700 flex flex-col">
        <div className="p-4 border-b border-gray-700">
          <h2 className="text-lg font-semibold text-white mb-4">Messages</h2>
          {error && (
            <div className="mb-3 text-sm text-red-400">
              {error}
            </div>
          )}
          
          {/* Search */}
          <div className="relative">
            <Search className="absolute left-3 top-3 w-4 h-4 text-gray-400" />
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Search conversations..."
              className="w-full pl-10 pr-4 py-2 bg-gray-800 border border-gray-600 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
            />
          </div>
        </div>

        {/* Conversation List */}
        <div className="flex-1 overflow-y-auto">
          {filteredConversations.length === 0 ? (
            <div className="text-center py-8">
              <CheckCheck className="w-12 h-12 text-gray-500 mx-auto mb-4" />
              <p className="text-gray-400">No conversations found</p>
            </div>
          ) : (
            filteredConversations.map((conversation, idx) => (
              <motion.div
                key={conversation.id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: idx * 0.1 }}
                className={`p-3 cursor-pointer hover:bg-gray-700 transition-colors ${
                  selectedConversation?.id === conversation.id ? 'bg-gray-700' : ''
                }`}
                onClick={() => selectConversation(conversation)}
              >
                <div className="flex items-center space-x-3">
                  <div className="relative">
                    {conversation.userAvatar ? (
                      <img
                        src={conversation.userAvatar}
                        alt={conversation.userName}
                        className="w-8 h-8 rounded-full object-cover"
                      />
                    ) : (
                      avatarFallback(conversation.userName, 'small')
                    )}
                    {conversation.unreadCount > 0 && (
                      <div className="absolute -top-1 -right-1 w-5 h-5 bg-red-500 rounded-full flex items-center justify-center text-xs text-white font-bold">
                        {conversation.unreadCount}
                      </div>
                    )}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="text-sm font-medium text-white truncate">
                      {conversation.userName}
                    </div>
                    <div className="text-xs text-gray-400 truncate">
                      {conversation.lastMessage}
                    </div>
                  </div>
                </div>
                <div className="text-xs text-gray-500">
                  {formatTime(conversation.lastMessageTime)}
                </div>
              </motion.div>
            ))
          )}
        </div>
      </div>

      {/* Selected Conversation */}
      {selectedConversation ? (
        <ConversationView
          conversation={selectedConversation}
          messagesLoading={messagesLoading}
          isTyping={newMessage.length > 0}
          newMessage={newMessage}
          setNewMessage={setNewMessage}
          handleKeyPress={handleKeyPress}
          handleSendMessage={handleSendMessage}
          sending={sending}
          inputRef={inputRef}
          messagesEndRef={messagesEndRef}
          formatTime={formatTime}
        />
      ) : (
        <div className="flex-1 flex items-center justify-center text-gray-500">
          <div className="text-center">
            <MoreVertical className="w-12 h-12 mx-auto mb-4" />
            <p className="text-lg">Select a conversation to start messaging</p>
          </div>
        </div>
      )}
    </motion.div>
  );
};

export default Messages;
