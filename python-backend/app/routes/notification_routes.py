from typing import Optional

from beanie import PydanticObjectId
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.encoders import jsonable_encoder

from app.middleware.auth_middleware import get_current_user
from app.models.notification import Notification
from app.models.user import User
from app.utils.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/api/notifications", tags=["Notifications"])


def _object_id(value: str, field_name: str = "id") -> PydanticObjectId:
    try:
        return PydanticObjectId(value)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid {field_name}",
        )


async def create_notification(
    user_id: PydanticObjectId,
    notification_type: str,
    title: str,
    message: str,
    related_user_id: Optional[PydanticObjectId] = None,
    related_swap_id: Optional[PydanticObjectId] = None,
    dedupe: bool = False,
) -> Optional[Notification]:
    if dedupe:
        existing = await Notification.find_one(
            {
                "user_id": user_id,
                "type": notification_type,
                "related_user_id": related_user_id,
                "related_swap_id": related_swap_id,
            }
        )
        if existing:
            return existing

    notification = Notification(
        user_id=user_id,
        type=notification_type,
        title=title,
        message=message,
        related_user_id=related_user_id,
        related_swap_id=related_swap_id,
    )
    await notification.insert()
    return notification


@router.get("")
async def get_notifications(current_user: User = Depends(get_current_user)):
    try:
        notifications = await Notification.find(
            {"user_id": current_user.id}
        ).sort("-created_at").to_list()

        return jsonable_encoder([
            notification.to_dict_safe()
            for notification in notifications
        ])
    except Exception as exc:
        logger.error(f"Get notifications error: {exc}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get notifications",
        )


@router.put("/read/{notification_id}")
async def mark_notification_read(
    notification_id: str,
    current_user: User = Depends(get_current_user),
):
    try:
        notification = await Notification.get(_object_id(notification_id, "notification_id"))
        if not notification:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Notification not found",
            )

        if str(notification.user_id) != str(current_user.id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have access to this notification",
            )

        notification.is_read = True
        await notification.save()
        return jsonable_encoder(notification.to_dict_safe())
    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"Mark notification read error: {exc}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to mark notification as read",
        )


@router.put("/read-all")
async def mark_all_notifications_read(current_user: User = Depends(get_current_user)):
    try:
        notifications = await Notification.find(
            {"user_id": current_user.id, "is_read": False}
        ).to_list()

        for notification in notifications:
            notification.is_read = True
            await notification.save()

        return jsonable_encoder({"message": "All notifications marked as read"})
    except Exception as exc:
        logger.error(f"Mark all notifications read error: {exc}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to mark notifications as read",
        )


@router.delete("/clear-all")
async def clear_all_notifications(current_user: User = Depends(get_current_user)):
    try:
        notifications = await Notification.find({"user_id": current_user.id}).to_list()
        for notification in notifications:
            await notification.delete()

        return jsonable_encoder({"message": "All notifications cleared"})
    except Exception as exc:
        logger.error(f"Clear all notifications error: {exc}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to clear notifications",
        )


@router.delete("/{notification_id}")
async def delete_notification(
    notification_id: str,
    current_user: User = Depends(get_current_user),
):
    try:
        notification = await Notification.get(_object_id(notification_id, "notification_id"))
        if not notification:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Notification not found",
            )

        if str(notification.user_id) != str(current_user.id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have access to this notification",
            )

        await notification.delete()
        return jsonable_encoder({"message": "Notification deleted"})
    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"Delete notification error: {exc}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete notification",
        )
