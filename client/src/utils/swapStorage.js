// Swap Request Storage Utilities
export const swapStorage = {
  // Get all swap requests
  getRequests: () => {
    const requests = localStorage.getItem('swapRequests');
    return requests ? JSON.parse(requests) : [];
  },

  // Save swap request
  saveRequest: (request) => {
    const requests = swapStorage.getRequests();
    requests.push(request);
    localStorage.setItem('swapRequests', JSON.stringify(requests));
  },

  // Update swap request status
  updateRequestStatus: (requestId, newStatus) => {
    const requests = swapStorage.getRequests();
    const updatedRequests = requests.map(req => 
      req.id === requestId ? { ...req, status: newStatus, updatedAt: new Date().toISOString() } : req
    );
    localStorage.setItem('swapRequests', JSON.stringify(updatedRequests));
  },

  // Get requests for current user
  getUserRequests: (userId) => {
    const requests = swapStorage.getRequests();
    return requests.filter(req => req.fromUser.id === userId || req.toUser.id === userId);
  },

  // Get pending requests for current user
  getPendingRequests: (userId) => {
    const requests = swapStorage.getUserRequests(userId);
    return requests.filter(req => req.status === 'pending');
  },

  // Get accepted requests for current user
  getAcceptedRequests: (userId) => {
    const requests = swapStorage.getUserRequests(userId);
    return requests.filter(req => req.status === 'accepted');
  },

  // Get requests by status
  getRequestsByStatus: (status) => {
    const requests = swapStorage.getRequests();
    return requests.filter(req => req.status === status);
  },

  // Delete swap request
  deleteRequest: (requestId) => {
    const requests = swapStorage.getRequests();
    const filteredRequests = requests.filter(req => req.id !== requestId);
    localStorage.setItem('swapRequests', JSON.stringify(filteredRequests));
  }
};
