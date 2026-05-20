"""
Dashboard Controller for SkillTrade.
Calculates authenticated user dashboard statistics from MongoDB.
"""

from typing import Any, Dict

from fastapi import HTTPException

from app.models.message import Message
from app.models.notification import Notification
from app.models.swap_request import SwapRequest
from app.models.user import User


def _normalize_skill(skill: str) -> str:
    return str(skill or "").strip().lower()


def _skill_set(skills) -> set:
    return {
        normalized
        for normalized in (_normalize_skill(skill) for skill in (skills or []))
        if normalized
    }


def _status_value(status) -> str:
    if hasattr(status, "value"):
        return status.value
    return str(status or "").replace("SwapStatus.", "").lower()


class DashboardController:
    """Controller for dashboard operations."""

    @staticmethod
    async def get_user_dashboard_stats(current_user: User) -> Dict[str, Any]:
        """Get dashboard statistics for the authenticated user."""
        try:
            all_swaps = await SwapRequest.find_all().to_list()
            user_swaps = []

            for swap in all_swaps:
                try:
                    await swap.fetch_link("sender")
                    await swap.fetch_link("receiver")

                    sender_id = str(swap.sender.id)
                    receiver_id = str(swap.receiver.id)
                    current_user_id = str(current_user.id)

                    if sender_id == current_user_id or receiver_id == current_user_id:
                        user_swaps.append(swap)
                except Exception:
                    continue

            total_swaps = len(user_swaps)
            pending_swaps = 0
            active_swaps = 0
            completed_swaps = 0
            cancelled_swaps = 0

            for swap in user_swaps:
                status = _status_value(swap.status)

                if status == "pending":
                    pending_swaps += 1
                elif status == "accepted":
                    active_swaps += 1
                elif status == "completed":
                    completed_swaps += 1
                elif status in ["cancelled", "rejected"]:
                    cancelled_swaps += 1

            success_rate = int((completed_swaps / total_swaps) * 100) if total_swaps else 0

            unread_messages = await Message.find(
                {
                    "receiver_id": current_user.id,
                    "is_read": False,
                }
            ).count()

            unread_notifications = await Notification.find(
                {
                    "user_id": current_user.id,
                    "is_read": False,
                }
            ).count()

            current_wanted = _skill_set(current_user.skills_wanted)
            current_offered = _skill_set(current_user.skills_offered)
            total_matchable_skills = len(current_wanted | current_offered)
            matches_count = 0

            if total_matchable_skills:
                users = await User.find_all().to_list()

                for user in users:
                    if str(user.id) == str(current_user.id):
                        continue

                    wanted_matches = current_wanted & _skill_set(user.skills_offered)
                    offered_matches = current_offered & _skill_set(user.skills_wanted)
                    matched_skills = wanted_matches | offered_matches
                    match_percentage = int((len(matched_skills) / total_matchable_skills) * 100)

                    if match_percentage >= 50:
                        matches_count += 1

            profile_views = 0

            return {
                "matches": matches_count,
                "total_swaps": total_swaps,
                "pending_swaps": pending_swaps,
                "active_swaps": active_swaps,
                "accepted_swaps": active_swaps,
                "completed_swaps": completed_swaps,
                "cancelled_swaps": cancelled_swaps,
                "success_rate": success_rate,
                "unread_messages": unread_messages,
                "unread_notifications": unread_notifications,
                "profile_views": profile_views,
            }
        except Exception as exc:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to get dashboard statistics: {exc}",
            )
