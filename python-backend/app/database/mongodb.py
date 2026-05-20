from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
import logging
from typing import List

from app.models.user import User
from app.models.swap_request import SwapRequest
from app.models.message import Message
from app.models.conversation import Conversation
from app.models.review import Review
from app.models.notification import Notification
from app.config.settings import settings

logger = logging.getLogger(__name__)

# Global database client
motor_client = None
database = None


async def init_db():
    """Initialize MongoDB connection and Beanie ODM"""
    global motor_client, database
    
    try:
        logger.info("Starting database initialization...")
        
        # Create Motor client
        logger.info("Connecting to MongoDB...")
        motor_client = AsyncIOMotorClient(
            settings.mongodb_uri,
            maxPoolSize=50,
            minPoolSize=10,
            serverSelectionTimeoutMS=5000
        )
        logger.info("MongoDB client created")
        
        # Test connection
        logger.info("Testing MongoDB connection...")
        await motor_client.admin.command('ping')
        logger.info("MongoDB connection successful")
        
        # Get database
        logger.info("Getting database reference...")
        database = motor_client[settings.database_name]
        logger.info(f"Database '{settings.database_name}' accessed")
        
        # Initialize Beanie with document models
        logger.info("Initializing Beanie ODM...")
        await init_beanie(
            database=database,
            document_models = [
                User,
                SwapRequest,
                Message,
                Conversation,
                Review,
                Notification
            ],
            allow_index_dropping=False  # Disable index dropping to avoid errors
        )
        logger.info("Beanie ODM initialized")
        
        # Create indexes
        logger.info("Creating database indexes...")
        await create_indexes()
        logger.info("Database indexes created")
        
        logger.info("Database initialization completed successfully")
        
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise


async def create_indexes():
    """Create necessary database indexes for performance"""
    try:
        # Note: Beanie automatically creates indexes from model Settings
        # Additional indexes can be created here if needed
        
        logger.info("Database indexes created successfully")
        
    except Exception as e:
        logger.error(f"Failed to create indexes: {str(e)}")
        raise


async def get_db():
    """Get database instance"""
    if database is None:
        raise RuntimeError("Database not initialized")
    return database


async def get_client():
    """Get Motor client instance"""
    if motor_client is None:
        raise RuntimeError("Database client not initialized")
    return motor_client


async def close_db():
    """Close database connection"""
    global motor_client, database
    
    if motor_client:
        motor_client.close()
        motor_client = None
        database = None
        logger.info("Database connection closed")
