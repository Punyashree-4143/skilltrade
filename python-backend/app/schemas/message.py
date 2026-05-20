from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from enum import Enum


class MessageType(str, Enum):
    TEXT = "text"
    IMAGE = "image"
    FILE = "file"


class MessageCreate(BaseModel):
    """Schema for creating a message"""
    receiver_id: str = Field(..., description="Receiver user ID")
    content: str = Field(..., min_length=1, max_length=1000, description="Message content")
    message_type: MessageType = Field(default=MessageType.TEXT, description="Message type")
    reply_to_id: Optional[str] = Field(None, description="Reply to message ID")
    
    @validator('content')
    def validate_content(cls, v):
        if not v.strip():
            raise ValueError('Message content cannot be empty')
        return v.strip()


class MessageUpdate(BaseModel):
    """Schema for updating a message"""
    content: str = Field(..., min_length=1, max_length=1000, description="Updated message content")
    
    @validator('content')
    def validate_content(cls, v):
        if not v.strip():
            raise ValueError('Message content cannot be empty')
        return v.strip()


class MessageResponse(BaseModel):
    """Schema for message response"""
    id: str = Field(..., description="Message ID")
    sender_id: str = Field(..., description="Sender user ID")
    receiver_id: str = Field(..., description="Receiver user ID")
    content: str = Field(..., description="Message content")
    message_type: MessageType = Field(..., description="Message type")
    file_url: Optional[str] = Field(None, description="File URL")
    file_name: Optional[str] = Field(None, description="File name")
    read: bool = Field(default=False, description="Read status")
    read_at: Optional[datetime] = Field(None, description="Read timestamp")
    edited: bool = Field(default=False, description="Edited status")
    edited_at: Optional[datetime] = Field(None, description="Edit timestamp")
    deleted: bool = Field(default=False, description="Deleted status")
    deleted_at: Optional[datetime] = Field(None, description="Delete timestamp")
    reply_to_id: Optional[str] = Field(None, description="Reply to message ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    
    class Config:
        from_attributes = True


class MessageWithUsers(MessageResponse):
    """Schema for message with user details"""
    sender: dict = Field(..., description="Sender user details")
    receiver: dict = Field(..., description="Receiver user details")
    reply_to: Optional["MessageWithUsers"] = Field(None, description="Replied message")
    
    class Config:
        from_attributes = True


class MessageReactionCreate(BaseModel):
    """Schema for creating message reaction"""
    emoji: str = Field(..., min_length=1, max_length=10, description="Reaction emoji")


class MessageReactionResponse(BaseModel):
    """Schema for message reaction response"""
    id: str = Field(..., description="Reaction ID")
    user_id: str = Field(..., description="User ID")
    emoji: str = Field(..., description="Reaction emoji")
    created_at: datetime = Field(..., description="Creation timestamp")
    
    class Config:
        from_attributes = True


class ConversationResponse(BaseModel):
    """Schema for conversation response"""
    user_id: str = Field(..., description="Other user ID")
    user: dict = Field(..., description="Other user details")
    last_message: MessageWithUsers = Field(..., description="Last message")
    unread_count: int = Field(default=0, description="Unread messages count")
    total_messages: int = Field(default=0, description="Total messages count")
    created_at: datetime = Field(..., description="Conversation start time")
    updated_at: datetime = Field(..., description="Last activity time")
    
    class Config:
        from_attributes = True


class MessageList(BaseModel):
    """Schema for message list response"""
    messages: List[MessageWithUsers] = Field(..., description="List of messages")
    pagination: dict = Field(..., description="Pagination information")
    unread_count: int = Field(default=0, description="Unread messages count")
    other_user: dict = Field(..., description="Other user details")


class ConversationList(BaseModel):
    """Schema for conversation list response"""
    conversations: List[ConversationResponse] = Field(..., description="List of conversations")
    pagination: dict = Field(..., description="Pagination information")
    total_unread: int = Field(default=0, description="Total unread messages")


class MessageFilterQuery(BaseModel):
    """Schema for message filtering"""
    page: int = Field(default=1, ge=1, description="Page number")
    limit: int = Field(default=50, ge=1, le=100, description="Items per page")
    message_type: Optional[MessageType] = Field(None, description="Filter by message type")
    read_status: Optional[bool] = Field(None, description="Filter by read status")


class MessageStatsResponse(BaseModel):
    """Schema for message statistics response"""
    total_messages: int = Field(default=0, description="Total messages sent")
    total_conversations: int = Field(default=0, description="Total conversations")
    unread_messages: int = Field(default=0, description="Unread messages")
    messages_today: int = Field(default=0, description="Messages sent today")
    messages_this_week: int = Field(default=0, description="Messages sent this week")
    average_response_time: Optional[float] = Field(None, description="Average response time in minutes")
    most_active_conversation: Optional[str] = Field(None, description="Most active conversation user ID")


class TypingIndicator(BaseModel):
    """Schema for typing indicator"""
    user_id: str = Field(..., description="User ID")
    conversation_id: str = Field(..., description="Conversation ID")
    is_typing: bool = Field(..., description="Typing status")
    timestamp: datetime = Field(..., description="Typing timestamp")


class OnlineStatus(BaseModel):
    """Schema for online status"""
    user_id: str = Field(..., description="User ID")
    is_online: bool = Field(..., description="Online status")
    last_seen: datetime = Field(..., description="Last seen timestamp")


class MessageSearch(BaseModel):
    """Schema for message search"""
    query: str = Field(..., min_length=1, max_length=100, description="Search query")
    user_id: Optional[str] = Field(None, description="Filter by user ID")
    message_type: Optional[MessageType] = Field(None, description="Filter by message type")
    date_from: Optional[datetime] = Field(None, description="Search from date")
    date_to: Optional[datetime] = Field(None, description="Search to date")
    page: int = Field(default=1, ge=1, description="Page number")
    limit: int = Field(default=20, ge=1, le=100, description="Items per page")


class MessageActivity(BaseModel):
    """Schema for message activity"""
    recent_messages: List[MessageWithUsers] = Field(default=[], description="Recent messages")
    active_conversations: List[ConversationResponse] = Field(default=[], description="Active conversations")
    unread_count: int = Field(default=0, description="Total unread count")
    typing_users: List[str] = Field(default=[], description="Currently typing users")


# Forward references for circular imports
MessageWithUsers.update_forward_refs()
