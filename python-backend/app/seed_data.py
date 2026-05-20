import asyncio
from datetime import datetime, timedelta
from app.models.user import ExploreUser
from app.database import get_database
import logging

logger = logging.getLogger(__name__)

async def seed_users():
    """Seed MongoDB with realistic user data for Explore module"""
    try:
        db = get_database()
        
        # Realistic user data for SkillTrade
        users_data = [
            {
                "id": "user-1",
                "name": "Sarah Chen",
                "bio": "Full-stack developer passionate about teaching React and learning guitar. Love skill sharing!",
                "avatar": "https://images.unsplash.com/photo-1494790108755-2616b612c4d7?w=100&h=100&fit=crop&crop=face",
                "location": {
                    "city": "San Francisco",
                    "country": "USA"
                },
                "skills_offered": [
                    "React", "JavaScript", "Node.js", "MongoDB", "Python"
                ],
                "skills_wanted": [
                    "UI Design", "Machine Learning", "GraphQL"
                ],
                "rating": 4.8,
                "availability": "Weekends",
                "experience_level": "expert",
                "total_reviews": 23,
                "is_online": True,
                "last_seen": (datetime.now() - timedelta(minutes=5)).isoformat(),
                "created_at": (datetime.now() - timedelta(days=30)).isoformat()
            },
            {
                "id": "user-2",
                "name": "Mike Rodriguez",
                "bio": "Professional photographer looking to learn web development. Can teach photography basics!",
                "avatar": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=100&h=100&fit=crop&crop=face",
                "location": {
                    "city": "Los Angeles",
                    "country": "USA"
                },
                "skills_offered": [
                    "Photography", "Photo Editing", "Videography"
                ],
                "skills_wanted": [
                    "Web Development", "React", "Python"
                ],
                "rating": 4.6,
                "availability": "Evenings",
                "experience_level": "advanced",
                "total_reviews": 18,
                "is_online": False,
                "last_seen": (datetime.now() - timedelta(minutes=30)).isoformat(),
                "created_at": (datetime.now() - timedelta(days=45)).isoformat()
            },
            {
                "id": "user-3",
                "name": "Emma Thompson",
                "bio": "Marketing expert turned yoga instructor. Love helping people find their balance!",
                "avatar": "https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=100&h=100&fit=crop&crop=face",
                "location": {
                    "city": "London",
                    "country": "UK"
                },
                "skills_offered": [
                    "Digital Marketing", "SEO", "Content Writing", "Yoga"
                ],
                "skills_wanted": [
                    "Web Development", "Data Science", "Photography"
                ],
                "rating": 4.9,
                "availability": "Flexible",
                "experience_level": "intermediate",
                "total_reviews": 31,
                "is_online": True,
                "last_seen": (datetime.now() - timedelta(hours=2)).isoformat(),
                "created_at": (datetime.now() - timedelta(days=60)).isoformat()
            },
            {
                "id": "user-4",
                "name": "Alex Johnson",
                "bio": "Data scientist specializing in machine learning and AI. Always eager to learn new skills!",
                "avatar": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=100&h=100&fit=crop&crop=face",
                "location": {
                    "city": "New York",
                    "country": "USA"
                },
                "skills_offered": [
                    "Machine Learning", "Python", "TensorFlow", "Data Science"
                ],
                "skills_wanted": [
                    "DevOps", "Cloud Architecture", "UI Design"
                ],
                "rating": 4.7,
                "availability": "Weekdays",
                "experience_level": "advanced",
                "total_reviews": 27,
                "is_online": True,
                "last_seen": (datetime.now() - timedelta(minutes=15)).isoformat(),
                "created_at": (datetime.now() - timedelta(days=90)).isoformat()
            },
            {
                "id": "user-5",
                "name": "Maria Garcia",
                "bio": "UX designer passionate about creating intuitive user experiences. Learning Spanish for better communication!",
                "avatar": "https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=100&h=100&fit=crop&crop=face",
                "location": {
                    "city": "Austin",
                    "country": "USA"
                },
                "skills_offered": [
                    "UI Design", "UX Design", "Figma", "Adobe Creative Suite"
                ],
                "skills_wanted": [
                    "Spanish", "User Research", "Frontend Development"
                ],
                "rating": 4.5,
                "availability": "Flexible",
                "experience_level": "intermediate",
                "total_reviews": 19,
                "is_online": False,
                "last_seen": (datetime.now() - timedelta(hours=8)).isoformat(),
                "created_at": (datetime.now() - timedelta(days=120)).isoformat()
            },
            {
                "id": "user-6",
                "name": "David Kim",
                "bio": "Full-stack developer with expertise in cloud technologies. Love mentoring junior developers!",
                "avatar": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=100&h=100&fit=crop&crop=face",
                "location": {
                    "city": "Seattle",
                    "country": "USA"
                },
                "skills_offered": [
                    "AWS", "Docker", "Kubernetes", "React", "Node.js"
                ],
                "skills_wanted": [
                    "Mobile Development", "GraphQL", "System Design"
                ],
                "rating": 4.9,
                "availability": "Weekdays",
                "experience_level": "expert",
                "total_reviews": 42,
                "is_online": True,
                "last_seen": (datetime.now() - timedelta(minutes=3)).isoformat(),
                "created_at": (datetime.now() - timedelta(days=15)).isoformat()
            },
            {
                "id": "user-7",
                "name": "Lisa Wang",
                "bio": "Creative director and motion graphics artist. Teaching animation and video production!",
                "avatar": "https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=100&h=100&fit=crop&crop=face",
                "location": {
                    "city": "Toronto",
                    "country": "Canada"
                },
                "skills_offered": [
                    "Animation", "3D Modeling", "Video Editing", "After Effects"
                ],
                "skills_wanted": [
                    "Web Development", "Business Strategy", "Project Management"
                ],
                "rating": 4.6,
                "availability": "Flexible",
                "experience_level": "expert",
                "total_reviews": 28,
                "is_online": True,
                "last_seen": (datetime.now() - timedelta(minutes=10)).isoformat(),
                "created_at": (datetime.now() - timedelta(days=75)).isoformat()
            },
            {
                "id": "user-8",
                "name": "James Wilson",
                "bio": "Marketing specialist turned content creator. Learning video production and social media marketing!",
                "avatar": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=100&h=100&fit=crop&crop=face",
                "location": {
                    "city": "Chicago",
                    "country": "USA"
                },
                "skills_offered": [
                    "Digital Marketing", "SEO", "Content Writing", "Social Media Marketing"
                ],
                "skills_wanted": [
                    "Video Production", "Photography", "Copywriting"
                ],
                "rating": 4.4,
                "availability": "Weekends",
                "experience_level": "intermediate",
                "total_reviews": 15,
                "is_online": False,
                "last_seen": (datetime.now() - timedelta(days=1)).isoformat(),
                "created_at": (datetime.now() - timedelta(days=180)).isoformat()
            },
            {
                "id": "user-9",
                "name": "Sophie Martin",
                "bio": "Language teacher and cultural exchange enthusiast. Teaching French and learning Mandarin!",
                "avatar": "https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=100&h=100&fit=crop&crop=face",
                "location": {
                    "city": "Paris",
                    "country": "France"
                },
                "skills_offered": [
                    "French", "Spanish", "English", "Translation"
                ],
                "skills_wanted": [
                    "Mandarin", "Chinese Culture", "Business Communication"
                ],
                "rating": 4.8,
                "availability": "Flexible",
                "experience_level": "expert",
                "total_reviews": 33,
                "is_online": True,
                "last_seen": (datetime.now() - timedelta(minutes=20)).isoformat(),
                "created_at": (datetime.now() - timedelta(days=200)).isoformat()
            },
            {
                "id": "user-10",
                "name": "Robert Taylor",
                "bio": "DevOps engineer and cloud architect. Specializing in scalable infrastructure solutions!",
                "avatar": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=100&h=100&fit=crop&crop=face",
                "location": {
                    "city": "Denver",
                    "country": "USA"
                },
                "skills_offered": [
                    "DevOps", "AWS", "Azure", "Terraform", "Python"
                ],
                "skills_wanted": [
                    "Machine Learning", "Security", "Compliance"
                ],
                "rating": 4.7,
                "availability": "Weekdays",
                "experience_level": "expert",
                "total_reviews": 38,
                "is_online": True,
                "last_seen": (datetime.now() - timedelta(minutes=5)).isoformat(),
                "created_at": (datetime.now() - timedelta(days=30)).isoformat()
            },
            {
                "id": "user-11",
                "name": "Anna Lee",
                "bio": "Product designer focused on user research and design systems. Learning React Native!",
                "avatar": "https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=100&h=100&fit=crop&crop=face",
                "location": {
                    "city": "Boston",
                    "country": "USA"
                },
                "skills_offered": [
                    "Product Design", "User Research", "Figma", "Prototyping"
                ],
                "skills_wanted": [
                    "React Native", "Mobile Development", "Data Analysis"
                ],
                "rating": 4.5,
                "availability": "Weekdays",
                "experience_level": "intermediate",
                "total_reviews": 21,
                "is_online": False,
                "last_seen": (datetime.now() - timedelta(hours=6)).isoformat(),
                "created_at": (datetime.now() - timedelta(days=45)).isoformat()
            },
            {
                "id": "user-12",
                "name": "Carlos Rodriguez",
                "bio": "Music producer and audio engineer. Teaching music production and sound design!",
                "avatar": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=100&h=100&fit=crop&crop=face",
                "location": {
                    "city": "Miami",
                    "country": "USA"
                },
                "skills_offered": [
                    "Music Production", "Audio Engineering", "Mixing", "Mastering"
                ],
                "skills_wanted": [
                    "Web Development", "Digital Marketing", "Business Development"
                ],
                "rating": 4.6,
                "availability": "Flexible",
                "experience_level": "advanced",
                "total_reviews": 17,
                "is_online": True,
                "last_seen": (datetime.now() - timedelta(minutes=12)).isoformat(),
                "created_at": (datetime.now() - timedelta(days=90)).isoformat()
            },
            {
                "id": "user-13",
                "name": "Nina Patel",
                "bio": "Data analyst and Python developer. Passionate about data visualization and automation!",
                "avatar": "https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=100&h=100&fit=crop&crop=face",
                "location": {
                    "city": "Atlanta",
                    "country": "USA"
                },
                "skills_offered": [
                    "Python", "Data Analysis", "SQL", "Tableau", "Power BI"
                ],
                "skills_wanted": [
                    "Machine Learning", "Cloud Computing", "Business Intelligence"
                ],
                "rating": 4.4,
                "availability": "Weekdays",
                "experience_level": "intermediate",
                "total_reviews": 25,
                "is_online": True,
                "last_seen": (datetime.now() - timedelta(minutes=8)).isoformat(),
                "created_at": (datetime.now() - timedelta(days=60)).isoformat()
            },
            {
                "id": "user-14",
                "name": "Tom Anderson",
                "bio": "Mobile app developer and UI/UX enthusiast. Creating beautiful and functional apps!",
                "avatar": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=100&h=100&fit=crop&crop=face",
                "location": {
                    "city": "Portland",
                    "country": "USA"
                },
                "skills_offered": [
                    "React Native", "Flutter", "Swift", "Kotlin", "UI Design"
                ],
                "skills_wanted": [
                    "Backend Development", "API Design", "Cloud Architecture"
                ],
                "rating": 4.7,
                "availability": "Flexible",
                "experience_level": "advanced",
                "total_reviews": 29,
                "is_online": False,
                "last_seen": (datetime.now() - timedelta(days=3)).isoformat(),
                "created_at": (datetime.now() - timedelta(days=150)).isoformat()
            },
            {
                "id": "user-15",
                "name": "Rachel Green",
                "bio": "Environmental scientist and sustainability advocate. Teaching climate science and data modeling!",
                "avatar": "https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=100&h=100&fit=crop&crop=face",
                "location": {
                    "city": "Vancouver",
                    "country": "Canada"
                },
                "skills_offered": [
                    "Environmental Science", "Data Science", "Climate Modeling", "Sustainability"
                ],
                "skills_wanted": [
                    "Policy Analysis", "Remote Sensing", "Geographic Information Systems"
                ],
                "rating": 4.9,
                "availability": "Flexible",
                "experience_level": "expert",
                "total_reviews": 35,
                "is_online": True,
                "last_seen": (datetime.now() - timedelta(minutes=25)).isoformat(),
                "created_at": (datetime.now() - timedelta(days=210)).isoformat()
            }
        ]
        
        # Clear existing users
        await ExploreUser.delete_all()
        
        # Insert new users
        users_to_insert = []
        for user_data in users_data:
            user = ExploreUser(**user_data)
            users_to_insert.append(user)
        
        # Bulk insert
        await ExploreUser.insert_many(users_to_insert)
        
        logger.info(f"Successfully seeded {len(users_to_insert)} users")
        return len(users_to_insert)
        
    except Exception as e:
        logger.error(f"Error seeding users: {str(e)}")
        raise Exception("Failed to seed users")

if __name__ == "__main__":
    asyncio.run(seed_users())
