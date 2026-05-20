from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional, Dict, Any
import logging
from datetime import datetime

from app.models.user import User
from app.utils.security import verify_token
from app.utils.exceptions import AuthenticationError, AuthorizationError
from app.utils.logging import get_logger

logger = get_logger(__name__)

# Security scheme for FastAPI
security = HTTPBearer(auto_error=False)


class AuthMiddleware:
    """Authentication middleware for FastAPI"""
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, request: Request, call_next):
        # Skip authentication for certain paths
        if self._should_skip_auth(request):
            return await call_next(request)
        
        # Extract and verify token
        user = await self._authenticate_request(request)
        
        # Add user to request state
        request.state.user = user
        
        # Continue with request
        response = await call_next(request)
        
        return response
    
    def _should_skip_auth(self, request: Request) -> bool:
        """Check if authentication should be skipped for this path"""
        skip_paths = [
            "/health",
            "/docs",
            "/redoc",
            "/openapi.json",
            "/favicon.ico",
            "/static",
        ]
        
        # Skip auth for public endpoints
        if request.url.path.startswith("/api/auth"):
            # Allow login and register endpoints
            if request.url.path in ["/api/auth/login", "/api/auth/register"]:
                return True
        
        # Skip auth for health and docs
        if any(request.url.path.startswith(path) for path in skip_paths):
            return True
        
        return False
    
    async def _authenticate_request(self, request: Request) -> Optional[User]:
        """Authenticate the request and return user"""
        try:
            # Get token from Authorization header
            authorization = request.headers.get("Authorization")
            
            if not authorization:
                raise AuthenticationError("No authorization token provided")
            
            # Extract token from "Bearer <token>" format
            if not authorization.startswith("Bearer "):
                raise AuthenticationError("Invalid authorization header format")
            
            token = authorization.split(" ")[1]
            
            print("=== JWT TOKEN RECEIVED ===")
            print(f"Token: {token[:20]}...")
            
            # Verify token
            payload = verify_token(token)
            
            print("=== JWT PAYLOAD ===")
            print(f"Payload: {payload}")
            
            user_id = payload.get("sub")
            print("=== USER ID FROM TOKEN ===")
            print(f"User ID: {user_id}")
            
            # Get user from database
            try:
                from bson import ObjectId
                user = await User.find_one({
                    "_id": ObjectId(user_id)
                })
            except Exception as e:
                print(f"=== USER LOOKUP ERROR ===")
                print(f"Error: {str(e)}")
                print(f"User ID type: {type(user_id)}")
                print(f"User ID value: {user_id}")
                user = None
            
            print("=== AUTHENTICATED USER ===")
            print(f"User: {user.email if user else 'NOT FOUND'}")
            
            if not user:
                raise AuthenticationError("User not found")
            
            # Update user online status
            user.is_online = True
            user.updated_at = datetime.utcnow()
            await user.save()
            
            logger.debug(f"User {user.id} authenticated successfully")
            
            return user
            
        except AuthenticationError:
            raise
        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            raise AuthenticationError("Authentication failed")


async def get_current_user(request: Request) -> User:
    """Get current authenticated user from request"""
    try:
        # Get token from Authorization header
        authorization = request.headers.get("Authorization")
        
        if not authorization:
            print("\n=== NO AUTH TOKEN ===")
            raise HTTPException(
                status_code=401,
                detail="No authorization token provided"
            )
        
        # Extract token from "Bearer <token>" format
        if not authorization.startswith("Bearer "):
            print("\n=== INVALID AUTH FORMAT ===")
            raise HTTPException(
                status_code=401,
                detail="Invalid authorization header format"
            )
        
        token = authorization.split(" ")[1]
        
        print("\n=== TOKEN RECEIVED ===")
        print(f"Token: {token[:20]}...")
        
        # Decode JWT token
        from app.config.settings import settings
        from jose import jwt, JWTError
        
        try:
            payload = jwt.decode(
                token,
                settings.jwt_secret,
                algorithms=[settings.jwt_algorithm]
            )
            
            print("\n=== JWT PAYLOAD ===")
            print(f"Payload: {payload}")
            
            user_id = payload.get("sub")
            
            print("\n=== USER ID FROM TOKEN ===")
            print(f"User ID: {user_id}")
            
            if not user_id:
                print("\n=== NO USER ID IN TOKEN ===")
                raise HTTPException(
                    status_code=401,
                    detail="Invalid token: no user ID"
                )
            
            # Find user in database
            from bson import ObjectId
            user = await User.find_one({
                "_id": ObjectId(user_id)
            })
            
            print("\n=== AUTHENTICATED USER ===")
            print(f"User: {user.email if user else 'NOT FOUND'}")
            
            if not user:
                print("\n=== USER NOT FOUND ===")
                raise HTTPException(
                    status_code=401,
                    detail="User not found"
                )
            
            return user
            
        except JWTError as e:
            print(f"\n=== JWT DECODE ERROR ===")
            print(f"Error: {str(e)}")
            raise HTTPException(
                status_code=401,
                detail="Invalid token"
            )
        except Exception as e:
            print(f"\n=== AUTH ERROR ===")
            print(f"Error: {str(e)}")
            raise HTTPException(
                status_code=401,
                detail="Authentication failed"
            )
            
    except Exception as e:
        print(f"\n=== MIDDLEWARE ERROR ===")
        print(f"Error: {str(e)}")
        raise HTTPException(
            status_code=401,
            detail="User not authenticated"
        )


async def get_current_user_optional(request: Request) -> Optional[User]:
    """Get current authenticated user (optional) from request"""
    if hasattr(request.state, 'user') and request.state.user:
        return request.state.user
    
    return None


async def get_current_active_user(request: Request) -> User:
    """Get current active authenticated user"""
    user = await get_current_user(request)
    
    # Add any additional checks for active user here
    # For example, check if user is not banned, etc.
    
    return user


def require_auth(request: Request) -> User:
    """Decorator to require authentication"""
    if not hasattr(request.state, 'user') or not request.state.user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    
    return request.state.user


def require_optional_auth(request: Request) -> Optional[User]:
    """Decorator to optionally get authenticated user"""
    if hasattr(request.state, 'user') and request.state.user:
        return request.state.user
    
    return None


class PermissionChecker:
    """Utility class for checking user permissions"""
    
    @staticmethod
    async def can_access_user(current_user: User, target_user_id: str) -> bool:
        """Check if current user can access target user's data"""
        # Users can always access their own data
        if current_user.id == target_user_id:
            return True
        
        # Add additional permission checks here
        # For example, admin users can access any user data
        
        return False
    
    @staticmethod
    async def can_access_swap(current_user: User, swap_request_id: str) -> bool:
        """Check if current user can access swap request"""
        # This would check if user is a participant in the swap
        # Implementation would depend on your swap request model
        
        return False
    
    @staticmethod
    async def can_access_message(current_user: User, message_id: str) -> bool:
        """Check if current user can access message"""
        # This would check if user is sender or receiver of the message
        
        return False
    
    @staticmethod
    async def can_access_review(current_user: User, review_id: str) -> bool:
        """Check if current user can access review"""
        # This would check if user is reviewer, reviewee, or has admin access
        
        return False


async def check_user_permission(
    request: Request, 
    target_user_id: str, 
    action: str = "read"
) -> bool:
    """Check if current user has permission to perform action on target user"""
    current_user = await get_current_user(request)
    
    if action == "read":
        return await PermissionChecker.can_access_user(current_user, target_user_id)
    elif action == "write":
        # Users can only write to their own profile
        return current_user.id == target_user_id
    elif action == "delete":
        # Users can only delete their own profile (with additional checks)
        return current_user.id == target_user_id
    
    return False


async def check_swap_permission(
    request: Request, 
    swap_request_id: str, 
    action: str = "read"
) -> bool:
    """Check if current user has permission to perform action on swap request"""
    current_user = await get_current_user(request)
    
    if action == "read":
        return await PermissionChecker.can_access_swap(current_user, swap_request_id)
    elif action in ["write", "delete"]:
        # Add additional checks for write/delete permissions
        return await PermissionChecker.can_access_swap(current_user, swap_request_id)
    
    return False


# Rate limiting for authentication endpoints (simplified approach)
# Note: For production, consider using Redis-based rate limiting


# Security headers middleware
async def add_security_headers(request: Request, call_next):
    """Add security headers to response"""
    response = await call_next(request)
    
    # Add security headers
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    
    return response


# CORS configuration
def configure_cors(app):
    """Configure CORS for the application"""
    from fastapi.middleware.cors import CORSMiddleware
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173", "http://localhost:5174"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


# Request logging middleware
async def log_requests(request: Request, call_next):
    """Log incoming requests"""
    start_time = time.time()
    
    # Log request
    logger.info(f"Request: {request.method} {request.url.path}")
    
    # Process request
    response = await call_next(request)
    
    # Log response
    process_time = time.time() - start_time
    logger.info(f"Response: {response.status_code} - {process_time:.4f}s")
    
    return response


# Import time for request logging
import time
