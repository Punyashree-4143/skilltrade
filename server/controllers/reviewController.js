import Review from '../models/Review.js';
import User from '../models/User.js';
import SwapRequest from '../models/SwapRequest.js';

export const createReview = async (req, res) => {
  try {
    const { reviewee, swapRequest, rating, comment, skills, wouldSwapAgain, helpfulness, communication, punctuality } = req.body;

    if (req.user._id.toString() === reviewee) {
      return res.status(400).json({ message: 'Cannot review yourself' });
    }

    const swap = await SwapRequest.findById(swapRequest);
    if (!swap) {
      return res.status(404).json({ message: 'Swap request not found' });
    }

    if (swap.status !== 'completed') {
      return res.status(400).json({ message: 'Can only review completed swaps' });
    }

    const isParticipant = 
      swap.sender.toString() === req.user._id.toString() ||
      swap.receiver.toString() === req.user._id.toString();

    if (!isParticipant) {
      return res.status(403).json({ message: 'Can only review swaps you participated in' });
    }

    const isRevieweeParticipant = 
      swap.sender.toString() === reviewee ||
      swap.receiver.toString() === reviewee;

    if (!isRevieweeParticipant) {
      return res.status(400).json({ message: 'Reviewee must be a participant in the swap' });
    }

    const existingReview = await Review.findOne({
      reviewer: req.user._id,
      reviewee,
      swapRequest
    });

    if (existingReview) {
      return res.status(400).json({ message: 'You have already reviewed this swap' });
    }

    const review = new Review({
      reviewer: req.user._id,
      reviewee,
      swapRequest,
      rating,
      comment,
      skills,
      wouldSwapAgain,
      helpfulness,
      communication,
      punctuality
    });

    await review.save();
    await review.populate([
      { path: 'reviewer', select: 'name avatar rating' },
      { path: 'reviewee', select: 'name avatar rating' },
      { path: 'swapRequest', select: 'offeredSkill requestedSkill' }
    ]);

    const revieweeUser = await User.findById(reviewee);
    if (revieweeUser) {
      revieweeUser.reviews.push({
        reviewer: req.user._id,
        rating,
        comment,
        swapRequest,
        createdAt: new Date()
      });
      revieweeUser.updateRating();
      await revieweeUser.save();
    }

    res.status(201).json({
      message: 'Review created successfully',
      review
    });
  } catch (error) {
    console.error('Create review error:', error);
    res.status(500).json({ message: 'Failed to create review', error: error.message });
  }
};

export const getReviews = async (req, res) => {
  try {
    const { userId, page = 1, limit = 20, rating, sortBy = 'recent' } = req.query;

    let query = {};
    
    if (userId) {
      query.reviewee = userId;
    }

    if (rating && rating !== 'all') {
      query.rating = parseInt(rating);
    }

    const sortOptions = {
      recent: { createdAt: -1 },
      rating_high: { rating: -1, createdAt: -1 },
      rating_low: { rating: 1, createdAt: -1 }
    };

    const skip = (page - 1) * limit;

    const reviews = await Review.find(query)
      .populate('reviewer', 'name avatar rating')
      .populate('reviewee', 'name avatar rating')
      .populate('swapRequest', 'offeredSkill requestedSkill')
      .sort(sortOptions[sortBy] || sortOptions.recent)
      .skip(skip)
      .limit(parseInt(limit));

    const total = await Review.countDocuments(query);

    const ratingStats = await Review.aggregate([
      { $match: { reviewee: userId ? new mongoose.Types.ObjectId(userId) : { $exists: true } } },
      {
        $group: {
          _id: '$rating',
          count: { $sum: 1 }
        }
      }
    ]);

    const stats = ratingStats.reduce((acc, stat) => {
      acc[stat._id] = stat.count;
      return acc;
    }, {});

    res.json({
      reviews,
      pagination: {
        page: parseInt(page),
        limit: parseInt(limit),
        total,
        pages: Math.ceil(total / limit)
      },
      stats
    });
  } catch (error) {
    console.error('Get reviews error:', error);
    res.status(500).json({ message: 'Failed to get reviews', error: error.message });
  }
};

export const getReview = async (req, res) => {
  try {
    const { reviewId } = req.params;

    const review = await Review.findById(reviewId)
      .populate('reviewer', 'name avatar rating')
      .populate('reviewee', 'name avatar rating')
      .populate('swapRequest', 'offeredSkill requestedSkill sender receiver');

    if (!review) {
      return res.status(404).json({ message: 'Review not found' });
    }

    res.json({ review });
  } catch (error) {
    console.error('Get review error:', error);
    res.status(500).json({ message: 'Failed to get review', error: error.message });
  }
};

export const updateReview = async (req, res) => {
  try {
    const { reviewId } = req.params;
    const { comment, isPublic } = req.body;

    const review = await Review.findById(reviewId);
    if (!review) {
      return res.status(404).json({ message: 'Review not found' });
    }

    if (review.reviewer.toString() !== req.user._id.toString()) {
      return res.status(403).json({ message: 'Can only edit your own reviews' });
    }

    const timeDiff = Date.now() - review.createdAt.getTime();
    if (timeDiff > 7 * 24 * 60 * 60 * 1000) {
      return res.status(400).json({ message: 'Can only edit reviews within 7 days' });
    }

    if (comment !== undefined) review.comment = comment;
    if (isPublic !== undefined) review.isPublic = isPublic;

    await review.save();
    await review.populate([
      { path: 'reviewer', select: 'name avatar rating' },
      { path: 'reviewee', select: 'name avatar rating' },
      { path: 'swapRequest', select: 'offeredSkill requestedSkill' }
    ]);

    res.json({
      message: 'Review updated successfully',
      review
    });
  } catch (error) {
    console.error('Update review error:', error);
    res.status(500).json({ message: 'Failed to update review', error: error.message });
  }
};

export const deleteReview = async (req, res) => {
  try {
    const { reviewId } = req.params;

    const review = await Review.findById(reviewId);
    if (!review) {
      return res.status(404).json({ message: 'Review not found' });
    }

    if (review.reviewer.toString() !== req.user._id.toString()) {
      return res.status(403).json({ message: 'Can only delete your own reviews' });
    }

    await Review.findByIdAndDelete(reviewId);

    const revieweeUser = await User.findById(review.reviewee);
    if (revieweeUser) {
      revieweeUser.reviews = revieweeUser.reviews.filter(
        r => r.toString() !== reviewId
      );
      revieweeUser.updateRating();
      await revieweeUser.save();
    }

    res.json({ message: 'Review deleted successfully' });
  } catch (error) {
    console.error('Delete review error:', error);
    res.status(500).json({ message: 'Failed to delete review', error: error.message });
  }
};

export const respondToReview = async (req, res) => {
  try {
    const { reviewId } = req.params;
    const { content } = req.body;

    const review = await Review.findById(reviewId);
    if (!review) {
      return res.status(404).json({ message: 'Review not found' });
    }

    if (review.reviewee.toString() !== req.user._id.toString()) {
      return res.status(403).json({ message: 'Can only respond to reviews about you' });
    }

    if (review.response) {
      return res.status(400).json({ message: 'Review already has a response' });
    }

    await review.addResponse(content);
    await review.populate([
      { path: 'reviewer', select: 'name avatar rating' },
      { path: 'reviewee', select: 'name avatar rating' },
      { path: 'swapRequest', select: 'offeredSkill requestedSkill' }
    ]);

    res.json({
      message: 'Response added successfully',
      review
    });
  } catch (error) {
    console.error('Respond to review error:', error);
    res.status(500).json({ message: 'Failed to add response', error: error.message });
  }
};

export const reportReview = async (req, res) => {
  try {
    const { reviewId } = req.params;
    const { reason } = req.body;

    const review = await Review.findById(reviewId);
    if (!review) {
      return res.status(404).json({ message: 'Review not found' });
    }

    await review.report(reason);

    res.json({ message: 'Review reported successfully' });
  } catch (error) {
    console.error('Report review error:', error);
    res.status(500).json({ message: 'Failed to report review', error: error.message });
  }
};

export const getUserReviewStats = async (req, res) => {
  try {
    const { userId } = req.params;

    const stats = await Review.aggregate([
      { $match: { reviewee: new mongoose.Types.ObjectId(userId) } },
      {
        $group: {
          _id: null,
          totalReviews: { $sum: 1 },
          averageRating: { $avg: '$rating' },
          fiveStar: { $sum: { $cond: [{ $eq: ['$rating', 5] }, 1, 0] } },
          fourStar: { $sum: { $cond: [{ $eq: ['$rating', 4] }, 1, 0] } },
          threeStar: { $sum: { $cond: [{ $eq: ['$rating', 3] }, 1, 0] } },
          twoStar: { $sum: { $cond: [{ $eq: ['$rating', 2] }, 1, 0] } },
          oneStar: { $sum: { $cond: [{ $eq: ['$rating', 1] }, 1, 0] } },
          averageHelpfulness: { $avg: '$helpfulness' },
          averageCommunication: { $avg: '$communication' },
          averagePunctuality: { $avg: '$punctuality' },
          wouldSwapAgainCount: { $sum: { $cond: ['$wouldSwapAgain', 1, 0] } }
        }
      }
    ]);

    const result = stats.length > 0 ? stats[0] : {
      totalReviews: 0,
      averageRating: 0,
      fiveStar: 0,
      fourStar: 0,
      threeStar: 0,
      twoStar: 0,
      oneStar: 0,
      averageHelpfulness: 0,
      averageCommunication: 0,
      averagePunctuality: 0,
      wouldSwapAgainCount: 0
    };

    result.wouldSwapAgainPercentage = result.totalReviews > 0 
      ? Math.round((result.wouldSwapAgainCount / result.totalReviews) * 100)
      : 0;

    res.json({ stats: result });
  } catch (error) {
    console.error('Get user review stats error:', error);
    res.status(500).json({ message: 'Failed to get review stats', error: error.message });
  }
};
