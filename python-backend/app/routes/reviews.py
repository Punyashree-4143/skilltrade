from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional, Dict, Any
import logging

from app.controllers.review_controller import ReviewController
from app.schemas.review import (
    ReviewCreate, ReviewUpdate, ReviewResponse, ReviewWithUsers,
    ReviewList, ReviewFilterQuery, ReviewStats, ReviewReport,
    ReviewResponseCreate, UserReviewSummary, ReviewActivity
)
from app.models.user import User
from app.middleware.auth_middleware import get_current_user
from app.utils.exceptions import SkillTradeException
from app.utils.logging import get_logger

logger = get_logger(__name__)

# Create router
router = APIRouter()


@router.post("/", response_model=ReviewWithUsers)
async def create_review(
    review_data: ReviewCreate,
    current_user: User = Depends(get_current_user)
) -> ReviewWithUsers:
    """
    Create a new review for a completed swap.
    
    - **reviewee_id**: ID of user being reviewed
    - **swap_request_id**: ID of completed swap request
    - **rating**: Overall rating (1-5)
    - **comment**: Review comment (10-500 characters)
    - **skills**: Skill-specific ratings (optional)
    - **would_swap_again**: Would swap again with this user
    - **helpfulness**: Helpfulness rating (1-5, optional)
    - **communication**: Communication rating (1-5, optional)
    - **punctuality**: Punctuality rating (1-5, optional)
    
    Requires authentication token and completed swap participation.
    """
    try:
        return await ReviewController.create_review(review_data, current_user)
    except SkillTradeException as e:
        raise HTTPException(
            status_code=e.status_code,
            detail=e.message
        )
    except Exception as e:
        logger.error(f"Create review endpoint error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create review"
        )


@router.get("/", response_model=ReviewList)
async def get_reviews(
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    rating: Optional[int] = Query(None, ge=1, le=5, description="Filter by rating"),
    would_swap_again: Optional[bool] = Query(None, description="Filter by would swap again"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    sort_by: str = Query("recent", description="Sort by field"),
    current_user: User = Depends(get_current_user)
) -> ReviewList:
    """
    Get reviews with filters.
    
    - **user_id**: Filter by specific user ID
    - **rating**: Filter by rating (1-5)
    - **would_swap_again**: Filter by would swap again preference
    - **page**: Page number for pagination
    - **limit**: Items per page
    - **sort_by**: Sort method (recent/rating_high/rating_low/helpful)
    
    Public reviews are shown by default. User sees all their own reviews.
    
    Requires authentication token.
    """
    try:
        filter_query = ReviewFilterQuery(
            user_id=user_id,
            rating=rating,
            would_swap_again=would_swap_again,
            page=page,
            limit=limit,
            sort_by=sort_by
        )
        
        return await ReviewController.get_reviews(filter_query, current_user)
    except SkillTradeException as e:
        raise HTTPException(
            status_code=e.status_code,
            detail=e.message
        )
    except Exception as e:
        logger.error(f"Get reviews endpoint error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get reviews"
        )


@router.get("/{review_id}", response_model=ReviewWithUsers)
async def get_review(
    review_id: str,
    current_user: User = Depends(get_current_user)
) -> ReviewWithUsers:
    """
    Get specific review by ID.
    
    - **review_id**: Review ID to fetch
    
    Public reviews are accessible to all. Private reviews only to participants.
    
    Requires authentication token.
    """
    try:
        return await ReviewController.get_review(review_id, current_user)
    except SkillTradeException as e:
        raise HTTPException(
            status_code=e.status_code,
            detail=e.message
        )
    except Exception as e:
        logger.error(f"Get review endpoint error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get review"
        )


@router.put("/{review_id}", response_model=ReviewWithUsers)
async def update_review(
    review_id: str,
    update_data: ReviewUpdate,
    current_user: User = Depends(get_current_user)
) -> ReviewWithUsers:
    """
    Update a review.
    
    - **review_id**: ID of review to update
    - **comment**: Updated review comment (optional)
    - **is_public**: Public visibility setting (optional)
    
    Reviews can only be edited within 7 days of creation by the reviewer.
    
    Requires authentication token and reviewer access.
    """
    try:
        return await ReviewController.update_review(review_id, update_data, current_user)
    except SkillTradeException as e:
        raise HTTPException(
            status_code=e.status_code,
            detail=e.message
        )
    except Exception as e:
        logger.error(f"Update review endpoint error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update review"
        )


@router.delete("/{review_id}")
async def delete_review(
    review_id: str,
    current_user: User = Depends(get_current_user)
) -> Dict[str, str]:
    """
    Delete a review.
    
    - **review_id**: ID of review to delete
    
    Only the reviewer can delete their own reviews.
    
    Requires authentication token and reviewer access.
    """
    try:
        return await ReviewController.delete_review(review_id, current_user)
    except SkillTradeException as e:
        raise HTTPException(
            status_code=e.status_code,
            detail=e.message
        )
    except Exception as e:
        logger.error(f"Delete review endpoint error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete review"
        )


@router.post("/{review_id}/respond", response_model=ReviewWithUsers)
async def respond_to_review(
    review_id: str,
    response_data: ReviewResponseCreate,
    current_user: User = Depends(get_current_user)
) -> ReviewWithUsers:
    """
    Respond to a review.
    
    - **review_id**: ID of review to respond to
    - **content**: Response content (10-500 characters)
    
    Only the reviewee can respond to reviews about them.
    Each review can only have one response.
    
    Requires authentication token and reviewee access.
    """
    try:
        return await ReviewController.respond_to_review(review_id, response_data, current_user)
    except SkillTradeException as e:
        raise HTTPException(
            status_code=e.status_code,
            detail=e.message
        )
    except Exception as e:
        logger.error(f"Respond to review endpoint error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to respond to review"
        )


@router.post("/{review_id}/report")
async def report_review(
    review_id: str,
    report_data: ReviewReport,
    current_user: User = Depends(get_current_user)
) -> Dict[str, str]:
    """
    Report a review for violation of terms.
    
    - **review_id**: ID of review to report
    - **reason**: Report reason (10-500 characters)
    
    Any user can report reviews. Reports will be reviewed by moderators.
    
    Requires authentication token.
    """
    try:
        return await ReviewController.report_review(review_id, report_data, current_user)
    except SkillTradeException as e:
        raise HTTPException(
            status_code=e.status_code,
            detail=e.message
        )
    except Exception as e:
        logger.error(f"Report review endpoint error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to report review"
        )


@router.get("/user/{user_id}/summary", response_model=UserReviewSummary)
async def get_user_review_summary(
    user_id: str,
    current_user: User = Depends(get_current_user)
) -> UserReviewSummary:
    """
    Get review summary for a specific user.
    
    - **user_id**: ID of user to get summary for
    
    Returns:
    - Total reviews and average rating
    - Recent reviews
    - Rating distribution
    - Skill-specific ratings
    - Would swap again rate
    
    Public reviews are shown to others. User sees all their own reviews.
    
    Requires authentication token.
    """
    try:
        return await ReviewController.get_user_review_summary(user_id, current_user)
    except SkillTradeException as e:
        raise HTTPException(
            status_code=e.status_code,
            detail=e.message
        )
    except Exception as e:
        logger.error(f"Get user review summary endpoint error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get user review summary"
        )


@router.get("/activity", response_model=ReviewActivity)
async def get_review_activity(
    current_user: User = Depends(get_current_user)
) -> ReviewActivity:
    """
    Get review activity for current user.
    
    Returns:
    - Number of reviews to write (completed swaps without reviews)
    - Recent reviews given
    - Recent reviews received
    - Review notifications count
    
    Requires authentication token.
    """
    try:
        return await ReviewController.get_review_activity(current_user)
    except SkillTradeException as e:
        raise HTTPException(
            status_code=e.status_code,
            detail=e.message
        )
    except Exception as e:
        logger.error(f"Get review activity endpoint error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get review activity"
    )


@router.get("/stats")
async def get_review_stats(
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    current_user: User = Depends(get_current_user)
) -> ReviewStats:
    """
    Get review statistics.
    
    - **user_id**: Filter by specific user ID (optional)
    
    Returns comprehensive review statistics including:
    - Total reviews and average rating
    - Rating distribution
    - Would swap again statistics
    
    Requires authentication token.
    """
    try:
        filter_query = ReviewFilterQuery(user_id=user_id)
        result = await ReviewController.get_reviews(filter_query, current_user)
        
        return ReviewStats(**result.stats)
        
    except SkillTradeException as e:
        raise HTTPException(
            status_code=e.status_code,
            detail=e.message
        )
    except Exception as e:
        logger.error(f"Get review stats endpoint error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get review statistics"
    )


@router.get("/health")
async def reviews_health() -> Dict[str, str]:
    """
    Health check for reviews service.
    """
    return {
        "status": "healthy",
        "service": "reviews"
    }
