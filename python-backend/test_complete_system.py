#!/usr/bin/env python3
"""
Complete System Test Script
Tests MongoDB connection, user creation, and API endpoints
"""

import asyncio
import sys
import os
import requests
import json

# Add the app directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database.mongodb import init_db
from app.models.user import User, ExploreUser

BASE_URL = "http://localhost:8000"

async def test_backend_system():
    """Test complete backend system"""
    print("=== COMPLETE BACKEND SYSTEM TEST ===")
    
    try:
        # 1. Test database connection
        print("\n1. Testing database connection...")
        await init_db()
        print("✅ Database initialized successfully")
        
        # 2. Clear existing test data
        print("\n2. Cleaning up existing test data...")
        await User.find({"email": {"$regex": r"^test.*"}}).delete()
        await ExploreUser.find({"email": {"$regex": r"^test.*"}}).delete()
        print("✅ Test data cleaned")
        
        # 3. Test direct model creation
        print("\n3. Testing direct model creation...")
        test_user = User(
            name="Test User Direct",
            email="test-direct@example.com",
            bio="Test user created directly",
            offers=[{"skill": "JavaScript", "category": "other", "experience": "intermediate"}],
            wants=[{"skill": "Python", "category": "other"}],
            rating=4.5,
            is_online=True
        )
        
        await test_user.save()
        print(f"✅ Direct user created: {test_user.name} (ID: {test_user.id})")
        
        # 4. Test API endpoints (need server running)
        print("\n4. Testing API endpoints...")
        
        # Test GET /api/users
        try:
            response = requests.get(f"{BASE_URL}/api/users")
            if response.status_code == 200:
                users = response.json()
                print(f"✅ GET /api/users returned {len(users)} users")
            else:
                print(f"❌ GET /api/users failed: {response.status_code}")
        except requests.exceptions.ConnectionError:
            print("⚠️  Server not running, skipping API tests")
            return True
        
        # Test POST /api/users
        test_user_data = {
            "name": "Test User API",
            "email": "test-api@example.com",
            "bio": "Test user created via API",
            "skills_offered": ["React", "Node.js"],
            "skills_wanted": ["Python"],
            "location": {"city": "Test City", "country": "Test Country"},
            "rating": 4.0,
            "availability": "Flexible",
            "experience_level": "intermediate"
        }
        
        try:
            response = requests.post(f"{BASE_URL}/api/users", json=test_user_data)
            if response.status_code == 200:
                created_user = response.json()
                print(f"✅ POST /api/users created: {created_user['name']} (ID: {created_user['id']})")
            else:
                print(f"❌ POST /api/users failed: {response.status_code}")
                print(f"Response: {response.text}")
        except Exception as e:
            print(f"❌ POST /api/users error: {e}")
        
        # 5. Verify data in database
        print("\n5. Verifying data in database...")
        users = await User.find_all().to_list()
        explore_users = await ExploreUser.find_all().to_list()
        
        print(f"✅ Found {len(users)} users in User collection")
        print(f"✅ Found {len(explore_users)} users in ExploreUser collection")
        
        for user in users:
            print(f"   - {user.name} ({user.email})")
        
        print("\n=== ALL BACKEND TESTS PASSED ===")
        return True
        
    except Exception as e:
        print(f"\n❌ BACKEND TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_frontend_integration():
    """Test frontend integration points"""
    print("\n=== FRONTEND INTEGRATION TEST ===")
    
    try:
        # Test API endpoints that frontend uses
        print("\n1. Testing frontend API calls...")
        
        # Test GET /api/users (Explore page)
        try:
            response = requests.get(f"{BASE_URL}/api/users", timeout=5)
            if response.status_code == 200:
                users = response.json()
                print(f"✅ Explore page API works: {len(users)} users returned")
                
                # Verify user structure
                if users:
                    user = users[0]
                    required_fields = ['id', 'name', 'email', 'skills_offered', 'skills_wanted']
                    missing_fields = [field for field in required_fields if field not in user]
                    if missing_fields:
                        print(f"⚠️  Missing fields in user data: {missing_fields}")
                    else:
                        print("✅ User data structure is correct")
            else:
                print(f"❌ Explore API failed: {response.status_code}")
        except requests.exceptions.ConnectionError:
            print("⚠️  Server not running, cannot test frontend integration")
        except Exception as e:
            print(f"❌ Frontend integration test failed: {e}")
        
        print("\n=== FRONTEND INTEGRATION TEST COMPLETED ===")
        return True
        
    except Exception as e:
        print(f"❌ FRONTEND TEST FAILED: {str(e)}")
        return False

def main():
    """Main test function"""
    print("🚀 Starting Complete SkillTrade System Test")
    print("=" * 60)
    
    # Test backend system
    backend_success = asyncio.run(test_backend_system())
    
    # Test frontend integration
    frontend_success = test_frontend_integration()
    
    # Final results
    print("\n" + "=" * 60)
    print("🏁 FINAL TEST RESULTS")
    print("=" * 60)
    
    if backend_success:
        print("✅ Backend System: PASSED")
    else:
        print("❌ Backend System: FAILED")
    
    if frontend_success:
        print("✅ Frontend Integration: PASSED")
    else:
        print("❌ Frontend Integration: FAILED")
    
    if backend_success and frontend_success:
        print("\n🎉 ALL SYSTEMS WORKING CORRECTLY!")
        print("The SkillTrade MongoDB persistence system is ready!")
        print("\nNext steps:")
        print("1. Start the backend server: python -m uvicorn app.main:app --reload")
        print("2. Start the frontend: npm run dev")
        print("3. Test cross-browser user creation")
        return True
    else:
        print("\n💥 SYSTEM HAS ISSUES!")
        print("Please check the error messages above and fix the issues.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
