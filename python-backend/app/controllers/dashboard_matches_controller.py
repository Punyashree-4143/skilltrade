"""
Dashboard Matches Controller for SkillTrade
Handles real user matching and recommendations
"""

from typing import Dict, Any, List
from app.models.user import User
from app.models.swap_request import SwapRequest
from fastapi import HTTPException


class DashboardMatchesController:
    """Controller for dashboard matches operations"""
    
    @staticmethod
    async def get_top_matches(current_user: User, limit: int = 5) -> List[Dict[str, Any]]:
        """Get top skill matches for authenticated user"""
        try:
            print(f"=== DASHBOARD MATCHES FOR USER ===")
            print(f"User ID: {current_user.id}")
            print(f"User Email: {current_user.email}")
            print(f"User Skills Offered: {current_user.skills_offered}")
            print(f"User Skills Wanted: {current_user.skills_wanted}")
            
            # Get all users except current user
            all_users = await User.find_all().to_list()
            other_users = [user for user in all_users if str(user.id) != str(current_user.id)]
            
            matches = []
            
            for user in other_users:
                try:
                    # Calculate match score based on skill compatibility
                    match_score = 0
                    matching_skills = []
                    
                    # Check if current user's offered skills match other user's wanted skills
                    if current_user.skills_offered and user.skills_wanted:
                        for skill in current_user.skills_offered:
                            if skill in user.skills_wanted:
                                match_score += 25
                                matching_skills.append(skill)
                    
                    # Check if current user's wanted skills match other user's offered skills
                    if current_user.skills_wanted and user.skills_offered:
                        for skill in current_user.skills_wanted:
                            if skill in user.skills_offered:
                                match_score += 25
                                matching_skills.append(skill)
                    
                    # Only include users with some skill compatibility
                    if match_score > 0:
                        # Get recent swap history between users (if any)
                        swap_history = await SwapRequest.find({
                            "$or": [
                                {"sender": current_user.id, "receiver": user.id},
                                {"sender": user.id, "receiver": current_user.id}
                            ]
                        }).to_list()
                        
                        match_data = {
                            "id": str(user.id),
                            "name": user.name,
                            "email": user.email,
                            "avatar": user.avatar_url if hasattr(user, 'avatar_url') else None,
                            "location": user.location if hasattr(user, 'location') else None,
                            "rating": user.rating if hasattr(user, 'rating') else 0.0,
                            "skills_offered": user.skills_offered or [],
                            "skills_wanted": user.skills_wanted or [],
                            "matching_skills": list(set(matching_skills)),
                            "match_score": min(match_score, 100),  # Cap at 100
                            "previous_swaps": len(swap_history),
                            "last_swap_date": None
                        }
                        
                        # Get last swap date if exists
                        if swap_history:
                            latest_swap = max(swap_history, key=lambda x: x.created_at or datetime.min)
                            match_data["last_swap_date"] = latest_swap.created_at.isoformat() if latest_swap.created_at else None
                        
                        matches.append(match_data)
                        print(f"Found match: {user.name} (Score: {match_score})")
                        
                except Exception as e:
                    print(f"Error processing match for user {user.id}: {e}")
                    continue
            
            # Sort by match score (highest first)
            matches.sort(key=lambda x: x["match_score"], reverse=True)
            
            # Limit results
            top_matches = matches[:limit]
            
            print(f"=== MATCHES RESULT ===")
            print(f"Found {len(top_matches)} top matches")
            for match in top_matches:
                print(f"- {match['name']}: {match['match_score']}% match")
            
            return top_matches
            
        except Exception as e:
            print(f"Error getting dashboard matches: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Failed to get dashboard matches"
            )
