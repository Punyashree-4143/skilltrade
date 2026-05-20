from fastapi import HTTPException, status, Depends
from typing import List, Optional, Dict, Any
import logging

from app.models.swap_request import SwapRequest, SwapStatus, SkillDetail
from app.models.user import User
from app.schemas.swap import (
    SwapRequestCreate, SwapRequestUpdate, SwapRequestResponse,
    SwapRequestWithUsers, SwapRequestList, SwapFilterQuery,
    SwapScheduleUpdate, SwapCompletion, SwapMessageAdd,
    SwapMessageList, SwapStatsResponse, SwapActivitySummary
)
from app.utils.exceptions import (
    ValidationError, NotFoundError, ConflictError,
    BusinessLogicError, create_swap_not_found_error,
    create_unauthorized_swap_access_error, create_swap_already_exists_error,
    create_invalid_swap_status_error, create_swap_not_completed_error
)
from app.utils.logging import get_logger
from app.middleware.auth_middleware import get_current_user

logger = get_logger(__name__)


async def _create_notification_safe(
    user_id,
    notification_type: str,
    title: str,
    message: str,
    related_user_id=None,
    related_swap_id=None,
    dedupe: bool = False,
):
    try:
        from app.routes.notification_routes import create_notification

        await create_notification(
            user_id=user_id,
            notification_type=notification_type,
            title=title,
            message=message,
            related_user_id=related_user_id,
            related_swap_id=related_swap_id,
            dedupe=dedupe,
        )
    except Exception as exc:
        logger.error(f"Notification creation failed: {exc}")


class SwapController:
    """Swap request controller"""
    
    @staticmethod
    async def create_swap_request(
        swap_data: SwapRequestCreate,
        current_user: User
    ) -> SwapRequestWithUsers:
        """Create a new swap request"""
        try:
            # Check if trying to send to self
            if swap_data.receiver_id == str(current_user.id):
                raise ValidationError("Cannot send swap request to yourself")
            
            # Check if receiver exists
            print("=== RECEIVER LOOKUP ===")
            print(f"Looking for receiver ID: {swap_data.receiver_id}")
            
            try:
                from bson import ObjectId
                receiver = await User.find_one({
                    "_id": ObjectId(swap_data.receiver_id)
                })
                print(f"Receiver found: {receiver.email if receiver else 'NOT FOUND'}")
            except Exception as e:
                print(f"Receiver lookup error: {str(e)}")
                raise create_user_not_found_error(swap_data.receiver_id)
            
            if not receiver:
                raise create_user_not_found_error(swap_data.receiver_id)
            
            # Check for existing active requests
            existing_request = await SwapRequest.find_one({
                "sender": current_user.id,
                "receiver": receiver.id,
                "status": {"$in": [SwapStatus.PENDING, SwapStatus.ACCEPTED]}
            })
            
            if existing_request:
                raise create_swap_already_exists_error(
                    str(current_user.id),
                    swap_data.receiver_id
                )
            
            # Create skill details
            offered_skill = SkillDetail(
                skill=swap_data.offered_skill.skill,
                category=swap_data.offered_skill.category,
                description=swap_data.offered_skill.description
            )
            
            requested_skill = SkillDetail(
                skill=swap_data.requested_skill.skill,
                category=swap_data.requested_skill.category,
                description=swap_data.requested_skill.description
            )
            
            # Create swap request
            print("=== SWAP CREATION DEBUG ===")
            print("Current User (Sender):", current_user.email)
            print("Current User ID:", str(current_user.id))
            print("Receiver User:", receiver.email)
            print("Receiver User ID:", str(receiver.id))
            print("Receiver ID from payload:", swap_data.receiver_id)
            
            swap_request = SwapRequest(
                sender=current_user,
                receiver=receiver,
                offered_skill=offered_skill,
                requested_skill=requested_skill,
                message=swap_data.message,
                proposed_duration=swap_data.proposed_duration,
                status=SwapStatus.PENDING
            )
            
            print("=== SWAP OBJECT CREATED ===")
            print(f"Swap Request Sender: {swap_request.sender}")
            print(f"Swap Request Receiver: {swap_request.receiver}")
            
            print(f"Swap object created: {swap_request}")
            
            # Calculate match score
            print("=== CALCULATING MATCH SCORE ===")
            await swap_request.calculate_match_score()
            print("Match score calculated")
            
            # Save swap request
            print("=== SAVING SWAP REQUEST ===")
            await swap_request.save()
            print("Swap request saved successfully")

            await _create_notification_safe(
                user_id=receiver.id,
                notification_type="swap_request",
                title="New Swap Request",
                message=f"{current_user.name} sent you a swap request.",
                related_user_id=current_user.id,
                related_swap_id=swap_request.id,
                dedupe=True,
            )

            if swap_request.match_score and swap_request.match_score >= 50:
                await _create_notification_safe(
                    user_id=current_user.id,
                    notification_type="new_match",
                    title="New Skill Match",
                    message=f"You have a new skill match with {receiver.name}.",
                    related_user_id=receiver.id,
                    related_swap_id=swap_request.id,
                    dedupe=True,
                )
                await _create_notification_safe(
                    user_id=receiver.id,
                    notification_type="new_match",
                    title="New Skill Match",
                    message=f"You have a new skill match with {current_user.name}.",
                    related_user_id=current_user.id,
                    related_swap_id=swap_request.id,
                    dedupe=True,
                )
            
            # Users are already embedded, no need to populate
            print("=== SWAP SAVED SUCCESSFULLY ===")
            print(f"Swap ID: {swap_request.id}")
            print(f"Sender: {current_user.email}")
            print(f"Receiver: {receiver.email}")
            print(f"Status: {swap_request.status}")
            logger.info(f"Swap request created: {current_user.email} -> {receiver.email}")
            
            print("=== SWAP REQUEST COMPLETED SUCCESSFULLY ===")
            print("=== BUILDING RESPONSE OBJECT ===")
            
            # Create properly serialized response
            response_data = {
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
                "offered_skill": swap_request.offered_skill.model_dump(),
                "requested_skill": swap_request.requested_skill.model_dump(),
                "message": swap_request.message,
                "status": swap_request.status,
                "proposed_duration": swap_request.proposed_duration,
                "match_score": swap_request.match_score,
                "created_at": swap_request.created_at,
                "updated_at": swap_request.updated_at,
            }
            
            print("=== RESPONSE OBJECT CREATED ===")
            print(f"Response data: {response_data}")
            print(f"Response type: {type(response_data)}")
            print(f"Response keys: {list(response_data.keys())}")
            
            return response_data
            
        except (ValidationError, ConflictError, NotFoundError):
            raise
        except Exception as e:
            print("\n=== SWAP CREATION EXCEPTION ===")
            print(f"Error: {str(e)}")
            print(f"Error type: {type(e)}")
            import traceback
            print("=== TRACEBACK ===")
            traceback.print_exc()
            
            logger.error(f"Create swap request error: {str(e)}")
            raise ValidationError("Failed to create swap request")
    
    @staticmethod
    async def get_swap_requests(
        current_user: User,
        request_type: str = "all"
    ) -> list:
        """Get swap requests with safe Python filtering"""
        try:
            print("=== FETCHING SWAPS ===")
            print(f"Current user: {current_user.email}")
            print(f"Request type: {request_type}")
            
            # FETCH EVERYTHING
            all_swaps = await SwapRequest.find_all().to_list()
            
            # STEP 1 — FETCH LINKS PROPERLY
            for swap in all_swaps:
                try:
                    await swap.fetch_link("sender")
                    await swap.fetch_link("receiver")
                    
                    print("=== POPULATED SWAP ===")
                    print(f"Swap ID: {swap.id}")
                    print("Sender:", swap.sender)
                    print("Receiver:", swap.receiver)
                    print("Sender Name:", swap.sender.name if swap.sender else "None")
                    print("Receiver Name:", swap.receiver.name if swap.receiver else "None")
                except Exception as fetch_error:
                    print(f"Error populating swap {swap.id}: {fetch_error}")
                    continue
            
            # SORT IN PYTHON if needed
            all_swaps.sort(
                key=lambda x: x.created_at,
                reverse=True
            )
            
            print(f"Total swaps in DB: {len(all_swaps)}")
            
            # FILTER IN PYTHON USING USER IDs (reliable for Link[User])
            filtered_swaps = []
            
            for swap in all_swaps:
                try:
                    # Links already fetched above
                    sender_id = str(swap.sender.id)
                    receiver_id = str(swap.receiver.id)
                    current_user_id = str(current_user.id)
                    
                    # VERIFY FETCHED SWAP
                    print("=== FETCHED SWAP ===")
                    print("Swap ID:", str(swap.id))
                    print("Sender:", swap.sender.email if swap.sender else "None")
                    print("Receiver:", swap.receiver.email if swap.receiver else "None")
                    print("Sender ID:", str(swap.sender.id) if swap.sender else "None")
                    print("Receiver ID:", str(swap.receiver.id) if swap.receiver else "None")
                    
                    sender_id = str(swap.sender.id)
                    receiver_id = str(swap.receiver.id)
                    current_user_id = str(current_user.id)
                    
                    print("=== SWAP CHECK ===")
                    print(f"Swap ID: {swap.id}")
                    print(f"Sender ID: {sender_id}")
                    print(f"Receiver ID: {receiver_id}")
                    print(f"Current User ID: {current_user_id}")
                    print(f"Request Type: {request_type}")
                    
                    if request_type == "received":
                        if receiver_id == current_user_id:
                            filtered_swaps.append(swap)
                            print("→ MATCH: User is receiver")
                        else:
                            print("→ NO MATCH: User is not receiver")
                            
                    elif request_type == "sent":
                        if sender_id == current_user_id:
                            filtered_swaps.append(swap)
                            print("→ MATCH: User is sender")
                        else:
                            print("→ NO MATCH: User is not sender")
                            
                    else:  # all
                        if sender_id == current_user_id or receiver_id == current_user_id:
                            filtered_swaps.append(swap)
                            print("→ MATCH: User is sender or receiver")
                        else:
                            print("→ NO MATCH: User is neither sender nor receiver")
                        
                except Exception as fetch_error:
                    print("=== FILTER ERROR ===")
                    print(f"Error filtering swap {swap.id}: {fetch_error}")
                    continue
            
            print(f"=== FILTERED SWAPS ===")
            print(f"Total filtered swaps: {len(filtered_swaps)}")
            
            # Apply pending filter if needed
            if request_type == "pending":
                swaps = [
                    swap for swap in filtered_swaps
                    if str(swap.status).lower() == "pending"
                ]
                print(f"Pending swaps after filtering: {len(swaps)}")
            else:
                swaps = filtered_swaps
            
            print(f"Final swaps count: {len(swaps)}")
            
            # DEBUG RAW SWAPS
            print("=== RAW SWAPS BEFORE SERIALIZATION ===")
            for i, swap in enumerate(swaps):
                print(f"Swap {i}: {swap}")
                print(f"  - ID: {swap.id}")
                print(f"  - Sender: {swap.sender}")
                print(f"  - Receiver: {swap.receiver}")
                print(f"  - Status: {swap.status}")
            
            # STEP 3 — FIX SERIALIZATION
            serialized_swaps = []
            for swap in swaps:
                try:
                    # Links already fetched above - use them directly
                    sender = swap.sender
                    receiver = swap.receiver
                    
                    serialized_swaps.append({
                        "id": str(swap.id) if swap.id else None,
                        "sender": {
                            "id": str(sender.id) if sender else None,
                            "name": sender.name if sender else "Unknown",
                            "email": sender.email if sender else "Unknown",
                        },
                        "receiver": {
                            "id": str(receiver.id) if receiver else None,
                            "name": receiver.name if receiver else "Unknown",
                            "email": receiver.email if receiver else "Unknown",
                        },
                        "status": str(swap.status) if swap.status else "pending",
                        "message": swap.message if swap.message else "",
                        "created_at": swap.created_at.isoformat() if swap.created_at else None
                    })
                except Exception as item_error:
                    print("=== SERIALIZATION ERROR ===")
                    print(f"Error serializing swap: {item_error}")
                    print(f"Swap data: {swap}")
                    # Continue with other swaps, don't crash entire request
                    continue
            
            # STEP 4 — DEBUG FINAL RESPONSE
            print("=== FINAL RESPONSE ===")
            for i, swap in enumerate(serialized_swaps):
                print(f"Serialized Swap {i}:")
                print(f"  - ID: {swap['id']}")
                print(f"  - Sender: {swap['sender']}")
                print(f"  - Receiver: {swap['receiver']}")
                print(f"  - Status: {swap['status']}")
            
            print(f"=== SERIALIZED SWAPS ===")
            print(f"Successfully serialized {len(serialized_swaps)} swaps")
            
            return serialized_swaps
            
        except Exception as e:
            import traceback
            print("=== GET SWAPS ERROR ===")
            print(str(e))
            traceback.print_exc()
            raise Exception(str(e))
    
    @staticmethod
    async def get_swap_request(
        swap_id: str,
        current_user: User
    ) -> SwapRequestWithUsers:
        """Get specific swap request"""
        try:
            swap_request = await SwapRequest.find_one({"_id": swap_id})
            
            if not swap_request:
                raise create_swap_not_found_error(swap_id)
            
            # Check if user is participant
            if (swap_request.sender.id != current_user.id and 
                swap_request.receiver.id != current_user.id):
                raise create_unauthorized_swap_access_error(swap_id, str(current_user.id))
            
            return swap_request
            
        except (NotFoundError, BusinessLogicError):
            raise
        except Exception as e:
            logger.error(f"Get swap request error: {str(e)}")
            raise ValidationError("Failed to get swap request")
    
    @staticmethod
    async def update_swap_request(
        swap_id: str,
        update_data: SwapRequestUpdate,
        current_user: User
    ) -> SwapRequestWithUsers:
        """Update swap request"""
        try:
            # STEP 1 — ADD FULL ERROR DEBUGGING
            print("=== ACCEPT/REJECT START ===")
            print("Swap ID:", swap_id)
            print("Update Data:", update_data)
            print("Current User:", current_user.email)
            
            # Get swap request
            swap_request = await SwapRequest.get(swap_id)
            if not swap_request:
                raise create_swap_not_found_error(swap_id)
            
            # FIX ACCEPT/REJECT CONTROLLER - fetch Link[User] objects
            await swap_request.fetch_link("sender")
            await swap_request.fetch_link("receiver")
            
            # Check permissions using ID comparison
            sender_id = str(swap_request.sender.id)
            receiver_id = str(swap_request.receiver.id)
            current_user_id = str(current_user.id)
            
            print("=== UPDATE SWAP DEBUG ===")
            print("Swap ID:", swap_id)
            print("Sender ID:", sender_id)
            print("Receiver ID:", receiver_id)
            print("Current User ID:", current_user_id)
            print("Update Status:", update_data.status)
            print("Current Swap Status:", swap_request.status)
            print("Current Status Type:", type(swap_request.status))
            
            is_sender = sender_id == current_user_id
            is_receiver = receiver_id == current_user_id
            
            print("Is Sender:", is_sender)
            print("Is Receiver:", is_receiver)
            
            # STEP 2 — FIX STATUS VALIDATION
            if update_data.status:
                # STEP 3 — VERIFY RECEIVER CHECK
                if not is_receiver:
                    raise HTTPException(
                        status_code=403,
                        detail="Only receiver can update this swap"
                    )
                
                # STEP 4 — SAVE STATUS with SAFE comparison
                current_status = str(swap_request.status).lower()
                new_status_str = str(update_data.status).lower()
                
                print("Current Status:", current_status)
                print("New Status:", new_status_str)
                
                # STEP 5 — RETURN DEBUG
                print("=== UPDATING SWAP ===")
                print("Swap ID:", swap_request.id)
                print("Old Status:", swap_request.status)
                print("New Status:", update_data.status)
                
                # Update status
                if new_status_str == "accepted":
                    swap_request.status = SwapStatus.ACCEPTED
                elif new_status_str == "rejected":
                    swap_request.status = SwapStatus.REJECTED
                elif new_status_str == "cancelled":
                    swap_request.status = SwapStatus.CANCELLED
                elif new_status_str == "completed":
                    swap_request.status = SwapStatus.COMPLETED
                else:
                    swap_request.status = update_data.status
            
            # Update fields
            if update_data.status:
                swap_request.status = update_data.status
            
            if update_data.scheduled_date:
                swap_request.scheduled_date = update_data.scheduled_date
            
            if update_data.scheduled_time:
                swap_request.scheduled_time = update_data.scheduled_time
            
            if update_data.location_type:
                swap_request.location_type = update_data.location_type
            
            if update_data.meeting_details:
                swap_request.meeting_details = update_data.meeting_details
            
            if update_data.completion_notes:
                swap_request.completion_notes = update_data.completion_notes
            
            # Add message if provided
            if update_data.message:
                await swap_request.add_message(current_user, update_data.message)
            
            # Save changes
            swap_request.updated_at = datetime.utcnow()
            await swap_request.save()

            final_status = (
                swap_request.status.value
                if hasattr(swap_request.status, "value")
                else str(swap_request.status).replace("SwapStatus.", "").lower()
            )

            if final_status == "accepted":
                await _create_notification_safe(
                    user_id=swap_request.sender.id,
                    notification_type="swap_accepted",
                    title="Swap Accepted",
                    message=f"{swap_request.receiver.name} accepted your swap request.",
                    related_user_id=swap_request.receiver.id,
                    related_swap_id=swap_request.id,
                    dedupe=True,
                )
            elif final_status == "rejected":
                await _create_notification_safe(
                    user_id=swap_request.sender.id,
                    notification_type="swap_rejected",
                    title="Swap Rejected",
                    message=f"{swap_request.receiver.name} rejected your swap request.",
                    related_user_id=swap_request.receiver.id,
                    related_swap_id=swap_request.id,
                    dedupe=True,
                )
            
            print("=== SWAP UPDATED SUCCESSFULLY ===")
            print("Final Status:", swap_request.status)
            
            # Users are already embedded, no need to populate
            logger.info(f"Swap request updated: {swap_id} - {update_data.status}")
            
            # FIX ResponseValidationError - return JSON-safe data
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
                    "category": str(swap_request.offered_skill.category),
                    "description": swap_request.offered_skill.description,
                },
                
                "requested_skill": {
                    "skill": swap_request.requested_skill.skill,
                    "category": str(swap_request.requested_skill.category),
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
            
        except (NotFoundError, BusinessLogicError):
            raise
        except Exception as e:
            # STEP 1 — ADD FULL ERROR DEBUGGING
            import traceback
            print("=== ACCEPT/REJECT ERROR ===")
            print(str(e))
            traceback.print_exc()
            raise ValidationError("Failed to update swap request")
    
    @staticmethod
    async def add_message_to_swap(
        swap_id: str,
        message_data: SwapMessageAdd,
        current_user: User
    ) -> SwapRequestWithUsers:
        """Add message to swap request"""
        try:
            # Get swap request
            swap_request = await SwapRequest.get(swap_id)
            if not swap_request:
                raise create_swap_not_found_error(swap_id)
            
            # Check if user is participant
            if (swap_request.sender.id != current_user.id and 
                swap_request.receiver.id != current_user.id):
                raise create_unauthorized_swap_access_error(swap_id, str(current_user.id))
            
            # Add message
            await swap_request.add_message(current_user, message_data.content)
            
            # Users are already embedded, no need to populate
            return swap_request
            
        except (NotFoundError, BusinessLogicError):
            raise
        except Exception as e:
            logger.error(f"Add message to swap error: {str(e)}")
            raise ValidationError("Failed to add message to swap")
    
    @staticmethod
    async def mark_swap_messages_read(
        swap_id: str,
        current_user: User
    ) -> Dict[str, str]:
        """Mark messages as read"""
        try:
            # Get swap request
            swap_request = await SwapRequest.get(swap_id)
            if not swap_request:
                raise create_swap_not_found_error(swap_id)
            
            # Check if user is participant
            if (swap_request.sender.id != current_user.id and 
                swap_request.receiver.id != current_user.id):
                raise create_unauthorized_swap_access_error(swap_id, str(current_user.id))
            
            # Mark messages as read
            await swap_request.mark_messages_as_read(current_user)
            
            return {"message": "Messages marked as read"}
            
        except (NotFoundError, BusinessLogicError):
            raise
        except Exception as e:
            logger.error(f"Mark messages as read error: {str(e)}")
            raise ValidationError("Failed to mark messages as read")
    
    @staticmethod
    async def get_swap_stats(current_user: User) -> SwapStatsResponse:
        """Get swap statistics"""
        try:
            # Get swap statistics
            stats = await SwapRequest.aggregate([
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
                        "_id": "$status",
                        "count": {"$sum": 1}
                    }
                }
            ])
            
            # Calculate totals
            total_requests = 0
            pending_requests = 0
            accepted_requests = 0
            completed_swaps = 0
            rejected_requests = 0
            cancelled_requests = 0
            
            for stat in stats:
                status = stat["_id"]
                count = stat["count"]
                total_requests += count
                
                if status == SwapStatus.PENDING:
                    pending_requests = count
                elif status == SwapStatus.ACCEPTED:
                    accepted_requests = count
                elif status == SwapStatus.COMPLETED:
                    completed_swaps = count
                elif status == SwapStatus.REJECTED:
                    rejected_requests = count
                elif status == SwapStatus.CANCELLED:
                    cancelled_requests = count
            
            # Calculate success rate
            success_rate = (completed_swaps / total_requests * 100) if total_requests > 0 else 0.0
            
            # Calculate average duration (placeholder)
            average_duration = None
            
            return SwapStatsResponse(
                total_requests=total_requests,
                pending_requests=pending_requests,
                accepted_requests=accepted_requests,
                completed_swaps=completed_swaps,
                rejected_requests=rejected_requests,
                cancelled_requests=cancelled_requests,
                success_rate=round(success_rate, 1),
                total_duration=0,  # Would be calculated from actual data
                average_duration=average_duration
            )
            
        except Exception as e:
            logger.error(f"Get swap stats error: {str(e)}")
            raise ValidationError("Failed to get swap statistics")
    
    @staticmethod
    async def get_swap_activity(current_user: User) -> SwapActivitySummary:
        """Get swap activity summary"""
        try:
            # Get recent swaps
            recent_swaps = await SwapRequest.find({
                "$or": [
                    {"sender": current_user.id},
                    {"receiver": current_user.id}
                ]
            }).populate("sender receiver").sort({"created_at": -1}).limit(5).to_list()
            
            # Get pending requests
            pending_requests = await SwapRequest.find({
                "receiver": current_user.id,
                "status": SwapStatus.PENDING
            }).populate("sender receiver").sort({"created_at": -1}).limit(5).to_list()
            
            # Get upcoming swaps (accepted and scheduled)
            upcoming_swaps = await SwapRequest.find({
                "$or": [
                    {"sender": current_user.id},
                    {"receiver": current_user.id}
                ],
                "status": SwapStatus.ACCEPTED,
                "scheduled_date": {"$exists": True}
            }).populate("sender receiver").sort({"scheduled_date": 1}).limit(5).to_list()
            
            # Calculate unread messages count
            unread_messages = 0
            for swap in pending_requests:
                unread_messages += len([msg for msg in swap.messages if not msg.read and msg.sender.id != current_user.id])
            
            return SwapActivitySummary(
                recent_swaps=recent_swaps,
                pending_requests=pending_requests,
                unread_messages=unread_messages,
                upcoming_swaps=upcoming_swaps
            )
            
        except Exception as e:
            logger.error(f"Get swap activity error: {str(e)}")
            raise ValidationError("Failed to get swap activity")
    
    @staticmethod
    def _is_valid_status_transition(current_status: SwapStatus, new_status: SwapStatus) -> bool:
        """Check if status transition is valid"""
        valid_transitions = {
            SwapStatus.PENDING: [SwapStatus.ACCEPTED, SwapStatus.REJECTED, SwapStatus.CANCELLED],
            SwapStatus.ACCEPTED: [SwapStatus.COMPLETED, SwapStatus.CANCELLED],
            SwapStatus.REJECTED: [SwapStatus.CANCELLED],
            SwapStatus.COMPLETED: [],  # Terminal state
            SwapStatus.CANCELLED: []   # Terminal state
        }
        
        return new_status in valid_transitions.get(current_status, [])


# Import datetime for use in controller
from datetime import datetime
