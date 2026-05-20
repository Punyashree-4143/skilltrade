"""
Dashboard Activities Controller for SkillTrade
Handles real user activity tracking and display
"""

from typing import Dict, Any, List
from datetime import datetime
from app.models.swap_request import SwapRequest, SwapStatus
from app.models.user import User
from fastapi import HTTPException


class DashboardActivitiesController:
    """Controller for dashboard activities operations"""
    
    @staticmethod
    async def get_user_activities(current_user: User, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent activities for authenticated user"""
        try:
            print(f"=== DASHBOARD ACTIVITIES FOR USER ===")
            print(f"User ID: {current_user.id}")
            print(f"User Email: {current_user.email}")
            
            # Get all swaps where user is sender OR receiver
            all_swaps = await SwapRequest.find_all().to_list()
            
            # Filter swaps for current user and sort by creation date
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
                        
                except Exception as e:
                    print(f"Error processing swap {swap.id}: {e}")
                    continue
            
            # Sort by creation date (newest first)
            user_swaps.sort(key=lambda x: x.created_at or datetime.min, reverse=True)
            
            # Generate activities from swaps
            activities = []
            for swap in user_swaps[:limit]:
                try:
                    sender_id = str(swap.sender.id)
                    receiver_id = str(swap.receiver.id)
                    current_user_id = str(current_user.id)
                    
                    is_sender = sender_id == current_user_id
                    is_receiver = receiver_id == current_user_id
                    
                    # Get status safely
                    status_str = str(swap.status).lower()
                    if 'swapstatus.' in status_str:
                        status_str = status_str.replace('swapstatus.', '')
                    
                    # Generate activity based on status and user role
                    activity = {
                        "type": "swap_created",
                        "message": "",
                        "timestamp": swap.created_at.isoformat() if swap.created_at else datetime.utcnow().isoformat(),
                        "swap_id": str(swap.id),
                        "other_user": {
                            "id": str(swap.receiver.id if is_sender else swap.sender.id),
                            "name": swap.receiver.name if is_sender else swap.sender.name,
                            "email": swap.receiver.email if is_sender else swap.sender.email
                        }
                    }
                    
                    if 'pending' in status_str:
                        if is_sender:
                            activity["type"] = "swap_sent"
                            activity["message"] = f"You sent a swap request to {activity['other_user']['name']}"
                        else:
                            activity["type"] = "swap_received"
                            activity["message"] = f"{activity['other_user']['name']} sent you a swap request"
                    
                    elif 'accepted' in status_str:
                        if is_sender:
                            activity["type"] = "swap_accepted_by_receiver"
                            activity["message"] = f"{activity['other_user']['name']} accepted your swap request"
                        else:
                            activity["type"] = "swap_accepted_by_sender"
                            activity["message"] = f"You accepted {activity['other_user']['name']}'s swap request"
                    
                    elif 'completed' in status_str:
                        activity["type"] = "swap_completed"
                        if is_sender:
                            activity["message"] = f"Swap with {activity['other_user']['name']} completed"
                        else:
                            activity["message"] = f"Swap with {activity['other_user']['name']} completed"
                    
                    elif 'cancelled' in status_str or 'rejected' in status_str:
                        if is_sender:
                            activity["type"] = "swap_cancelled"
                            activity["message"] = f"Swap with {activity['other_user']['name']} was cancelled"
                        else:
                            activity["type"] = "swap_rejected"
                            activity["message"] = f"You cancelled swap with {activity['other_user']['name']}"
                    
                    # Use updated_at for status changes if available and recent
                    if swap.updated_at and swap.updated_at != swap.created_at:
                        activity["timestamp"] = swap.updated_at.isoformat()
                    
                    activities.append(activity)
                    print(f"Generated activity: {activity['type']} - {activity['message']}")
                    
                except Exception as e:
                    print(f"Error generating activity for swap {swap.id}: {e}")
                    continue
            
            # Sort by timestamp (newest first)
            activities.sort(key=lambda x: x["timestamp"], reverse=True)
            
            print(f"=== ACTIVITIES RESULT ===")
            print(f"Generated {len(activities)} activities")
            
            return activities
            
        except Exception as e:
            print(f"Error getting dashboard activities: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Failed to get dashboard activities"
            )
