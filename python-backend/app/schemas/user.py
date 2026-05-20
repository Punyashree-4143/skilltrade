from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

from app.schemas.auth import LocationResponse


class SkillCategory(str, Enum):
    TECHNOLOGY = "technology"
    CREATIVE = "creative"
    BUSINESS = "business"
    EDUCATION = "education"
    HEALTH = "health"
    LIFESTYLE = "lifestyle"
    OTHER = "other"


class ExperienceLevel(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class SkillOfferCreate(BaseModel):
    """Schema for creating a skill offer"""
    skill: str = Field(..., min_length=2, max_length=50, description="Skill name")
    category: SkillCategory = Field(..., description="Skill category")
    experience: ExperienceLevel = Field(default=ExperienceLevel.INTERMEDIATE, description="Experience level")
    description: Optional[str] = Field(None, max_length=200, description="Skill description")
    
    @validator('skill')
    def validate_skill_name(cls, v):
        if not v.strip():
            raise ValueError('Skill name cannot be empty')
        return v.strip().lower()


class SkillWantCreate(BaseModel):
    """Schema for creating a skill want"""
    skill: str = Field(..., min_length=2, max_length=50, description="Skill name")
    category: SkillCategory = Field(..., description="Skill category")
    description: Optional[str] = Field(None, max_length=200, description="Skill description")
    
    @validator('skill')
    def validate_skill_name(cls, v):
        if not v.strip():
            raise ValueError('Skill name cannot be empty')
        return v.strip().lower()


class SkillOfferResponse(BaseModel):
    """Schema for skill offer response"""
    skill: str = Field(..., description="Skill name")
    category: SkillCategory = Field(..., description="Skill category")
    experience: ExperienceLevel = Field(..., description="Experience level")
    description: Optional[str] = Field(None, description="Skill description")
    
    class Config:
        from_attributes = True


class SkillWantResponse(BaseModel):
    """Schema for skill want response"""
    skill: str = Field(..., description="Skill name")
    category: SkillCategory = Field(..., description="Skill category")
    description: Optional[str] = Field(None, description="Skill description")
    
    class Config:
        from_attributes = True


class AvailabilityCreate(BaseModel):
    """Schema for creating availability"""
    monday: Optional[Dict[str, Any]] = Field(None, description="Monday availability")
    tuesday: Optional[Dict[str, Any]] = Field(None, description="Tuesday availability")
    wednesday: Optional[Dict[str, Any]] = Field(None, description="Wednesday availability")
    thursday: Optional[Dict[str, Any]] = Field(None, description="Thursday availability")
    friday: Optional[Dict[str, Any]] = Field(None, description="Friday availability")
    saturday: Optional[Dict[str, Any]] = Field(None, description="Saturday availability")
    sunday: Optional[Dict[str, Any]] = Field(None, description="Sunday availability")


class AvailabilityResponse(BaseModel):
    """Schema for availability response"""
    monday: Optional[Dict[str, Any]] = Field(None, description="Monday availability")
    tuesday: Optional[Dict[str, Any]] = Field(None, description="Tuesday availability")
    wednesday: Optional[Dict[str, Any]] = Field(None, description="Wednesday availability")
    thursday: Optional[Dict[str, Any]] = Field(None, description="Thursday availability")
    friday: Optional[Dict[str, Any]] = Field(None, description="Friday availability")
    saturday: Optional[Dict[str, Any]] = Field(None, description="Saturday availability")
    sunday: Optional[Dict[str, Any]] = Field(None, description="Sunday availability")
    
    class Config:
        from_attributes = True


class UserPreferencesCreate(BaseModel):
    """Schema for creating user preferences"""
    max_distance: float = Field(default=50.0, ge=1.0, le=500.0, description="Maximum distance for matches in km")
    notifications: Dict[str, bool] = Field(
        default={
            "email": True,
            "push": True,
            "messages": True,
            "swaps": True
        },
        description="Notification preferences"
    )


class UserPreferencesResponse(BaseModel):
    """Schema for user preferences response"""
    max_distance: float = Field(..., description="Maximum distance for matches in km")
    notifications: Dict[str, bool] = Field(..., description="Notification preferences")
    
    class Config:
        from_attributes = True


class UserProfileUpdate(BaseModel):
    """Schema for updating user profile"""
    name: Optional[str] = Field(None, min_length=2, max_length=50, description="User's name")
    bio: Optional[str] = Field(None, max_length=500, description="User's bio")
    avatar: Optional[str] = Field(None, description="Avatar URL")
    location: Optional["LocationCreate"] = Field(None, description="User's location")
    offers: Optional[List[SkillOfferCreate]] = Field(None, description="Skills user can offer")
    wants: Optional[List[SkillWantCreate]] = Field(None, description="Skills user wants to learn")
    availability: Optional[AvailabilityCreate] = Field(None, description="User's availability")
    preferences: Optional[UserPreferencesCreate] = Field(None, description="User preferences")
    
    @validator('name')
    def validate_name(cls, v):
        if v is not None:
            if not v.strip():
                raise ValueError('Name cannot be empty')
            if not all(c.isalnum() or c.isspace() or c in "-'" for c in v):
                raise ValueError('Name contains invalid characters')
            return v.strip()
        return v


class UserProfileResponse(BaseModel):
    """Schema for user profile response"""
    id: str = Field(..., description="User ID")
    name: str = Field(..., description="User's name")
    email: str = Field(..., description="User's email")
    bio: Optional[str] = Field(None, description="User's bio")
    avatar: Optional[str] = Field(None, description="Avatar URL")
    offers: List[SkillOfferResponse] = Field(default=[], description="Skills user can offer")
    wants: List[SkillWantResponse] = Field(default=[], description="Skills user wants to learn")
    rating: float = Field(default=0.0, description="User's average rating")
    total_reviews: int = Field(default=0, description="Total number of reviews")
    location: Optional[LocationResponse] = Field(None, description="User's location")
    availability: Optional[AvailabilityResponse] = Field(None, description="User's availability")
    preferences: Optional[UserPreferencesResponse] = Field(None, description="User preferences")
    is_online: bool = Field(default=False, description="User's online status")
    last_seen: datetime = Field(..., description="Last seen timestamp")
    created_at: datetime = Field(..., description="Account creation date")
    updated_at: datetime = Field(..., description="Last update timestamp")
    
    class Config:
        from_attributes = True


class UserSearchQuery(BaseModel):
    """Schema for user search query"""
    query: Optional[str] = Field(None, description="Search query string")
    skills: Optional[List[str]] = Field(None, description="Filter by skills")
    category: Optional[SkillCategory] = Field(None, description="Filter by skill category")
    distance: Optional[float] = Field(default=50.0, ge=1.0, le=500.0, description="Maximum distance in km")
    page: int = Field(default=1, ge=1, description="Page number")
    limit: int = Field(default=20, ge=1, le=100, description="Items per page")
    sort_by: str = Field(default="relevance", description="Sort by field")
    
    @validator('skills')
    def validate_skills(cls, v):
        if v is not None:
            return [skill.lower().strip() for skill in v if skill.strip()]
        return v


class UserMatchResponse(BaseModel):
    """Schema for user match response"""
    user: UserProfileResponse = Field(..., description="Matched user")
    match_score: float = Field(..., ge=0.0, le=100.0, description="Match compatibility score")
    offered_skills: List[SkillOfferResponse] = Field(..., description="Skills that match user's wants")
    requested_skills: List[SkillWantResponse] = Field(..., description="Skills that match user's offers")
    distance: Optional[float] = Field(None, description="Distance in km")
    common_skills: List[str] = Field(default=[], description="Common skills")
    
    class Config:
        from_attributes = True


class UserStatsResponse(BaseModel):
    """Schema for user statistics response"""
    total_swaps: int = Field(default=0, description="Total number of swaps")
    completed_swaps: int = Field(default=0, description="Completed swaps")
    pending_swaps: int = Field(default=0, description="Pending swaps")
    accepted_swaps: int = Field(default=0, description="Accepted swaps")
    average_swap_duration: Optional[float] = Field(None, description="Average swap duration in minutes")
    success_rate: float = Field(default=0.0, description="Swap success rate")
    total_messages: int = Field(default=0, description="Total messages sent")
    profile_views: int = Field(default=0, description="Profile views")
    last_active: datetime = Field(..., description="Last activity timestamp")
    
    class Config:
        from_attributes = True


class UserOnlineStatus(BaseModel):
    """Schema for user online status"""
    user_id: str = Field(..., description="User ID")
    is_online: bool = Field(..., description="Online status")
    last_seen: datetime = Field(..., description="Last seen timestamp")
    
    class Config:
        from_attributes = True


# Forward references for circular imports
from app.schemas.auth import LocationCreate
UserProfileUpdate.update_forward_refs()
