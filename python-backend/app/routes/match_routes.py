from typing import Dict, List, Set

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.encoders import jsonable_encoder

from app.middleware.auth_middleware import get_current_user
from app.models.user import User
from app.utils.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/api/matches", tags=["Matches"])


def _normalize_skill(skill: str) -> str:
    return str(skill or "").strip().lower()


def _skill_lookup(skills: List[str]) -> Dict[str, str]:
    lookup = {}
    for skill in skills or []:
        normalized = _normalize_skill(skill)
        if normalized:
            lookup[normalized] = str(skill).strip()
    return lookup


def _match_type(score: int) -> str:
    if score >= 90:
        return "excellent"
    if score >= 70:
        return "good"
    return "potential"


def _user_payload(user: User) -> dict:
    return {
        "id": str(user.id),
        "name": user.name,
        "email": str(user.email),
        "avatar": user.avatar,
        "bio": user.bio,
        "location": user.location,
        "experience_level": user.experience_level,
        "rating": user.rating,
        "total_reviews": user.total_reviews,
        "is_online": user.is_online,
        "skills_offered": user.skills_offered or [],
        "skills_wanted": user.skills_wanted or [],
    }


@router.get("")
async def get_matches(current_user: User = Depends(get_current_user)):
    try:
        current_wanted = _skill_lookup(current_user.skills_wanted or [])
        current_offered = _skill_lookup(current_user.skills_offered or [])
        total_skills = len(set(current_wanted.keys()) | set(current_offered.keys()))

        if total_skills == 0:
            return jsonable_encoder([])

        users = await User.find_all().to_list()
        matches = []

        for other_user in users:
            if str(other_user.id) == str(current_user.id):
                continue

            other_offered = _skill_lookup(other_user.skills_offered or [])
            other_wanted = _skill_lookup(other_user.skills_wanted or [])

            wanted_matches: Set[str] = set(current_wanted.keys()) & set(other_offered.keys())
            offered_matches: Set[str] = set(current_offered.keys()) & set(other_wanted.keys())
            all_matched_keys = wanted_matches | offered_matches

            if not all_matched_keys:
                continue

            match_percentage = int((len(all_matched_keys) / total_skills) * 100)
            if match_percentage < 50:
                continue

            matching_skills = [
                current_wanted.get(skill)
                or current_offered.get(skill)
                or other_offered.get(skill)
                or other_wanted.get(skill)
                for skill in sorted(all_matched_keys)
            ]

            matches.append({
                "user": _user_payload(other_user),
                "match_percentage": min(match_percentage, 100),
                "match_type": _match_type(match_percentage),
                "matching_skills": matching_skills,
                "wanted_skill_matches": [
                    current_wanted[skill] for skill in sorted(wanted_matches)
                ],
                "offered_skill_matches": [
                    current_offered[skill] for skill in sorted(offered_matches)
                ],
            })

        matches.sort(key=lambda item: item["match_percentage"], reverse=True)
        return jsonable_encoder(matches)
    except Exception as exc:
        logger.error(f"Get matches error: {exc}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get matches",
        )
