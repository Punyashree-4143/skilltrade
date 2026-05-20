"""
Swap Completion Controller for SkillTrade
Handles marking swaps as completed
"""

from typing import Dict, Any
from datetime import datetime
from app.models.swap_request import SwapRequest, SwapStatus
from app.models.user import User
from fastapi import HTTPException


class SwapCompletionController:
    """Controller for swap completion operations"""
    
    @staticmethod
    async def complete_swap_request(
        swap_id: str,
        current_user: User
    ) -> Dict[str, Any]:
        """Mark a swap request as completed"""
        try:
            print(f"=== SWAP COMPLETION START ===")
            print(f"Swap ID: {swap_id}")
            print(f"Current User: {current_user.email}")
            print(f"Current User ID: {current_user.id}")
            
            # Get swap request
            swap_request = await SwapRequest.get(swap_id)
            if not swap_request:
                raise HTTPException(
                    status_code=404,
                    detail="Swap request not found"
                )
            
            # Fetch sender and receiver links
            await swap_request.fetch_link("sender")
            await swap_request.fetch_link("receiver")
            
            # Check permissions - user must be sender or receiver
            sender_id = str(swap_request.sender.id)
            receiver_id = str(swap_request.receiver.id)
            current_user_id = str(current_user.id)
            
            print(f"=== PERMISSION CHECK ===")
            print(f"Sender ID: {sender_id}")
            print(f"Receiver ID: {receiver_id}")
            print(f"Current User ID: {current_user_id}")
            
            is_sender = sender_id == current_user_id
            is_receiver = receiver_id == current_user_id
            
            if not (is_sender or is_receiver):
                raise HTTPException(
                    status_code=403,
                    detail="Only participants can mark swap as completed"
                )
            
            # Check if swap is currently accepted
            current_status = str(swap_request.status).lower()
            print(f"Current Status: {current_status}")
            
            if 'accepted' not in current_status:
                raise HTTPException(
                    status_code=400,
                    detail="Only accepted swaps can be marked as completed"
                )
            
            # Mark as completed
            print(f"=== MARKING AS COMPLETED ===")
            swap_request.status = SwapStatus.COMPLETED
            swap_request.updated_at = datetime.utcnow()
            
            await swap_request.save()
            
            print(f"=== SWAP COMPLETED SUCCESSFULLY ===")
            print(f"Final Status: {swap_request.status}")
            
            # Return JSON-safe response
            return {
                "id": str(swap_request.id),
                
                "sender_id": str(swap_request.sender.id),
                "receiver_id": str(swap_request.receiver.id),
                
                "sender": {
                    "id": str(swap_request.sender.id),
                    "name": swap_request.sender.name,
                    "email": swap_request.sender.email,
                },
                
                "receiver": {
                    "id": str(swap_request.receiver.id),
                    "name": swap_request.receiver.name,
                    "email": swap_request.receiver.email,
                },
                
                "offered_skill": {
                    "skill": swap_request.offered_skill.skill,
                    "category": swap_request.offered_skill.category.value,
                    "description": swap_request.offered_skill.description,
                },
                
                "requested_skill": {
                    "skill": swap_request.requested_skill.skill,
                    "category": swap_request.requested_skill.category.value,
                    "description": swap_request.requested_skill.description,
                },
                
                "message": swap_request.message,
                "proposed_duration": swap_request.proposed_duration,
                
                "status": swap_request.status.value if hasattr(swap_request.status, 'value') else str(swap_request.status),
                
                "messages": [
                    {
                        "id": str(index),
                        "sender_id": str(msg.sender.id),
                        "content": msg.content,
                        "timestamp": msg.timestamp.isoformat(),
                        "read": msg.read,
                    }
                    for index, msg in enumerate(swap_request.messages)
                ],
                
                "created_at": swap_request.created_at.isoformat() if swap_request.created_at else None,
                "updated_at": swap_request.updated_at.isoformat() if hasattr(swap_request, 'updated_at') and swap_request.updated_at else None,
            }
            
        except HTTPException:
            raise
        except Exception as e:
            print(f"Error completing swap request: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Failed to complete swap request"
            )
