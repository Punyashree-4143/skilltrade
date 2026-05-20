from fastapi import (
    APIRouter,
    HTTPException,
    Depends,
)

from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import logging
import traceback

from app.models.user import User
from app.middleware.auth_middleware import (
    get_current_user,
)

router = APIRouter()
logger = logging.getLogger(__name__)

print("=== USERS ROUTE MODULE LOADED ===")


# PROFILE UPDATE SCHEMA
class ProfileUpdateRequest(BaseModel):

    name: Optional[str] = None

    bio: Optional[str] = None

    avatar: Optional[str] = None

    skills_offered: Optional[List[str]] = None

    skills_wanted: Optional[List[str]] = None

    location: Optional[dict] = None

    availability: Optional[str] = None

    experience_level: Optional[str] = None


# PUBLIC EXPLORE ROUTE
@router.get("/")
async def get_users():

    """
    Public Explore endpoint
    """

    try:

        print("\n========== GET USERS ==========")

        # FETCH ALL USERS
        users = await User.find().to_list()

        print(f"Users found: {len(users)}")

        for user in users:
            print(user.email)

        print("===========================")

        return [
            user.to_dict_safe()
            for user in users
        ]

    except Exception as e:

        print("\n========== GET USERS ERROR ==========")
        print(f"Error: {str(e)}")
        traceback.print_exc()
        print("=====================================\n")

        logger.error(
            f"Error fetching users: {str(e)}"
        )

        return []


# DEBUG ROUTE
@router.get("/debug/all-users")
async def debug_all_users():

    """
    Debug route to inspect MongoDB users
    """

    try:

        users = await User.find().to_list()

        print("\n========== DEBUG USERS ==========")

        for user in users:
            print(user)

        print("=================================\n")

        return [
            user.to_dict_safe()
            for user in users
        ]

    except Exception as e:

        print("\n========== DEBUG ERROR ==========")
        print(f"Error: {str(e)}")
        traceback.print_exc()
        print("=================================\n")

        raise HTTPException(
            status_code=500,
            detail=str(e),
        )


# UPDATE PROFILE
@router.put("/profile")
async def update_profile(
    profile_data: ProfileUpdateRequest,
    current_user: User = Depends(
        get_current_user
    )
):

    """
    Update logged-in user profile
    """

    try:

        print(
            "\n========== PROFILE UPDATE =========="
        )

        print(f"User: {current_user.email}")

        update_data = profile_data.dict(
            exclude_unset=True
        )

        print(f"Update Data: {update_data}")

        # UPDATE FIELDS
        for field, value in update_data.items():

            setattr(
                current_user,
                field,
                value,
            )

        # MARK PROFILE COMPLETE
        current_user.profile_completed = True

        current_user.updated_at = (
            datetime.utcnow()
        )

        # SAVE USER
        await current_user.save()

        print(
            f"Profile updated successfully "
            f"for {current_user.email}"
        )

        print("===================================\n")

        return current_user.to_dict_safe()

    except Exception as e:

        print(
            "\n========== PROFILE UPDATE ERROR =========="
        )

        print(f"Error: {str(e)}")

        traceback.print_exc()

        print(
            "==========================================\n"
        )

        logger.error(
            f"Error updating profile: {str(e)}"
        )

        raise HTTPException(
            status_code=500,
            detail=str(e),
        )


# CLEANUP ROUTE
@router.get("/debug/cleanup-users")
async def cleanup_users():
    """
    Clean up invalid users without password_hash
    """
    try:
        from app.database.mongodb import get_database
        
        db = get_database()
        
        result = await db["users"].delete_many({
            "password_hash": {
                "$exists": False
            }
        })
        
        print(f"========== CLEANUP COMPLETE ==========")
        print(f"Deleted {result.deleted_count} invalid users")
        print("====================================")
        
        return {
            "deleted_users": result.deleted_count,
            "message": f"Cleaned up {result.deleted_count} invalid users"
        }
        
    except Exception as e:
        print(f"========== CLEANUP ERROR ==========")
        print(f"Error: {str(e)}")
        print("=================================")
        
        raise HTTPException(
            status_code=500,
            detail=f"Cleanup failed: {str(e)}"
        )