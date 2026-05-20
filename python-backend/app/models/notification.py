from datetime import datetime
from typing import Any, Dict, Optional

from beanie import Document, PydanticObjectId
from pydantic import Field


class Notification(Document):
    """Persistent user notification."""

    id: PydanticObjectId = Field(default_factory=PydanticObjectId, alias="_id")
    user_id: PydanticObjectId = Field(..., description="Notification owner")
    type: str = Field(..., min_length=1, max_length=50)
    title: str = Field(..., min_length=1, max_length=120)
    message: str = Field(..., min_length=1, max_length=500)
    related_user_id: Optional[PydanticObjectId] = None
    related_swap_id: Optional[PydanticObjectId] = None
    is_read: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "notifications"
        indexes = [
            "user_id",
            [("user_id", 1), ("created_at", -1)],
            [("user_id", 1), ("is_read", 1)],
            [("user_id", 1), ("type", 1), ("related_user_id", 1), ("related_swap_id", 1)],
        ]

    def to_dict_safe(self) -> Dict[str, Any]:
        return {
            "id": str(self.id),
            "user_id": str(self.user_id),
            "type": self.type,
            "title": self.title,
            "message": self.message,
            "related_user_id": str(self.related_user_id) if self.related_user_id else None,
            "related_swap_id": str(self.related_swap_id) if self.related_swap_id else None,
            "is_read": self.is_read,
            "created_at": self.created_at.isoformat(),
        }
