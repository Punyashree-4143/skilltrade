from pydantic import (
    BaseModel,
    Field,
    EmailStr,
    field_validator,
    ValidationInfo,
)

from typing import Optional
from datetime import datetime


class UserRegister(BaseModel):
    """Schema for user registration"""

    name: str = Field(
        ...,
        min_length=2,
        max_length=50,
        description="User's full name"
    )

    email: EmailStr = Field(
        ...,
        description="User's email address"
    )

    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="User's password"
    )

    password_confirm: str = Field(
        ...,
        description="Password confirmation"
    )

    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        if not v.strip():
            raise ValueError('Name cannot be empty')

        return v.strip()

    @field_validator('password')
    @classmethod
    def validate_password_strength(cls, v):
        if len(v) < 8:
            raise ValueError(
                'Password must be at least 8 characters long'
            )

        has_upper = any(c.isupper() for c in v)
        has_lower = any(c.islower() for c in v)
        has_digit = any(c.isdigit() for c in v)

        if not (has_upper and has_lower and has_digit):
            raise ValueError(
                'Password must contain uppercase, lowercase, and digit'
            )

        return v

    # FIXED FOR PYDANTIC V2
    @field_validator('password_confirm')
    @classmethod
    def passwords_match(
        cls,
        v,
        info: ValidationInfo
    ):
        password = info.data.get('password')

        if password and v != password:
            raise ValueError('Passwords do not match')

        return v


class UserLogin(BaseModel):
    """Schema for user login"""

    email: EmailStr = Field(
        ...,
        description="User's email address"
    )

    password: str = Field(
        ...,
        description="User's password"
    )


class TokenResponse(BaseModel):
    """Schema for token response"""

    access_token: str = Field(
        ...,
        description="JWT access token"
    )

    token_type: str = Field(
        default="bearer",
        description="Token type"
    )

    user: dict = Field(
        ...,
        description="User data"
    )


class UserResponse(BaseModel):
    """Schema for user response"""

    id: str = Field(..., description="User ID")

    name: str = Field(..., description="User's name")

    email: EmailStr = Field(
        ...,
        description="User's email"
    )

    bio: Optional[str] = Field(
        None,
        description="User's bio"
    )

    avatar: Optional[str] = Field(
        None,
        description="Avatar URL"
    )

    skills_offered: list = Field(
        default=[],
        description="Skills user can offer"
    )

    skills_wanted: list = Field(
        default=[],
        description="Skills user wants to learn"
    )

    location: Optional[dict] = Field(
        None,
        description="User's location"
    )

    availability: Optional[str] = Field(
        None,
        description="User's availability"
    )

    rating: float = Field(
        default=0.0,
        description="User's average rating"
    )

    total_reviews: int = Field(
        default=0,
        description="Total number of reviews"
    )

    is_online: bool = Field(
        default=False,
        description="User's online status"
    )

    profile_completed: bool = Field(
        default=False,
        description="Whether user has completed profile"
    )

    created_at: str = Field(
        ...,
        description="Account creation date"
    )

    updated_at: str = Field(
        ...,
        description="Last update date"
    )

    class Config:
        from_attributes = True


class LocationCreate(BaseModel):
    """Schema for location creation"""

    coordinates: list[float] = Field(
        ...,
        min_items=2,
        max_items=2,
        description="Geographic coordinates [longitude, latitude]"
    )

    city: Optional[str] = Field(
        None,
        max_length=100,
        description="City name"
    )

    country: Optional[str] = Field(
        None,
        max_length=100,
        description="Country name"
    )

    @field_validator('coordinates')
    @classmethod
    def validate_coordinates(cls, v):
        if len(v) != 2:
            raise ValueError(
                'Coordinates must be [longitude, latitude]'
            )

        longitude, latitude = v

        if not (-180 <= longitude <= 180):
            raise ValueError(
                'Longitude must be between -180 and 180'
            )

        if not (-90 <= latitude <= 90):
            raise ValueError(
                'Latitude must be between -90 and 90'
            )

        return v


class LocationResponse(BaseModel):
    """Schema for location response"""

    type: str = Field(
        default="Point",
        description="GeoJSON type"
    )

    coordinates: list[float] = Field(
        ...,
        description="Geographic coordinates [longitude, latitude]"
    )

    city: Optional[str] = Field(
        None,
        description="City name"
    )

    country: Optional[str] = Field(
        None,
        description="Country name"
    )

    full_location: Optional[str] = Field(
        None,
        description="Formatted location string"
    )

    class Config:
        from_attributes = True


class PasswordChange(BaseModel):
    """Schema for password change"""

    current_password: str = Field(
        ...,
        description="Current password"
    )

    new_password: str = Field(
        ...,
        min_length=6,
        max_length=128,
        description="New password"
    )

    @field_validator('new_password')
    @classmethod
    def validate_password_strength(cls, v):
        if len(v) < 8:
            raise ValueError(
                'Password must be at least 8 characters long'
            )

        has_upper = any(c.isupper() for c in v)
        has_lower = any(c.islower() for c in v)
        has_digit = any(c.isdigit() for c in v)

        if not (has_upper and has_lower and has_digit):
            raise ValueError(
                'Password must contain uppercase, lowercase, and digit'
            )

        return v


class PasswordReset(BaseModel):
    """Schema for password reset request"""

    email: EmailStr = Field(
        ...,
        description="User's email address"
    )


class PasswordResetConfirm(BaseModel):
    """Schema for password reset confirmation"""

    token: str = Field(
        ...,
        description="Password reset token"
    )

    new_password: str = Field(
        ...,
        min_length=6,
        max_length=128,
        description="New password"
    )

    @field_validator('new_password')
    @classmethod
    def validate_password_strength(cls, v):
        if len(v) < 8:
            raise ValueError(
                'Password must be at least 8 characters long'
            )

        has_upper = any(c.isupper() for c in v)
        has_lower = any(c.islower() for c in v)
        has_digit = any(c.isdigit() for c in v)

        if not (has_upper and has_lower and has_digit):
            raise ValueError(
                'Password must contain uppercase, lowercase, and digit'
            )

        return v


class RefreshToken(BaseModel):
    """Schema for token refresh"""

    refresh_token: str = Field(
        ...,
        description="Refresh token"
    )


LocationCreate.update_forward_refs()
LocationResponse.update_forward_refs()