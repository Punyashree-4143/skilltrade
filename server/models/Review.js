import mongoose from 'mongoose';

const reviewSchema = new mongoose.Schema({
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
  swapRequest: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'SwapRequest',
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
    required: true,
    maxlength: [500, 'Review comment cannot exceed 500 characters']
  },
  skills: [{
    name: {
      type: String,
      required: true
    },
    rating: {
      type: Number,
      min: 1,
      max: 5
    }
  }],
  wouldSwapAgain: {
    type: Boolean,
    required: true
  },
  helpfulness: {
    type: Number,
    min: 1,
    max: 5
  },
  communication: {
    type: Number,
    min: 1,
    max: 5
  },
  punctuality: {
    type: Number,
    min: 1,
    max: 5
  },
  isPublic: {
    type: Boolean,
    default: true
  },
  reported: {
    type: Boolean,
    default: false
  },
  reportReason: {
    type: String
  },
  response: {
    content: {
      type: String,
      maxlength: [500, 'Response cannot exceed 500 characters']
    },
    createdAt: {
      type: Date
    }
  }
}, {
  timestamps: true,
  toJSON: { virtuals: true },
  toObject: { virtuals: true }
});

reviewSchema.index({ reviewer: 1, reviewee: 1 });
reviewSchema.index({ reviewee: 1, rating: -1 });
reviewSchema.index({ swapRequest: 1 });
reviewSchema.index({ createdAt: -1 });

reviewSchema.pre('save', function(next) {
  if (this.reviewer.toString() === this.reviewee.toString()) {
    const error = new Error('Cannot review yourself');
    return next(error);
  }
  next();
});

reviewSchema.methods.addResponse = function(content) {
  this.response = {
    content: content,
    createdAt: new Date()
  };
  return this.save();
};

reviewSchema.methods.report = function(reason) {
  this.reported = true;
  this.reportReason = reason;
  return this.save();
};

reviewSchema.virtual('averageSkillRating').get(function() {
  if (this.skills.length === 0) return 0;
  const total = this.skills.reduce((sum, skill) => sum + (skill.rating || 0), 0);
  return Math.round((total / this.skills.length) * 10) / 10;
});

reviewSchema.virtual('timeAgo').get(function() {
  const now = new Date();
  const diff = now - this.createdAt;
  const minutes = Math.floor(diff / 60000);
  const hours = Math.floor(diff / 3600000);
  const days = Math.floor(diff / 86400000);
  
  if (minutes < 1) return 'just now';
  if (minutes < 60) return `${minutes}m ago`;
  if (hours < 24) return `${hours}h ago`;
  if (days < 7) return `${days}d ago`;
  return this.createdAt.toLocaleDateString();
});

export default mongoose.model('Review', reviewSchema);
