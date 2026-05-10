import express from 'express';
import {
  createReview,
  getReviews,
  getReview,
  updateReview,
  deleteReview,
  respondToReview,
  reportReview,
  getUserReviewStats
} from '../controllers/reviewController.js';
import { validateReview } from '../middleware/validation.js';

const router = express.Router();

router.post('/', validateReview, createReview);
router.get('/', getReviews);
router.get('/stats/:userId', getUserReviewStats);
router.get('/:reviewId', getReview);
router.put('/:reviewId', updateReview);
router.delete('/:reviewId', deleteReview);
router.post('/:reviewId/respond', respondToReview);
router.post('/:reviewId/report', reportReview);

export default router;
