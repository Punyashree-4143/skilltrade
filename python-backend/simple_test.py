#!/usr/bin/env python3
"""
Simple MongoDB Test - Focus on core functionality
"""

import asyncio
import sys
import os
import requests

# Add the app directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database.mongodb import init_db
from app.models.user import User

BASE_URL = "http://localhost:8000"

async def test_core_functionality():
    """Test core MongoDB functionality"""
    print("=== CORE FUNCTIONALITY TEST ===")
    
    try:
        # 1. Test database connection
        print("\n1. Testing database connection...")
        await init_db()
        print("✅ Database initialized successfully")
        
        # 2. Test User model creation
        print("\n2. Testing User model creation...")
        test_user = User(
            name="Test User",
            email="test@example.com",
            bio="Test user for verification",
            offers=[{"skill": "JavaScript", "category": "other", "experience": "intermediate"}],
            wants=[{"skill": "Python", "category": "other"}],
            rating=4.5,
            is_online=True
        )
        
        await test_user.save()
        print(f"✅ User created: {test_user.name} (ID: {test_user.id})")
        
        # 3. Test User model fetching
        print("\n3. Testing User model fetching...")
        users = await User.find_all().to_list()
        print(f"✅ Found {len(users)} users in database")
        
        for user in users:
            print(f"   - {user.name} ({user.email})")
        
        print("\n=== CORE FUNCTIONALITY WORKS ===")
        return True
        
    except Exception as e:
        print(f"\n❌ CORE TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_api_endpoints():
    """Test API endpoints"""
    print("\n=== API ENDPOINTS TEST ===")
    
    try:
        # Test GET /api/users
        print("\n1. Testing GET /api/users...")
        try:
            response = requests.get(f"{BASE_URL}/api/users", timeout=5)
            if response.status_code == 200:
                users = response.json()
                print(f"✅ GET /api/users returned {len(users)} users")
                
                # Verify user structure
                if users:
                    user = users[0]
                    print(f"   Sample user: {user.get('name', 'Unknown')} ({user.get('email', 'Unknown')})")
                    print(f"   Skills offered: {user.get('skills_offered', [])}")
                    print(f"   Skills wanted: {user.get('skills_wanted', [])}")
            else:
                print(f"❌ GET /api/users failed: {response.status_code}")
                return False
        except requests.exceptions.ConnectionError:
            print("⚠️  Server not running - start with: python -m uvicorn app.main:app --reload")
            return False
        except Exception as e:
            print(f"❌ API test error: {e}")
            return False
        
        # Test POST /api/users
        print("\n2. Testing POST /api/users...")
        test_user_data = {
            "name": "API Test User",
            "email": "api-test@example.com",
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
                return False
        except Exception as e:
            print(f"❌ POST test error: {e}")
            return False
        
        print("\n=== API ENDPOINTS WORK ===")
        return True
        
    except Exception as e:
        print(f"❌ API TEST FAILED: {str(e)}")
        return False

def main():
    """Main test function"""
    print("🚀 SkillTrade MongoDB System Test")
    print("=" * 50)
    
    # Test core functionality
    core_success = asyncio.run(test_core_functionality())
    
    # Test API endpoints
    api_success = test_api_endpoints()
    
    # Results
    print("\n" + "=" * 50)
    print("🏁 TEST RESULTS")
    print("=" * 50)
    
    if core_success:
        print("✅ MongoDB Core: PASSED")
    else:
        print("❌ MongoDB Core: FAILED")
    
    if api_success:
        print("✅ API Endpoints: PASSED")
    else:
        print("❌ API Endpoints: FAILED")
    
    if core_success and api_success:
        print("\n🎉 SYSTEM IS READY!")
        print("\nNext steps:")
        print("1. Backend is working correctly")
        print("2. Frontend can now create and fetch real users")
        print("3. Test cross-browser synchronization")
        return True
    else:
        print("\n💥 SYSTEM NEEDS FIXES!")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
