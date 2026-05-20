# SkillTrade FastAPI Backend

A modern, production-ready Python FastAPI backend for the SkillTrade skill exchange platform.

## 🚀 Features

- **FastAPI**: Modern, fast web framework for building APIs
- **Motor**: Async MongoDB driver for high performance
- **Beanie**: Async ODM for MongoDB with Pydantic integration
- **JWT Authentication**: Secure token-based authentication
- **Geospatial Queries**: Location-based user matching
- **Real-time Messaging**: WebSocket support for live chat
- **Skill Matching**: Intelligent algorithm for skill compatibility
- **Rate Limiting**: Protection against API abuse
- **Comprehensive Logging**: Structured logging with security events
- **API Documentation**: Auto-generated OpenAPI/Swagger docs

## 🛠 Tech Stack

- **Python 3.9+**
- **FastAPI** - Web framework
- **Motor** - Async MongoDB driver
- **Beanie** - Async ODM
- **Pydantic** - Data validation
- **JWT** - Authentication
- **Socket.IO** - Real-time communication
- **Uvicorn** - ASGI server

## 📦 Installation

### Prerequisites

- Python 3.9 or higher
- MongoDB (local or Atlas)
- pip or poetry

### Setup

1. **Clone the repository**
```bash
git clone <repository-url>
cd skilltrade/python-backend
```

2. **Create virtual environment**
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Unix/MacOS
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. **Start MongoDB**
```bash
# Local MongoDB
mongod

# Or use MongoDB Atlas
# Update MONGODB_URI in .env
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file with the following variables:

```env
# Server Configuration
PORT=8000
HOST=0.0.0.0
DEBUG=true
ENVIRONMENT=development

# Database
MONGODB_URI=mongodb://localhost:27017/skilltrade
DATABASE_NAME=skilltrade

# JWT
JWT_SECRET=your_super_secret_jwt_key_here_change_in_production
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=10080

# CORS
FRONTEND_URL=http://localhost:5173
ALLOWED_ORIGINS=["http://localhost:5173", "http://localhost:5174"]

# Rate Limiting
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=900

# WebSocket
WEBSOCKET_HEARTBEAT_INTERVAL=30
```

## 🚀 Running the Application

### Development Mode

```bash
# Using the run script
python run.py

# Or directly with uvicorn
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Production Mode

```bash
# Using gunicorn
pip install gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000

# Using docker (Dockerfile included)
docker build -t skilltrade-backend .
docker run -p 8000:8000 skilltrade-backend
```

## 📚 API Documentation

Once the server is running, visit:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **OpenAPI JSON**: `http://localhost:8000/openapi.json`

## 🔗 API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - User login
- `GET /api/auth/me` - Get current user
- `POST /api/auth/logout` - User logout
- `POST /api/auth/change-password` - Change password
- `POST /api/auth/reset-password` - Request password reset

### Users
- `PUT /api/users/profile` - Update profile
- `GET /api/users/profile/{user_id}` - Get user profile
- `GET /api/users/search` - Search users
- `GET /api/users/nearby` - Get nearby users
- `GET /api/users/matches` - Get skill matches
- `GET /api/users/notifications` - Get notifications
- `GET /api/users/stats` - Get user statistics

### Swap Requests
- `POST /api/swaps/` - Create swap request
- `GET /api/swaps/` - Get swap requests
- `GET /api/swaps/{swap_id}` - Get specific swap
- `PUT /api/swaps/{swap_id}` - Update swap request
- `POST /api/swaps/{swap_id}/messages` - Add message to swap
- `PUT /api/swaps/{swap_id}/messages/read` - Mark messages as read

### Messages
- `POST /api/messages/` - Send message
- `GET /api/messages/conversations` - Get conversations
- `GET /api/messages/conversation/{user_id}` - Get conversation
- `PUT /api/messages/{message_id}` - Update message
- `DELETE /api/messages/{message_id}` - Delete message

### Reviews
- `POST /api/reviews/` - Create review
- `GET /api/reviews/` - Get reviews
- `GET /api/reviews/{review_id}` - Get specific review
- `PUT /api/reviews/{review_id}` - Update review
- `DELETE /api/reviews/{review_id}` - Delete review

## 🏗️ Project Structure

```
python-backend/
├── app/
│   ├── controllers/         # Business logic
│   │   ├── auth_controller.py
│   │   ├── user_controller.py
│   │   ├── swap_controller.py
│   │   ├── message_controller.py
│   │   └── review_controller.py
│   ├── database/           # Database setup
│   │   └── mongodb.py
│   ├── middleware/         # Custom middleware
│   │   └── auth_middleware.py
│   ├── models/            # Database models
│   │   ├── user.py
│   │   ├── swap_request.py
│   │   ├── message.py
│   │   └── review.py
│   ├── routes/            # API routes
│   │   ├── auth.py
│   │   ├── users.py
│   │   ├── swaps.py
│   │   ├── messages.py
│   │   └── reviews.py
│   ├── schemas/           # Pydantic schemas
│   │   ├── auth.py
│   │   ├── user.py
│   │   ├── swap.py
│   │   ├── message.py
│   │   └── review.py
│   ├── utils/             # Utility functions
│   │   ├── security.py
│   │   ├── helpers.py
│   │   ├── logging.py
│   │   └── exceptions.py
│   ├── config/            # Configuration
│   │   └── settings.py
│   └── main.py            # FastAPI app
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables template
├── run.py                # Startup script
└── README.md             # This file
```

## 🔒 Security Features

- **JWT Authentication**: Secure token-based authentication
- **Password Hashing**: bcrypt for secure password storage
- **Rate Limiting**: Protection against API abuse
- **CORS**: Cross-origin resource sharing configuration
- **Input Validation**: Comprehensive Pydantic validation
- **Security Headers**: HTTP security headers
- **SQL Injection Prevention**: MongoDB ODM prevents injection
- **XSS Protection**: Input sanitization and output encoding

## 📊 Monitoring & Logging

### Logging Levels
- **DEBUG**: Detailed debugging information
- **INFO**: General information about application flow
- **WARNING**: Unexpected behavior that doesn't stop the program
- **ERROR**: Serious error that prevented operation
- **CRITICAL**: Critical error that may cause the program to stop

### Security Events
- Login attempts (success/failure)
- Registration attempts
- Token validation
- Suspicious activities

### Performance Monitoring
- Request timing
- Database query performance
- Memory usage
- Error rates

## 🧪 Testing

### Running Tests
```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test file
pytest tests/test_auth.py
```

### Test Structure
```
tests/
├── test_auth.py
├── test_users.py
├── test_swaps.py
├── test_messages.py
└── test_reviews.py
```

## 🚀 Deployment

### Docker Deployment
```bash
# Build image
docker build -t skilltrade-backend .

# Run container
docker run -d \
  --name skilltrade-backend \
  -p 8000:8000 \
  --env-file .env \
  skilltrade-backend
```

### Environment Variables for Production
```env
ENVIRONMENT=production
DEBUG=false
JWT_SECRET=your_production_secret
MONGODB_URI=mongodb+srv://user:pass@cluster.mongodb.net/skilltrade
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new features
5. Run tests and ensure they pass
6. Submit a pull request

## 📝 License

This project is licensed under the MIT License.

## 🔗 Related Projects

- **Frontend**: React application for SkillTrade
- **Database**: MongoDB with geospatial indexing
- **Infrastructure**: Docker, Kubernetes deployment

## 📞 Support

For support and questions:
- Create an issue on GitHub
- Email: support@skilltrade.com
- Documentation: [Link to docs]

---

**Built with ❤️ using FastAPI and modern Python practices**
