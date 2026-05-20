from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from typing import Dict, Any
import traceback

from app.controllers.auth_controller import AuthController
from app.schemas.auth import (
    UserRegister,
    UserLogin,
    TokenResponse,
    UserResponse,
    PasswordChange,
    PasswordReset,
    PasswordResetConfirm
)
from app.models.user import User
from app.middleware.auth_middleware import get_current_user
from app.utils.exceptions import SkillTradeException
from app.utils.logging import get_logger

logger = get_logger(__name__)

# Create router
router = APIRouter()

# Security scheme
security = HTTPBearer()


@router.post("/register", response_model=TokenResponse)
async def register(user_data: UserRegister) -> TokenResponse:
    """
    Register a new user.

    - **name**: User's full name (2-50 characters)
    - **email**: Valid email address
    - **password**: Strong password
    - **location**: Geographic coordinates [longitude, latitude]
    """
    try:
        print("\n========== REGISTER REQUEST ==========")
        print(user_data)
        print("======================================\n")

        result = await AuthController.register(user_data)

        print("\n========== REGISTER SUCCESS ==========")
        print(result)
        print("======================================\n")

        return result

    except SkillTradeException as e:
        print("\n========== SKILLTRADE ERROR ==========")
        print(str(e))
        traceback.print_exc()
        print("======================================\n")

        raise HTTPException(
            status_code=e.status_code,
            detail=e.message
        )

    except Exception as e:
        print("\n========== REGISTER ERROR ==========")
        print(str(e))
        traceback.print_exc()
        print("====================================\n")

        logger.error(f"Register endpoint error: {str(e)}")

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/login", response_model=TokenResponse)
async def login(login_data: UserLogin) -> TokenResponse:
    """
    Login user with email and password.

    - **email**: User's email address
    - **password**: User's password
    """
    try:
        return await AuthController.login(login_data)

    except SkillTradeException as e:
        raise HTTPException(
            status_code=e.status_code,
            detail=e.message
        )

    except Exception as e:
        print("\n========== LOGIN ERROR ==========")
        print(str(e))
        traceback.print_exc()
        print("=================================\n")

        logger.error(f"Login endpoint error: {str(e)}")

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(
    current_user: User = Depends(get_current_user)
) -> UserResponse:
    """
    Get current user's profile.

    Requires authentication token.
    """
    try:
        return await AuthController.get_current_user(current_user)

    except SkillTradeException as e:
        raise HTTPException(
            status_code=e.status_code,
            detail=e.message
        )

    except Exception as e:
        print("\n========== GET USER ERROR ==========")
        print(str(e))
        traceback.print_exc()
        print("====================================\n")

        logger.error(f"Get current user endpoint error: {str(e)}")

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/logout")
async def logout(
    current_user: User = Depends(get_current_user)
) -> Dict[str, str]:
    """
    Logout current user.

    Requires authentication token.
    """
    try:
        return await AuthController.logout(current_user)

    except SkillTradeException as e:
        raise HTTPException(
            status_code=e.status_code,
            detail=e.message
        )

    except Exception as e:
        print("\n========== LOGOUT ERROR ==========")
        print(str(e))
        traceback.print_exc()
        print("==================================\n")

        logger.error(f"Logout endpoint error: {str(e)}")

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/change-password")
async def change_password(
    password_data: PasswordChange,
    current_user: User = Depends(get_current_user)
) -> Dict[str, str]:
    """
    Change user's password.
    """
    try:
        return await AuthController.change_password(
            password_data,
            current_user
        )

    except SkillTradeException as e:
        raise HTTPException(
            status_code=e.status_code,
            detail=e.message
        )

    except Exception as e:
        print("\n========== CHANGE PASSWORD ERROR ==========")
        print(str(e))
        traceback.print_exc()
        print("===========================================\n")

        logger.error(f"Change password endpoint error: {str(e)}")

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/reset-password")
async def request_password_reset(
    reset_data: PasswordReset
) -> Dict[str, str]:
    """
    Request password reset link.
    """
    try:
        return await AuthController.request_password_reset(reset_data)

    except SkillTradeException as e:
        raise HTTPException(
            status_code=e.status_code,
            detail=e.message
        )

    except Exception as e:
        print("\n========== RESET PASSWORD ERROR ==========")
        print(str(e))
        traceback.print_exc()
        print("==========================================\n")

        logger.error(f"Password reset request endpoint error: {str(e)}")

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/reset-password/confirm")
async def confirm_password_reset(
    reset_data: PasswordResetConfirm
) -> Dict[str, str]:
    """
    Confirm password reset with token.
    """
    try:
        return await AuthController.confirm_password_reset(reset_data)

    except SkillTradeException as e:
        raise HTTPException(
            status_code=e.status_code,
            detail=e.message
        )

    except Exception as e:
        print("\n========== CONFIRM RESET ERROR ==========")
        print(str(e))
        traceback.print_exc()
        print("=========================================\n")

        logger.error(f"Password reset confirm endpoint error: {str(e)}")

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/refresh-token", response_model=TokenResponse)
async def refresh_token(
    current_user: User = Depends(get_current_user)
) -> TokenResponse:
    """
    Refresh access token.
    """
    try:
        return await AuthController.refresh_token(current_user)

    except SkillTradeException as e:
        raise HTTPException(
            status_code=e.status_code,
            detail=e.message
        )

    except Exception as e:
        print("\n========== REFRESH TOKEN ERROR ==========")
        print(str(e))
        traceback.print_exc()
        print("=========================================\n")

        logger.error(f"Refresh token endpoint error: {str(e)}")

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/verify-token")
async def verify_token(
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Verify if token is valid.
    """
    try:
        return {
            "valid": True,
            "user_id": str(current_user.id),
            "email": current_user.email,
            "name": current_user.name
        }

    except Exception as e:
        print("\n========== VERIFY TOKEN ERROR ==========")
        print(str(e))
        traceback.print_exc()
        print("========================================\n")

        logger.error(f"Verify token endpoint error: {str(e)}")

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/health")
async def auth_health() -> Dict[str, str]:
    """
    Health check for authentication service.
    """
    return {
        "status": "healthy",
        "service": "authentication"
    }