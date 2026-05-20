#!/bin/bash

# SkillTrade FastAPI Backend Startup Script

echo "🚀 Starting SkillTrade FastAPI Backend..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚙️  Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env file with your configuration"
fi

# Check if MongoDB is running
echo "🗄️  Checking MongoDB connection..."
python -c "
import os
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

import asyncio
asyncio.run(check_mongo())
"

# Start the server
echo "🌐 Starting FastAPI server..."
echo "📚 API Documentation: http://localhost:8000/docs"
echo "🔗 Health Check: http://localhost:8000/health"
echo ""

# Run the application
python run.py
