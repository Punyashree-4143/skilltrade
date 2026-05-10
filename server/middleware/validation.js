import { body, validationResult } from 'express-validator';

export const handleValidationErrors = (req, res, next) => {
  const errors = validationResult(req);
  if (!errors.isEmpty()) {
    return res.status(400).json({
      message: 'Validation failed',
      errors: errors.array()
    });
  }
  next();
};

export const validateRegister = [
  body('name')
    .trim()
    .isLength({ min: 2, max: 50 })
    .withMessage('Name must be between 2 and 50 characters')
    .matches(/^[a-zA-Z\s]+$/)
    .withMessage('Name can only contain letters and spaces'),
  
  body('email')
    .isEmail()
    .withMessage('Please provide a valid email')
    .normalizeEmail(),
  
  body('password')
    .isLength({ min: 6 })
    .withMessage('Password must be at least 6 characters long')
    .matches(/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/)
    .withMessage('Password must contain at least one uppercase letter, one lowercase letter, and one number'),
  
  body('location.coordinates')
    .isArray({ min: 2, max: 2 })
    .withMessage('Location coordinates must be an array with 2 elements'),
  
  body('location.coordinates.*')
    .isFloat({ min: -180, max: 180 })
    .withMessage('Coordinates must be valid longitude/latitude values'),
  
  handleValidationErrors
];

export const validateLogin = [
  body('email')
    .isEmail()
    .withMessage('Please provide a valid email')
    .normalizeEmail(),
  
  body('password')
    .notEmpty()
    .withMessage('Password is required'),
  
  handleValidationErrors
];

export const validateProfileUpdate = [
  body('name')
    .optional()
    .trim()
    .isLength({ min: 2, max: 50 })
    .withMessage('Name must be between 2 and 50 characters'),
  
  body('bio')
    .optional()
    .trim()
    .isLength({ max: 500 })
    .withMessage('Bio cannot exceed 500 characters'),
  
  body('offers')
    .optional()
    .isArray()
    .withMessage('Offers must be an array'),
  
  body('offers.*.skill')
    .optional()
    .trim()
    .isLength({ min: 2, max: 50 })
    .withMessage('Skill name must be between 2 and 50 characters'),
  
  body('offers.*.category')
    .optional()
    .isIn(['technology', 'creative', 'business', 'education', 'health', 'lifestyle', 'other'])
    .withMessage('Invalid skill category'),
  
  body('wants')
    .optional()
    .isArray()
    .withMessage('Wants must be an array'),
  
  body('wants.*.skill')
    .optional()
    .trim()
    .isLength({ min: 2, max: 50 })
    .withMessage('Skill name must be between 2 and 50 characters'),
  
  body('wants.*.category')
    .optional()
    .isIn(['technology', 'creative', 'business', 'education', 'health', 'lifestyle', 'other'])
    .withMessage('Invalid skill category'),
  
  body('location.coordinates')
    .optional()
    .isArray({ min: 2, max: 2 })
    .withMessage('Location coordinates must be an array with 2 elements'),
  
  handleValidationErrors
];

export const validateSwapRequest = [
  body('receiver')
    .isMongoId()
    .withMessage('Invalid receiver ID'),
  
  body('offeredSkill.skill')
    .trim()
    .isLength({ min: 2, max: 50 })
    .withMessage('Offered skill must be between 2 and 50 characters'),
  
  body('offeredSkill.category')
    .isIn(['technology', 'creative', 'business', 'education', 'health', 'lifestyle', 'other'])
    .withMessage('Invalid skill category'),
  
  body('requestedSkill.skill')
    .trim()
    .isLength({ min: 2, max: 50 })
    .withMessage('Requested skill must be between 2 and 50 characters'),
  
  body('requestedSkill.category')
    .isIn(['technology', 'creative', 'business', 'education', 'health', 'lifestyle', 'other'])
    .withMessage('Invalid skill category'),
  
  body('message')
    .trim()
    .isLength({ min: 10, max: 1000 })
    .withMessage('Message must be between 10 and 1000 characters'),
  
  body('proposedDuration')
    .isInt({ min: 15, max: 480 })
    .withMessage('Duration must be between 15 and 480 minutes'),
  
  handleValidationErrors
];

export const validateMessage = [
  body('receiver')
    .isMongoId()
    .withMessage('Invalid receiver ID'),
  
  body('content')
    .trim()
    .isLength({ min: 1, max: 1000 })
    .withMessage('Message must be between 1 and 1000 characters'),
  
  handleValidationErrors
];

export const validateReview = [
  body('reviewee')
    .isMongoId()
    .withMessage('Invalid reviewee ID'),
  
  body('swapRequest')
    .isMongoId()
    .withMessage('Invalid swap request ID'),
  
  body('rating')
    .isInt({ min: 1, max: 5 })
    .withMessage('Rating must be between 1 and 5'),
  
  body('comment')
    .trim()
    .isLength({ min: 10, max: 500 })
    .withMessage('Review comment must be between 10 and 500 characters'),
  
  body('wouldSwapAgain')
    .isBoolean()
    .withMessage('wouldSwapAgain must be a boolean'),
  
  handleValidationErrors
];
