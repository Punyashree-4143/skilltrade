from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional, Dict, Any
from app.models.swap_request import SwapRequest
import logging

from app.controllers.swap_controller import SwapController
from app.schemas.swap import (
    SwapRequestCreate, SwapRequestUpdate, SwapRequestResponse,
    SwapRequestWithUsers, SwapRequestList, SwapFilterQuery,
    SwapScheduleUpdate, SwapCompletion, SwapMessageAdd,
    SwapStatsResponse, SwapActivitySummary
)
from app.models.user import User
from app.middleware.auth_middleware import get_current_user
from app.utils.exceptions import SkillTradeException
from app.utils.logging import get_logger

logger = get_logger(__name__)

# Create router
router = APIRouter()


@router.post("/", response_model=SwapRequestWithUsers)
async def create_swap_request(
    swap_data: SwapRequestCreate,
    current_user: User = Depends(get_current_user)
) -> SwapRequestWithUsers:
    """
    Create a new swap request.
    
    - **receiver_id**: ID of user to send request to
    - **offered_skill**: Skill you're offering
    - **requested_skill**: Skill you want to learn
    - **message**: Request message (10-1000 characters)
    - **proposed_duration**: Proposed duration in minutes (15-480)
    
    Requires authentication token.
    """
    try:
        print("\n=== SWAP REQUEST START ===")
        print(f"Current user: {current_user.email}")
        print(f"Current user ID: {current_user.id}")
        print("=== SWAP DATA RECEIVED ===")
        print(f"Swap data: {swap_data.dict()}")
        print(f"Swap data type: {type(swap_data)}")
        print("=== INDIVIDUAL FIELDS ===")
        print(f"Receiver ID: {swap_data.receiver_id}")
        print(f"Offered Skill: {swap_data.offered_skill}")
        print(f"Requested Skill: {swap_data.requested_skill}")
        print(f"Message: {swap_data.message}")
        print(f"Duration: {swap_data.proposed_duration}")
        
        result = await SwapController.create_swap_request(swap_data, current_user)
        
        print("=== SWAP REQUEST SUCCESS ===")
        print(f"Created swap: {result}")
        print("=== SWAP REQUEST COMPLETED SUCCESSFULLY ===")
        
        return result
    except SkillTradeException as e:
        print(f"=== SWAP SKILL TRADE EXCEPTION ===")
        print(f"Error: {e.message}")
        print(f"Status code: {e.status_code}")
        raise HTTPException(
            status_code=e.status_code,
            detail=e.message
        )
    except Exception as e:
        print(f"=== SWAP GENERAL EXCEPTION ===")
        print(f"Error: {str(e)}")
        print(f"Error type: {type(e)}")
        import traceback
        traceback.print_exc()
        logger.error(f"Create swap request endpoint error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create swap request"
        )


@router.get("/", response_model=List[dict])
async def get_swap_requests(
    status: Optional[str] = Query(None, description="Filter by status"),
    type: str = Query("all", description="Filter by type (sent/received/all)"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    sort_by: str = Query("recent", description="Sort by field"),
    current_user: User = Depends(get_current_user)
) -> List[dict]:
    """
    Get swap requests with filters.
    
    - **status**: Filter by swap status
    - **type**: Filter by request type (sent/received/all)
    - **page**: Page number for pagination
    - **limit**: Items per page
    - **sort_by**: Sort method
    
    Requires authentication token.
    """
    try:
        filter_query = SwapFilterQuery(
            status=status,
            type=type,
            page=page,
            limit=limit,
            sort_by=sort_by
        )
        
        return await SwapController.get_swap_requests(
            current_user=current_user,
            request_type=filter_query.type
        )
    except SkillTradeException as e:
        raise HTTPException(
            status_code=e.status_code,
            detail=e.message
        )
    except Exception as e:
        logger.error(f"Get swap requests endpoint error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to get swap requests"
        )


@router.get("/{swap_id}", response_model=SwapRequestWithUsers)
async def get_swap_request(
    swap_id: str,
    current_user: User = Depends(get_current_user)
) -> SwapRequestWithUsers:
    """
    Get specific swap request by ID.
    
    - **swap_id**: Swap request ID
    
    Requires authentication token and participant access.
    """
    try:
        return await SwapController.get_swap_request(swap_id, current_user)
    except SkillTradeException as e:
        raise HTTPException(
            status_code=e.status_code,
            detail=e.message
        )
    except Exception as e:
        logger.error(f"Get swap request endpoint error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get swap request"
        )


@router.put("/{swap_id}", response_model=SwapRequestWithUsers)
async def update_swap_request(
    swap_id: str,
    update_data: SwapRequestUpdate,
    current_user: User = Depends(get_current_user)
) -> SwapRequestWithUsers:
    """
    Update swap request.
    
    - **status**: New status (pending/accepted/rejected/completed/cancelled)
    - **message**: Update message (optional)
    - **scheduled_date**: Scheduled date (optional)
    - **scheduled_time**: Scheduled time (optional)
    - **location_type**: Location type (online/in-person)
    - **meeting_details**: Meeting details (optional)
    - **completion_notes**: Completion notes (optional)
    
    Requires authentication token and participant access.
    """
    try:
        return await SwapController.update_swap_request(swap_id, update_data, current_user)
    except SkillTradeException as e:
        raise HTTPException(
            status_code=e.status_code,
            detail=e.message
        )
    except Exception as e:
        logger.error(f"Update swap request endpoint error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update swap request"
        )


@router.post("/{swap_id}/messages", response_model=SwapRequestWithUsers)
async def add_message_to_swap(
    swap_id: str,
    message_data: SwapMessageAdd,
    current_user: User = Depends(get_current_user)
) -> SwapRequestWithUsers:
    """
    Add message to swap request conversation.
    
    - **content**: Message content (1-1000 characters)
    
    Requires authentication token and participant access.
    """
    try:
        return await SwapController.add_message_to_swap(swap_id, message_data, current_user)
    except SkillTradeException as e:
        raise HTTPException(
            status_code=e.status_code,
            detail=e.message
        )
    except Exception as e:
        logger.error(f"Add message to swap endpoint error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to add message to swap"
        )


@router.put("/{swap_id}/messages/read")
async def mark_swap_messages_read(
    swap_id: str,
    current_user: User = Depends(get_current_user)
) -> Dict[str, str]:
    """
    Mark messages as read in swap request.
    
    Requires authentication token and participant access.
    """
    try:
        return await SwapController.mark_swap_messages_read(swap_id, current_user)
    except SkillTradeException as e:
        raise HTTPException(
            status_code=e.status_code,
            detail=e.message
        )
    except Exception as e:
        logger.error(f"Mark messages as read endpoint error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to mark messages as read"
        )


@router.get("/stats", response_model=SwapStatsResponse)
async def get_swap_stats(
    current_user: User = Depends(get_current_user)
) -> SwapStatsResponse:
    """
    Get swap statistics for current user.
    
    Returns:
    - Total requests
    - Completed swaps
    - Success rate
    - Other statistics
    
    Requires authentication token.
    """
    try:
        return await SwapController.get_swap_stats(current_user)
    except SkillTradeException as e:
        raise HTTPException(
            status_code=e.status_code,
            detail=e.message
        )
    except Exception as e:
        logger.error(f"Get swap stats endpoint error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get swap statistics"
        )


@router.get("/activity", response_model=SwapActivitySummary)
async def get_swap_activity(
    current_user: User = Depends(get_current_user)
) -> SwapActivitySummary:
    """
    Get swap activity summary.
    
    Returns:
    - Recent swaps
    - Pending requests
    - Upcoming swaps
    - Unread messages count
    
    Requires authentication token.
    """
    try:
        return await SwapController.get_swap_activity(current_user)
    except SkillTradeException as e:
        raise HTTPException(
            status_code=e.status_code,
            detail=e.message
        )
    except Exception as e:
        logger.error(f"Get swap activity endpoint error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get swap activity"
        )


@router.post("/{swap_id}/schedule")
async def schedule_swap(
    swap_id: str,
    schedule_data: SwapScheduleUpdate,
    current_user: User = Depends(get_current_user)
) -> SwapRequestWithUsers:
    """
    Schedule a swap request.
    
    - **scheduled_date**: Date for the swap
    - **scheduled_time**: Time for the swap
    - **location_type**: Location type (online/in-person)
    - **meeting_details**: Meeting details (optional)
    
    Requires authentication token and participant access.
    """
    try:
        update_data = SwapRequestUpdate(
            scheduled_date=schedule_data.scheduled_date,
            scheduled_time=schedule_data.scheduled_time,
            location_type=schedule_data.location_type,
            meeting_details=schedule_data.meeting_details
        )
        
        return await SwapController.update_swap_request(swap_id, update_data, current_user)
    except SkillTradeException as e:
        raise HTTPException(
            status_code=e.status_code,
            detail=e.message
        )
    except Exception as e:
        logger.error(f"Schedule swap endpoint error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to schedule swap"
        )


@router.post("/{swap_id}/complete")
async def complete_swap(
    swap_id: str,
    completion_data: SwapCompletion,
    current_user: User = Depends(get_current_user)
) -> SwapRequestWithUsers:
    """
    Mark swap request as completed.
    
    - **completion_notes**: Notes about the completion (optional)
    - **actual_duration**: Actual duration in minutes (optional)
    
    Requires authentication token and participant access.
    """
    try:
        update_data = SwapRequestUpdate(
            status="completed",
            completion_notes=completion_data.completion_notes
        )
        
        return await SwapController.update_swap_request(swap_id, update_data, current_user)
    except SkillTradeException as e:
        raise HTTPException(
            status_code=e.status_code,
            detail=e.message
        )
    except Exception as e:
        logger.error(f"Complete swap endpoint error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to complete swap"
        )


@router.post("/{swap_id}/accept")
async def accept_swap_request(
    swap_id: str,
    current_user: User = Depends(get_current_user)
) -> SwapRequestWithUsers:
    """
    Accept a swap request.
    
    Requires authentication token and receiver access.
    """
    try:
        update_data = SwapRequestUpdate(
            status="accepted",
            message="Swap request accepted"
        )
        
        return await SwapController.update_swap_request(swap_id, update_data, current_user)
    except SkillTradeException as e:
        raise HTTPException(
            status_code=e.status_code,
            detail=e.message
        )
    except Exception as e:
        logger.error(f"Accept swap request endpoint error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to accept swap request"
        )


@router.post("/{swap_id}/reject")
async def reject_swap_request(
    swap_id: str,
    current_user: User = Depends(get_current_user)
) -> SwapRequestWithUsers:
    """
    Reject a swap request.
    
    Requires authentication token and receiver access.
    """
    try:
        update_data = SwapRequestUpdate(
            status="rejected",
            message="Swap request rejected"
        )
        
        return await SwapController.update_swap_request(swap_id, update_data, current_user)
    except SkillTradeException as e:
        raise HTTPException(
            status_code=e.status_code,
            detail=e.message
        )
    except Exception as e:
        logger.error(f"Reject swap request endpoint error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to reject swap request"
        )


@router.post("/{swap_id}/cancel")
async def cancel_swap_request(
    swap_id: str,
    current_user: User = Depends(get_current_user)
) -> SwapRequestWithUsers:
    """
    Cancel a swap request.
    
    Requires authentication token and participant access.
    """
    try:
        update_data = SwapRequestUpdate(
            status="cancelled",
            message="Swap request cancelled"
        )
        
        return await SwapController.update_swap_request(swap_id, update_data, current_user)
    except SkillTradeException as e:
        raise HTTPException(
            status_code=e.status_code,
            detail=e.message
        )
    except Exception as e:
        logger.error(f"Cancel swap request endpoint error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to cancel swap request"
        )


@router.post("/{swap_id}/complete")
async def complete_swap_request(
    swap_id: str,
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Mark a swap request as completed.
    
    Requires authentication token and participant access.
    Only accepted swaps can be marked as completed.
    """
    try:
        from app.controllers.swap_completion_controller import SwapCompletionController
        return await SwapCompletionController.complete_swap_request(swap_id, current_user)
    except SkillTradeException as e:
        raise HTTPException(
            status_code=e.status_code,
            detail=e.message
        )
    except Exception as e:
        logger.error(f"Complete swap request endpoint error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to complete swap request"
        )


@router.get("/health")
async def swaps_health() -> Dict[str, str]:
    """
    Health check for swaps service.
    """
    return {
        "status": "healthy",
        "service": "swaps"
    }


@router.get("/test-auth")
async def test_auth(current_user: User = Depends(get_current_user)) -> Dict[str, Any]:
    """
    Test endpoint to verify authentication is working
    """
    try:
        print("=== TEST AUTH ENDPOINT ===")
        print(f"Current user: {current_user.email}")
        print(f"Current user ID: {current_user.id}")
        
        return {
            "status": "success",
            "user": {
                "id": str(current_user.id),
                "email": current_user.email,
                "name": current_user.name
            },
            "message": "Authentication is working correctly"
        }
    except Exception as e:
        print(f"=== TEST AUTH ERROR ===")
        print(f"Error: {str(e)}")
        return {
            "status": "error",
            "error": str(e),
            "message": "Authentication test failed"
        }
@router.delete("/delete-all")
async def delete_all_swaps():

    swaps = await SwapRequest.find_all().to_list()

    for swap in swaps:
        await swap.delete()

    return {
        "message": "All swaps deleted successfully"
    }