@echo off
REM SkillTrade FastAPI Backend Startup Script (Windows)

echo 🚀 Starting SkillTrade FastAPI Backend...

REM Check if virtual environment exists
if not exist "venv" (
    echo 📦 Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo 📦 Installing dependencies...
pip install -r requirements.txt

REM Check if .env file exists
if not exist ".env" (
    echo ⚙️  Creating .env file from template...
    copy .env.example .env
    echo ⚠️  Please edit .env file with your configuration
)

REM Check if MongoDB is running
echo 🗄️  Checking MongoDB connection...
python -c "
import os
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from app.config.settings import settings

async def check_mongo():
    try:
        client = AsyncIOMotorClient(settings.mongodb_uri)
        await client.admin.command('ping')
        print('✅ MongoDB connection successful')
        await client.close()
    except Exception as e:
        print(f'❌ MongoDB connection failed: {e}')
        print('Please ensure MongoDB is running and MONGODB_URI is correct')
        exit(1)

asyncio.run(check_mongo())
"

REM Start the server
echo 🌐 Starting FastAPI server...
echo 📚 API Documentation: http://localhost:8000/docs
echo 🔗 Health Check: http://localhost:8000/health
echo.

REM Run the application
python run.py

pause
