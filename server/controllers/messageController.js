import Message from '../models/Message.js';
import User from '../models/User.js';

export const sendMessage = async (req, res) => {
  try {
    const { receiver, content, messageType = 'text' } = req.body;

    if (req.user._id.toString() === receiver) {
      return res.status(400).json({ message: 'Cannot send message to yourself' });
    }

    const receiverUser = await User.findById(receiver);
    if (!receiverUser) {
      return res.status(404).json({ message: 'Receiver not found' });
    }

    const message = new Message({
      sender: req.user._id,
      receiver,
      content,
      messageType
    });

    await message.save();
    await message.populate('sender receiver', 'name avatar');

    res.status(201).json({
      message: 'Message sent successfully',
      messageData: message
    });
  } catch (error) {
    console.error('Send message error:', error);
    res.status(500).json({ message: 'Failed to send message', error: error.message });
  }
};

export const getMessages = async (req, res) => {
  try {
    const { userId } = req.params;
    const { page = 1, limit = 50 } = req.query;

    if (req.user._id.toString() === userId) {
      return res.status(400).json({ message: 'Cannot get messages with yourself' });
    }

    const otherUser = await User.findById(userId);
    if (!otherUser) {
      return res.status(404).json({ message: 'User not found' });
    }

    const skip = (page - 1) * limit;

    const messages = await Message.find({
      $or: [
        { sender: req.user._id, receiver: userId },
        { sender: userId, receiver: req.user._id }
      ],
      deleted: false
    })
    .populate('sender receiver', 'name avatar')
    .sort({ createdAt: -1 })
    .skip(skip)
    .limit(parseInt(limit));

    const total = await Message.countDocuments({
      $or: [
        { sender: req.user._id, receiver: userId },
        { sender: userId, receiver: req.user._id }
      ],
      deleted: false
    });

    const unreadCount = await Message.countDocuments({
      sender: userId,
      receiver: req.user._id,
      read: false,
      deleted: false
    });

    await Message.updateMany(
      { sender: userId, receiver: req.user._id, read: false },
      { read: true, readAt: new Date() }
    );

    res.json({
      messages: messages.reverse(),
      pagination: {
        page: parseInt(page),
        limit: parseInt(limit),
        total,
        pages: Math.ceil(total / limit)
      },
      unreadCount,
      otherUser: otherUser.toSafeObject()
    });
  } catch (error) {
    console.error('Get messages error:', error);
    res.status(500).json({ message: 'Failed to get messages', error: error.message });
  }
};

export const getConversations = async (req, res) => {
  try {
    const { page = 1, limit = 20 } = req.query;

    const conversations = await Message.aggregate([
      {
        $match: {
          $or: [
            { sender: req.user._id },
            { receiver: req.user._id }
          ],
          deleted: false
        }
      },
      {
        $sort: { createdAt: -1 }
      },
      {
        $group: {
          _id: {
            $cond: [
              { $eq: ['$sender', req.user._id] },
              '$receiver',
              '$sender'
            ]
          },
          lastMessage: { $first: '$$ROOT' },
          unreadCount: {
            $sum: {
              $cond: [
                {
                  $and: [
                    { $eq: ['$receiver', req.user._id] },
                    { $eq: ['$read', false] }
                  ]
                },
                1,
                0
              ]
            }
          }
        }
      },
      {
        $lookup: {
          from: 'users',
          localField: '_id',
          foreignField: '_id',
          as: 'user',
          pipeline: [
            {
              $project: {
                name: 1,
                avatar: 1,
                rating: 1,
                isOnline: 1,
                lastSeen: 1
              }
            }
          ]
        }
      },
      {
        $unwind: '$user'
      },
      {
        $sort: { 'lastMessage.createdAt': -1 }
      },
      {
        $skip: (page - 1) * limit
      },
      {
        $limit: parseInt(limit)
      }
    ]);

    const totalConversations = await Message.aggregate([
      {
        $match: {
          $or: [
            { sender: req.user._id },
            { receiver: req.user._id }
          ],
          deleted: false
        }
      },
      {
        $group: {
          _id: {
            $cond: [
              { $eq: ['$sender', req.user._id] },
              '$receiver',
              '$sender'
            ]
          }
        }
      },
      {
        $count: 'total'
      }
    ]);

    const total = totalConversations.length > 0 ? totalConversations[0].total : 0;

    res.json({
      conversations,
      pagination: {
        page: parseInt(page),
        limit: parseInt(limit),
        total,
        pages: Math.ceil(total / limit)
      }
    });
  } catch (error) {
    console.error('Get conversations error:', error);
    res.status(500).json({ message: 'Failed to get conversations', error: error.message });
  }
};

export const editMessage = async (req, res) => {
  try {
    const { messageId } = req.params;
    const { content } = req.body;

    const message = await Message.findById(messageId);
    if (!message) {
      return res.status(404).json({ message: 'Message not found' });
    }

    if (message.sender.toString() !== req.user._id.toString()) {
      return res.status(403).json({ message: 'Can only edit your own messages' });
    }

    if (message.deleted) {
      return res.status(400).json({ message: 'Cannot edit deleted message' });
    }

    const timeDiff = Date.now() - message.createdAt.getTime();
    if (timeDiff > 15 * 60 * 1000) {
      return res.status(400).json({ message: 'Can only edit messages within 15 minutes' });
    }

    await message.edit(content);
    await message.populate('sender receiver', 'name avatar');

    res.json({
      message: 'Message edited successfully',
      messageData: message
    });
  } catch (error) {
    console.error('Edit message error:', error);
    res.status(500).json({ message: 'Failed to edit message', error: error.message });
  }
};

export const deleteMessage = async (req, res) => {
  try {
    const { messageId } = req.params;

    const message = await Message.findById(messageId);
    if (!message) {
      return res.status(404).json({ message: 'Message not found' });
    }

    if (message.sender.toString() !== req.user._id.toString()) {
      return res.status(403).json({ message: 'Can only delete your own messages' });
    }

    await message.softDelete();

    res.json({ message: 'Message deleted successfully' });
  } catch (error) {
    console.error('Delete message error:', error);
    res.status(500).json({ message: 'Failed to delete message', error: error.message });
  }
};

export const addReaction = async (req, res) => {
  try {
    const { messageId } = req.params;
    const { emoji } = req.body;

    const message = await Message.findById(messageId);
    if (!message) {
      return res.status(404).json({ message: 'Message not found' });
    }

    const isParticipant = 
      message.sender.toString() === req.user._id.toString() ||
      message.receiver.toString() === req.user._id.toString();

    if (!isParticipant) {
      return res.status(403).json({ message: 'Access denied' });
    }

    await message.addReaction(req.user._id, emoji);
    await message.populate('sender receiver', 'name avatar');

    res.json({
      message: 'Reaction added successfully',
      messageData: message
    });
  } catch (error) {
    console.error('Add reaction error:', error);
    res.status(500).json({ message: 'Failed to add reaction', error: error.message });
  }
};

export const removeReaction = async (req, res) => {
  try {
    const { messageId } = req.params;

    const message = await Message.findById(messageId);
    if (!message) {
      return res.status(404).json({ message: 'Message not found' });
    }

    await message.removeReaction(req.user._id);
    await message.populate('sender receiver', 'name avatar');

    res.json({
      message: 'Reaction removed successfully',
      messageData: message
    });
  } catch (error) {
    console.error('Remove reaction error:', error);
    res.status(500).json({ message: 'Failed to remove reaction', error: error.message });
  }
};

export const getUnreadCount = async (req, res) => {
  try {
    const unreadCount = await Message.countDocuments({
      receiver: req.user._id,
      read: false,
      deleted: false
    });

    res.json({ unreadCount });
  } catch (error) {
    console.error('Get unread count error:', error);
    res.status(500).json({ message: 'Failed to get unread count', error: error.message });
  }
};
