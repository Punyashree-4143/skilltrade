from beanie import (
    Document,
    Indexed,
    PydanticObjectId,
)

from pydantic import (
    BaseModel,
    Field,
    EmailStr,
    field_validator,
)

from typing import (
    Optional,
    List,
    Dict,
    Any,
    Literal,
)

from datetime import datetime
from enum import Enum

from app.utils.security import (
    hash_password,
    verify_password,
)


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


# Explore Model
class ExploreUser(Document):
    """Simplified user model for Explore module"""

    # FIXED OBJECT ID
    id: Optional[PydanticObjectId] = Field(
        default=None,
        alias="_id",
    )

    email: str = Field(
        ...,
        description="User email"
    )

    name: str = Field(
        ...,
        description="User full name"
    )

    bio: Optional[str] = Field(
        None,
        description="User bio"
    )

    avatar: Optional[str] = Field(
        None,
        description="Avatar image"
    )

    location: Optional[dict] = Field(
        None,
        description="Location"
    )

    skills_offered: List[str] = Field(
        default_factory=list
    )

    skills_wanted: List[str] = Field(
        default_factory=list
    )

    rating: Optional[float] = Field(
        None,
        ge=0,
        le=5
    )

    availability: Optional[Any] = None

    experience_level: Optional[str] = None

    total_reviews: Optional[int] = Field(
        default=0
    )

    is_online: bool = Field(default=True)

    last_seen: Optional[datetime] = None

    created_at: datetime = Field(
        default_factory=datetime.utcnow
    )

    updated_at: Optional[datetime] = None

    class Settings:
        name = "explore_users"

        indexes = [
            "name",
            "skills_offered",
            "skills_wanted",
            "rating",
        ]

    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "name": self.name,
            "bio": self.bio,
            "avatar": self.avatar,
            "location": self.location,
            "skills_offered": self.skills_offered,
            "skills_wanted": self.skills_wanted,
            "rating": self.rating,
            "availability": self.availability,
            "experience_level": self.experience_level,
            "total_reviews": self.total_reviews,
            "is_online": self.is_online,
            "last_seen": (
                self.last_seen.isoformat()
                if self.last_seen
                else None
            ),
            "created_at": self.created_at.isoformat(),
            "updated_at": (
                self.updated_at.isoformat()
                if self.updated_at
                else None
            ),
        }


class SkillOffer(BaseModel):
    skill: str = Field(
        ...,
        min_length=2,
        max_length=50,
    )

    category: SkillCategory

    experience: ExperienceLevel = (
        ExperienceLevel.INTERMEDIATE
    )

    description: Optional[str] = Field(
        None,
        max_length=200,
    )


class SkillWant(BaseModel):
    skill: str = Field(
        ...,
        min_length=2,
        max_length=50,
    )

    category: SkillCategory

    description: Optional[str] = Field(
        None,
        max_length=200,
    )


class Availability(BaseModel):
    monday: Optional[Dict[str, Any]] = None
    tuesday: Optional[Dict[str, Any]] = None
    wednesday: Optional[Dict[str, Any]] = None
    thursday: Optional[Dict[str, Any]] = None
    friday: Optional[Dict[str, Any]] = None
    saturday: Optional[Dict[str, Any]] = None
    sunday: Optional[Dict[str, Any]] = None


class Location(BaseModel):
    type: Literal["Point"] = "Point"

    coordinates: List[float] = Field(
        ...,
        min_length=2,
        max_length=2,
    )

    city: Optional[str] = None

    country: Optional[str] = None


class UserPreferences(BaseModel):
    max_distance: float = Field(
        default=50.0,
        ge=1.0,
        le=500.0,
    )

    notifications: Dict[str, bool] = Field(
        default_factory=lambda: {
            "email": True,
            "push": True,
            "messages": True,
            "swaps": True,
        }
    )


# MAIN USER MODEL
class User(Document):

    # FIXED OBJECT ID
    id: Optional[PydanticObjectId] = Field(
        default=None,
        alias="_id",
    )

    # Basic Info
    name: str = Field(
        ...,
        min_length=2,
        max_length=50,
    )

    email: EmailStr = Field(
        ...,
        unique=True,
    )

    password_hash: Optional[str] = Field(
        default=None,
        exclude=True,
    )

    # Profile
    bio: Optional[str] = Field(
        None,
        max_length=500,
    )

    avatar: Optional[str] = None

    # Skills
    skills_offered: List[str] = Field(
        default_factory=list
    )

    skills_wanted: List[str] = Field(
        default_factory=list
    )

    # Location
    location: Optional[Any] = None

    availability: Optional[Any] = None

    experience_level: Optional[str] = "intermediate"

    # Rating
    rating: float = Field(
        default=0.0,
        ge=0.0,
        le=5.0,
    )

    total_reviews: int = Field(default=0)

    # Status
    is_online: bool = Field(default=False)

    profile_completed: bool = Field(
        default=False
    )

    # Timestamps
    created_at: datetime = Field(
        default_factory=datetime.utcnow
    )

    updated_at: datetime = Field(
        default_factory=datetime.utcnow
    )

    class Settings:
        name = "users"

        indexes = [
            "email",
            "skills_offered",
            "skills_wanted",
            "rating",
            "created_at",
        ]

    @field_validator("password_hash")
    @classmethod
    def validate_password_hash(cls, v):
        return v

    def set_password(self, password: str):
        self.password_hash = hash_password(password)

        self.updated_at = datetime.utcnow()

    def verify_password(
        self,
        password: str,
    ) -> bool:
        return verify_password(
            password,
            self.password_hash,
        )

    def to_dict_safe(self) -> Dict[str, Any]:
        return {
            "id": str(self.id),
            "name": self.name,
            "email": self.email,
            "bio": self.bio,
            "avatar": self.avatar,
            "skills_offered": self.skills_offered,
            "skills_wanted": self.skills_wanted,
            "location": self.location,
            "availability": self.availability,
            "experience_level": self.experience_level,
            "rating": self.rating,
            "total_reviews": self.total_reviews,
            "is_online": self.is_online,
            "profile_completed": self.profile_completed,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }