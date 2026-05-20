import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import {
  Calendar,
  CheckCircle,
  X,
  User,
  Star,
  MessageCircle
} from 'lucide-react';

import LoadingSpinner from '../components/LoadingSpinner';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const SwapRequests = () => {
  const navigate = useNavigate();
  const { user: currentUser, token } = useAuth();

  const [activeTab, setActiveTab] = useState('pending');
  const [loading, setLoading] = useState(true);
  const [startingConversationId, setStartingConversationId] = useState(null);

  const [swaps, setSwaps] = useState({
    incoming: [],
    outgoing: [],
    pending: [],
    accepted: [],
    completed: [],
    cancelled: []
  });

  // =========================
  // STATUS NORMALIZER
  // =========================

  const normalizeStatus = (status) => {
    if (!status) return '';

    return String(status)
      .toLowerCase()
      .replace('swapstatus.', '')
      .trim();
  };

  const getCurrentUserId = () => {
    return currentUser?.id || currentUser?._id;
  };

  const getOtherParticipant = (swap) => {
    const currentUserId = String(getCurrentUserId() || '');
    const senderId = String(swap?.sender_id || swap?.sender?.id || swap?.sender?._id || '');
    const receiverId = String(swap?.receiver_id || swap?.receiver?.id || swap?.receiver?._id || '');

    if (senderId && senderId === currentUserId) {
      return swap?.receiver || {
        id: receiverId,
        name: swap?.receiver_name || 'Unknown'
      };
    }

    if (receiverId && receiverId === currentUserId) {
      return swap?.sender || {
        id: senderId,
        name: swap?.sender_name || 'Unknown'
      };
    }

    return swap?.receiver || swap?.sender || null;
  };

  const getUserId = (user) => {
    return user?.id || user?._id;
  };

  // =========================
  // LOAD SWAPS
  // =========================

  const loadSwaps = async () => {

    try {

      setLoading(true);

      console.log("=== LOADING SWAPS ===");

      const token = localStorage.getItem('authToken');

      // =========================
      // FETCH RECEIVED
      // =========================

      console.log("=== FETCHING INCOMING SWAPS ===");

      const incomingResponse = await axios.get(
        'http://localhost:8000/api/swaps/?type=received',
        {
          headers: {
            Authorization: `Bearer ${token}`
          }
        }
      );

      console.log("=== INCOMING SWAPS RESPONSE ===");
      console.log(incomingResponse.data);

      // =========================
      // FETCH SENT
      // =========================

      console.log("=== FETCHING OUTGOING SWAPS ===");

      const outgoingResponse = await axios.get(
        'http://localhost:8000/api/swaps/?type=sent',
        {
          headers: {
            Authorization: `Bearer ${token}`
          }
        }
      );

      console.log("=== OUTGOING SWAPS RESPONSE ===");
      console.log(outgoingResponse.data);

      const incomingArray = Array.isArray(incomingResponse.data)
        ? incomingResponse.data
        : [];

      const outgoingArray = Array.isArray(outgoingResponse.data)
        ? outgoingResponse.data
        : [];

      console.log("=== ORGANIZING SWAPS ===");

      incomingArray.forEach((swap) => {
        console.log("RAW STATUS:", swap.status);
        console.log(
          "NORMALIZED:",
          normalizeStatus(swap.status)
        );
      });

      // =========================
      // FILTERS
      // =========================

      const allSwaps = [
        ...incomingArray,
        ...outgoingArray
      ];

      const pendingSwaps = allSwaps.filter(
        swap =>
          normalizeStatus(swap.status) === 'pending'
      );

      const acceptedSwaps = allSwaps.filter(
        swap =>
          normalizeStatus(swap.status) === 'accepted'
      );

      const completedSwaps = allSwaps.filter(
        swap =>
          normalizeStatus(swap.status) === 'completed'
      );

      const cancelledSwaps = allSwaps.filter(
        swap =>
          normalizeStatus(swap.status) === 'cancelled'
      );

      // =========================
      // FINAL ORGANIZED
      // =========================

      const organized = {
        incoming: incomingArray,
        outgoing: outgoingArray,
        pending: pendingSwaps,
        accepted: acceptedSwaps,
        completed: completedSwaps,
        cancelled: cancelledSwaps
      };

      console.log("=== FINAL ORGANIZED ===");

      console.log({
        incoming: incomingArray.length,
        outgoing: outgoingArray.length,
        pending: pendingSwaps.length,
        accepted: acceptedSwaps.length,
        completed: completedSwaps.length,
        cancelled: cancelledSwaps.length
      });

      setSwaps(organized);

    } catch (error) {

      console.error('Error loading swaps:', error);

      setSwaps({
        incoming: [],
        outgoing: [],
        pending: [],
        accepted: [],
        completed: [],
        cancelled: []
      });

    } finally {

      setLoading(false);

    }
  };

  // =========================
  // INITIAL LOAD
  // =========================

  useEffect(() => {
    loadSwaps();
  }, []);

  // =========================
  // ACCEPT
  // =========================

  const handleAcceptSwap = async (swapId) => {

    try {

      const token = localStorage.getItem('authToken');

      await axios.post(
        `http://localhost:8000/api/swaps/${swapId}/accept`,
        {},
        {
          headers: {
            Authorization: `Bearer ${token}`
          }
        }
      );

      console.log("Accepted swap:", swapId);

      await loadSwaps();

    } catch (error) {

      console.error(
        'Error accepting swap:',
        error
      );

    }
  };

  // =========================
  // REJECT
  // =========================

  const handleRejectSwap = async (swapId) => {

    try {

      const token = localStorage.getItem('authToken');

      await axios.post(
        `http://localhost:8000/api/swaps/${swapId}/reject`,
        {},
        {
          headers: {
            Authorization: `Bearer ${token}`
          }
        }
      );

      console.log("Rejected swap:", swapId);

      await loadSwaps();

    } catch (error) {

      console.error(
        'Error rejecting swap:',
        error
      );

    }
  };

  // =========================
  // COMPLETE
  // =========================

  const handleCompleteSwap = async (swapId) => {

    try {

      const token = localStorage.getItem('authToken');

      await axios.post(
        `http://localhost:8000/api/swaps/${swapId}/complete`,
        {},
        {
          headers: {
            Authorization: `Bearer ${token}`
          }
        }
      );

      console.log("Completed swap:", swapId);

      await loadSwaps();

    } catch (error) {

      console.error(
        'Error completing swap:',
        error
      );

    }
  };

  const startConversation = async (receiverId, swapId) => {
    try {
      const authToken = token || localStorage.getItem('authToken');

      if (!authToken) {
        console.error("START CONVERSATION ERROR", "Missing auth token");
        return;
      }

      if (!receiverId || String(receiverId) === String(getCurrentUserId())) {
        console.error("START CONVERSATION ERROR", "Invalid receiver");
        return;
      }

      setStartingConversationId(swapId);

      await axios.post(
        "http://localhost:8000/api/messages/send",
        {
          receiver_id: receiverId,
          message: "Hi!"
        },
        {
          headers: {
            Authorization: `Bearer ${authToken}`
          }
        }
      );

      navigate("/messages");

    } catch (error) {
      console.error("START CONVERSATION ERROR", error);
    } finally {
      setStartingConversationId(null);
    }
  };

  // =========================
  // CARD
  // =========================

  const SwapCard = ({ swap, type }) => {

    if (!swap) return null;

    console.log("=== FULL SWAP ===");
    console.log(swap);

    const otherParticipant = getOtherParticipant(swap);
    const otherParticipantId = getUserId(otherParticipant);
    const currentUserId = getCurrentUserId();
    const canMessage =
      type === 'accepted' &&
      currentUserId &&
      otherParticipantId &&
      String(otherParticipantId) !== String(currentUserId);

    const displayName =
      otherParticipant?.name ||
      (type === 'pending'
        ? swap?.sender?.name
        : swap?.receiver?.name || swap?.sender?.name);

    return (
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        whileHover={{ scale: 1.02 }}
        className="glass-morphism p-6 rounded-xl border border-gray-700 hover:border-primary transition-all"
      >

        <div className="flex items-start justify-between mb-4">

          <div className="flex items-center space-x-3">

            <div className="w-12 h-12 rounded-full bg-gradient-to-br from-primary to-purple-600 flex items-center justify-center">
              <User className="w-6 h-6 text-white" />
            </div>

            <div>

              <div className="font-semibold text-white">
                {displayName || "Unknown"}
              </div>

              <div className="text-sm text-gray-400">
                {swap.message || "Skill Exchange"}
              </div>

            </div>
          </div>

          <div
            className={`
              px-3 py-1 rounded-full text-xs font-medium
              ${type === 'pending'
                ? 'bg-yellow-900/30 text-yellow-400'
                : ''}
              ${type === 'accepted'
                ? 'bg-green-900/30 text-green-400'
                : ''}
              ${type === 'completed'
                ? 'bg-blue-900/30 text-blue-400'
                : ''}
              ${type === 'cancelled'
                ? 'bg-red-900/30 text-red-400'
                : ''}
            `}
          >
            {normalizeStatus(swap.status)}
          </div>
        </div>

        <div className="space-y-3">

          <div className="flex items-center text-sm text-gray-400">
            <Calendar className="w-4 h-4 mr-2" />
            Proposed Duration:
            {" "}
            {swap.proposed_duration || 60}
            {" "}
            mins
          </div>

          <div className="text-sm text-gray-300">

            <div className="text-xs text-gray-500 mb-1">
              Message:
            </div>

            <p className="line-clamp-4">
              {swap.message}
            </p>

          </div>

        </div>

        {/* ACTIONS */}

        {type === 'pending' && (

          <div className="flex space-x-2 mt-6">

            <button
              onClick={() =>
                handleAcceptSwap(swap.id)
              }
              className="flex-1 bg-green-600 hover:bg-green-700 text-white py-2 px-4 rounded-lg transition"
            >
              Accept
            </button>

            <button
              onClick={() =>
                handleRejectSwap(swap.id)
              }
              className="flex-1 bg-red-600 hover:bg-red-700 text-white py-2 px-4 rounded-lg transition"
            >
              Reject
            </button>

          </div>
        )}

        {type === 'accepted' && (

          <div className="flex space-x-2 mt-6">

            <button
              onClick={() =>
                handleCompleteSwap(swap.id)
              }
              className="flex-1 bg-blue-600 hover:bg-blue-700 text-white py-2 px-4 rounded-lg transition"
            >
              Mark Completed
            </button>

            {canMessage && (
              <button
                onClick={() =>
                  startConversation(otherParticipantId, swap.id || swap._id)
                }
                disabled={startingConversationId === (swap.id || swap._id)}
                className="flex-1 bg-primary hover:bg-primary/80 text-white py-2 px-4 rounded-lg transition disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Message User
              </button>
            )}

          </div>
        )}

      </motion.div>
    );
  };

  // =========================
  // LOADING
  // =========================

  if (loading) {

    return (
      <div className="min-h-screen flex items-center justify-center bg-primary">
        <LoadingSpinner size="large" />
      </div>
    );
  }

  // =========================
  // UI
  // =========================

  return (

    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-8 p-6"
    >

      <div>

        <h1 className="text-3xl font-bold text-white mb-2">
          Swap Requests
        </h1>

        <p className="text-gray-400">
          Manage your skill exchange requests
        </p>

      </div>

      {/* TABS */}

      <div className="glass-morphism p-2 rounded-xl border border-gray-700">

        <div className="flex space-x-2">

          {[
            'pending',
            'accepted',
            'completed',
            'cancelled'
          ].map(tab => (

            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`px-6 py-3 rounded-lg font-medium transition
                ${activeTab === tab
                  ? 'bg-primary text-white'
                  : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                }
              `}
            >
              {tab.charAt(0).toUpperCase() + tab.slice(1)}
              {" "}
              ({swaps[tab]?.length || 0})
            </button>

          ))}

        </div>
      </div>

      {/* CONTENT */}

      {swaps[activeTab]?.length === 0 ? (

        <div className="text-center py-12">

          <MessageCircle className="w-12 h-12 text-gray-500 mx-auto mb-4" />

          <p className="text-gray-400 text-lg">
            No {activeTab} swaps
          </p>

        </div>

      ) : (

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">

          {swaps[activeTab].map((swap, idx) => (

            <motion.div
              key={swap.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: idx * 0.1 }}
            >
              <SwapCard
                swap={swap}
                type={activeTab}
              />
            </motion.div>

          ))}

        </div>

      )}

    </motion.div>
  );
};

export default SwapRequests;
