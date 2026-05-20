from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from enum import Enum

from app.schemas.user import SkillCategory


class SwapStatus(str, Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class LocationType(str, Enum):
    ONLINE = "online"
    IN_PERSON = "in_person"


class SkillDetailCreate(BaseModel):
    """Schema for creating skill details"""
    skill: str = Field(..., min_length=2, max_length=50, description="Skill name")
    category: SkillCategory = Field(..., description="Skill category")
    description: Optional[str] = Field(None, max_length=200, description="Skill description")
    
    @validator('skill')
    def validate_skill_name(cls, v):
        if not v.strip():
            raise ValueError('Skill name cannot be empty')
        return v.strip().lower()


class SkillDetailResponse(BaseModel):
    """Schema for skill detail response"""
    skill: str = Field(..., description="Skill name")
    category: SkillCategory = Field(..., description="Skill category")
    description: Optional[str] = Field(None, description="Skill description")
    
    class Config:
        from_attributes = True


class SwapMessageCreate(BaseModel):
    """Schema for creating swap message"""
    content: str = Field(..., min_length=1, max_length=1000, description="Message content")
    
    @validator('content')
    def validate_content(cls, v):
        if not v.strip():
            raise ValueError('Message content cannot be empty')
        return v.strip()


class SwapMessageResponse(BaseModel):
    """Schema for swap message response"""
    id: str = Field(..., description="Message ID")
    sender_id: str = Field(..., description="Sender ID")
    content: str = Field(..., description="Message content")
    timestamp: datetime = Field(..., description="Message timestamp")
    read: bool = Field(default=False, description="Read status")
    
    class Config:
        from_attributes = True


class SwapRequestCreate(BaseModel):
    """Schema for creating a swap request"""
    receiver_id: str = Field(..., description="Receiver user ID")
    offered_skill: SkillDetailCreate = Field(..., description="Skill being offered")
    requested_skill: SkillDetailCreate = Field(..., description="Skill being requested")
    message: str = Field(..., min_length=10, max_length=1000, description="Request message")
    proposed_duration: int = Field(..., ge=15, le=480, description="Proposed duration in minutes")
    
    @validator('message')
    def validate_message(cls, v):
        if not v.strip():
            raise ValueError('Message cannot be empty')
        return v.strip()


class SwapRequestUpdate(BaseModel):
    """Schema for updating a swap request"""
    status: Optional[SwapStatus] = Field(None, description="New status")
    message: Optional[str] = Field(None, min_length=1, max_length=1000, description="Update message")
    scheduled_date: Optional[datetime] = Field(None, description="Scheduled date")
    scheduled_time: Optional[str] = Field(None, description="Scheduled time")
    location_type: Optional[LocationType] = Field(None, description="Location type")
    meeting_details: Optional[str] = Field(None, max_length=500, description="Meeting details")
    completion_notes: Optional[str] = Field(None, max_length=1000, description="Completion notes")
    
    @validator('message')
    def validate_message(cls, v):
        if v is not None and not v.strip():
            raise ValueError('Message cannot be empty')
        return v.strip() if v else v


class SwapRequestResponse(BaseModel):
    """Schema for swap request response"""
    id: str = Field(..., description="Swap request ID")
    sender_id: str = Field(..., description="Sender user ID")
    receiver_id: str = Field(..., description="Receiver user ID")
    offered_skill: SkillDetailResponse = Field(..., description="Skill being offered")
    requested_skill: SkillDetailResponse = Field(..., description="Skill being requested")
    message: str = Field(..., description="Request message")
    proposed_duration: int = Field(..., description="Proposed duration in minutes")
    status: SwapStatus = Field(..., description="Current status")
    scheduled_date: Optional[datetime] = Field(None, description="Scheduled date")
    scheduled_time: Optional[str] = Field(None, description="Scheduled time")
    location_type: LocationType = Field(default=LocationType.ONLINE, description="Location type")
    meeting_details: Optional[str] = Field(None, description="Meeting details")
    completion_notes: Optional[str] = Field(None, description="Completion notes")
    match_score: Optional[float] = Field(None, description="Match compatibility score")
    messages: List[SwapMessageResponse] = Field(default=[], description="Swap messages")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    
    class Config:
        from_attributes = True


class SwapRequestWithUsers(SwapRequestResponse):
    """Schema for swap request with user details"""
    sender: dict = Field(..., description="Sender user details")
    receiver: dict = Field(..., description="Receiver user details")
    
    class Config:
        from_attributes = True


class SwapRequestList(BaseModel):
    """Schema for swap request list response"""
    swap_requests: List[SwapRequestWithUsers] = Field(..., description="List of swap requests")
    pagination: dict = Field(..., description="Pagination information")
    unread_count: Optional[int] = Field(None, description="Unread messages count")


class SwapStatsResponse(BaseModel):
    """Schema for swap statistics response"""
    total_requests: int = Field(default=0, description="Total swap requests")
    pending_requests: int = Field(default=0, description="Pending requests")
    accepted_requests: int = Field(default=0, description="Accepted requests")
    completed_swaps: int = Field(default=0, description="Completed swaps")
    rejected_requests: int = Field(default=0, description="Rejected requests")
    cancelled_requests: int = Field(default=0, description="Cancelled requests")
    average_response_time: Optional[float] = Field(None, description="Average response time in hours")
    success_rate: float = Field(default=0.0, description="Success rate percentage")
    total_duration: int = Field(default=0, description="Total swap duration in minutes")
    average_duration: Optional[float] = Field(None, description="Average duration in minutes")


class SwapFilterQuery(BaseModel):
    """Schema for swap request filtering"""
    status: Optional[SwapStatus] = Field(None, description="Filter by status")
    type: Optional[str] = Field(default="all", description="Filter by type (sent/received/all)")
    page: int = Field(default=1, ge=1, description="Page number")
    limit: int = Field(default=20, ge=1, le=100, description="Items per page")
    sort_by: str = Field(default="recent", description="Sort by field")
    
    @validator('type')
    def validate_type(cls, v):
        if v not in ["all", "sent", "received"]:
            raise ValueError('Type must be one of: all, sent, received')
        return v


class SwapScheduleUpdate(BaseModel):
    """Schema for scheduling a swap"""
    scheduled_date: datetime = Field(..., description="Scheduled date")
    scheduled_time: str = Field(..., description="Scheduled time")
    location_type: LocationType = Field(default=LocationType.ONLINE, description="Location type")
    meeting_details: Optional[str] = Field(None, max_length=500, description="Meeting details")


class SwapCompletion(BaseModel):
    """Schema for completing a swap"""
    completion_notes: Optional[str] = Field(None, max_length=1000, description="Completion notes")
    actual_duration: Optional[int] = Field(None, ge=1, le=480, description="Actual duration in minutes")


class SwapMessageAdd(BaseModel):
    """Schema for adding message to swap"""
    content: str = Field(..., min_length=1, max_length=1000, description="Message content")
    
    @validator('content')
    def validate_content(cls, v):
        if not v.strip():
            raise ValueError('Message content cannot be empty')
        return v.strip()


class SwapMessageList(BaseModel):
    """Schema for swap messages list"""
    messages: List[SwapMessageResponse] = Field(..., description="List of messages")
    unread_count: int = Field(default=0, description="Unread messages count")
    pagination: dict = Field(..., description="Pagination information")


class SwapActivitySummary(BaseModel):
    """Schema for swap activity summary"""
    recent_swaps: List[SwapRequestResponse] = Field(default=[], description="Recent swaps")
    pending_requests: List[SwapRequestResponse] = Field(default=[], description="Pending requests")
    unread_messages: int = Field(default=0, description="Unread messages count")
    upcoming_swaps: List[SwapRequestResponse] = Field(default=[], description="Upcoming scheduled swaps")
