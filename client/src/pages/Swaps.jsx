import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { AlertCircle, Calendar, Users } from 'lucide-react';
import axios from 'axios';
import { useAuth } from '../context/AuthContext';
import LoadingSpinner from '../components/LoadingSpinner';

const API_URL = import.meta.env.VITE_API_URL;

const Swaps = () => {
  const [activeTab, setActiveTab] = useState('sent');
  const [sentRequests, setSentRequests] = useState([]);
  const [receivedRequests, setReceivedRequests] = useState([]);
  const { user } = useAuth();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchSwapRequests = async () => {
      try {
        setLoading(true);
        setError(null);

        const token = localStorage.getItem('authToken');

        const response = await axios.get(
          `${API_URL}/api/swaps/`,
          {
            headers: {
              Authorization: `Bearer ${token}`,
            },
          }
        );

        const allSwaps = response.data.swaps || [];

        const sent = allSwaps.filter(
          (swap) => swap.sender_id === user?._id
        );

        const received = allSwaps.filter(
          (swap) => swap.receiver_id === user?._id
        );

        setSentRequests(sent);
        setReceivedRequests(received);
      } catch (error) {
        console.error('Error fetching swap requests:', error);
        setError('Failed to load swap requests');

        setSentRequests([]);
        setReceivedRequests([]);
      } finally {
        setLoading(false);
      }
    };

    if (user) {
      fetchSwapRequests();
    }
  }, [user]);

  const handleAcceptRequest = async (requestId) => {
    try {
      const token = localStorage.getItem('authToken');

      const response = await axios.put(
        `${API_URL}/api/swaps/${requestId}/accept`,
        {
          status: 'accepted',
          message: 'Request accepted!',
        },
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      const updatedRequest = response.data.swapRequest;

      setReceivedRequests((prev) =>
        prev.map((req) =>
          req._id === requestId
            ? { ...req, ...updatedRequest }
            : req
        )
      );

      alert('Swap request accepted!');
    } catch (error) {
      console.error('Error accepting request:', error);
      alert('Failed to accept request.');
    }
  };

  const handleRejectRequest = async (requestId) => {
    try {
      const token = localStorage.getItem('authToken');

      const response = await axios.put(
        `${API_URL}/api/swaps/${requestId}/reject`,
        {
          status: 'rejected',
          message: 'Request rejected.',
        },
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      const updatedRequest = response.data.swapRequest;

      setReceivedRequests((prev) =>
        prev.map((req) =>
          req._id === requestId
            ? { ...req, ...updatedRequest }
            : req
        )
      );

      alert('Swap request rejected.');
    } catch (error) {
      console.error('Error rejecting request:', error);
      alert('Failed to reject request.');
    }
  };

  const handleCancelRequest = async (requestId) => {
    try {
      const token = localStorage.getItem('authToken');

      await axios.put(
        `${API_URL}/api/swaps/${requestId}`,
        {
          status: 'cancelled',
          message: 'Request cancelled.',
        },
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      setSentRequests((prev) =>
        prev.filter((req) => req._id !== requestId)
      );

      setReceivedRequests((prev) =>
        prev.filter((req) => req._id !== requestId)
      );

      alert('Swap request cancelled.');
    } catch (error) {
      console.error('Error cancelling request:', error);
      alert('Failed to cancel request.');
    }
  };

  const handleCompleteSwap = async (requestId) => {
    try {
      const token = localStorage.getItem('authToken');

      const response = await axios.put(
        `${API_URL}/api/swaps/${requestId}`,
        {
          status: 'completed',
          message: 'Swap completed successfully!',
        },
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      const updatedRequest = response.data.swapRequest;

      setReceivedRequests((prev) =>
        prev.map((req) =>
          req._id === requestId
            ? { ...req, ...updatedRequest }
            : req
        )
      );

      alert('Swap completed!');
    } catch (error) {
      console.error('Error completing swap:', error);
      alert('Failed to complete swap.');
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'pending':
        return 'text-yellow-400';
      case 'accepted':
        return 'text-green-400';
      case 'rejected':
        return 'text-red-400';
      case 'completed':
        return 'text-blue-400';
      default:
        return 'text-gray-400';
    }
  };

  const RequestCard = ({ request, type }) => {
    const isSent = type === 'sent';
    const otherUser = isSent
      ? request.receiver
      : request.sender;

    return (
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="glass-morphism p-6 rounded-xl border border-gray-700"
      >
        <div className="flex items-start space-x-4">
          <img
            src={
              otherUser?.avatar ||
              `https://ui-avatars.com/api/?name=${encodeURIComponent(
                otherUser?.name || 'User'
              )}&background=6366f1&color=fff`
            }
            alt={otherUser?.name}
            className="w-12 h-12 rounded-full"
          />

          <div className="flex-1">
            <div className="flex items-center justify-between mb-2">
              <h3 className="text-lg font-semibold text-white">
                {otherUser?.name}
              </h3>

              <span
                className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(
                  request.status
                )}`}
              >
                {request.status}
              </span>
            </div>

            <div className="space-y-2 text-sm text-gray-400">
              <div className="flex items-center space-x-2">
                <Calendar className="w-4 h-4" />
                <span>
                  Requested{' '}
                  {new Date(
                    request.createdAt
                  ).toLocaleDateString()}
                </span>
              </div>

              <div className="flex items-center space-x-2">
                <Users className="w-4 h-4" />
                <span>
                  Offered:{' '}
                  {request.offeredSkill?.skill || 'N/A'}
                </span>
              </div>

              <div className="flex items-center space-x-2">
                <Users className="w-4 h-4" />
                <span>
                  Requested:{' '}
                  {request.requestedSkill?.skill || 'N/A'}
                </span>
              </div>
            </div>

            {request.message && (
              <div className="mt-3 p-3 bg-gray-700 rounded-lg">
                <p className="text-sm text-gray-300">
                  {request.message}
                </p>
              </div>
            )}

            <div className="flex flex-wrap gap-2 mt-4">
              {request.status === 'pending' && (
                <>
                  {!isSent && (
                    <>
                      <button
                        onClick={() =>
                          handleAcceptRequest(request._id)
                        }
                        className="px-3 py-1 bg-green-600 hover:bg-green-700 rounded-lg text-white text-sm"
                      >
                        Accept
                      </button>

                      <button
                        onClick={() =>
                          handleRejectRequest(request._id)
                        }
                        className="px-3 py-1 bg-red-600 hover:bg-red-700 rounded-lg text-white text-sm"
                      >
                        Reject
                      </button>
                    </>
                  )}

                  <button
                    onClick={() =>
                      handleCancelRequest(request._id)
                    }
                    className="px-3 py-1 bg-gray-600 hover:bg-gray-700 rounded-lg text-white text-sm"
                  >
                    Cancel
                  </button>
                </>
              )}

              {request.status === 'accepted' && (
                <button
                  onClick={() =>
                    handleCompleteSwap(request._id)
                  }
                  className="px-3 py-1 bg-blue-600 hover:bg-blue-700 rounded-lg text-white text-sm"
                >
                  Complete
                </button>
              )}
            </div>
          </div>
        </div>
      </motion.div>
    );
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
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="space-y-8 p-6"
    >
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold text-white">
          Skill Swaps
        </h1>
      </div>

      <div className="glass-morphism rounded-xl border border-gray-700 p-1 flex">
        <button
          onClick={() => setActiveTab('sent')}
          className={`px-4 py-2 rounded-lg ${
            activeTab === 'sent'
              ? 'bg-primary text-white'
              : 'text-gray-400'
          }`}
        >
          Sent ({sentRequests.length})
        </button>

        <button
          onClick={() => setActiveTab('received')}
          className={`px-4 py-2 rounded-lg ${
            activeTab === 'received'
              ? 'bg-primary text-white'
              : 'text-gray-400'
          }`}
        >
          Received ({receivedRequests.length})
        </button>
      </div>

      {error && (
        <div className="text-red-400">
          {error}
        </div>
      )}

      <div className="space-y-4">
        {activeTab === 'sent' ? (
          sentRequests.length > 0 ? (
            sentRequests.map((request) => (
              <RequestCard
                key={request._id}
                request={request}
                type="sent"
              />
            ))
          ) : (
            <div className="text-center py-12">
              <AlertCircle className="w-12 h-12 text-gray-500 mx-auto mb-4" />
              <p className="text-gray-400">
                No sent requests
              </p>
            </div>
          )
        ) : receivedRequests.length > 0 ? (
          receivedRequests.map((request) => (
            <RequestCard
              key={request._id}
              request={request}
              type="received"
            />
          ))
        ) : (
          <div className="text-center py-12">
            <AlertCircle className="w-12 h-12 text-gray-500 mx-auto mb-4" />
            <p className="text-gray-400">
              No received requests
            </p>
          </div>
        )}
      </div>
    </motion.div>
  );
};

export default Swaps;