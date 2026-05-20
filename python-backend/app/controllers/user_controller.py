from typing import List, Optional, Dict, Any
from app.models.user import User
from app.database import get_database
import logging
from datetime import datetime
from beanie import PydanticObjectId

logger = logging.getLogger(__name__)


class UserController:
    """Controller for user operations"""

    @staticmethod
    async def get_all_users(
        limit: int = 50,
        offset: int = 0,
        search: Optional[str] = None,
        skill: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get all users - simplified for debugging
        """

        try:
            # Fetch ALL users without any filters
            users = await User.find().to_list()

            print("========== RAW USERS ==========")
            for user in users:
                print(
                    user.email,
                    user.profile_completed
                )
            print("================================")

            print(f"Total users found: {len(users)}")

            # SAFE SERIALIZATION
            return [
                user.to_dict_safe()
                for user in users
            ]

        except Exception as e:
            logger.error(
                f"Error fetching users: {str(e)}"
            )

            raise Exception("Failed to fetch users")

    @staticmethod
    async def get_user_by_id(
        user_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get a specific user by ID
        """

        try:
            print(f"Fetching user: {user_id}")

            user = await User.get(
                PydanticObjectId(user_id)
            )

            if not user:
                return None

            return user.to_dict_safe()

        except Exception as e:
            logger.error(
                f"Error fetching user {user_id}: {str(e)}"
            )

            raise Exception("Failed to fetch user")

    @staticmethod
    async def get_similar_users(
        user_id: str,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Get users similar to a specific user based on skills
        """

        try:
            target_user = await User.get(
                PydanticObjectId(user_id)
            )

            if not target_user:
                return []

            target_skills = (
                target_user.skills_offered +
                target_user.skills_wanted
            )

            similar_users = await User.find({
                "_id": {
                    "$ne": target_user.id
                },
                "$or": [
                    {
                        "skills_offered": {
                            "$in": target_skills
                        }
                    },
                    {
                        "skills_wanted": {
                            "$in": target_skills
                        }
                    }
                ]
            }).limit(limit).to_list()

            return [
                user.to_dict_safe()
                for user in similar_users
            ]

        except Exception as e:
            logger.error(
                f"Error finding similar users for {user_id}: {str(e)}"
            )

            raise Exception(
                "Failed to find similar users"
            )

    @staticmethod
    async def get_all_skills() -> List[str]:
        """
        Get all unique skills from all users
        """

        try:
            db = get_database()

            pipeline = [
                {
                    "$project": {
                        "skills_offered": 1,
                        "skills_wanted": 1
                    }
                },
                {
                    "$project": {
                        "all_skills": {
                            "$setUnion": [
                                "$skills_offered",
                                "$skills_wanted"
                            ]
                        }
                    }
                },
                {
                    "$unwind": "$all_skills"
                },
                {
                    "$group": {
                        "_id": "$all_skills",
                        "count": {
                            "$sum": 1
                        }
                    }
                },
                {
                    "$sort": {
                        "count": -1
                    }
                },
                {
                    "$limit": 50
                }
            ]

            result = await db["users"].aggregate(
                pipeline
            ).to_list(length=50)

            skills = [
                item["_id"]
                for item in result
            ]

            return skills

        except Exception as e:
            logger.error(
                f"Error fetching skills: {str(e)}"
            )

            raise Exception("Failed to fetch skills")

    @staticmethod
    async def get_users_stats() -> Dict[str, Any]:
        """
        Get statistics about users
        """

        try:
            db = get_database()

            total_users = await User.count()

            online_users = await User.find({
                "is_online": True
            }).count()

            top_offered = await db["users"].aggregate([
                {
                    "$unwind": "$skills_offered"
                },
                {
                    "$group": {
                        "_id": "$skills_offered",
                        "count": {
                            "$sum": 1
                        }
                    }
                },
                {
                    "$sort": {
                        "count": -1
                    }
                },
                {
                    "$limit": 10
                }
            ]).to_list(length=10)

            top_wanted = await db["users"].aggregate([
                {
                    "$unwind": "$skills_wanted"
                },
                {
                    "$group": {
                        "_id": "$skills_wanted",
                        "count": {
                            "$sum": 1
                        }
                    }
                },
                {
                    "$sort": {
                        "count": -1
                    }
                },
                {
                    "$limit": 10
                }
            ]).to_list(length=10)

            return {
                "total_users": total_users,
                "online_users": online_users,
                "top_offered_skills": [
                    {
                        "skill": item["_id"],
                        "count": item["count"]
                    }
                    for item in top_offered
                ],
                "top_wanted_skills": [
                    {
                        "skill": item["_id"],
                        "count": item["count"]
                    }
                    for item in top_wanted
                ]
            }

        except Exception as e:
            logger.error(
                f"Error fetching user stats: {str(e)}"
            )

            raise Exception(
                "Failed to fetch user statistics"
            )