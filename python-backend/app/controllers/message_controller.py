from fastapi import HTTPException, status, Depends
from typing import List, Optional, Dict, Any
import logging

from app.models.message import Message, MessageType
from app.models.user import User
from app.schemas.message import (
    MessageCreate, MessageUpdate, MessageResponse, MessageWithUsers,
    ConversationResponse, MessageList, ConversationList, MessageFilterQuery,
    MessageStatsResponse, MessageSearch, MessageActivity
)
from app.utils.exceptions import (
    ValidationError, NotFoundError, create_message_not_found_error,
    create_unauthorized_swap_access_error
)
from app.utils.helpers import paginate_query, calculate_pagination_info
from app.utils.logging import get_logger
from app.middleware.auth_middleware import get_current_user

logger = get_logger(__name__)


class MessageController:
    """Message controller"""
    
    @staticmethod
    async def send_message(
        message_data: MessageCreate,
        current_user: User
    ) -> MessageWithUsers:
        """Send a message to another user"""
        try:
            # Check if receiver exists
            receiver = await User.get(message_data.receiver_id)
            if not receiver:
                raise create_user_not_found_error(message_data.receiver_id)
            
            # Check if trying to send to self
            if message_data.receiver_id == str(current_user.id):
                raise ValidationError("Cannot send message to yourself")
            
            # Create message
            message = Message(
                sender=current_user,
                receiver=receiver,
                content=message_data.content,
                message_type=message_data.message_type
            )
            
            # Handle reply
            if message_data.reply_to_id:
                reply_to_message = await Message.get(message_data.reply_to_id)
                if reply_to_message:
                    message.reply_to = reply_to_message
            
            # Save message
            await message.save()
            
            # Populate sender and receiver
            await message.populate("sender receiver")
            
            # Update receiver's last seen
            await receiver.update_online_status(receiver.is_online)
            
            logger.info(f"Message sent: {current_user.email} -> {receiver.email}")
            
            return message
            
        except (ValidationError, NotFoundError):
            raise
        except Exception as e:
            logger.error(f"Send message error: {str(e)}")
            raise ValidationError("Failed to send message")
    
    @staticmethod
    async def get_conversation(
        user_id: str,
        page: int = 1,
        limit: int = 50,
        current_user: User = Depends(get_current_user)
    ) -> MessageList:
        """Get conversation with specific user"""
        try:
            # Check if conversation partner exists
            partner = await User.get(user_id)
            if not partner:
                raise create_user_not_found_error(user_id)
            
            # Check if user is participant
            if user_id != str(current_user.id):
                # This is a conversation with another user
                pass  # Additional validation can be added here
            
            # Build query
            query = {
                "$or": [
                    {"sender": current_user.id, "receiver": partner.id},
                    {"sender": partner.id, "receiver": current_user.id}
                ]
            }
            
            # Pagination
            skip, limit = paginate_query(page, limit)
            
            # Get messages
            messages = await Message.find(query).populate("sender receiver").sort(
                {"created_at": -1}
            ).skip(skip).limit(limit).to_list()
            
            # Reverse to show oldest first
            messages.reverse()
            
            # Get total count
            total = await Message.count_documents(query)
            
            # Calculate unread count
            unread_count = await Message.count_documents({
                "sender": partner.id,
                "receiver": current_user.id,
                "read": False
            })
            
            # Pagination info
            pagination = calculate_pagination_info(total, page, limit)
            
            return MessageList(
                messages=messages,
                pagination=pagination,
                unread_count=unread_count,
                other_user=partner.to_dict_safe()
            )
            
        except (ValidationError, NotFoundError):
            raise
        except Exception as e:
            logger.error(f"Get conversation error: {str(e)}")
            raise ValidationError("Failed to get conversation")
    
    @staticmethod
    async def get_conversations(
        page: int = 1,
        limit: int = 20,
        current_user: User = Depends(get_current_user)
    ) -> ConversationList:
        """Get all conversations for current user"""
        try:
            # Get all conversations with last message
            pipeline = [
                {
                    "$match": {
                        "$or": [
                            {"sender": current_user.id},
                            {"receiver": current_user.id}
                        ]
                    }
                },
                {
                    "$sort": {"created_at": -1}
                },
                {
                    "$group": {
                        "_id": {
                            "$cond": {
                                "if": {"$eq": ["$sender", current_user.id]},
                                "then": "$receiver",
                                "else": "$sender"
                            }
                        },
                        "last_message": {"$first": "$$ROOT"},
                        "total_messages": {"$sum": 1},
                        "unread_count": {
                            "$sum": {
                                "$cond": {
                                    "if": {
                                        "$and": [
                                            {"$eq": ["$receiver", current_user.id]},
                                            {"$eq": ["$read", False]}
                                        ]
                                    },
                                    "then": 1,
                                    "else": 0
                                }
                            }
                        }
                    }
                },
                {
                    "$sort": {"last_message.created_at": -1}
                }
            ]
            
            # Pagination
            skip, limit = paginate_query(page, limit)
            pipeline.extend([
                {"$skip": skip},
                {"$limit": limit}
            ])
            
            # Execute aggregation
            conversations_data = await Message.aggregate(pipeline).to_list()
            
            # Build conversation responses
            conversations = []
            total_unread = 0
            
            for conv_data in conversations_data:
                # Get other user
                other_user_id = conv_data["_id"]
                other_user = await User.get(other_user_id)
                
                if other_user:
                    # Get last message details
                    last_message = Message(**conv_data["last_message"])
                    await last_message.populate("sender receiver")
                    
                    conversation = ConversationResponse(
                        user_id=str(other_user.id),
                        user=other_user.to_dict_safe(),
                        last_message=last_message,
                        unread_count=conv_data["unread_count"],
                        total_messages=conv_data["total_messages"],
                        created_at=last_message.created_at,
                        updated_at=last_message.created_at
                    )
                    
                    conversations.append(conversation)
                    total_unread += conv_data["unread_count"]
            
            # Get total count
            total = await Message.aggregate([
                {
                    "$match": {
                        "$or": [
                            {"sender": current_user.id},
                            {"receiver": current_user.id}
                        ]
                    }
                },
                {
                    "$group": {
                        "_id": {
                            "$cond": {
                                "if": {"$eq": ["$sender", current_user.id]},
                                "then": "$receiver",
                                "else": "$sender"
                            }
                        }
                    }
                },
                {"$count": "total"}
            ])
            
            total_conversations = total[0]["total"] if total else 0
            
            # Pagination info
            pagination = calculate_pagination_info(total_conversations, page, limit)
            
            return ConversationList(
                conversations=conversations,
                pagination=pagination,
                total_unread=total_unread
            )
            
        except Exception as e:
            logger.error(f"Get conversations error: {str(e)}")
            raise ValidationError("Failed to get conversations")
    
    @staticmethod
    async def update_message(
        message_id: str,
        update_data: MessageUpdate,
        current_user: User
    ) -> MessageWithUsers:
        """Update message content"""
        try:
            # Get message
            message = await Message.get(message_id)
            if not message:
                raise create_message_not_found_error(message_id)
            
            # Check if user is sender
            if message.sender.id != current_user.id:
                raise create_unauthorized_swap_access_error(message_id, str(current_user.id))
            
            # Update content
            await message.edit_content(update_data.content)
            
            # Populate and return
            await message.populate("sender receiver")
            
            return message
            
        except (ValidationError, NotFoundError):
            raise
        except Exception as e:
            logger.error(f"Update message error: {str(e)}")
            raise ValidationError("Failed to update message")
    
    @staticmethod
    async def delete_message(
        message_id: str,
        current_user: User
    ) -> Dict[str, str]:
        """Soft delete a message"""
        try:
            # Get message
            message = await Message.get(message_id)
            if not message:
                raise create_message_not_found_error(message_id)
            
            # Check if user is sender
            if message.sender.id != current_user.id:
                raise create_unauthorized_swap_access_error(message_id, str(current_user.id))
            
            # Soft delete
            await message.soft_delete()
            
            return {"message": "Message deleted successfully"}
            
        except (ValidationError, NotFoundError):
            raise
        except Exception as e:
            logger.error(f"Delete message error: {str(e)}")
            raise ValidationError("Failed to delete message")
    
    @staticmethod
    async def mark_message_as_read(
        message_id: str,
        current_user: User
    ) -> Dict[str, str]:
        """Mark message as read"""
        try:
            # Get message
            message = await Message.get(message_id)
            if not message:
                raise create_message_not_found_error(message_id)
            
            # Check if user is receiver
            if message.receiver.id != current_user.id:
                raise create_unauthorized_swap_access_error(message_id, str(current_user.id))
            
            # Mark as read
            await message.mark_as_read()
            
            return {"message": "Message marked as read"}
            
        except (ValidationError, NotFoundError):
            raise
        except Exception as e:
            logger.error(f"Mark message as read error: {str(e)}")
            raise ValidationError("Failed to mark message as read")
    
    @staticmethod
    async def mark_conversation_as_read(
        user_id: str,
        current_user: User
    ) -> Dict[str, str]:
        """Mark all messages in conversation as read"""
        try:
            # Check if conversation partner exists
            partner = await User.get(user_id)
            if not partner:
                raise create_user_not_found_error(user_id)
            
            # Mark all messages as read
            await Message.update_many(
                {
                    "sender": partner.id,
                    "receiver": current_user.id,
                    "read": False
                },
                {"$set": {"read": True, "read_at": datetime.utcnow()}}
            )
            
            return {"message": "Conversation marked as read"}
            
        except (ValidationError, NotFoundError):
            raise
        except Exception as e:
            logger.error(f"Mark conversation as read error: {str(e)}")
            raise ValidationError("Failed to mark conversation as read")
    
    @staticmethod
    async def search_messages(
        search_data: MessageSearch,
        current_user: User
    ) -> MessageList:
        """Search messages"""
        try:
            # Build query
            query = {
                "$and": [
                    {
                        "$or": [
                            {"sender": current_user.id},
                            {"receiver": current_user.id}
                        ]
                    },
                    {"content": {"$regex": search_data.query, "$options": "i"}}
                ]
            }
            
            # Add filters
            if search_data.user_id:
                query["$and"].append({
                    "$or": [
                        {"sender": search_data.user_id},
                        {"receiver": search_data.user_id}
                    ]
                })
            
            if search_data.message_type:
                query["message_type"] = search_data.message_type
            
            if search_data.date_from:
                query["created_at"]["$gte"] = search_data.date_from
            
            if search_data.date_to:
                query["created_at"]["$lte"] = search_data.date_to
            
            # Pagination
            skip, limit = paginate_query(search_data.page, search_data.limit)
            
            # Get messages
            messages = await Message.find(query).populate("sender receiver").sort(
                {"created_at": -1}
            ).skip(skip).limit(limit).to_list()
            
            # Get total count
            total = await Message.count_documents(query)
            
            # Pagination info
            pagination = calculate_pagination_info(total, search_data.page, search_data.limit)
            
            return MessageList(
                messages=messages,
                pagination=pagination,
                unread_count=0
            )
            
        except Exception as e:
            logger.error(f"Search messages error: {str(e)}")
            raise ValidationError("Failed to search messages")
    
    @staticmethod
    async def get_message_stats(current_user: User) -> MessageStatsResponse:
        """Get message statistics"""
        try:
            # Get total messages
            total_messages = await Message.count_documents({
                "$or": [
                    {"sender": current_user.id},
                    {"receiver": current_user.id}
                ]
            })
            
            # Get total conversations
            conversations_pipeline = [
                {
                    "$match": {
                        "$or": [
                            {"sender": current_user.id},
                            {"receiver": current_user.id}
                        ]
                    }
                },
                {
                    "$group": {
                        "_id": {
                            "$cond": {
                                "if": {"$eq": ["$sender", current_user.id]},
                                "then": "$receiver",
                                "else": "$sender"
                            }
                        }
                    }
                },
                {"$count": "total"}
            ]
            
            conversations_result = await Message.aggregate(conversations_pipeline).to_list()
            total_conversations = conversations_result[0]["total"] if conversations_result else 0
            
            # Get unread messages
            unread_messages = await Message.count_documents({
                "receiver": current_user.id,
                "read": False
            })
            
            # Get messages today
            today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            messages_today = await Message.count_documents({
                "$or": [
                    {"sender": current_user.id},
                    {"receiver": current_user.id}
                ],
                "created_at": {"$gte": today}
            })
            
            # Get messages this week
            week_ago = datetime.utcnow() - timedelta(days=7)
            messages_this_week = await Message.count_documents({
                "$or": [
                    {"sender": current_user.id},
                    {"receiver": current_user.id}
                ],
                "created_at": {"$gte": week_ago}
            })
            
            return MessageStatsResponse(
                total_messages=total_messages,
                total_conversations=total_conversations,
                unread_messages=unread_messages,
                messages_today=messages_today,
                messages_this_week=messages_this_week
            )
            
        except Exception as e:
            logger.error(f"Get message stats error: {str(e)}")
            raise ValidationError("Failed to get message statistics")
    
    @staticmethod
    async def get_message_activity(current_user: User) -> MessageActivity:
        """Get message activity summary"""
        try:
            # Get recent messages
            recent_messages = await Message.find({
                "$or": [
                    {"sender": current_user.id},
                    {"receiver": current_user.id}
                ]
            }).populate("sender receiver").sort({"created_at": -1}).limit(10).to_list()
            
            # Get active conversations (with recent messages)
            active_conversations_pipeline = [
                {
                    "$match": {
                        "$or": [
                            {"sender": current_user.id},
                            {"receiver": current_user.id}
                        ],
                        "created_at": {"$gte": datetime.utcnow() - timedelta(days=7)}
                    }
                },
                {
                    "$group": {
                        "_id": {
                            "$cond": {
                                "if": {"$eq": ["$sender", current_user.id]},
                                "then": "$receiver",
                                "else": "$sender"
                            }
                        },
                        "last_message": {"$first": "$$ROOT"},
                        "unread_count": {
                            "$sum": {
                                "$cond": {
                                    "if": {
                                        "$and": [
                                            {"$eq": ["$receiver", current_user.id]},
                                            {"$eq": ["$read", False]}
                                        ]
                                    },
                                    "then": 1,
                                    "else": 0
                                }
                            }
                        }
                    }
                },
                {"$sort": {"last_message.created_at": -1}},
                {"$limit": 5}
            ]
            
            active_conversations_data = await Message.aggregate(active_conversations_pipeline).to_list()
            
            active_conversations = []
            total_unread = 0
            
            for conv_data in active_conversations_data:
                other_user = await User.get(conv_data["_id"])
                if other_user:
                    last_message = Message(**conv_data["last_message"])
                    await last_message.populate("sender receiver")
                    
                    conversation = ConversationResponse(
                        user_id=str(other_user.id),
                        user=other_user.to_dict_safe(),
                        last_message=last_message,
                        unread_count=conv_data["unread_count"],
                        total_messages=0,  # Would need additional query
                        created_at=last_message.created_at,
                        updated_at=last_message.created_at
                    )
                    
                    active_conversations.append(conversation)
                    total_unread += conv_data["unread_count"]
            
            return MessageActivity(
                recent_messages=recent_messages,
                active_conversations=active_conversations,
                unread_count=total_unread,
                typing_users=[]  # Would need WebSocket integration
            )
            
        except Exception as e:
            logger.error(f"Get message activity error: {str(e)}")
            raise ValidationError("Failed to get message activity")


# Import datetime and timedelta for use in controller
from datetime import datetime, timedelta
