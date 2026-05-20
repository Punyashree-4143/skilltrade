from beanie import Document, PydanticObjectId
from pydantic import Field
from typing import List, Optional, Dict, Any
from datetime import datetime


class Conversation(Document):
    """Conversation model for SkillTrade messaging system"""
    
    # FIXED OBJECT ID
    id: PydanticObjectId = Field(default_factory=PydanticObjectId, alias="_id")
    
    # Participants
    participants: List[PydanticObjectId] = Field(
        ...,
        min_length=2,
        max_length=2,
        description="List of participant user IDs"
    )
    
    # Last message info
    last_message: Optional[str] = Field(None, description="Last message content preview")
    last_message_time: datetime = Field(default_factory=datetime.utcnow, description="Last message timestamp")
    
    # Timestamps
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")
    
    class Settings:
        name = "conversations"
        
        indexes = [
            "participants",
            [("last_message_time", -1)],
            [("participants", 1), ("updated_at", -1)],
        ]
    
    def to_dict_safe(self) -> Dict[str, Any]:
        """Helper method to serialize ObjectId properly for JSON responses"""
        return {
            "id": str(self.id),
            "participants": [str(p) for p in self.participants],
            "last_message": self.last_message,
            "last_message_time": self.last_message_time.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
