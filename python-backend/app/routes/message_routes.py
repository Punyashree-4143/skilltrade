from datetime import datetime
from typing import Any, Dict, List, Optional

from beanie import PydanticObjectId
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, Field, model_validator

from app.middleware.auth_middleware import get_current_user
from app.models.conversation import Conversation
from app.models.message import Message
from app.models.swap_request import SwapRequest, SwapStatus
from app.models.user import User
from app.utils.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/api/messages", tags=["Messages"])


async def _create_message_notification(receiver: User, sender: User):
    try:
        from app.routes.notification_routes import create_notification

        await create_notification(
            user_id=receiver.id,
            notification_type="new_message",
            title="New Message",
            message=f"{sender.name} sent you a message.",
            related_user_id=sender.id,
        )
    except Exception as exc:
        logger.error(f"Message notification creation failed: {exc}")


class SendMessageRequest(BaseModel):
    receiver_id: str = Field(..., min_length=1)
    message: Optional[str] = Field(None, min_length=1, max_length=5000)
    content: Optional[str] = Field(None, min_length=1, max_length=5000)
    swap_id: Optional[str] = None

    @model_validator(mode="after")
    def normalize_message(self) -> "SendMessageRequest":
        text = self.message if self.message is not None else self.content
        if text is None or not text.strip():
            raise ValueError("Message cannot be empty")

        self.message = text.strip()
        return self


def _object_id(value: str, field_name: str = "id") -> PydanticObjectId:
    try:
        return PydanticObjectId(value)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid {field_name}",
        )


def _status_value(value: Any) -> str:
    if hasattr(value, "value"):
        return value.value
    return str(value).lower()


def _user_summary(user: User) -> Dict[str, Any]:
    return {
        "id": str(user.id),
        "name": user.name,
        "email": str(user.email),
        "avatar": user.avatar,
        "is_online": user.is_online,
    }


def _message_payload(message: Message) -> Dict[str, Any]:
    return {
        "id": str(message.id),
        "sender_id": str(message.sender_id),
        "receiver_id": str(message.receiver_id),
        "conversation_id": message.conversation_id,
        "message": message.message,
        "content": message.message,
        "is_read": message.is_read,
        "created_at": message.created_at,
    }


async def _get_swap_participant_ids(swap: SwapRequest) -> List[str]:
    await swap.fetch_link("sender")
    await swap.fetch_link("receiver")
    return [str(swap.sender.id), str(swap.receiver.id)]


async def _is_accepted_swap_between(
    swap: SwapRequest,
    user_id: str,
    other_user_id: str,
) -> bool:
    if _status_value(swap.status) != SwapStatus.ACCEPTED.value:
        return False

    participant_ids = await _get_swap_participant_ids(swap)
    return set(participant_ids) == {user_id, other_user_id}


async def _find_accepted_swap(
    current_user: User,
    other_user: User,
    swap_id: Optional[str] = None,
) -> SwapRequest:
    current_user_id = str(current_user.id)
    other_user_id = str(other_user.id)

    if swap_id:
        swap = await SwapRequest.get(_object_id(swap_id, "swap_id"))
        if not swap:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Swap request not found",
            )

        if await _is_accepted_swap_between(swap, current_user_id, other_user_id):
            return swap

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accepted swap not found for these participants",
        )

    accepted_swaps = await SwapRequest.find(
        SwapRequest.status == SwapStatus.ACCEPTED
    ).to_list()

    for swap in accepted_swaps:
        if await _is_accepted_swap_between(swap, current_user_id, other_user_id):
            return swap

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Accepted swap required before messaging",
    )


async def _get_or_create_conversation(
    current_user: User,
    other_user: User,
) -> Conversation:
    participant_ids = [_object_id(str(current_user.id)), _object_id(str(other_user.id))]
    conversation = await Conversation.find_one(
        {"participants": {"$all": participant_ids, "$size": 2}}
    )

    if conversation:
        return conversation

    conversation = Conversation(
        participants=participant_ids,
        last_message=None,
        last_message_time=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    await conversation.insert()
    return conversation


async def _conversation_response(
    conversation: Conversation,
    current_user: User,
) -> Dict[str, Any]:
    current_user_id = str(current_user.id)
    participant_ids = [str(participant_id) for participant_id in conversation.participants]

    if current_user_id not in participant_ids:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this conversation",
        )

    other_user_id = next(
        participant_id for participant_id in participant_ids if participant_id != current_user_id
    )
    other_user = await User.get(_object_id(other_user_id, "participant_id"))
    if not other_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation participant not found",
        )

    unread_count = await Message.find(
        {
            "conversation_id": str(conversation.id),
            "receiver_id": _object_id(current_user_id),
            "is_read": False,
        }
    ).count()

    return {
        "conversation_id": str(conversation.id),
        "other_participant": _user_summary(other_user),
        "last_message": conversation.last_message,
        "unread_count": unread_count,
        "updated_at": conversation.updated_at,
    }


@router.get("/conversations")
async def get_conversations(current_user: User = Depends(get_current_user)):
    try:
        conversations = await Conversation.find(
            {"participants": _object_id(str(current_user.id))}
        ).sort("-updated_at").to_list()

        data = [
            await _conversation_response(conversation, current_user)
            for conversation in conversations
        ]
        return jsonable_encoder(data)
    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"Get conversations error: {exc}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get conversations",
        )


@router.get("/{conversation_id}")
async def get_messages(
    conversation_id: str,
    current_user: User = Depends(get_current_user),
):
    try:
        conversation = await Conversation.get(_object_id(conversation_id, "conversation_id"))
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found",
            )

        participant_ids = [str(participant_id) for participant_id in conversation.participants]
        if str(current_user.id) not in participant_ids:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have access to this conversation",
            )

        messages = await Message.find(
            {"conversation_id": str(conversation.id)}
        ).sort("created_at").to_list()

        return jsonable_encoder([_message_payload(message) for message in messages])
    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"Get messages error: {exc}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get messages",
        )


@router.post("/send")
async def send_message(
    payload: SendMessageRequest,
    current_user: User = Depends(get_current_user),
):
    try:
        receiver_id = _object_id(payload.receiver_id, "receiver_id")
        if str(receiver_id) == str(current_user.id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot send message to yourself",
            )

        receiver = await User.get(receiver_id)
        if not receiver:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Receiver not found",
            )

        await _find_accepted_swap(current_user, receiver, payload.swap_id)
        conversation = await _get_or_create_conversation(current_user, receiver)

        now = datetime.utcnow()
        message = Message(
            sender_id=_object_id(str(current_user.id)),
            receiver_id=receiver_id,
            conversation_id=str(conversation.id),
            message=payload.message,
            is_read=False,
            created_at=now,
        )
        await message.insert()

        await _create_message_notification(receiver, current_user)

        conversation.last_message = payload.message
        conversation.last_message_time = now
        conversation.updated_at = now
        await conversation.save()

        return jsonable_encoder(_message_payload(message))
    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"Send message error: {exc}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send message",
        )


@router.put("/read/{message_id}")
async def mark_message_read(
    message_id: str,
    current_user: User = Depends(get_current_user),
):
    try:
        message = await Message.get(_object_id(message_id, "message_id"))
        if not message:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Message not found",
            )

        if str(message.receiver_id) != str(current_user.id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only the receiver can mark this message as read",
            )

        message.is_read = True
        await message.save()

        return jsonable_encoder(_message_payload(message))
    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"Mark message read error: {exc}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to mark message as read",
        )
