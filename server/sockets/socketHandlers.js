import jwt from 'jsonwebtoken';
import User from '../models/User.js';
import Message from '../models/Message.js';
import SwapRequest from '../models/SwapRequest.js';

const connectedUsers = new Map();

export const setupSocketHandlers = (io) => {
  io.use(async (socket, next) => {
    try {
      const token = socket.handshake.auth.token;
      if (!token) {
        return next(new Error('Authentication token required'));
      }

      const decoded = jwt.verify(token, process.env.JWT_SECRET);
      const user = await User.findById(decoded.userId).select('-password');
      
      if (!user) {
        return next(new Error('User not found'));
      }

      socket.userId = user._id.toString();
      socket.user = user;
      next();
    } catch (error) {
      next(new Error('Authentication failed'));
    }
  });

  io.on('connection', (socket) => {
    console.log(`User ${socket.user.name} connected`);
    
    connectedUsers.set(socket.userId, {
      socketId: socket.id,
      user: socket.user,
      connectedAt: new Date()
    });

    socket.on('go_online', async () => {
      try {
        await User.findByIdAndUpdate(socket.userId, {
          isOnline: true,
          lastSeen: new Date()
        });
        
        socket.broadcast.emit('user_online', {
          userId: socket.userId,
          user: socket.user.toSafeObject()
        });
      } catch (error) {
        console.error('Go online error:', error);
      }
    });

    socket.on('go_offline', async () => {
      try {
        await User.findByIdAndUpdate(socket.userId, {
          isOnline: false,
          lastSeen: new Date()
        });
        
        socket.broadcast.emit('user_offline', {
          userId: socket.userId
        });
      } catch (error) {
        console.error('Go offline error:', error);
      }
    });

    socket.on('join_room', (roomId) => {
      socket.join(roomId);
      console.log(`User ${socket.user.name} joined room ${roomId}`);
    });

    socket.on('leave_room', (roomId) => {
      socket.leave(roomId);
      console.log(`User ${socket.user.name} left room ${roomId}`);
    });

    socket.on('send_message', async (data) => {
      try {
        const { receiverId, content, messageType = 'text' } = data;
        
        if (!receiverId || !content) {
          socket.emit('message_error', { message: 'Receiver ID and content are required' });
          return;
        }

        const message = new Message({
          sender: socket.userId,
          receiver: receiverId,
          content,
          messageType
        });

        await message.save();
        
        await message.populate('sender', 'name avatar');
        await message.populate('receiver', 'name avatar');

        const receiverSocket = Array.from(connectedUsers.values())
          .find(user => user.user._id.toString() === receiverId);

        if (receiverSocket) {
          io.to(receiverSocket.socketId).emit('new_message', message);
        }

        socket.emit('message_sent', message);

        const unreadCount = await Message.countDocuments({
          receiver: receiverId,
          read: false
        });

        if (receiverSocket) {
          io.to(receiverSocket.socketId).emit('unread_count', { count: unreadCount });
        }

      } catch (error) {
        console.error('Send message error:', error);
        socket.emit('message_error', { message: 'Failed to send message' });
      }
    });

    socket.on('mark_messages_read', async (senderId) => {
      try {
        await Message.updateMany(
          { sender: senderId, receiver: socket.userId, read: false },
          { read: true, readAt: new Date() }
        );

        const unreadCount = await Message.countDocuments({
          receiver: socket.userId,
          read: false
        });

        socket.emit('unread_count', { count: 0 });

        const senderSocket = Array.from(connectedUsers.values())
          .find(user => user.user._id.toString() === senderId);

        if (senderSocket) {
          io.to(senderSocket.socketId).emit('messages_read', {
            readerId: socket.userId
          });
        }

      } catch (error) {
        console.error('Mark messages read error:', error);
      }
    });

    socket.on('typing_start', (receiverId) => {
      const receiverSocket = Array.from(connectedUsers.values())
        .find(user => user.user._id.toString() === receiverId);

      if (receiverSocket) {
        io.to(receiverSocket.socketId).emit('user_typing', {
          userId: socket.userId,
          userName: socket.user.name
        });
      }
    });

    socket.on('typing_stop', (receiverId) => {
      const receiverSocket = Array.from(connectedUsers.values())
        .find(user => user.user._id.toString() === receiverId);

      if (receiverSocket) {
        io.to(receiverSocket.socketId).emit('user_stop_typing', {
          userId: socket.userId
        });
      }
    });

    socket.on('send_swap_request', async (data) => {
      try {
        const { receiverId, offeredSkill, requestedSkill, message, proposedDuration } = data;
        
        const swapRequest = new SwapRequest({
          sender: socket.userId,
          receiver: receiverId,
          offeredSkill,
          requestedSkill,
          message,
          proposedDuration
        });

        await swapRequest.save();
        await swapRequest.populate('sender', 'name avatar rating');
        await swapRequest.populate('receiver', 'name avatar rating');

        const receiverSocket = Array.from(connectedUsers.values())
          .find(user => user.user._id.toString() === receiverId);

        if (receiverSocket) {
          io.to(receiverSocket.socketId).emit('new_swap_request', swapRequest);
        }

        socket.emit('swap_request_sent', swapRequest);

      } catch (error) {
        console.error('Send swap request error:', error);
        socket.emit('swap_request_error', { message: 'Failed to send swap request' });
      }
    });

    socket.on('respond_swap_request', async (data) => {
      try {
        const { requestId, status, message } = data;
        
        const swapRequest = await SwapRequest.findByIdAndUpdate(
          requestId,
          { 
            status,
            $push: {
              messages: {
                sender: socket.userId,
                content: message || `Request ${status}`,
                timestamp: new Date()
              }
            }
          },
          { new: true }
        ).populate('sender receiver', 'name avatar');

        if (!swapRequest) {
          socket.emit('swap_response_error', { message: 'Swap request not found' });
          return;
        }

        const otherUserId = swapRequest.sender._id.toString() === socket.userId 
          ? swapRequest.receiver._id.toString()
          : swapRequest.sender._id.toString();

        const otherUserSocket = Array.from(connectedUsers.values())
          .find(user => user.user._id.toString() === otherUserId);

        if (otherUserSocket) {
          io.to(otherUserSocket.socketId).emit('swap_request_updated', swapRequest);
        }

        socket.emit('swap_request_responded', swapRequest);

      } catch (error) {
        console.error('Respond swap request error:', error);
        socket.emit('swap_response_error', { message: 'Failed to respond to swap request' });
      }
    });

    socket.on('get_online_users', () => {
      const onlineUsers = Array.from(connectedUsers.values()).map(user => ({
        userId: user.user._id,
        name: user.user.name,
        avatar: user.user.avatar,
        connectedAt: user.connectedAt
      }));

      socket.emit('online_users', onlineUsers);
    });

    socket.on('disconnect', async () => {
      console.log(`User ${socket.user.name} disconnected`);
      
      connectedUsers.delete(socket.userId);

      try {
        await User.findByIdAndUpdate(socket.userId, {
          isOnline: false,
          lastSeen: new Date()
        });
        
        socket.broadcast.emit('user_offline', {
          userId: socket.userId
        });
      } catch (error) {
        console.error('Disconnect error:', error);
      }
    });
  });
};

export const getConnectedUsers = () => {
  return Array.from(connectedUsers.values());
};

export const isUserOnline = (userId) => {
  return connectedUsers.has(userId);
};
