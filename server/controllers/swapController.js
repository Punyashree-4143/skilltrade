import SwapRequest from '../models/SwapRequest.js';
import User from '../models/User.js';
import Review from '../models/Review.js';

export const createSwapRequest = async (req, res) => {
  try {
    const { receiver, offeredSkill, requestedSkill, message, proposedDuration } = req.body;

    if (req.user._id.toString() === receiver) {
      return res.status(400).json({ message: 'Cannot send swap request to yourself' });
    }

    const receiverUser = await User.findById(receiver);
    if (!receiverUser) {
      return res.status(404).json({ message: 'Receiver not found' });
    }

    const existingRequest = await SwapRequest.findOne({
      sender: req.user._id,
      receiver,
      status: { $in: ['pending', 'accepted'] }
    });

    if (existingRequest) {
      return res.status(400).json({ message: 'Active swap request already exists' });
    }

    const swapRequest = new SwapRequest({
      sender: req.user._id,
      receiver,
      offeredSkill,
      requestedSkill,
      message,
      proposedDuration
    });

    await swapRequest.save();
    await swapRequest.populate('sender receiver', 'name avatar rating location');

    const matchScore = calculateMatchScore(req.user, receiverUser, offeredSkill, requestedSkill);
    swapRequest.matchScore = matchScore;
    await swapRequest.save();

    res.status(201).json({
      message: 'Swap request sent successfully',
      swapRequest
    });
  } catch (error) {
    console.error('Create swap request error:', error);
    res.status(500).json({ message: 'Failed to create swap request', error: error.message });
  }
};

export const getSwapRequests = async (req, res) => {
  try {
    const { status, page = 1, limit = 20, type = 'all' } = req.query;

    let query = {};
    
    if (type === 'sent') {
      query.sender = req.user._id;
    } else if (type === 'received') {
      query.receiver = req.user._id;
    } else {
      query.$or = [
        { sender: req.user._id },
        { receiver: req.user._id }
      ];
    }

    if (status && status !== 'all') {
      query.status = status;
    }

    const skip = (page - 1) * limit;

    const swapRequests = await SwapRequest.find(query)
      .populate('sender receiver', 'name avatar rating location')
      .sort({ createdAt: -1 })
      .skip(skip)
      .limit(parseInt(limit));

    const total = await SwapRequest.countDocuments(query);

    res.json({
      swapRequests,
      pagination: {
        page: parseInt(page),
        limit: parseInt(limit),
        total,
        pages: Math.ceil(total / limit)
      }
    });
  } catch (error) {
    console.error('Get swap requests error:', error);
    res.status(500).json({ message: 'Failed to get swap requests', error: error.message });
  }
};

export const getSwapRequest = async (req, res) => {
  try {
    const { requestId } = req.params;

    const swapRequest = await SwapRequest.findById(requestId)
      .populate('sender receiver', 'name avatar rating location')
      .populate('messages.sender', 'name avatar');

    if (!swapRequest) {
      return res.status(404).json({ message: 'Swap request not found' });
    }

    const isParticipant = 
      swapRequest.sender._id.toString() === req.user._id.toString() ||
      swapRequest.receiver._id.toString() === req.user._id.toString();

    if (!isParticipant) {
      return res.status(403).json({ message: 'Access denied' });
    }

    res.json({ swapRequest });
  } catch (error) {
    console.error('Get swap request error:', error);
    res.status(500).json({ message: 'Failed to get swap request', error: error.message });
  }
};

export const updateSwapRequest = async (req, res) => {
  try {
    const { requestId } = req.params;
    const { status, message, scheduledDate, scheduledTime, location, meetingDetails } = req.body;

    const swapRequest = await SwapRequest.findById(requestId);
    if (!swapRequest) {
      return res.status(404).json({ message: 'Swap request not found' });
    }

    const isReceiver = swapRequest.receiver.toString() === req.user._id.toString();
    const isSender = swapRequest.sender.toString() === req.user._id.toString();

    if ((status === 'accepted' || status === 'rejected') && !isReceiver) {
      return res.status(403).json({ message: 'Only receiver can accept or reject requests' });
    }

    if (status === 'cancelled' && !isSender && !isReceiver) {
      return res.status(403).json({ message: 'Only participants can cancel requests' });
    }

    if (status === 'completed' && !isSender && !isReceiver) {
      return res.status(403).json({ message: 'Only participants can mark requests as completed' });
    }

    const updates = { status };

    if (message) {
      updates.$push = {
        messages: {
          sender: req.user._id,
          content: message,
          timestamp: new Date()
        }
      };
    }

    if (scheduledDate) updates.scheduledDate = scheduledDate;
    if (scheduledTime) updates.scheduledTime = scheduledTime;
    if (location) updates.location = location;
    if (meetingDetails) updates.meetingDetails = meetingDetails;

    const updatedRequest = await SwapRequest.findByIdAndUpdate(
      requestId,
      updates,
      { new: true }
    ).populate('sender receiver', 'name avatar rating');

    res.json({
      message: `Swap request ${status} successfully`,
      swapRequest: updatedRequest
    });
  } catch (error) {
    console.error('Update swap request error:', error);
    res.status(500).json({ message: 'Failed to update swap request', error: error.message });
  }
};

export const addMessageToSwap = async (req, res) => {
  try {
    const { requestId } = req.params;
    const { content } = req.body;

    const swapRequest = await SwapRequest.findById(requestId);
    if (!swapRequest) {
      return res.status(404).json({ message: 'Swap request not found' });
    }

    const isParticipant = 
      swapRequest.sender.toString() === req.user._id.toString() ||
      swapRequest.receiver.toString() === req.user._id.toString();

    if (!isParticipant) {
      return res.status(403).json({ message: 'Access denied' });
    }

    await swapRequest.addMessage(req.user._id, content);

    const updatedRequest = await SwapRequest.findById(requestId)
      .populate('sender receiver', 'name avatar rating')
      .populate('messages.sender', 'name avatar');

    res.json({
      message: 'Message added successfully',
      swapRequest: updatedRequest
    });
  } catch (error) {
    console.error('Add message to swap error:', error);
    res.status(500).json({ message: 'Failed to add message', error: error.message });
  }
};

export const markSwapMessagesAsRead = async (req, res) => {
  try {
    const { requestId } = req.params;

    const swapRequest = await SwapRequest.findById(requestId);
    if (!swapRequest) {
      return res.status(404).json({ message: 'Swap request not found' });
    }

    const isParticipant = 
      swapRequest.sender.toString() === req.user._id.toString() ||
      swapRequest.receiver.toString() === req.user._id.toString();

    if (!isParticipant) {
      return res.status(403).json({ message: 'Access denied' });
    }

    await swapRequest.markMessagesAsRead(req.user._id);

    res.json({ message: 'Messages marked as read' });
  } catch (error) {
    console.error('Mark messages as read error:', error);
    res.status(500).json({ message: 'Failed to mark messages as read', error: error.message });
  }
};

function calculateMatchScore(user1, user2, offeredSkill, requestedSkill) {
  let score = 0;

  const user1Offers = user1.offers.map(o => o.skill.toLowerCase());
  const user1Wants = user1.wants.map(w => w.skill.toLowerCase());
  const user2Offers = user2.offers.map(o => o.skill.toLowerCase());
  const user2Wants = user2.wants.map(w => w.skill.toLowerCase());

  const directMatch = user1Offers.includes(requestedSkill.skill.toLowerCase()) &&
                      user2Offers.includes(offeredSkill.skill.toLowerCase());
  
  if (directMatch) score += 50;

  const partialMatch = user1Wants.includes(offeredSkill.skill.toLowerCase()) ||
                       user2Wants.includes(requestedSkill.skill.toLowerCase());
  
  if (partialMatch) score += 25;

  score += Math.min(user2.rating, 5) * 10;

  if (user1.location && user2.location && 
      user1.location.coordinates && user2.location.coordinates) {
    const distance = calculateDistance(
      user1.location.coordinates,
      user2.location.coordinates
    );
    score += Math.max(0, 50 - distance) * 0.5;
  }

  return Math.min(100, Math.round(score));
}

function calculateDistance(coords1, coords2) {
  const R = 6371;
  const dLat = toRad(coords2[1] - coords1[1]);
  const dLon = toRad(coords2[0] - coords1[0]);
  const lat1 = toRad(coords1[1]);
  const lat2 = toRad(coords2[1]);

  const a = Math.sin(dLat/2) * Math.sin(dLat/2) +
    Math.sin(dLon/2) * Math.sin(dLon/2) * Math.cos(lat1) * Math.cos(lat2);
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
  
  return Math.round(R * c);
}

function toRad(deg) {
  return deg * (Math.PI/180);
}
