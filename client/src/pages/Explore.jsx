import React, { useState, useEffect, useMemo } from 'react';
import { motion } from 'framer-motion';
import {
  Search,
  MapPin,
  Star,
  Users,
  MessageCircle,
} from 'lucide-react';
import axios from 'axios';
import { useAuth } from '../context/AuthContext';

import LoadingSpinner from '../components/LoadingSpinner';
import SwapRequestModal from '../components/SwapRequestModal';

const Explore = () => {
  const { user: currentUser } = useAuth();
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);

  const [searchTerm, setSearchTerm] = useState('');
  const [selectedLocation, setSelectedLocation] = useState('all');

  const [swapModalOpen, setSwapModalOpen] = useState(false);
  const [selectedUser, setSelectedUser] = useState(null);

  useEffect(() => {
    const loadUsers = async () => {
      setLoading(true);
      console.log('=== FETCHING USERS FROM BACKEND ===');

      try {
        const response = await axios.get(
          'http://localhost:8000/api/users'
        );
        
        console.log('=== USERS FETCHED SUCCESSFULLY ===');
        console.log('Response data:', response.data);
        console.log('Number of users:', response.data?.length || 0);

        setUsers(response.data || []);
      } catch (error) {
        console.error('=== USERS FETCH ERROR ===');
        console.error('Error fetching users:', error);
        
        if (error.response) {
          console.error('Response status:', error.response.status);
          console.error('Response data:', error.response.data);
        }
        
        setUsers([]);
      } finally {
        setLoading(false);
      }
    };

    loadUsers();
  }, []);

  const filteredUsers = useMemo(() => {
    let filtered = users.filter((user) => {
      return user.id !== currentUser?.id;
    });

    // Search Filter
    if (searchTerm) {
      filtered = filtered.filter((user) => {
        return (
          user.name?.toLowerCase().includes(
            searchTerm.toLowerCase()
          ) ||
          user.bio?.toLowerCase().includes(
            searchTerm.toLowerCase()
          ) ||
          user.skills_offered?.some((skill) =>
            skill.toLowerCase().includes(
              searchTerm.toLowerCase()
            )
          ) ||
          user.skills_wanted?.some((skill) =>
            skill.toLowerCase().includes(
              searchTerm.toLowerCase()
            )
          )
        );
      });
    }


    // Location Filter
    if (selectedLocation !== 'all') {
      filtered = filtered.filter((user) => {
        return (
          user.location?.city
            ?.toLowerCase()
            .includes(selectedLocation.toLowerCase()) ||
          user.location?.country
            ?.toLowerCase()
            .includes(selectedLocation.toLowerCase())
        );
      });
    }


    return filtered;
  }, [
    users,
    searchTerm,
    selectedLocation,
  ]);


  const locations = [
    'all',
    ...Array.from(
      new Set(
        users
          .map((u) => u.location?.city || '')
          .filter(Boolean)
      )
    ),
  ];

  const handleConnect = (user) => {
    // STEP 2 — DEBUG MODAL OPENING
    console.log("=== CLICKED USER ===");
    console.log("clicked user:", user);
    console.log("clicked user email:", user?.email);
    console.log("clicked user id:", user?.id);
    console.log("current user:", currentUser);
    console.log("current user email:", currentUser?.email);
    
    setSelectedUser(user);
    setSwapModalOpen(true);
  };

  const UserCard = ({ user }) => (
    <motion.div
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      whileHover={{ scale: 1.02 }}
      className="glass-morphism p-6 rounded-xl border border-gray-700 hover:border-primary transition-all cursor-pointer"
      onClick={() => handleConnect(user)}
    >
      <div className="flex items-start space-x-4">
        <img
          src={
            user.avatar ||
            `https://ui-avatars.com/api/?name=${encodeURIComponent(user.name)}&background=6366f1&color=fff`
          }
          alt={user.name}
          className="w-16 h-16 rounded-full object-cover"
          onError={(e) => {
            e.target.src = `https://api.dicebear.com/7.x/initials/svg?seed=${encodeURIComponent(user.name)}`;
          }}
        />

        <div className="flex-1 min-w-0">
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-lg font-semibold text-white">
              {user.name}
            </h3>

            <div className="flex items-center space-x-1">
              <Star className="w-4 h-4 text-yellow-400 fill-current" />

              <span className="text-sm text-gray-300">
                {(user.rating || 0).toFixed(1)}
              </span>

              <span className="text-xs text-gray-500">
                ({user.total_reviews || 0})
              </span>
            </div>
          </div>

          <div className="space-y-3">
            <div className="flex items-center space-x-2 text-sm text-gray-400">
              <MapPin className="w-4 h-4" />

              <span>
                {user.location?.city ||
                  'Location not set'}
              </span>

              <span>•</span>

              <span>
                {user.location?.country || ''}
              </span>
            </div>

            {/* Skills Offered */}
            <div className="flex flex-wrap gap-2">
              <span className="text-xs text-gray-500 w-full">
                Offers:
              </span>

              {user.skills_offered
                ?.slice(0, 3)
                .map((skill, index) => (
                  <span
                    key={index}
                    className="px-2 py-1 bg-primary/20 text-primary rounded-full text-xs"
                  >
                    {skill}
                  </span>
                ))}

              {(user.skills_offered?.length || 0) >
                3 && (
                <span className="px-2 py-1 bg-gray-700 text-gray-400 rounded-full text-xs">
                  +
                  {(user.skills_offered?.length || 0) -
                    3}
                </span>
              )}
            </div>

            {/* Skills Wanted */}
            <div className="flex flex-wrap gap-2">
              <span className="text-xs text-gray-500 w-full">
                Wants:
              </span>

              {user.skills_wanted
                ?.slice(0, 3)
                .map((skill, index) => (
                  <span
                    key={index}
                    className="px-2 py-1 bg-secondary/20 text-secondary rounded-full text-xs"
                  >
                    {skill}
                  </span>
                ))}

              {(user.skills_wanted?.length || 0) >
                3 && (
                <span className="px-2 py-1 bg-gray-700 text-gray-400 rounded-full text-xs">
                  +
                  {(user.skills_wanted?.length || 0) -
                    3}
                </span>
              )}
            </div>
          </div>

          <div className="mt-4 flex items-center justify-between">
            <div className="text-sm text-gray-500">
              {user.is_online ? (
                <div className="flex items-center space-x-1">
                  <div className="w-2 h-2 bg-green-400 rounded-full"></div>

                  <span>Online now</span>
                </div>
              ) : (
                <div className="flex items-center space-x-1">
                  <div className="w-2 h-2 bg-gray-400 rounded-full"></div>

                  <span>
                    Last seen{' '}
                    {user.last_seen || 'recently'}
                  </span>
                </div>
              )}
            </div>

            <button className="bg-gradient-to-r from-primary to-secondary hover:shadow-lg text-white px-4 py-2 rounded-lg transition-all flex items-center space-x-2">
              <MessageCircle className="w-4 h-4" />

              <span>Connect</span>
            </button>
          </div>
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

  return (
    <>
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="space-y-8 p-6"
      >
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-white mb-2">
            Explore Users
          </h1>

          <p className="text-gray-400">
            Discover skilled people and connect for
            skill exchange
          </p>
        </div>

        {/* Filters */}
        <div className="glass-morphism p-6 rounded-xl border border-gray-700 mb-8">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-6">
            {/* Search */}
            <div className="lg:col-span-2">
              <label className="block text-sm font-medium text-gray-300 mb-2">
                <Search className="w-4 h-4 inline mr-2" />
                Search Users
              </label>

              <input
                type="text"
                value={searchTerm}
                onChange={(e) =>
                  setSearchTerm(e.target.value)
                }
                placeholder="Search by name or skills..."
                className="w-full px-4 py-2 bg-gray-800 border border-gray-600 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-primary"
              />
            </div>

            {/* Location */}
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                <MapPin className="w-4 h-4 inline mr-2" />
                Location
              </label>

              <select
                value={selectedLocation}
                onChange={(e) =>
                  setSelectedLocation(e.target.value)
                }
                className="w-full px-4 py-2 bg-gray-800 border border-gray-600 rounded-lg text-white"
              >
                {locations.map((location) => (
                  <option
                    key={location}
                    value={location}
                  >
                    {location === 'all'
                      ? 'All Locations'
                      : location}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {/* Filter Summary */}
          <div className="flex items-center justify-between">
            <div className="text-sm text-gray-400">
              Showing {filteredUsers.length} of{' '}
              {users.length} users
            </div>

            {(searchTerm || selectedLocation !== 'all') && (
              <button
                onClick={() => {
                  setSearchTerm('');
                  setSelectedLocation('all');
                }}
                className="text-sm text-primary hover:text-secondary transition-colors"
              >
                Clear Filters
              </button>
            )}
          </div>
        </div>

        {/* User Grid */}
        {filteredUsers.length === 0 ? (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="text-center py-12"
          >
            <Users className="w-12 h-12 text-gray-500 mx-auto mb-4" />

            <p className="text-gray-400 text-lg">
              No users found
            </p>

            <p className="text-gray-500">
              Try adjusting your filters
            </p>
          </motion.div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredUsers.map((user, index) => (
              <motion.div
                key={user.id || index}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{
                  delay: index * 0.05,
                }}
              >
                <UserCard user={user} />
              </motion.div>
            ))}
          </div>
        )}
      </motion.div>

      {/* Swap Request Modal */}
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
    </>
  );
};

export default Explore;