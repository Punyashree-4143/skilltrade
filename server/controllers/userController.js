import User from '../models/User.js';
import SwapRequest from '../models/SwapRequest.js';
import Message from '../models/Message.js';
import Review from '../models/Review.js';

export const updateProfile = async (req, res) => {
  try {
    const allowedUpdates = [
      'name', 'bio', 'avatar', 'offers', 'wants', 'availability', 
      'location', 'preferences'
    ];
    
    const updates = {};
    Object.keys(req.body).forEach(key => {
      if (allowedUpdates.includes(key)) {
        updates[key] = req.body[key];
      }
    });

    if (updates.location && updates.location.coordinates) {
      updates.location = {
        type: 'Point',
        coordinates: updates.location.coordinates,
        city: updates.location.city || req.user.location.city,
        country: updates.location.country || req.user.location.country
      };
    }

    const user = await User.findByIdAndUpdate(
      req.user._id,
      { $set: updates },
      { new: true, runValidators: true }
    );

    res.json({
      message: 'Profile updated successfully',
      user: user.toSafeObject()
    });
  } catch (error) {
    console.error('Profile update error:', error);
    res.status(500).json({ message: 'Profile update failed', error: error.message });
  }
};

export const getProfile = async (req, res) => {
  try {
    const { userId } = req.params;
    
    const user = await User.findById(userId)
      .select('-password')
      .populate('reviews.reviewer', 'name avatar rating');

    if (!user) {
      return res.status(404).json({ message: 'User not found' });
    }

    const swapStats = await SwapRequest.aggregate([
      { $match: { $or: [{ sender: user._id }, { receiver: user._id }] } },
      {
        $group: {
          _id: '$status',
          count: { $sum: 1 }
        }
      }
    ]);

    const stats = swapStats.reduce((acc, stat) => {
      acc[stat._id] = stat.count;
      return acc;
    }, {});

    res.json({
      user: user.toSafeObject(),
      stats: {
        total: Object.values(stats).reduce((a, b) => a + b, 0),
        completed: stats.completed || 0,
        pending: stats.pending || 0,
        accepted: stats.accepted || 0
      }
    });
  } catch (error) {
    console.error('Get profile error:', error);
    res.status(500).json({ message: 'Failed to get profile', error: error.message });
  }
};

export const searchUsers = async (req, res) => {
  try {
    const {
      query,
      skills,
      category,
      distance = 50,
      page = 1,
      limit = 20,
      sortBy = 'relevance'
    } = req.query;

    const searchCriteria = { _id: { $ne: req.user._id } };

    if (query) {
      searchCriteria.$text = { $search: query };
    }

    if (skills) {
      const skillArray = Array.isArray(skills) ? skills : skills.split(',');
      searchCriteria.$or = [
        { 'offers.skill': { $in: skillArray } },
        { 'wants.skill': { $in: skillArray } }
      ];
    }

    if (category) {
      searchCriteria.$or = [
        { 'offers.category': category },
        { 'wants.category': category }
      ];
    }

    let aggregationPipeline = [];

    if (req.user.location && req.user.location.coordinates) {
      aggregationPipeline.push({
        $geoNear: {
          near: {
            type: 'Point',
            coordinates: req.user.location.coordinates
          },
          distanceField: 'distance',
          maxDistance: distance * 1000,
          spherical: true
        }
      });
    } else {
      aggregationPipeline.push({ $match: searchCriteria });
    }

    if (query || skills || category) {
      aggregationPipeline.push({ $match: searchCriteria });
    }

    const sortOptions = {
      relevance: { score: { $meta: 'textScore' }, distance: 1 },
      distance: { distance: 1 },
      rating: { rating: -1, distance: 1 },
      recent: { createdAt: -1 }
    };

    aggregationPipeline.push({
      $sort: sortOptions[sortBy] || sortOptions.relevance
    });

    const skip = (page - 1) * limit;
    aggregationPipeline.push({ $skip: skip });
    aggregationPipeline.push({ $limit: parseInt(limit) });

    aggregationPipeline.push({
      $project: {
        password: 0,
        'preferences.notifications': 0
      }
    });

    const users = await User.aggregate(aggregationPipeline);

    const total = await User.countDocuments(searchCriteria);

    res.json({
      users,
      pagination: {
        page: parseInt(page),
        limit: parseInt(limit),
        total,
        pages: Math.ceil(total / limit)
      }
    });
  } catch (error) {
    console.error('Search users error:', error);
    res.status(500).json({ message: 'Search failed', error: error.message });
  }
};

export const getNearbyUsers = async (req, res) => {
  try {
    const { distance = 50, limit = 10 } = req.query;

    if (!req.user.location || !req.user.location.coordinates) {
      return res.status(400).json({ message: 'Location not set' });
    }

    const users = await User.find({
      _id: { $ne: req.user._id },
      location: {
        $near: {
          $geometry: {
            type: 'Point',
            coordinates: req.user.location.coordinates
          },
          $maxDistance: distance * 1000
        }
      }
    })
    .select('-password -preferences.notifications')
    .limit(parseInt(limit))
    .sort({ rating: -1 });

    res.json({ users });
  } catch (error) {
    console.error('Get nearby users error:', error);
    res.status(500).json({ message: 'Failed to get nearby users', error: error.message });
  }
};

export const getMatches = async (req, res) => {
  try {
    const user = req.user;
    
    if (!user.offers.length || !user.wants.length) {
      return res.json({ matches: [], message: 'Add skills to get matches' });
    }

    const offeredSkills = user.offers.map(o => o.skill.toLowerCase());
    const wantedSkills = user.wants.map(w => w.skill.toLowerCase());

    const potentialMatches = await User.find({
      _id: { $ne: user._id },
      $or: [
        {
          'offers.skill': { $in: wantedSkills },
          'wants.skill': { $in: offeredSkills }
        }
      ]
    }).select('-password -preferences.notifications');

    const matches = potentialMatches.map(matchUser => {
      const matchOffers = matchUser.offers.filter(o => 
        wantedSkills.includes(o.skill.toLowerCase())
      );
      const matchWants = matchUser.wants.filter(w => 
        offeredSkills.includes(w.skill.toLowerCase())
      );

      let score = 0;
      
      score += (matchOffers.length + matchWants.length) * 20;
      
      score += Math.min(matchUser.rating, 5) * 10;
      
      if (user.location && matchUser.location && user.location.coordinates && matchUser.location.coordinates) {
        const distance = calculateDistance(
          user.location.coordinates,
          matchUser.location.coordinates
        );
        score += Math.max(0, 50 - distance) * 0.5;
      }

      return {
        user: matchUser.toSafeObject(),
        matchScore: Math.min(100, Math.round(score)),
        offeredSkills: matchOffers,
        requestedSkills: matchWants,
        distance: user.location && matchUser.location ? 
          calculateDistance(user.location.coordinates, matchUser.location.coordinates) : null
      };
    });

    matches.sort((a, b) => b.matchScore - a.matchScore);

    res.json({ matches: matches.slice(0, 20) });
  } catch (error) {
    console.error('Get matches error:', error);
    res.status(500).json({ message: 'Failed to get matches', error: error.message });
  }
};

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

export const getNotifications = async (req, res) => {
  try {
    const { page = 1, limit = 20 } = req.query;
    
    const swapRequests = await SwapRequest.find({
      receiver: req.user._id,
      status: 'pending'
    })
    .populate('sender', 'name avatar rating')
    .sort({ createdAt: -1 });

    const unreadMessages = await Message.find({
      receiver: req.user._id,
      read: false
    })
    .populate('sender', 'name avatar')
    .sort({ createdAt: -1 });

    const notifications = [
      ...swapRequests.map(sr => ({
        id: sr._id,
        type: 'swap_request',
        title: 'New Swap Request',
        message: `${sr.sender.name} wants to swap ${sr.requestedSkill.skill} for ${sr.offeredSkill.skill}`,
        sender: sr.sender,
        createdAt: sr.createdAt,
        read: false,
        data: sr
      })),
      ...unreadMessages.map(msg => ({
        id: msg._id,
        type: 'message',
        title: 'New Message',
        message: `${msg.sender.name}: ${msg.content.substring(0, 100)}...`,
        sender: msg.sender,
        createdAt: msg.createdAt,
        read: false,
        data: msg
      }))
    ];

    notifications.sort((a, b) => b.createdAt - a.createdAt);

    const startIndex = (page - 1) * limit;
    const paginatedNotifications = notifications.slice(startIndex, startIndex + parseInt(limit));

    res.json({
      notifications: paginatedNotifications,
      unreadCount: notifications.length,
      pagination: {
        page: parseInt(page),
        limit: parseInt(limit),
        total: notifications.length
      }
    });
  } catch (error) {
    console.error('Get notifications error:', error);
    res.status(500).json({ message: 'Failed to get notifications', error: error.message });
  }
};
