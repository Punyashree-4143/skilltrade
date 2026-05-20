"""
Dashboard Routes for SkillTrade
Provides dashboard statistics and analytics endpoints
"""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from typing import List, Dict, Any
import logging

from app.controllers.dashboard_controller import DashboardController
from app.models.user import User
from app.middleware.auth_middleware import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/stats")
async def get_dashboard_stats(
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get dashboard statistics for authenticated user.
    
    Returns comprehensive statistics including:
    - Total swaps
    - Pending swaps
    - Accepted swaps
    - Completed swaps
    - Cancelled swaps
    - Unread messages
    - Profile views
    - Success rate
    
    Requires authentication token.
    """
    try:
        stats = await DashboardController.get_user_dashboard_stats(current_user)
        return jsonable_encoder(stats)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Dashboard stats endpoint error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to get dashboard statistics"
        )


@router.get("/activities")
async def get_dashboard_activities(
    limit: int = 10,
    current_user: User = Depends(get_current_user)
) -> List[Dict[str, Any]]:
    """
    Get recent activities for authenticated user.
    
    Returns latest swap activities including:
    - swap requests sent/received
    - acceptances
    - completions
    - cancellations
    
    Requires authentication token.
    """
    try:
        from app.controllers.dashboard_activities_controller import DashboardActivitiesController
        return await DashboardActivitiesController.get_user_activities(current_user, limit)
    except HTTPException:
        raise
    except Exception as e:
        print(f"Dashboard activities endpoint error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to get dashboard activities"
        )


@router.get("/top-matches")
async def get_top_matches(
    limit: int = 5,
    current_user: User = Depends(get_current_user)
) -> List[Dict[str, Any]]:
    """
    Get top skill matches for authenticated user.
    
    Returns users with compatible skills:
    - Skill matching algorithm
    - Match scores
    - Previous swap history
    - User ratings
    
    Requires authentication token.
    """
    try:
        from app.controllers.dashboard_matches_controller import DashboardMatchesController
        return await DashboardMatchesController.get_top_matches(current_user, limit)
    except HTTPException:
        raise
    except Exception as e:
        print(f"Dashboard matches endpoint error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to get dashboard matches"
        )


@router.get("/health")
async def dashboard_health():
    """Health check for dashboard service"""
    return {
        "status": "healthy",
        "service": "dashboard",
        "timestamp": "2024-05-12T00:00:00Z"
    }
