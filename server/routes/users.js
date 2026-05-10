import express from 'express';
import {
  updateProfile,
  getProfile,
  searchUsers,
  getNearbyUsers,
  getMatches,
  getNotifications
} from '../controllers/userController.js';
import { validateProfileUpdate } from '../middleware/validation.js';

const router = express.Router();

router.put('/profile', validateProfileUpdate, updateProfile);
router.get('/profile/:userId', getProfile);
router.get('/search', searchUsers);
router.get('/nearby', getNearbyUsers);
router.get('/matches', getMatches);
router.get('/notifications', getNotifications);

export default router;
