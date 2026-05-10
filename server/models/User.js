import mongoose from 'mongoose';
import bcrypt from 'bcryptjs';

const userSchema = new mongoose.Schema({
  name: {
    type: String,
    required: [true, 'Name is required'],
    trim: true,
    maxlength: [50, 'Name cannot exceed 50 characters']
  },
  email: {
    type: String,
    required: [true, 'Email is required'],
    unique: true,
    lowercase: true,
    trim: true,
    match: [/^\w+([.-]?\w+)*@\w+([.-]?\w+)*(\.\w{2,3})+$/, 'Please enter a valid email']
  },
  password: {
    type: String,
    required: [true, 'Password is required'],
    minlength: [6, 'Password must be at least 6 characters long'],
    select: false
  },
  bio: {
    type: String,
    maxlength: [500, 'Bio cannot exceed 500 characters'],
    default: ''
  },
  avatar: {
    type: String,
    default: ''
  },
  offers: [{
    skill: {
      type: String,
      required: true,
      trim: true
    },
    category: {
      type: String,
      required: true,
      enum: ['technology', 'creative', 'business', 'education', 'health', 'lifestyle', 'other']
    },
    experience: {
      type: String,
      enum: ['beginner', 'intermediate', 'advanced', 'expert'],
      default: 'intermediate'
    },
    description: {
      type: String,
      maxlength: [200, 'Description cannot exceed 200 characters']
    }
  }],
  wants: [{
    skill: {
      type: String,
      required: true,
      trim: true
    },
    category: {
      type: String,
      required: true,
      enum: ['technology', 'creative', 'business', 'education', 'health', 'lifestyle', 'other']
    },
    description: {
      type: String,
      maxlength: [200, 'Description cannot exceed 200 characters']
    }
  }],
  rating: {
    type: Number,
    default: 0,
    min: 0,
    max: 5
  },
  totalReviews: {
    type: Number,
    default: 0
  },
  reviews: [{
    reviewer: {
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
    swapId: {
      type: mongoose.Schema.Types.ObjectId,
      ref: 'SwapRequest'
    },
    createdAt: {
      type: Date,
      default: Date.now
    }
  }],
  availability: {
    monday: { available: Boolean, hours: String },
    tuesday: { available: Boolean, hours: String },
    wednesday: { available: Boolean, hours: String },
    thursday: { available: Boolean, hours: String },
    friday: { available: Boolean, hours: String },
    saturday: { available: Boolean, hours: String },
    sunday: { available: Boolean, hours: String }
  },
  location: {
    type: {
      type: String,
      enum: ['Point'],
      default: 'Point'
    },
    coordinates: {
      type: [Number],
      required: true,
      validate: {
        validator: function(coordinates) {
          return coordinates.length === 2 && 
                 coordinates[0] >= -180 && coordinates[0] <= 180 &&
                 coordinates[1] >= -90 && coordinates[1] <= 90;
        },
        message: 'Invalid coordinates. Format: [longitude, latitude]'
      }
    },
    city: String,
    country: String
  },
  isOnline: {
    type: Boolean,
    default: false
  },
  lastSeen: {
    type: Date,
    default: Date.now
  },
  preferences: {
    maxDistance: {
      type: Number,
      default: 50,
      min: 1,
      max: 500
    },
    notifications: {
      email: { type: Boolean, default: true },
      push: { type: Boolean, default: true },
      messages: { type: Boolean, default: true },
      swaps: { type: Boolean, default: true }
    }
  }
}, {
  timestamps: true,
  toJSON: { virtuals: true },
  toObject: { virtuals: true }
});

userSchema.index({ location: '2dsphere' });
userSchema.index({ email: 1 });
userSchema.index({ 'offers.skill': 'text', 'wants.skill': 'text' });

userSchema.pre('save', async function(next) {
  if (!this.isModified('password')) return next();
  
  try {
    const salt = await bcrypt.genSalt(12);
    this.password = await bcrypt.hash(this.password, salt);
    next();
  } catch (error) {
    next(error);
  }
});

userSchema.methods.comparePassword = async function(candidatePassword) {
  return await bcrypt.compare(candidatePassword, this.password);
};

userSchema.methods.updateRating = function() {
  if (this.reviews.length === 0) {
    this.rating = 0;
    this.totalReviews = 0;
    return;
  }
  
  const totalRating = this.reviews.reduce((sum, review) => sum + review.rating, 0);
  this.rating = Math.round((totalRating / this.reviews.length) * 10) / 10;
  this.totalReviews = this.reviews.length;
};

userSchema.methods.toSafeObject = function() {
  const obj = this.toObject();
  delete obj.password;
  return obj;
};

userSchema.virtual('fullLocation').get(function() {
  const parts = [];
  if (this.location.city) parts.push(this.location.city);
  if (this.location.country) parts.push(this.location.country);
  return parts.join(', ');
});

export default mongoose.model('User', userSchema);
