import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { ArrowLeft, ArrowRight, Clock, Calendar, Check, X, AlertCircle, Users } from 'lucide-react';
import axios from 'axios';
import { useAuth } from '../context/AuthContext';
import LoadingSpinner from '../components/LoadingSpinner';

const Swaps = () => {
  const [activeTab, setActiveTab] = useState('sent');
  const { user } = useAuth();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchSwapRequests = async () => {
      try {
        setLoading(true);
        setError(null);
        
        // Fetch swap requests from our API
        const response = await axios.get('http://localhost:8000/api/swaps/');
        const allSwaps = response.data.swaps || [];
        
        // Separate sent and received requests
        const sent = allSwaps.filter(swap => swap.sender_id === user._id);
        const received = allSwaps.filter(swap => swap.receiver_id === user._id);
        
        setSentRequests(sent);
        setReceivedRequests(received);
      } catch (error) {
        console.error('Error fetching swap requests:', error);
        setError('Failed to load swap requests');
        // Fallback to empty arrays on error
        setSentRequests([]);
        setReceivedRequests([]);
      } finally {
        setLoading(false);
      }
    };

    fetchSwapRequests();
  }, []);

  const handleAcceptRequest = async (requestId) => {
    try {
      const token = localStorage.getItem('authToken');
      const response = await axios.put(`http://localhost:8000/api/swaps/${requestId}/accept`, {
        status: 'accepted',
        message: 'Request accepted!'
      }, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      
      // Update local state with response data
      const updatedRequest = response.data.swapRequest;
      setReceivedRequests(prev => 
        prev.map(req => 
          req._id === requestId ? { ...req, ...updatedRequest } : req
        )
      );
      
      alert('Swap request accepted! You can now coordinate.');
    } catch (error) {
      console.error('Error accepting request:', error);
      alert('Failed to accept request. Please try again.');
    }
  };

  const handleRejectRequest = async (requestId) => {
    try {
      const token = localStorage.getItem('authToken');
      const response = await axios.put(`http://localhost:8000/api/swaps/${requestId}/reject`, {
        status: 'rejected',
        message: 'Request rejected.'
      }, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      
      // Update local state with response data
      const updatedRequest = response.data.swapRequest;
      setReceivedRequests(prev => 
        prev.map(req => 
          req._id === requestId ? { ...req, ...updatedRequest } : req
        )
      );
      
      alert('Swap request rejected.');
    } catch (error) {
      console.error('Error rejecting request:', error);
      alert('Failed to reject request. Please try again.');
    }
  };

  const handleCancelRequest = async (requestId) => {
    try {
      const token = localStorage.getItem('authToken');
      await axios.put(`http://localhost:8000/api/swaps/${requestId}`, {
        status: 'cancelled',
        message: 'Request cancelled.'
      }, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      
      // Update local state
      setSentRequests(prev => prev.filter(req => req._id !== requestId));
      setReceivedRequests(prev => prev.filter(req => req._id !== requestId));
      
      alert('Swap request cancelled.');
    } catch (error) {
      console.error('Error cancelling request:', error);
      alert('Failed to cancel request. Please try again.');
    }
  };

  const handleCompleteSwap = async (requestId) => {
    try {
      const token = localStorage.getItem('authToken');
      const response = await axios.put(`http://localhost:8000/api/swaps/${requestId}`, {
        status: 'completed',
        message: 'Swap completed successfully!'
      }, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      
      // Update local state with response data
      const updatedRequest = response.data.swapRequest;
      setReceivedRequests(prev => 
        prev.map(req => 
          req._id === requestId ? { ...req, ...updatedRequest } : req
        )
      );
      
      alert('Swap completed! Skills have been exchanged.');
    } catch (error) {
      console.error('Error completing swap:', error);
      alert('Failed to complete swap. Please try again.');
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'pending': return 'text-yellow-400';
      case 'accepted': return 'text-green-400';
      case 'rejected': return 'text-red-400';
      case 'completed': return 'text-blue-400';
      default: return 'text-gray-400';
    }
  };

  const getStatusBg = (status) => {
    switch (status) {
      case 'pending': return 'bg-yellow-900/20';
      case 'accepted': return 'bg-green-900/20';
      case 'rejected': return 'bg-red-900/20';
      case 'completed': return 'bg-blue-900/20';
      default: return 'bg-gray-900/20';
    }
  };

  const RequestCard = ({ request, type }) => {
    const isSent = type === 'sent';
    const otherUser = isSent ? request.receiver : request.sender;
    
    return (
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="glass-morphism p-6 rounded-xl border border-gray-700"
      >
        <div className="flex items-start space-x-4">
          <img
            src={otherUser.avatar || `https://ui-avatars.com/api/?name=${encodeURIComponent(otherUser.name)}&background=6366f1&color=fff`}
            alt={otherUser.name}
            className="w-12 h-12 rounded-full"
            onError={(e) => {
              e.target.src = `https://api.dicebear.com/7.x/initials/svg?seed=${encodeURIComponent(otherUser.name)}`;
            }}
          />
          
          <div className="flex-1 min-w-0">
            <div className="flex items-center justify-between mb-2">
              <h3 className="text-lg font-semibold text-white">{otherUser.name}</h3>
              <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(request.status)}`}>
                {request.status.charAt(0).toUpperCase() + request.status.slice(1)}
              </span>
            </div>
            
            <div className="space-y-2">
              <div className="flex items-center space-x-2 text-sm text-gray-400">
                <Calendar className="w-4 h-4" />
                <span>Requested {new Date(request.createdAt).toLocaleDateString()}</span>
              </div>
              
              <div className="flex items-center space-x-2 text-sm text-gray-400">
                <Users className="w-4 h-4" />
                <span>
                  {isSent ? 'You offered' : 'They offered'}: {request.offeredSkill?.skill || 'N/A'}
                </span>
              </div>
              
              <div className="flex items-center space-x-2 text-sm text-gray-400">
                <Users className="w-4 h-4" />
                <span>
                  {isSent ? 'They want' : 'You want'}: {request.requestedSkill?.skill || 'N/A'}
                </span>
              </div>
              
              {request.message && (
                <div className="mt-3 p-3 bg-gray-700 rounded-lg">
                  <p className="text-sm text-gray-300">{request.message}</p>
                </div>
              )}
            </div>
            
            <div className="flex items-center justify-between mt-4">
              <div className="text-xs text-gray-500">
                Last updated: {new Date(request.updatedAt).toLocaleString()}
              </div>
              
              <div className="flex space-x-2">
                {request.status === 'pending' && (
                  <>
                    <button
                      onClick={() => handleCancelRequest(request._id)}
                      className="px-3 py-1 bg-red-600 hover:bg-red-700 text-white text-sm rounded-lg transition-colors"
                    >
                      Cancel
                    </button>
                    
                    {!isSent && (
                      <>
                        <button
                          onClick={() => handleAcceptRequest(request._id)}
                          className="px-3 py-1 bg-green-600 hover:bg-green-700 text-white text-sm rounded-lg transition-colors"
                        >
                          Accept
                        </button>
                        <button
                          onClick={() => handleRejectRequest(request._id)}
                          className="px-3 py-1 bg-red-600 hover:bg-red-700 text-white text-sm rounded-lg transition-colors"
                        >
                          Reject
                        </button>
                      </>
                    )}
                  </>
                )}
                
                {request.status === 'accepted' && (
                  <>
                    <button
                      onClick={() => handleCompleteSwap(request._id)}
                      className="px-3 py-1 bg-green-600 hover:bg-green-700 text-white text-sm rounded-lg transition-colors"
                    >
                      Complete
                    </button>
                    
                    <button
                      onClick={() => alert('Feature coming soon: Message user')}
                      className="px-3 py-1 bg-blue-600 hover:bg-blue-700 text-white text-sm rounded-lg transition-colors"
                    >
                      Message
                    </button>
                  </>
                )}
                
                {request.status === 'rejected' && (
                  <button
                    onClick={() => alert('Feature coming soon: Send new request')}
                    className="px-3 py-1 bg-gray-600 hover:bg-gray-700 text-white text-sm rounded-lg transition-colors"
                  >
                    Send New
                  </button>
                )}
              </div>
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
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-8 p-6"
    >
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <h1 className="text-3xl font-bold text-white">Skill Swaps</h1>
        <p className="text-gray-400">Manage your skill exchange requests</p>
      </div>

      {/* Tabs */}
      <div className="glass-morphism rounded-xl border border-gray-700 p-1">
        <div className="flex space-x-1">
          <button
            onClick={() => setActiveTab('sent')}
            className={`px-4 py-2 rounded-lg transition-colors ${
              activeTab === 'sent' 
                ? 'bg-primary text-white' 
                : 'text-gray-400 hover:text-white'
            }`}
          >
            Sent ({sentRequests.length})
          </button>
          <button
            onClick={() => setActiveTab('received')}
            className={`px-4 py-2 rounded-lg transition-colors ${
              activeTab === 'received' 
                ? 'bg-primary text-white' 
                : 'text-gray-400 hover:text-white'
            }`}
          >
            Received ({receivedRequests.length})
          </button>
        </div>
      </div>

      {/* Content */}
      <div className="space-y-6">
        {activeTab === 'sent' && (
          <div>
            <h2 className="text-xl font-semibold text-white mb-4">Sent Requests</h2>
            {sentRequests.length === 0 ? (
              <div className="text-center py-12">
                <AlertCircle className="w-12 h-12 text-gray-500 mx-auto mb-4" />
                <p className="text-gray-400 text-lg">No sent requests</p>
                <p className="text-gray-500">Start connecting with users to send swap requests</p>
              </div>
            ) : (
              <div className="space-y-4">
                {sentRequests.map((request, index) => (
                  <motion.div
                    key={request._id}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: index * 0.1 }}
                  >
                    <RequestCard request={request} type="sent" />
                  </motion.div>
                ))}
              </div>
            )}
          </div>
        )}

        {activeTab === 'received' && (
          <div>
            <h2 className="text-xl font-semibold text-white mb-4">Received Requests</h2>
            {receivedRequests.length === 0 ? (
              <div className="text-center py-12">
                <AlertCircle className="w-12 h-12 text-gray-500 mx-auto mb-4" />
                <p className="text-gray-400 text-lg">No received requests</p>
                <p className="text-gray-500">Users will send you requests when interested in your skills</p>
              </div>
            ) : (
              <div className="space-y-4">
                {receivedRequests.map((request, index) => (
                  <motion.div
                    key={request._id}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: index * 0.1 }}
                  >
                    <RequestCard request={request} type="received" />
                  </motion.div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </motion.div>
  );
};

export default Swaps;
