import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Send, User, Clock, Calendar, Star } from 'lucide-react';
import axios from 'axios';
import { useAuth } from '../context/AuthContext';

const SwapRequestModal = ({ isOpen, onClose, targetUser }) => {
  const { user } = useAuth();
  const [offeredSkill, setOfferedSkill] = useState('');
  const [requestedSkill, setRequestedSkill] = useState('');
  const [message, setMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // STEP 1 — DEBUG MODAL VALUES
  console.log("=== CURRENT USER ===");
  console.log("currentUser:", user);
  console.log("currentUser email:", user?.email);
  console.log("currentUser id:", user?.id);
  
  console.log("=== TARGET USER ===");
  console.log("targetUser:", targetUser);
  console.log("targetUser email:", targetUser?.email);
  console.log("targetUser id:", targetUser?.id);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!offeredSkill || !requestedSkill || !message) {
      setError('Please fill in all required fields');
      return;
    }
    
    // Validate message length (minimum 10 characters)
    if (message.trim().length < 10) {
      setError('Message must be at least 10 characters long');
      return;
    }

    setLoading(true);
    setError('');
    
    try {
      // Get JWT token from localStorage
      const token = localStorage.getItem('authToken');
      
      // STEP 2 — ADD FINAL DEBUGGING
      console.log("=== CURRENT USER ===");
      console.log("Current User:", user);
      console.log("Current User Email:", user?.email);
      console.log("Current User ID:", user?.id);
      
      console.log("=== TARGET USER ===");
      console.log("Target User:", targetUser);
      console.log("Target User Email:", targetUser?.email);
      console.log("Target User ID:", targetUser?.id);
      console.log("Target User _id:", targetUser?._id);
      
      // CORRECT PAYLOAD - Receiver MUST be target profile user
      const swapRequestData = {
        receiver_id: targetUser?.id || targetUser?._id,
        offered_skill: {
          skill: offeredSkill,
          category: "technology", // Valid SkillCategory enum
          description: `Offering skill: ${offeredSkill}`
        },
        requested_skill: {
          skill: requestedSkill,
          category: "technology", // Valid SkillCategory enum
          description: `Want to learn: ${requestedSkill}`
        },
        message,
        proposed_duration: 60 // Default 1 hour
      };
      
      console.log("=== SWAP PAYLOAD ===");
      console.log("Final swapRequestData:", swapRequestData);
      console.log("receiver_id being sent:", swapRequestData.receiver_id);
      console.log("Expected receiver_id (target user):", targetUser?.id || targetUser?._id);
      console.log("Should NOT be current user ID:", user?.id);
      console.log("Is receiver_id correct?", swapRequestData.receiver_id !== user?.id);
      
      console.log('=== SWAP REQUEST ===');
      console.log('Token:', token ? 'Present' : 'Missing');
      console.log('Target User:', targetUser.email);
      console.log('=== SWAP PAYLOAD ===');
      console.log('Swap Request Data:', swapRequestData);
      console.log('=== FINAL SWAP PAYLOAD ===');
      console.log(JSON.stringify(swapRequestData, null, 2));
      console.log('=== PAYLOAD VERIFICATION ===');
      console.log('offered_skill type:', typeof swapRequestData.offered_skill);
      console.log('requested_skill type:', typeof swapRequestData.requested_skill);
      console.log('offered_skill value:', swapRequestData.offered_skill);
      console.log('requested_skill value:', swapRequestData.requested_skill);

      // Send to backend API with Authorization header (note trailing slash)
      const response = await axios.post('http://localhost:8000/api/swaps/', swapRequestData, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      
      if (response.data) {
        // Clear form
        setOfferedSkill('');
        setRequestedSkill('');
        setMessage('');
        
        // Close modal
        onClose();
        
        alert('Swap request sent successfully!');
      }
      
    } catch (error) {
      console.error('=== SWAP ERROR ===');
      console.error('Error:', error);
      console.error('Response:', error.response);
      console.error('Status:', error.response?.status);
      console.error('Data:', error.response?.data);
      
      // Safely extract error message as string
      let errorMessage = 'Failed to send swap request. Please try again.';
      
      if (error.response?.data) {
        const details = error.response.data.detail;
        
        if (Array.isArray(details)) {
          // Handle array of validation errors
          errorMessage = details.map(item => item.msg || item.message || item).join(', ');
        } else if (typeof details === 'string') {
          // Handle single detail message
          errorMessage = details;
        } else if (error.response.data.message) {
          // Handle message field
          errorMessage = String(error.response.data.message);
        } else {
          // Handle any other structure
          errorMessage = String(error.response.data);
        }
      }
      
      console.error('Final Error Message:', errorMessage);
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
        onClick={onClose}
      >
        <motion.div
          initial={{ scale: 0.9, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          exit={{ scale: 0.9, opacity: 0 }}
          className="bg-gray-800 rounded-xl p-6 max-w-md w-full max-h-[90vh] overflow-y-auto border border-gray-700"
          onClick={(e) => e.stopPropagation()}
        >
          {/* Header */}
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-bold text-white flex items-center">
              <User className="w-5 h-5 mr-2" />
              Request Skill Swap
            </h2>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-white transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* User Info */}
          <div className="flex items-center space-x-4 mb-6 p-4 bg-gray-700 rounded-lg">
            <img
              src={targetUser.avatar || `https://ui-avatars.com/api/?name=${encodeURIComponent(targetUser.name)}&background=6366f1&color=fff`}
              alt={targetUser.name}
              className="w-12 h-12 rounded-full"
              onError={(e) => {
                e.target.src = `https://api.dicebear.com/7.x/initials/svg?seed=${encodeURIComponent(targetUser.name)}`;
              }}
            />
            <div>
              <h3 className="text-lg font-semibold text-white">{targetUser.name}</h3>
              <p className="text-sm text-gray-400">{targetUser.email}</p>
              <div className="flex items-center space-x-1 mt-1">
                <Star className="w-4 h-4 text-yellow-400 fill-current" />
                <span className="text-sm text-gray-300">
                  {targetUser.rating || 'No rating'}
                </span>
              </div>
            </div>
          </div>

          {/* Form */}
          <form onSubmit={handleSubmit} className="space-y-4">
            {/* What You Can Offer */}
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                What can you offer?
              </label>
              <input
                type="text"
                value={offeredSkill}
                onChange={(e) => setOfferedSkill(e.target.value)}
                placeholder="Enter a skill you can teach..."
                className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
                required
              />
            </div>

            {/* What You Want */}
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                What do you want to learn?
              </label>
              <input
                type="text"
                value={requestedSkill}
                onChange={(e) => setRequestedSkill(e.target.value)}
                placeholder="Enter a skill you want to learn..."
                className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
                required
              />
            </div>

            {/* Message */}
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Message
              </label>
              <textarea
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                placeholder="Introduce yourself and explain why you'd like to swap skills..."
                className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent resize-none"
                rows="4"
                required
              />
            </div>

            {/* Error Message */}
            {error && (
              <div className="p-3 bg-red-900/20 border border-red-600 rounded-lg">
                <p className="text-sm text-red-400">{error}</p>
              </div>
            )}

            {/* Submit Button */}
            <button
              type="submit"
              disabled={loading}
              className="w-full bg-gradient-to-r from-primary to-secondary hover:shadow-lg text-white py-3 rounded-lg transition-all flex items-center justify-center space-x-2 disabled:opacity-50"
            >
              {loading ? (
                <>
                  <div className="w-4 h-4 border-2 border-t-white border-r-transparent animate-spin rounded-full"></div>
                  <span>Sending...</span>
                </>
              ) : (
                <>
                  <Send className="w-4 h-4" />
                  <span>Send Swap Request</span>
                </>
              )}
            </button>
          </form>

          {/* Footer Info */}
          <div className="mt-4 p-3 bg-gray-700 rounded-lg">
            <div className="flex items-center text-sm text-gray-400">
              <Clock className="w-4 h-4 mr-2" />
              <span>Response time: Usually within 24-48 hours</span>
            </div>
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
};

export default SwapRequestModal;
