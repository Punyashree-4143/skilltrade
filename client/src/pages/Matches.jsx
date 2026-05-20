import React, { useEffect, useMemo, useState } from 'react';
import { motion } from 'framer-motion';
import {
  ArrowRight,
  Heart,
  MessageCircle,
  Star,
  Target,
  TrendingUp,
  Users
} from 'lucide-react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import LoadingSpinner from '../components/LoadingSpinner';
import SwapRequestModal from '../components/SwapRequestModal';

const API_BASE_URL = 'http://localhost:8000';

const Matches = () => {
  const { user, token } = useAuth();
  const navigate = useNavigate();
  const [matches, setMatches] = useState([]);
  const [loading, setLoading] = useState(true);
  const [sortBy, setSortBy] = useState('compatibility');
  const [error, setError] = useState('');
  const [swapModalOpen, setSwapModalOpen] = useState(false);
  const [selectedUser, setSelectedUser] = useState(null);

  const authHeaders = () => ({
    Authorization: `Bearer ${token || localStorage.getItem('authToken')}`
  });

  const normalizeMatch = (item) => {
    const matchedUser = item.user || {};

    return {
      id: matchedUser.id,
      user: matchedUser,
      name: matchedUser.name || 'Unknown user',
      email: matchedUser.email,
      avatar: matchedUser.avatar,
      bio: matchedUser.bio,
      location: matchedUser.location || {},
      experienceLevel: matchedUser.experience_level || 'intermediate',
      rating: matchedUser.rating || 0,
      compatibilityScore: item.match_percentage || 0,
      matchType: item.match_type || 'potential',
      matchingSkills: item.matching_skills || [],
      sharedSkills: item.offered_skill_matches || [],
      mutualInterests: item.wanted_skill_matches || [],
      skillsOffered: matchedUser.skills_offered || [],
      skillsWanted: matchedUser.skills_wanted || []
    };
  };

  useEffect(() => {
    const fetchMatches = async () => {
      const authToken = token || localStorage.getItem('authToken');
      if (!authToken) {
        setMatches([]);
        setLoading(false);
        return;
      }

      try {
        setLoading(true);
        const response = await axios.get(`${API_BASE_URL}/api/matches`, {
          headers: authHeaders()
        });

        const realMatches = Array.isArray(response.data)
          ? response.data.map(normalizeMatch)
          : [];

        setMatches(realMatches);
        setError('');
      } catch (err) {
        console.error('Error fetching matches:', err);
        setMatches([]);
        setError(err.response?.data?.message || err.response?.data?.detail || 'Failed to load matches');
      } finally {
        setLoading(false);
      }
    };

    if (user || token || localStorage.getItem('authToken')) {
      fetchMatches();
    } else {
      setLoading(false);
    }
  }, [user, token]);

  const filteredMatches = useMemo(() => {
    const filtered = [...matches];

    switch (sortBy) {
      case 'compatibility':
        filtered.sort((a, b) => b.compatibilityScore - a.compatibilityScore);
        break;
      case 'newest':
        filtered.sort((a, b) => a.name.localeCompare(b.name));
        break;
      case 'rating':
        filtered.sort((a, b) => b.rating - a.rating);
        break;
      default:
        break;
    }

    return filtered;
  }, [matches, sortBy]);

  const getMatchTypeColor = (type) => {
    switch (type) {
      case 'excellent': return 'text-green-400';
      case 'good': return 'text-blue-400';
      case 'potential': return 'text-yellow-400';
      default: return 'text-gray-400';
    }
  };

  const getMatchTypeBg = (type) => {
    switch (type) {
      case 'excellent': return 'bg-green-900';
      case 'good': return 'bg-blue-900';
      case 'potential': return 'bg-yellow-900';
      default: return 'bg-gray-900';
    }
  };

  const openSwapRequest = (match) => {
    setSelectedUser(match.user);
    setSwapModalOpen(true);
  };

  const startConversation = async (match) => {
    try {
      await axios.post(`${API_BASE_URL}/api/messages/send`, {
        receiver_id: match.id,
        message: 'Hi!'
      }, {
        headers: authHeaders()
      });

      navigate('/app/messages');
    } catch (err) {
      console.error('START CONVERSATION ERROR', err);
      alert(err.response?.data?.message || err.response?.data?.detail || 'You can message users after an accepted swap.');
    }
  };

  const MatchCard = ({ match }) => (
    <motion.div
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      whileHover={{ scale: 1.02 }}
      className="glass-morphism p-6 rounded-xl border border-gray-700 hover:border-primary transition-all cursor-pointer"
    >
      <div className="flex items-start space-x-4">
        <img
          src={match.avatar || `https://ui-avatars.com/api/?name=${encodeURIComponent(match.name)}&background=6366f1&color=fff`}
          alt={match.name}
          className="w-16 h-16 rounded-full object-cover"
          onError={(e) => {
            e.target.src = `https://api.dicebear.com/7.x/initials/svg?seed=${encodeURIComponent(match.name)}`;
          }}
        />
        <div className="flex-1 min-w-0">
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-lg font-semibold text-white">{match.name}</h3>
            <div className="flex items-center space-x-2">
              <span className={`text-xs px-2 py-1 rounded-full ${getMatchTypeBg(match.matchType)}`}>
                {match.compatibilityScore}% Match
              </span>
              <span className={`text-sm ${getMatchTypeColor(match.matchType)}`}>
                {match.matchType}
              </span>
            </div>
          </div>

          <div className="space-y-2">
            <div className="flex items-center space-x-2 text-sm text-gray-400">
              <Users className="w-4 h-4" />
              <span>{match.location?.city || 'Location not set'}</span>
              <span>-</span>
              <span>{match.experienceLevel}</span>
            </div>

            {match.bio && (
              <p className="text-sm text-gray-300 line-clamp-2">{match.bio}</p>
            )}

            <div className="flex flex-wrap gap-1">
              {match.matchingSkills.slice(0, 3).map((skill, index) => (
                <span
                  key={index}
                  className="px-2 py-1 bg-primary/20 text-primary rounded-full text-xs"
                >
                  {skill}
                </span>
              ))}
              {match.matchingSkills.length > 3 && (
                <span className="px-2 py-1 bg-gray-700 text-gray-400 rounded-full text-xs">
                  +{match.matchingSkills.length - 3}
                </span>
              )}
            </div>

            <div className="flex flex-wrap gap-1">
              {match.skillsOffered.slice(0, 3).map((skill, index) => (
                <span
                  key={index}
                  className="px-2 py-1 bg-secondary/20 text-secondary rounded-full text-xs"
                >
                  {skill}
                </span>
              ))}
              {match.skillsOffered.length > 3 && (
                <span className="px-2 py-1 bg-gray-700 text-gray-400 rounded-full text-xs">
                  +{match.skillsOffered.length - 3}
                </span>
              )}
            </div>
          </div>

          <div className="mt-4 flex items-center justify-between">
            <div className="text-sm text-gray-500">
              You teach: <span className="text-primary font-medium">
                {match.sharedSkills.length > 0 ? match.sharedSkills.join(', ') : 'N/A'}
              </span>
            </div>
            <div className="text-sm text-gray-500">
              They teach: <span className="text-secondary font-medium">
                {match.mutualInterests.length > 0 ? match.mutualInterests.join(', ') : 'N/A'}
              </span>
            </div>
          </div>

          <div className="mt-4 grid grid-cols-2 gap-2">
            <button
              onClick={() => startConversation(match)}
              className="bg-gray-700 hover:bg-gray-600 text-white px-4 py-2 rounded-lg transition-all flex items-center justify-center space-x-2"
            >
              <MessageCircle className="w-4 h-4" />
              <span>Message User</span>
            </button>
            <button
              onClick={() => openSwapRequest(match)}
              className="bg-gradient-to-r from-primary to-secondary hover:shadow-lg text-white px-4 py-2 rounded-lg transition-all flex items-center justify-center space-x-2"
            >
              <Target className="w-4 h-4" />
              <span>Send Swap</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        </div>
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

  const excellentMatches = filteredMatches.filter(m => m.matchType === 'excellent');
  const goodMatches = filteredMatches.filter(m => m.matchType === 'good');
  const potentialMatches = filteredMatches.filter(m => m.matchType === 'potential');

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold text-white mb-2">Skill Matches</h1>
          <p className="text-gray-400">
            Find users who complement your skills and learning goals
          </p>
          {error && (
            <p className="text-sm text-red-400 mt-2">{error}</p>
          )}
        </div>

        <div className="flex items-center space-x-4">
          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value)}
            className="bg-gray-800 border border-gray-600 rounded-lg px-4 py-2 text-white focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
          >
            <option value="compatibility">Compatibility</option>
            <option value="newest">Newest</option>
            <option value="rating">Rating</option>
          </select>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="glass-morphism p-6 rounded-xl border border-gray-700">
          <div className="flex items-center justify-between mb-2">
            <Heart className="w-5 h-5 text-green-400" />
            <span className="text-2xl font-bold text-white">{excellentMatches.length}</span>
          </div>
          <p className="text-gray-400 text-sm">Excellent Matches</p>
        </div>

        <div className="glass-morphism p-6 rounded-xl border border-gray-700">
          <div className="flex items-center justify-between mb-2">
            <Star className="w-5 h-5 text-blue-400" />
            <span className="text-2xl font-bold text-white">{goodMatches.length}</span>
          </div>
          <p className="text-gray-400 text-sm">Good Matches</p>
        </div>

        <div className="glass-morphism p-6 rounded-xl border border-gray-700">
          <div className="flex items-center justify-between mb-2">
            <TrendingUp className="w-5 h-5 text-yellow-400" />
            <span className="text-2xl font-bold text-white">{potentialMatches.length}</span>
          </div>
          <p className="text-gray-400 text-sm">Potential Matches</p>
        </div>
      </div>

      {/* Matches Grid */}
      {filteredMatches.length === 0 ? (
        <div className="text-center py-12">
          <Users className="w-12 h-12 text-gray-500 mx-auto mb-4" />
          <p className="text-gray-400 text-lg">No matches found</p>
          <p className="text-gray-500">
            Try updating your skills or interests to find better matches
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredMatches.map((match, index) => (
            <motion.div
              key={match.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
            >
              <MatchCard match={match} />
            </motion.div>
          ))}
        </div>
      )}

      {selectedUser && (
        <SwapRequestModal
          isOpen={swapModalOpen}
          onClose={() => {
            setSwapModalOpen(false);
            setSelectedUser(null);
          }}
          targetUser={selectedUser}
        />
      )}
    </div>
  );
};

export default Matches;
