#!/usr/bin/env python3
"""
MongoDB Connection Test Script
Run this to verify MongoDB connection and user operations work
"""

import asyncio
import sys
import os

# Add the app directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database.mongodb import init_db
from app.models.user import User, ExploreUser

async def test_mongodb_connection():
    """Test MongoDB connection and basic operations"""
    print("=== MONGODB CONNECTION TEST ===")
    
    try:
        # Initialize database
        print("1. Initializing database...")
        await init_db()
        print("✅ Database initialized successfully")
        
        # Test user creation
        print("\n2. Testing user creation...")
        test_user = User(
            name="Test User",
            email="test@example.com",
            bio="Test user for MongoDB verification",
            offers=[{"skill": "JavaScript", "category": "other", "experience": "intermediate"}],
            wants=[{"skill": "Python", "category": "other"}],
            rating=4.5,
            is_online=True
        )
        
        await test_user.save()
        print(f"✅ User created: {test_user.name} (ID: {test_user.id})")
        
        # Test user fetching
        print("\n3. Testing user fetching...")
        users = await User.find_all().to_list()
        print(f"✅ Found {len(users)} users in database")
        
        for user in users:
            print(f"   - {user.name} ({user.email})")
        
        # Test ExploreUser creation
        print("\n4. Testing ExploreUser creation...")
        explore_user = ExploreUser(
            id=str(test_user.id),
            email=test_user.email,
            name=test_user.name,
            bio=test_user.bio,
            skills_offered=["JavaScript"],
            skills_wanted=["Python"],
            rating=test_user.rating,
            total_reviews=0,
            is_online=True
        )
        
        await explore_user.save()
        print(f"✅ ExploreUser created: {explore_user.name} (ID: {explore_user.id})")
        
        # Test ExploreUser fetching
        print("\n5. Testing ExploreUser fetching...")
        explore_users = await ExploreUser.find_all().to_list()
        print(f"✅ Found {len(explore_users)} explore users in database")
        
        print("\n=== ALL TESTS PASSED ===")
        print("MongoDB connection and user operations are working correctly!")
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    print("Starting MongoDB Connection Test...")
    print("Make sure MongoDB is running on localhost:27017")
    print("-" * 50)
    
    success = asyncio.run(test_mongodb_connection())
    
    if success:
        print("\n🎉 MongoDB system is ready!")
    else:
        print("\n💥 MongoDB system has issues!")
        sys.exit(1)
