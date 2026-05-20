from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime


class SkillRatingCreate(BaseModel):
    """Schema for creating skill rating"""
    name: str = Field(..., min_length=2, max_length=50, description="Skill name")
    rating: int = Field(..., ge=1, le=5, description="Skill rating")

    @validator('name')
    def validate_skill_name(cls, v):
        if not v.strip():
            raise ValueError('Skill name cannot be empty')
        return v.strip().lower()


class SkillRatingResponse(BaseModel):
    """Schema for skill rating response"""
    name: str = Field(..., description="Skill name")
    rating: int = Field(..., description="Skill rating")

    class Config:
        from_attributes = True


class ReviewResponseData(BaseModel):
    """Schema for review response data"""
    content: str = Field(..., description="Response content")
    created_at: datetime = Field(..., description="Response timestamp")

    class Config:
        from_attributes = True


class ReviewCreate(BaseModel):
    """Schema for creating a review"""
    reviewee_id: str = Field(..., description="Reviewee user ID")
    swap_request_id: str = Field(..., description="Related swap request ID")
    rating: int = Field(..., ge=1, le=5, description="Rating (1-5)")
    comment: str = Field(..., min_length=10, max_length=500, description="Review comment")

    skills: Optional[List[SkillRatingCreate]] = Field(
        default=[],
        description="Skill-specific ratings"
    )

    would_swap_again: bool = Field(..., description="Would swap again")

    helpfulness: Optional[int] = Field(
        None,
        ge=1,
        le=5,
        description="Helpfulness rating"
    )

    communication: Optional[int] = Field(
        None,
        ge=1,
        le=5,
        description="Communication rating"
    )

    punctuality: Optional[int] = Field(
        None,
        ge=1,
        le=5,
        description="Punctuality rating"
    )

    @validator('comment')
    def validate_comment(cls, v):
        if not v.strip():
            raise ValueError('Review comment cannot be empty')
        return v.strip()


class ReviewUpdate(BaseModel):
    """Schema for updating a review"""
    comment: Optional[str] = Field(
        None,
        min_length=10,
        max_length=500,
        description="Updated review comment"
    )

    is_public: Optional[bool] = Field(
        None,
        description="Public visibility"
    )

    @validator('comment')
    def validate_comment(cls, v):
        if v is not None and not v.strip():
            raise ValueError('Review comment cannot be empty')
        return v.strip() if v else v


class ReviewResponse(BaseModel):
    """Schema for review response"""
    id: str = Field(..., description="Review ID")
    reviewer_id: str = Field(..., description="Reviewer user ID")
    reviewee_id: str = Field(..., description="Reviewee user ID")
    swap_request_id: str = Field(..., description="Related swap request ID")

    rating: int = Field(..., description="Overall rating")
    comment: str = Field(..., description="Review comment")

    skills: List[SkillRatingResponse] = Field(
        default=[],
        description="Skill-specific ratings"
    )

    would_swap_again: bool = Field(..., description="Would swap again")

    helpfulness: Optional[int] = Field(
        None,
        description="Helpfulness rating"
    )

    communication: Optional[int] = Field(
        None,
        description="Communication rating"
    )

    punctuality: Optional[int] = Field(
        None,
        description="Punctuality rating"
    )

    is_public: bool = Field(
        default=True,
        description="Public visibility"
    )

    reported: bool = Field(
        default=False,
        description="Reported status"
    )

    report_reason: Optional[str] = Field(
        None,
        description="Report reason"
    )

    response: Optional[ReviewResponseData] = Field(
        None,
        description="Reviewee response"
    )

    created_at: datetime = Field(
        ...,
        description="Creation timestamp"
    )

    updated_at: datetime = Field(
        ...,
        description="Last update timestamp"
    )

    class Config:
        from_attributes = True


class ReviewWithUsers(ReviewResponse):
    """Schema for review with user details"""

    reviewer: dict = Field(
        ...,
        description="Reviewer user details"
    )

    reviewee: dict = Field(
        ...,
        description="Reviewee user details"
    )

    swap_request: dict = Field(
        ...,
        description="Related swap request details"
    )

    class Config:
        from_attributes = True


class ReviewList(BaseModel):
    """Schema for review list response"""

    reviews: List[ReviewWithUsers] = Field(
        ...,
        description="List of reviews"
    )

    pagination: dict = Field(
        ...,
        description="Pagination information"
    )

    stats: dict = Field(
        ...,
        description="Review statistics"
    )


class ReviewStats(BaseModel):
    """Schema for review statistics"""

    total_reviews: int = Field(
        default=0,
        description="Total number of reviews"
    )

    average_rating: float = Field(
        default=0.0,
        description="Average rating"
    )

    five_star: int = Field(
        default=0,
        description="5-star reviews count"
    )

    four_star: int = Field(
        default=0,
        description="4-star reviews count"
    )

    three_star: int = Field(
        default=0,
        description="3-star reviews count"
    )

    two_star: int = Field(
        default=0,
        description="2-star reviews count"
    )

    one_star: int = Field(
        default=0,
        description="1-star reviews count"
    )

    would_swap_again_count: int = Field(
        default=0,
        description="Would swap again count"
    )

    would_swap_again_percentage: float = Field(
        default=0.0,
        description="Would swap again percentage"
    )

    average_helpfulness: Optional[float] = Field(
        None,
        description="Average helpfulness rating"
    )

    average_communication: Optional[float] = Field(
        None,
        description="Average communication rating"
    )

    average_punctuality: Optional[float] = Field(
        None,
        description="Average punctuality rating"
    )


class ReviewFilterQuery(BaseModel):
    """Schema for review filtering"""

    user_id: Optional[str] = Field(
        None,
        description="Filter by user ID"
    )

    rating: Optional[int] = Field(
        None,
        ge=1,
        le=5,
        description="Filter by rating"
    )

    would_swap_again: Optional[bool] = Field(
        None,
        description="Filter by would swap again"
    )

    page: int = Field(
        default=1,
        ge=1,
        description="Page number"
    )

    limit: int = Field(
        default=20,
        ge=1,
        le=100,
        description="Items per page"
    )

    sort_by: str = Field(
        default="recent",
        description="Sort by field"
    )


class ReviewReport(BaseModel):
    """Schema for reporting a review"""

    reason: str = Field(
        ...,
        min_length=10,
        max_length=500,
        description="Report reason"
    )

    @validator('reason')
    def validate_reason(cls, v):
        if not v.strip():
            raise ValueError('Report reason cannot be empty')
        return v.strip()


class ReviewResponseCreate(BaseModel):
    """Schema for creating review response"""

    content: str = Field(
        ...,
        min_length=10,
        max_length=500,
        description="Response content"
    )

    @validator('content')
    def validate_content(cls, v):
        if not v.strip():
            raise ValueError('Response content cannot be empty')
        return v.strip()


class UserReviewSummary(BaseModel):
    """Schema for user review summary"""

    user_id: str = Field(
        ...,
        description="User ID"
    )

    total_reviews: int = Field(
        default=0,
        description="Total reviews"
    )

    average_rating: float = Field(
        default=0.0,
        description="Average rating"
    )

    recent_reviews: List[ReviewWithUsers] = Field(
        default=[],
        description="Recent reviews"
    )

    rating_distribution: dict = Field(
        default={},
        description="Rating distribution"
    )

    skill_ratings: List[SkillRatingResponse] = Field(
        default=[],
        description="Skill-specific ratings"
    )

    would_swap_again_rate: float = Field(
        default=0.0,
        description="Would swap again rate"
    )


class ReviewActivity(BaseModel):
    """Schema for review activity"""

    pending_reviews: int = Field(
        default=0,
        description="Reviews to write"
    )

    recent_reviews_given: List[ReviewWithUsers] = Field(
        default=[],
        description="Recent reviews given"
    )

    recent_reviews_received: List[ReviewWithUsers] = Field(
        default=[],
        description="Recent reviews received"
    )

    review_notifications: int = Field(
        default=0,
        description="Unread review notifications"
    )


class ReviewAnalytics(BaseModel):
    """Schema for review analytics"""

    total_reviews_all_time: int = Field(
        default=0,
        description="Total reviews all time"
    )

    reviews_this_month: int = Field(
        default=0,
        description="Reviews this month"
    )

    average_rating_trend: List[float] = Field(
        default=[],
        description="Average rating trend"
    )

    most_reviewed_skills: List[dict] = Field(
        default=[],
        description="Most reviewed skills"
    )

    review_completion_rate: float = Field(
        default=0.0,
        description="Review completion rate"
    )