from beanie import Document, PydanticObjectId
from pydantic import Field
from typing import Dict, Any
from datetime import datetime


class Message(Document):
    """Message model for SkillTrade messaging system"""
    
    # FIXED OBJECT ID
    id: PydanticObjectId = Field(default_factory=PydanticObjectId, alias="_id")
    
    # Participants
    sender_id: PydanticObjectId = Field(..., description="Message sender ID")
    receiver_id: PydanticObjectId = Field(..., description="Message receiver ID")
    
    # Conversation
    conversation_id: str = Field(..., description="Conversation ID")
    
    # Content
    message: str = Field(..., min_length=1, max_length=5000, description="Message content")
    
    # Status
    is_read: bool = Field(default=False, description="Read status")
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    
    class Settings:
        name = "messages"
        
        indexes = [
            "conversation_id",
            [("created_at", -1)],
            [("sender_id", 1), ("receiver_id", 1)],
            [("conversation_id", 1), ("created_at", -1)],
        ]
    
    def to_dict_safe(self) -> Dict[str, Any]:
        """Helper method to serialize ObjectId properly for JSON responses"""
        return {
            "id": str(self.id),
            "sender_id": str(self.sender_id),
            "receiver_id": str(self.receiver_id),
            "conversation_id": self.conversation_id,
            "message": self.message,
            "is_read": self.is_read,
            "created_at": self.created_at.isoformat(),
        }
