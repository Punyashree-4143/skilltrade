import express from 'express';
import {
  createSwapRequest,
  getSwapRequests,
  getSwapRequest,
  updateSwapRequest,
  addMessageToSwap,
  markSwapMessagesAsRead
} from '../controllers/swapController.js';
import { validateSwapRequest } from '../middleware/validation.js';

const router = express.Router();

router.post('/', validateSwapRequest, createSwapRequest);
router.get('/', getSwapRequests);
router.get('/:requestId', getSwapRequest);
router.put('/:requestId', updateSwapRequest);
router.post('/:requestId/messages', addMessageToSwap);
router.put('/:requestId/messages/read', markSwapMessagesAsRead);

export default router;
