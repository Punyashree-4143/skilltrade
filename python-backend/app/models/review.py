from beanie import Document, Indexed, Link
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

from app.models.user import User
from app.models.swap_request import SwapRequest


class ReviewResponse(BaseModel):
    content: str = Field(..., max_length=500)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class SkillRating(BaseModel):
    name: str = Field(..., min_length=2, max_length=50)
    rating: int = Field(..., ge=1, le=5)


class Review(Document):
    # Participants
    reviewer: Link[User] = Field(..., description="Review author")
    reviewee: Link[User] = Field(..., description="Review subject")
    swap_request: Link[SwapRequest] = Field(..., description="Related swap request")
    
    # Rating
    rating: int = Field(..., ge=1, le=5)
    comment: str = Field(..., min_length=10, max_length=500)
    
    # Skill Ratings
    skills: List[SkillRating] = Field(default_factory=list)
    
    # Recommendation
    would_swap_again: bool = Field(...)
    
    # Detailed Ratings (optional)
    helpfulness: Optional[int] = Field(None, ge=1, le=5)
    communication: Optional[int] = Field(None, ge=1, le=5)
    punctuality: Optional[int] = Field(None, ge=1, le=5)
    
    # Visibility
    is_public: bool = Field(default=True)
    
    # Reporting
    reported: bool = Field(default=False)
    report_reason: Optional[str] = Field(None, max_length=500)
    
    # Response
    response: Optional[ReviewResponse] = None
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "reviews"
        indexes = [
            [("reviewer", 1), ("reviewee", 1)],
            [("reviewee", 1), ("rating", -1)],
            "swap_request",
            "created_at"
        ]
    
    @validator('reviewee')
    def validate_different_users(cls, v, values):
        if 'reviewer' in values and v == values['reviewer']:
            raise ValueError('Reviewer and reviewee cannot be the same')
        return v
    
    async def add_response(self, content: str):
        """Add a response from the reviewee"""
        self.response = ReviewResponse(content=content)
        self.updated_at = datetime.utcnow()
        await self.save()
    
    async def report_review(self, reason: str):
        """Report the review"""
        self.reported = True
        self.report_reason = reason
        self.updated_at = datetime.utcnow()
        await self.save()
    
    @property
    def average_skill_rating(self) -> float:
        """Calculate average skill rating"""
        if not self.skills:
            return 0.0
        
        total = sum(skill.rating for skill in self.skills)
        return round(total / len(self.skills), 1)
    
    @property
    def time_ago(self) -> str:
        """Get human-readable time ago string"""
        now = datetime.utcnow()
        diff = now - self.created_at
        
        minutes = int(diff.total_seconds() / 60)
        hours = int(diff.total_seconds() / 3600)
        days = int(diff.total_seconds() / 86400)
        
        if minutes < 1:
            return "just now"
        elif minutes < 60:
            return f"{minutes}m ago"
        elif hours < 24:
            return f"{hours}h ago"
        elif days < 7:
            return f"{days}d ago"
        else:
            return self.created_at.strftime("%b %d")
    
    async def get_participants(self) -> Dict[str, User]:
        """Get all participants in the review"""
        reviewer = await self.reviewer.fetch()
        reviewee = await self.reviewee.fetch()
        swap_request = await self.swap_request.fetch()
        
        return {
            "reviewer": reviewer,
            "reviewee": reviewee,
            "swap_request": swap_request
        }
    
    async def can_be_edited(self, user: User) -> bool:
        """Check if user can edit the review"""
        if self.reviewer.id != user.id:
            return False
        
        # Can only edit within 7 days
        time_diff = datetime.utcnow() - self.created_at
        return time_diff.total_seconds() < 604800  # 7 days
    
    async def can_be_responded(self, user: User) -> bool:
        """Check if user can respond to the review"""
        return self.reviewee.id == user.id and self.response is None
    
    async def calculate_impact_score(self) -> float:
        """Calculate review impact score for rating algorithm"""
        score = 0.0
        
        # Base rating impact
        score += self.rating * 0.4
        
        # Detailed ratings impact
        if self.helpfulness:
            score += self.helpfulness * 0.2
        if self.communication:
            score += self.communication * 0.2
        if self.punctuality:
            score += self.punctuality * 0.1
        
        # Recommendation impact
        score += (1.0 if self.would_swap_again else 0.0) * 0.1
        
        return min(5.0, score)
