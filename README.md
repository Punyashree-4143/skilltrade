# SkillTrade – The Barter Network

A modern skill exchange platform where users trade skills and services instead of money. Connect with skilled individuals in your area, exchange what you know for what you want to learn.

## 🌟 Features

- **Skill Matching Algorithm**: Intelligently matches users based on skills, location, and preferences
- **Real-time Chat**: Instant messaging with typing indicators and read receipts
- **Geolocation**: Find nearby users for in-person meetups
- **Rating System**: Build trust with community-driven reviews
- **Swap Requests**: Send and manage skill exchange requests
- **Responsive Design**: Beautiful UI that works on all devices

## 🛠 Tech Stack

### Frontend
- **React.js** with Vite
- **Tailwind CSS** for styling
- **Framer Motion** for animations
- **React Router** for navigation
- **Axios** for API calls
- **Socket.IO Client** for real-time features
- **Leaflet.js** for maps

### Backend
- **Node.js** with Express.js
- **MongoDB** with Mongoose ODM
- **Socket.IO** for real-time communication
- **JWT** for authentication
- **bcryptjs** for password hashing
- **Express Validator** for input validation

## 🚀 Quick Start

### Prerequisites
- Node.js (v18 or higher)
- MongoDB (local or Atlas)
- npm or yarn

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd skilltrade
```

2. **Install dependencies**
```bash
# Install client dependencies
cd client
npm install

# Install server dependencies
cd ../server
npm install
```

3. **Set up environment variables**

**Client (.env)**
```env
VITE_API_URL=http://localhost:5000/api
VITE_MAP_API_KEY=your_mapbox_api_key_here
VITE_SOCKET_URL=http://localhost:5000
```

**Server (.env)**
```env
PORT=5000
NODE_ENV=development
MONGODB_URI=mongodb://localhost:27017/skilltrade
JWT_SECRET=your_super_secret_jwt_key_here_change_in_production
JWT_EXPIRE=7d
FRONTEND_URL=http://localhost:5173
```

4. **Start the applications**

**Start the backend server**
```bash
cd server
npm run dev
```

**Start the frontend development server**
```bash
cd client
npm run dev
```

5. **Open your browser**
Navigate to `http://localhost:5173` to access the application.

## 📁 Project Structure

```
skilltrade/
├── client/                 # React frontend
│   ├── src/
│   │   ├── components/     # Reusable UI components
│   │   ├── context/        # React contexts
│   │   ├── pages/          # Page components
│   │   └── utils/          # Utility functions
│   ├── public/
│   └── package.json
├── server/                 # Node.js backend
│   ├── config/            # Configuration files
│   ├── controllers/       # Route controllers
│   ├── middleware/        # Custom middleware
│   ├── models/           # MongoDB models
│   ├── routes/           # API routes
│   ├── services/         # Business logic
│   ├── sockets/          # Socket.IO handlers
│   └── utils/            # Utility functions
└── README.md
```

## 🔧 API Documentation

### Authentication Endpoints

- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - User login
- `POST /api/auth/logout` - User logout
- `GET /api/auth/me` - Get current user

### User Endpoints

- `GET /api/users/profile/:userId` - Get user profile
- `PUT /api/users/profile` - Update user profile
- `GET /api/users/search` - Search users
- `GET /api/users/matches` - Get skill matches
- `GET /api/users/nearby` - Get nearby users

### Swap Requests Endpoints

- `POST /api/swaps` - Create swap request
- `GET /api/swaps` - Get swap requests
- `PUT /api/swaps/:id` - Update swap request
- `POST /api/swaps/:id/messages` - Add message to swap

### Messages Endpoints

- `POST /api/messages` - Send message
- `GET /api/messages/:userId` - Get conversation
- `GET /api/messages/conversations` - Get all conversations

### Reviews Endpoints

- `POST /api/reviews` - Create review
- `GET /api/reviews` - Get reviews
- `PUT /api/reviews/:id` - Update review

## 🎯 Core Features

### Skill Matching Algorithm

The matching algorithm considers:
- **Skill Compatibility**: What you offer vs what others want
- **Location**: Proximity for in-person exchanges
- **Ratings**: User reputation and success rate
- **Availability**: User scheduling preferences

### Real-time Features

- **Live Chat**: Instant messaging with Socket.IO
- **Online Status**: See who's online
- **Typing Indicators**: Know when someone is typing
- **Read Receipts**: Message delivery confirmation

### Geolocation

- **Location-based Search**: Find users near you
- **Distance Filters**: Set maximum distance preferences
- **Map View**: Visual representation of nearby users

## 🔐 Security Features

- **JWT Authentication**: Secure token-based auth
- **Password Hashing**: bcryptjs for secure passwords
- **Input Validation**: Express validator for data integrity
- **Rate Limiting**: Prevent API abuse
- **CORS Protection**: Secure cross-origin requests

## 🎨 UI/UX Features

- **Glassmorphism Design**: Modern glass-like UI elements
- **Dark Theme**: Easy on the eyes dark mode
- **Responsive Layout**: Works on all screen sizes
- **Smooth Animations**: Framer Motion transitions
- **Loading States**: Skeleton loaders and spinners
- **Toast Notifications**: Non-intrusive feedback

## 🚀 Deployment

### Frontend (Vercel/Netlify)
```bash
cd client
npm run build
# Deploy dist/ folder
```

### Backend (Heroku/Railway)
```bash
cd server
npm start
# Deploy with environment variables
```

### Database (MongoDB Atlas)
1. Create cluster on MongoDB Atlas
2. Add connection string to `.env`
3. Ensure IP whitelist includes your deployment

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For support, please contact:
- Create an issue on GitHub
- Email: support@skilltrade.com
- Discord: [Join our community]

## 🎯 Future Roadmap

- [ ] Mobile app (React Native)
- [ ] Video calling integration
- [ ] Advanced filtering options
- [ ] Skill verification system
- [ ] Payment processing for premium features
- [ ] AI-powered skill recommendations
- [ ] Community events and workshops

---

**Built with ❤️ by the SkillTrade team**
