from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional, Dict, Any
import logging

from app.controllers.message_controller import MessageController
from app.schemas.message import (
    MessageCreate, MessageUpdate, MessageResponse, MessageWithUsers,
    ConversationResponse, MessageList, ConversationList, MessageFilterQuery,
    MessageStatsResponse, MessageSearch, MessageActivity
)
from app.models.user import User
from app.middleware.auth_middleware import get_current_user
from app.utils.exceptions import SkillTradeException
from app.utils.logging import get_logger

logger = get_logger(__name__)

# Create router
router = APIRouter()


@router.post("/", response_model=MessageWithUsers)
async def send_message(
    message_data: MessageCreate,
    current_user: User = Depends(get_current_user)
) -> MessageWithUsers:
    """
    Send a message to another user.
    
    - **receiver_id**: ID of user to send message to
    - **content**: Message content (1-1000 characters)
    - **message_type**: Message type (text/image/file)
    - **reply_to_id**: Reply to message ID (optional)
    
    Requires authentication token.
    """
    try:
        return await MessageController.send_message(message_data, current_user)
    except SkillTradeException as e:
        raise HTTPException(
            status_code=e.status_code,
            detail=e.message
        )
    except Exception as e:
        logger.error(f"Send message endpoint error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send message"
        )


@router.get("/conversations", response_model=ConversationList)
async def get_conversations(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=50, description="Items per page"),
    current_user: User = Depends(get_current_user)
) -> ConversationList:
    """
    Get all conversations for current user.
    
    - **page**: Page number for pagination
    - **limit**: Items per page
    
    Returns list of conversations with last message and unread count.
    
    Requires authentication token.
    """
    try:
        return await MessageController.get_conversations(page, limit, current_user)
    except SkillTradeException as e:
        raise HTTPException(
            status_code=e.status_code,
            detail=e.message
        )
    except Exception as e:
        logger.error(f"Get conversations endpoint error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get conversations"
        )


@router.get("/conversation/{user_id}", response_model=MessageList)
async def get_conversation(
    user_id: str,
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(50, ge=1, le=100, description="Items per page"),
    current_user: User = Depends(get_current_user)
) -> MessageList:
    """
    Get conversation with specific user.
    
    - **user_id**: ID of conversation partner
    - **page**: Page number for pagination
    - **limit**: Items per page
    
    Returns messages in chronological order with unread count.
    
    Requires authentication token.
    """
    try:
        return await MessageController.get_conversation(user_id, page, limit, current_user)
    except SkillTradeException as e:
        raise HTTPException(
            status_code=e.status_code,
            detail=e.message
        )
    except Exception as e:
        logger.error(f"Get conversation endpoint error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get conversation"
        )


@router.put("/{message_id}", response_model=MessageWithUsers)
async def update_message(
    message_id: str,
    update_data: MessageUpdate,
    current_user: User = Depends(get_current_user)
) -> MessageWithUsers:
    """
    Update message content.
    
    - **message_id**: ID of message to update
    - **content**: Updated message content (1-1000 characters)
    
    Messages can only be edited within 15 minutes of creation.
    
    Requires authentication token and sender access.
    """
    try:
        return await MessageController.update_message(message_id, update_data, current_user)
    except SkillTradeException as e:
        raise HTTPException(
            status_code=e.status_code,
            detail=e.message
        )
    except Exception as e:
        logger.error(f"Update message endpoint error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update message"
        )


@router.delete("/{message_id}")
async def delete_message(
    message_id: str,
    current_user: User = Depends(get_current_user)
) -> Dict[str, str]:
    """
    Soft delete a message.
    
    - **message_id**: ID of message to delete
    
    Message is marked as deleted but not removed from database.
    
    Requires authentication token and sender access.
    """
    try:
        return await MessageController.delete_message(message_id, current_user)
    except SkillTradeException as e:
        raise HTTPException(
            status_code=e.status_code,
            detail=e.message
        )
    except Exception as e:
        logger.error(f"Delete message endpoint error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete message"
        )


@router.put("/{message_id}/read")
async def mark_message_as_read(
    message_id: str,
    current_user: User = Depends(get_current_user)
) -> Dict[str, str]:
    """
    Mark message as read.
    
    - **message_id**: ID of message to mark as read
    
    Requires authentication token and receiver access.
    """
    try:
        return await MessageController.mark_message_as_read(message_id, current_user)
    except SkillTradeException as e:
        raise HTTPException(
            status_code=e.status_code,
            detail=e.message
        )
    except Exception as e:
        logger.error(f"Mark message as read endpoint error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to mark message as read"
        )


@router.put("/conversation/{user_id}/read")
async def mark_conversation_as_read(
    user_id: str,
    current_user: User = Depends(get_current_user)
) -> Dict[str, str]:
    """
    Mark all messages in conversation as read.
    
    - **user_id**: ID of conversation partner
    
    Requires authentication token.
    """
    try:
        return await MessageController.mark_conversation_as_read(user_id, current_user)
    except SkillTradeException as e:
        raise HTTPException(
            status_code=e.status_code,
            detail=e.message
        )
    except Exception as e:
        logger.error(f"Mark conversation as read endpoint error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to mark conversation as read"
        )


@router.post("/search", response_model=MessageList)
async def search_messages(
    search_data: MessageSearch,
    current_user: User = Depends(get_current_user)
) -> MessageList:
    """
    Search messages.
    
    - **query**: Search query string (1-100 characters)
    - **user_id**: Filter by specific user ID (optional)
    - **message_type**: Filter by message type (optional)
    - **date_from**: Search from date (optional)
    - **date_to**: Search to date (optional)
    - **page**: Page number for pagination
    - **limit**: Items per page
    
    Requires authentication token.
    """
    try:
        return await MessageController.search_messages(search_data, current_user)
    except SkillTradeException as e:
        raise HTTPException(
            status_code=e.status_code,
            detail=e.message
        )
    except Exception as e:
        logger.error(f"Search messages endpoint error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to search messages"
        )


@router.get("/stats", response_model=MessageStatsResponse)
async def get_message_stats(
    current_user: User = Depends(get_current_user)
) -> MessageStatsResponse:
    """
    Get message statistics for current user.
    
    Returns:
    - Total messages sent/received
    - Total conversations
    - Unread messages count
    - Messages sent today/this week
    
    Requires authentication token.
    """
    try:
        return await MessageController.get_message_stats(current_user)
    except SkillTradeException as e:
        raise HTTPException(
            status_code=e.status_code,
            detail=e.message
        )
    except Exception as e:
        logger.error(f"Get message stats endpoint error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get message statistics"
        )


@router.get("/activity", response_model=MessageActivity)
async def get_message_activity(
    current_user: User = Depends(get_current_user)
) -> MessageActivity:
    """
    Get message activity summary.
    
    Returns:
    - Recent messages
    - Active conversations
    - Unread messages count
    - Currently typing users
    
    Requires authentication token.
    """
    try:
        return await MessageController.get_message_activity(current_user)
    except SkillTradeException as e:
        raise HTTPException(
            status_code=e.status_code,
            detail=e.message
        )
    except Exception as e:
        logger.error(f"Get message activity endpoint error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get message activity"
        )


@router.get("/unread/count")
async def get_unread_count(
    current_user: User = Depends(get_current_user)
) -> Dict[str, int]:
    """
    Get total unread messages count.
    
    Requires authentication token.
    """
    try:
        from app.models.message import Message
        
        unread_count = await Message.count_documents({
            "receiver": current_user.id,
            "read": False
        })
        
        return {"unread_count": unread_count}
        
    except Exception as e:
        logger.error(f"Get unread count endpoint error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get unread count"
        )


@router.get("/health")
async def messages_health() -> Dict[str, str]:
    """
    Health check for messages service.
    """
    return {
        "status": "healthy",
        "service": "messages"
    }
