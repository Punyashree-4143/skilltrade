import express from 'express';
import {
  sendMessage,
  getMessages,
  getConversations,
  editMessage,
  deleteMessage,
  addReaction,
  removeReaction,
  getUnreadCount
} from '../controllers/messageController.js';
import { validateMessage } from '../middleware/validation.js';

const router = express.Router();

router.post('/', validateMessage, sendMessage);
router.get('/conversations', getConversations);
router.get('/unread/count', getUnreadCount);
router.get('/:userId', getMessages);
router.put('/:messageId', editMessage);
router.delete('/:messageId', deleteMessage);
router.post('/:messageId/reactions', addReaction);
router.delete('/:messageId/reactions', removeReaction);

export default router;
