from beanie import Document, Indexed, Link
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

from app.models.user import SkillCategory, User
from app.utils.helpers import calculate_distance


class SwapStatus(str, Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class LocationType(str, Enum):
    ONLINE = "online"
    IN_PERSON = "in_person"


class SkillDetail(BaseModel):
    skill: str = Field(..., min_length=2, max_length=50)
    category: SkillCategory
    description: Optional[str] = Field(None, max_length=200)


class SwapMessage(BaseModel):
    sender: Link[User] = Field(..., description="Message sender")
    content: str = Field(..., min_length=1, max_length=1000)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    read: bool = Field(default=False)


class SwapReview(BaseModel):
    reviewer: Link[User] = Field(..., description="Review author")
    reviewee: Link[User] = Field(..., description="Review subject")
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = Field(None, max_length=500)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class SwapRequest(Document):
    # Participants
    sender: Link[User] = Field(..., description="Request sender")
    receiver: Link[User] = Field(..., description="Request receiver")
    
    # Skills
    offered_skill: SkillDetail = Field(...)
    requested_skill: SkillDetail = Field(...)
    
    # Request Details
    message: str = Field(..., min_length=10, max_length=1000)
    proposed_duration: int = Field(..., ge=15, le=480, description="Duration in minutes")
    
    # Status
    status: SwapStatus = Field(default=SwapStatus.PENDING)
    
    # Scheduling
    scheduled_date: Optional[datetime] = None
    scheduled_time: Optional[str] = None
    location_type: LocationType = Field(default=LocationType.ONLINE)
    meeting_details: Optional[str] = Field(None, max_length=500)
    
    # Completion
    completion_notes: Optional[str] = Field(None, max_length=1000)
    
    # Matching
    match_score: Optional[float] = Field(None, ge=0.0, le=100.0)
    
    # Messages
    messages: List[SwapMessage] = Field(default_factory=list)
    
    # Reviews
    reviews: List[SwapReview] = Field(default_factory=list)
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "swap_requests"
        indexes = [
            [("sender", 1), ("receiver", 1)],
            [("receiver", 1), ("status", 1)],
            [("status", 1), ("created_at", -1)],
            "created_at"
        ]
    
    @validator('receiver')
    def validate_different_users(cls, v, values):
        if 'sender' in values and v == values['sender']:
            raise ValueError('Sender and receiver cannot be the same')
        return v
    
    async def add_message(self, sender: User, content: str):
        """Add a message to the swap request"""
        message = SwapMessage(sender=sender, content=content)
        self.messages.append(message)
        self.updated_at = datetime.utcnow()
        await self.save()
        return message
    
    async def mark_messages_as_read(self, user: User):
        """Mark messages as read for a user"""
        for message in self.messages:
            if message.sender.id != user.id:
                message.read = True
        self.updated_at = datetime.utcnow()
        await self.save()
    
    def get_unread_count(self, user: User) -> int:
        """Get unread message count for a user"""
        return len([
            msg for msg in self.messages 
            if msg.sender.id != user.id and not msg.read
        ])
    
    async def update_status(self, status: SwapStatus, message: Optional[str] = None):
        """Update swap request status"""
        self.status = status
        self.updated_at = datetime.utcnow()
        
        if message:
            await self.add_message(
                sender=self.sender,
                content=message
            )
        
        await self.save()
    
    async def add_review(self, reviewer: User, reviewee: User, rating: int, comment: Optional[str] = None):
        """Add a review to the swap request"""
        review = SwapReview(
            reviewer=reviewer,
            reviewee=reviewee,
            rating=rating,
            comment=comment
        )
        self.reviews.append(review)
        self.updated_at = datetime.utcnow()
        await self.save()
        return review
    
    @property
    def is_completed(self) -> bool:
        """Check if swap is completed"""
        return self.status == SwapStatus.COMPLETED
    
    @property
    def can_be_reviewed(self) -> bool:
        """Check if swap can be reviewed"""
        if self.status != SwapStatus.COMPLETED:
            return False
        
        # Check if both participants have already reviewed
        reviewer_ids = [review.reviewer.id for review in self.reviews]
        return len(reviewer_ids) < 2
    
    async def calculate_match_score(self):
        """Calculate compatibility score between participants"""
        # Fetch User objects from links
        sender = await self.fetch_link("sender")
        receiver = await self.fetch_link("receiver")
        
        # Defensive check
        if not sender or not receiver:
            print("=== MATCH SCORE ERROR ===")
            print("Sender or receiver is None")
            return 0.0
        
        print("=== MATCH SCORE CALCULATION ===")
        print(f"Sender: {sender.email}")
        print(f"Receiver: {receiver.email}")
        print(f"Offered Skill: {self.offered_skill.skill}")
        print(f"Requested Skill: {self.requested_skill.skill}")
        
        score = 0.0
        
        # Direct match: current swap skills match
        direct_match = (
            self.requested_skill.skill.lower() == self.offered_skill.skill.lower()
        )
        
        if direct_match:
            score += 50.0
            print("Direct match found: +50")
        
        # Partial match: one skill matches
        partial_match = (
            self.requested_skill.skill.lower() == self.offered_skill.skill.lower() or
            self.offered_skill.skill.lower() == self.requested_skill.skill.lower()
        )
        
        if partial_match:
            score += 25.0
            print("Partial match found: +25")
        
        # Rating factor
        score += min(receiver.rating, 5.0) * 10.0
        
        # Distance factor (if locations are available)
        if (sender.location and receiver.location and 
            sender.location.coordinates and receiver.location.coordinates):
            
            distance = calculate_distance(
                sender.location.coordinates,
                receiver.location.coordinates
            )
            score += max(0.0, 50.0 - distance) * 0.5
        
        self.match_score = min(100.0, round(score))
        await self.save()
    
    async def get_participants(self) -> List[User]:
        """Get both participants of the swap"""
        # Use User objects directly - no need to fetch
        sender = self.sender
        receiver = self.receiver
        return [sender, receiver]
