from fastapi import HTTPException, status, Depends
from typing import List, Optional, Dict, Any
import logging

from app.models.review import Review
from app.models.swap_request import SwapRequest
from app.models.user import User
from app.schemas.review import (
    ReviewCreate, ReviewUpdate, ReviewResponse, ReviewWithUsers,
    ReviewList, ReviewFilterQuery, ReviewStats, ReviewReport,
    ReviewResponseCreate, UserReviewSummary, ReviewActivity
)
from app.utils.exceptions import (
    ValidationError, NotFoundError, ConflictError,
    BusinessLogicError, create_review_not_found_error,
    create_review_already_exists_error, create_swap_not_completed_error,
    create_unauthorized_swap_access_error
)
from app.utils.helpers import paginate_query, calculate_pagination_info
from app.utils.logging import get_logger
from app.middleware.auth_middleware import get_current_user

logger = get_logger(__name__)


class ReviewController:
    """Review controller"""
    
    @staticmethod
    async def create_review(
        review_data: ReviewCreate,
        current_user: User
    ) -> ReviewWithUsers:
        """Create a new review"""
        try:
            # Check if swap request exists and is completed
            swap_request = await SwapRequest.get(review_data.swap_request_id)
            if not swap_request:
                raise create_swap_not_found_error(review_data.swap_request_id)
            
            # Check if swap is completed
            if swap_request.status.value != "completed":
                raise create_swap_not_completed_error(review_data.swap_request_id)
            
            # Check if user is participant
            is_sender = swap_request.sender.id == current_user.id
            is_receiver = swap_request.receiver.id == current_user.id
            
            if not (is_sender or is_receiver):
                raise create_unauthorized_swap_access_error(
                    review_data.swap_request_id, 
                    str(current_user.id)
                )
            
            # Check if review already exists
            existing_review = await Review.find_one({
                "reviewer": current_user.id,
                "swap_request": swap_request.id
            })
            
            if existing_review:
                raise create_review_already_exists_error(
                    review_data.swap_request_id,
                    str(current_user.id)
                )
            
            # Determine reviewee
            reviewee_id = swap_request.receiver.id if is_sender else swap_request.sender.id
            reviewee = await User.get(reviewee_id)
            
            if not reviewee:
                raise create_user_not_found_error(reviewee_id)
            
            # Create skill ratings
            skill_ratings = []
            if review_data.skills:
                for skill_data in review_data.skills:
                    skill_ratings.append({
                        "name": skill_data.name,
                        "rating": skill_data.rating
                    })
            
            # Create review
            review = Review(
                reviewer=current_user,
                reviewee=reviewee,
                swap_request=swap_request,
                rating=review_data.rating,
                comment=review_data.comment,
                skills=skill_ratings,
                would_swap_again=review_data.would_swap_again,
                helpfulness=review_data.helpfulness,
                communication=review_data.communication,
                punctuality=review_data.punctuality
            )
            
            # Save review
            await review.save()
            
            # Update reviewee's rating
            await ReviewController._update_user_rating(reviewee)
            
            # Populate and return
            await review.populate("reviewer reviewee swap_request")
            
            logger.info(f"Review created: {current_user.email} -> {reviewee.email}")
            
            return review
            
        except (ValidationError, NotFoundError, ConflictError, BusinessLogicError):
            raise
        except Exception as e:
            logger.error(f"Create review error: {str(e)}")
            raise ValidationError("Failed to create review")
    
    @staticmethod
    async def get_reviews(
        filter_query: ReviewFilterQuery,
        current_user: User = None
    ) -> ReviewList:
        """Get reviews with filters"""
        try:
            # Build query
            query = {}
            
            # Filter by user
            if filter_query.user_id:
                query["$or"] = [
                    {"reviewer": filter_query.user_id},
                    {"reviewee": filter_query.user_id}
                ]
            
            # Filter by rating
            if filter_query.rating:
                query["rating"] = filter_query.rating
            
            # Filter by would_swap_again
            if filter_query.would_swap_again is not None:
                query["would_swap_again"] = filter_query.would_swap_again
            
            # Only show public reviews unless user is viewing their own
            if current_user and filter_query.user_id != str(current_user.id):
                query["is_public"] = True
            
            # Pagination
            skip, limit = paginate_query(filter_query.page, filter_query.limit)
            
            # Sort options
            sort_options = {
                "recent": {"created_at": -1},
                "rating_high": {"rating": -1},
                "rating_low": {"rating": 1},
                "helpful": {"helpfulness": -1}
            }
            
            sort_field = sort_options.get(filter_query.sort_by, sort_options["recent"])
            
            # Get reviews
            reviews = await Review.find(query).populate("reviewer reviewee swap_request").sort(
                sort_field
            ).skip(skip).limit(limit).to_list()
            
            # Get total count
            total = await Review.count_documents(query)
            
            # Calculate statistics
            stats = await ReviewController._calculate_review_stats(query)
            
            # Pagination info
            pagination = calculate_pagination_info(total, filter_query.page, filter_query.limit)
            
            return ReviewList(
                reviews=reviews,
                pagination=pagination,
                stats=stats
            )
            
        except Exception as e:
            logger.error(f"Get reviews error: {str(e)}")
            raise ValidationError("Failed to get reviews")
    
    @staticmethod
    async def get_review(
        review_id: str,
        current_user: User = None
    ) -> ReviewWithUsers:
        """Get specific review"""
        try:
            review = await Review.find_one({"_id": review_id}).populate("reviewer reviewee swap_request")
            
            if not review:
                raise create_review_not_found_error(review_id)
            
            # Check if review is public or user has access
            if not review.is_public:
                if not current_user or (
                    current_user.id != review.reviewer.id and 
                    current_user.id != review.reviewee.id
                ):
                    raise BusinessLogicError("Access to this review is restricted")
            
            return review
            
        except (NotFoundError, BusinessLogicError):
            raise
        except Exception as e:
            logger.error(f"Get review error: {str(e)}")
            raise ValidationError("Failed to get review")
    
    @staticmethod
    async def update_review(
        review_id: str,
        update_data: ReviewUpdate,
        current_user: User
    ) -> ReviewWithUsers:
        """Update review"""
        try:
            # Get review
            review = await Review.get(review_id)
            if not review:
                raise create_review_not_found_error(review_id)
            
            # Check if user is reviewer
            if review.reviewer.id != current_user.id:
                raise create_unauthorized_swap_access_error(review_id, str(current_user.id))
            
            # Check if review can be edited (within 7 days)
            if not await review.can_be_edited(current_user):
                raise BusinessLogicError("Review can only be edited within 7 days")
            
            # Update fields
            if update_data.comment is not None:
                review.comment = update_data.comment
            
            if update_data.is_public is not None:
                review.is_public = update_data.is_public
            
            # Save changes
            review.updated_at = datetime.utcnow()
            await review.save()
            
            # Update reviewee's rating
            await ReviewController._update_user_rating(await review.reviewee.fetch())
            
            # Populate and return
            await review.populate("reviewer reviewee swap_request")
            
            return review
            
        except (NotFoundError, BusinessLogicError):
            raise
        except Exception as e:
            logger.error(f"Update review error: {str(e)}")
            raise ValidationError("Failed to update review")
    
    @staticmethod
    async def delete_review(
        review_id: str,
        current_user: User
    ) -> Dict[str, str]:
        """Delete review"""
        try:
            # Get review
            review = await Review.get(review_id)
            if not review:
                raise create_review_not_found_error(review_id)
            
            # Check if user is reviewer
            if review.reviewer.id != current_user.id:
                raise create_unauthorized_swap_access_error(review_id, str(current_user.id))
            
            # Get reviewee before deletion
            reviewee = await review.reviewee.fetch()
            
            # Delete review
            await review.delete()
            
            # Update reviewee's rating
            await ReviewController._update_user_rating(reviewee)
            
            return {"message": "Review deleted successfully"}
            
        except (NotFoundError, BusinessLogicError):
            raise
        except Exception as e:
            logger.error(f"Delete review error: {str(e)}")
            raise ValidationError("Failed to delete review")
    
    @staticmethod
    async def respond_to_review(
        review_id: str,
        response_data: ReviewResponseCreate,
        current_user: User
    ) -> ReviewWithUsers:
        """Respond to a review"""
        try:
            # Get review
            review = await Review.get(review_id)
            if not review:
                raise create_review_not_found_error(review_id)
            
            # Check if user is reviewee
            if review.reviewee.id != current_user.id:
                raise BusinessLogicError("Only reviewee can respond to reviews")
            
            # Check if response already exists
            if review.response:
                raise BusinessLogicError("Response already exists for this review")
            
            # Add response
            await review.add_response(response_data.content)
            
            # Populate and return
            await review.populate("reviewer reviewee swap_request")
            
            return review
            
        except (NotFoundError, BusinessLogicError):
            raise
        except Exception as e:
            logger.error(f"Respond to review error: {str(e)}")
            raise ValidationError("Failed to respond to review")
    
    @staticmethod
    async def report_review(
        review_id: str,
        report_data: ReviewReport,
        current_user: User
    ) -> Dict[str, str]:
        """Report a review"""
        try:
            # Get review
            review = await Review.get(review_id)
            if not review:
                raise create_review_not_found_error(review_id)
            
            # Report review
            await review.report_review(report_data.reason)
            
            logger.info(f"Review reported: {review_id} by {current_user.email}")
            
            return {"message": "Review reported successfully"}
            
        except NotFoundError:
            raise
        except Exception as e:
            logger.error(f"Report review error: {str(e)}")
            raise ValidationError("Failed to report review")
    
    @staticmethod
    async def get_user_review_summary(
        user_id: str,
        current_user: User = None
    ) -> UserReviewSummary:
        """Get user review summary"""
        try:
            # Get user
            user = await User.get(user_id)
            if not user:
                raise create_user_not_found_error(user_id)
            
            # Get reviews for user
            reviews_query = {"reviewee": user.id, "is_public": True}
            
            # If user is viewing their own profile, show all reviews
            if current_user and user_id == str(current_user.id):
                reviews_query = {"reviewee": user.id}
            
            reviews = await Review.find(reviews_query).populate("reviewer").sort(
                {"created_at": -1}
            ).limit(10).to_list()
            
            # Calculate rating distribution
            rating_pipeline = [
                {"$match": reviews_query},
                {"$group": {"_id": "$rating", "count": {"$sum": 1}}},
                {"$sort": {"_id": 1}}
            ]
            
            rating_distribution_raw = await Review.aggregate(rating_pipeline).to_list()
            rating_distribution = {}
            
            for rating_data in rating_distribution_raw:
                rating_distribution[str(rating_data["_id"])] = rating_data["count"]
            
            # Calculate skill ratings
            skill_ratings_pipeline = [
                {"$match": reviews_query},
                {"$unwind": "$skills"},
                {"$group": {
                    "_id": "$skills.name",
                    "avg_rating": {"$avg": "$skills.rating"},
                    "count": {"$sum": 1}
                }},
                {"$sort": {"count": -1}},
                {"$limit": 10}
            ]
            
            skill_ratings_raw = await Review.aggregate(skill_ratings_pipeline).to_list()
            skill_ratings = []
            
            for skill_data in skill_ratings_raw:
                skill_ratings.append({
                    "name": skill_data["_id"],
                    "rating": round(skill_data["avg_rating"], 1),
                    "count": skill_data["count"]
                })
            
            # Calculate would_swap_again rate
            swap_again_pipeline = [
                {"$match": reviews_query},
                {"$group": {
                    "_id": "$would_swap_again",
                    "count": {"$sum": 1}
                }}
            ]
            
            swap_again_raw = await Review.aggregate(swap_again_pipeline).to_list()
            swap_again_count = 0
            total_reviews = 0
            
            for swap_data in swap_again_raw:
                if swap_data["_id"]:
                    swap_again_count = swap_data["count"]
                total_reviews += swap_data["count"]
            
            would_swap_again_rate = (swap_again_count / total_reviews * 100) if total_reviews > 0 else 0.0
            
            return UserReviewSummary(
                user_id=user_id,
                total_reviews=user.total_reviews,
                average_rating=user.rating,
                recent_reviews=reviews,
                rating_distribution=rating_distribution,
                skill_ratings=skill_ratings,
                would_swap_again_rate=round(would_swap_again_rate, 1)
            )
            
        except NotFoundError:
            raise
        except Exception as e:
            logger.error(f"Get user review summary error: {str(e)}")
            raise ValidationError("Failed to get user review summary")
    
    @staticmethod
    async def get_review_activity(current_user: User) -> ReviewActivity:
        """Get review activity for current user"""
        try:
            # Get reviews to write (completed swaps without reviews)
            completed_swaps = await SwapRequest.find({
                "$or": [
                    {"sender": current_user.id},
                    {"receiver": current_user.id}
                ],
                "status": "completed"
            }).to_list()
            
            swap_ids = [swap.id for swap in completed_swaps]
            
            existing_reviews = await Review.find({
                "reviewer": current_user.id,
                "swap_request": {"$in": swap_ids}
            }).to_list()
            
            reviewed_swap_ids = [str(review.swap_request.id) for review in existing_reviews]
            pending_reviews = [swap for swap in completed_swaps if str(swap.id) not in reviewed_swap_ids]
            
            # Get recent reviews given
            recent_given = await Review.find({
                "reviewer": current_user.id
            }).populate("reviewee swap_request").sort({"created_at": -1}).limit(5).to_list()
            
            # Get recent reviews received
            recent_received = await Review.find({
                "reviewee": current_user.id
            }).populate("reviewer swap_request").sort({"created_at": -1}).limit(5).to_list()
            
            # Get review notifications (new reviews received)
            review_notifications = len(recent_received)
            
            return ReviewActivity(
                pending_reviews=len(pending_reviews),
                recent_reviews_given=recent_given,
                recent_reviews_received=recent_received,
                review_notifications=review_notifications
            )
            
        except Exception as e:
            logger.error(f"Get review activity error: {str(e)}")
            raise ValidationError("Failed to get review activity")
    
    @staticmethod
    async def _update_user_rating(user: User):
        """Update user's average rating based on reviews"""
        try:
            # Calculate new average rating
            rating_pipeline = [
                {"$match": {"reviewee": user.id}},
                {"$group": {"_id": None, "avg_rating": {"$avg": "$rating"}, "count": {"$sum": 1}}}
            ]
            
            rating_result = await Review.aggregate(rating_pipeline).to_list()
            
            if rating_result:
                user.rating = round(rating_result[0]["avg_rating"], 1)
                user.total_reviews = rating_result[0]["count"]
            else:
                user.rating = 0.0
                user.total_reviews = 0
            
            await user.save()
            
        except Exception as e:
            logger.error(f"Update user rating error: {str(e)}")
    
    @staticmethod
    async def _calculate_review_stats(query: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate review statistics"""
        try:
            # Total reviews
            total_reviews = await Review.count_documents(query)
            
            # Average rating
            rating_pipeline = [
                {"$match": query},
                {"$group": {"_id": None, "avg_rating": {"$avg": "$rating"}}}
            ]
            
            rating_result = await Review.aggregate(rating_pipeline).to_list()
            average_rating = rating_result[0]["avg_rating"] if rating_result else 0.0
            
            # Rating distribution
            distribution_pipeline = [
                {"$match": query},
                {"$group": {"_id": "$rating", "count": {"$sum": 1}}},
                {"$sort": {"_id": 1}}
            ]
            
            distribution_raw = await Review.aggregate(distribution_pipeline).to_list()
            rating_distribution = {}
            
            for rating_data in distribution_raw:
                rating_distribution[str(rating_data["_id"])] = rating_data["count"]
            
            # Would swap again statistics
            swap_again_pipeline = [
                {"$match": query},
                {"$group": {"_id": "$would_swap_again", "count": {"$sum": 1}}}
            ]
            
            swap_again_raw = await Review.aggregate(swap_again_pipeline).to_list()
            would_swap_again_count = 0
            total_count = 0
            
            for swap_data in swap_again_raw:
                if swap_data["_id"]:
                    would_swap_again_count = swap_data["count"]
                total_count += swap_data["count"]
            
            would_swap_again_percentage = (would_swap_again_count / total_count * 100) if total_count > 0 else 0.0
            
            return {
                "total_reviews": total_reviews,
                "average_rating": round(average_rating, 1),
                "rating_distribution": rating_distribution,
                "would_swap_again_count": would_swap_again_count,
                "would_swap_again_percentage": round(would_swap_again_percentage, 1)
            }
            
        except Exception as e:
            logger.error(f"Calculate review stats error: {str(e)}")
            return {}


# Import datetime for use in controller
from datetime import datetime
