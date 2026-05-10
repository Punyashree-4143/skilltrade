import mongoose from 'mongoose';

const swapRequestSchema = new mongoose.Schema({
  sender: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User',
    required: true
  },
  receiver: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User',
    required: true
  },
  offeredSkill: {
    skill: {
      type: String,
      required: true
    },
    category: {
      type: String,
      required: true,
      enum: ['technology', 'creative', 'business', 'education', 'health', 'lifestyle', 'other']
    },
    description: String
  },
  requestedSkill: {
    skill: {
      type: String,
      required: true
    },
    category: {
      type: String,
      required: true,
      enum: ['technology', 'creative', 'business', 'education', 'health', 'lifestyle', 'other']
    },
    description: String
  },
  message: {
    type: String,
    required: true,
    maxlength: [1000, 'Message cannot exceed 1000 characters']
  },
  status: {
    type: String,
    enum: ['pending', 'accepted', 'rejected', 'completed', 'cancelled'],
    default: 'pending'
  },
  proposedDuration: {
    type: Number,
    required: true,
    min: 1,
    max: 480
  },
  scheduledDate: {
    type: Date
  },
  scheduledTime: {
    type: String
  },
  location: {
    type: String,
    enum: ['online', 'in-person'],
    default: 'online'
  },
  meetingDetails: {
    type: String,
    maxlength: [500, 'Meeting details cannot exceed 500 characters']
  },
  completionNotes: {
    type: String,
    maxlength: [1000, 'Completion notes cannot exceed 1000 characters']
  },
  matchScore: {
    type: Number,
    min: 0,
    max: 100
  },
  messages: [{
    sender: {
      type: mongoose.Schema.Types.ObjectId,
      ref: 'User',
      required: true
    },
    content: {
      type: String,
      required: true,
      maxlength: [1000, 'Message cannot exceed 1000 characters']
    },
    timestamp: {
      type: Date,
      default: Date.now
    },
    read: {
      type: Boolean,
      default: false
    }
  }],
  reviews: [{
    reviewer: {
      type: mongoose.Schema.Types.ObjectId,
      ref: 'User',
      required: true
    },
    reviewee: {
      type: mongoose.Schema.Types.ObjectId,
      ref: 'User',
      required: true
    },
    rating: {
      type: Number,
      required: true,
      min: 1,
      max: 5
    },
    comment: {
      type: String,
      maxlength: [500, 'Review comment cannot exceed 500 characters']
    },
    createdAt: {
      type: Date,
      default: Date.now
    }
  }]
}, {
  timestamps: true,
  toJSON: { virtuals: true },
  toObject: { virtuals: true }
});

swapRequestSchema.index({ sender: 1, receiver: 1 });
swapRequestSchema.index({ receiver: 1, status: 1 });
swapRequestSchema.index({ status: 1, createdAt: -1 });

swapRequestSchema.pre('save', function(next) {
  if (this.sender.toString() === this.receiver.toString()) {
    const error = new Error('Cannot send swap request to yourself');
    return next(error);
  }
  next();
});

swapRequestSchema.methods.addMessage = function(senderId, content) {
  this.messages.push({
    sender: senderId,
    content: content,
    timestamp: new Date(),
    read: false
  });
  return this.save();
};

swapRequestSchema.methods.markMessagesAsRead = function(userId) {
  this.messages.forEach(message => {
    if (message.sender.toString() !== userId.toString()) {
      message.read = true;
    }
  });
  return this.save();
};

swapRequestSchema.methods.getUnreadCount = function(userId) {
  return this.messages.filter(message => 
    message.sender.toString() !== userId.toString() && !message.read
  ).length;
};

swapRequestSchema.virtual('isCompleted').get(function() {
  return this.status === 'completed';
});

swapRequestSchema.virtual('canBeReviewed').get(function() {
  return this.status === 'completed' && 
         !this.reviews.some(review => 
           review.reviewer.toString() === this.sender.toString() ||
           review.reviewee.toString() === this.sender.toString()
         );
});

export default mongoose.model('SwapRequest', swapRequestSchema);
