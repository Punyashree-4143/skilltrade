from fastapi import HTTPException
import traceback
from datetime import datetime

from app.models.user import User
from app.schemas.auth import (
    UserRegister,
    UserLogin,
    TokenResponse,
    UserResponse,
    PasswordChange,
    PasswordReset,
    PasswordResetConfirm,
)

from app.utils.exceptions import (
    AuthenticationError,
    ValidationError,
    ConflictError,
    create_email_already_exists_error,
)

from app.utils.logging import (
    get_logger,
    security_logger,
)

from app.utils.security import (
    create_access_token,
    hash_password,
)

logger = get_logger(__name__)


class AuthController:
    """Authentication controller"""

    @staticmethod
    async def register(
        user_data: UserRegister
    ) -> TokenResponse:
        """Register a new user"""

        try:
            print("STEP 1: Starting registration")
            print(f"User data: {user_data}")

            # Check if user exists
            print("STEP 2: Checking for existing user")

            existing_user = await User.find_one(
                {"email": user_data.email}
            )

            if existing_user:
                raise create_email_already_exists_error(
                    user_data.email
                )

            print("STEP 3: No existing user found")

            # Create user dictionary
            print("STEP 4: Creating user data dict")

            user_data_dict = {
                "name": user_data.name,
                "email": user_data.email,
                "bio": "",
                "skills_offered": [],
                "skills_wanted": [],
                "rating": 0.0,
                "total_reviews": 0,
                "is_online": False,
                "profile_completed": False,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
            }

            print("STEP 5: Hashing password")

            hashed_password = hash_password(user_data.password)
            user_data_dict["password_hash"] = hashed_password

            print("STEP 6: Creating User model")

            user = User(**user_data_dict)

            print(f"User model created: {user}")

            # Save user
            print("STEP 7: Saving user")

            await user.save()

            print(
                f"User saved successfully with ID: {user.id}"
            )

            # Security logging
            security_logger.log_registration_attempt(
                email=user_data.email,
                success=True,
            )

            # Generate JWT
            print("STEP 8: Creating JWT token")

            access_token = create_access_token(
                data={"sub": str(user.id)}
            )

            print(
                f"JWT token created: {access_token[:20]}..."
            )

            logger.info(
                f"User registered successfully: {user.email}"
            )

            # Return response
            print("STEP 9: Returning response")

            return TokenResponse(
                access_token=access_token,
                token_type="bearer",
                user=user.to_dict_safe(),
            )

        except ConflictError:
            raise

        except Exception as e:
            print("\n========== REGISTER ERROR ==========")
            print(f"Error: {str(e)}")
            traceback.print_exc()
            print("====================================\n")

            logger.error(f"Register error: {str(e)}")

            security_logger.log_registration_attempt(
                email=user_data.email,
                success=False,
                error=str(e),
            )

            raise HTTPException(
                status_code=500,
                detail=str(e),
            )

    @staticmethod
    async def login(
        login_data: UserLogin
    ) -> TokenResponse:
        """Login user"""

        try:
            # Find user
            user = await User.find_one(
                {"email": login_data.email}
            )

            if not user:
                raise AuthenticationError(
                    "Invalid email or password"
                )

            # Verify password
            if not user.verify_password(
                login_data.password
            ):
                raise AuthenticationError(
                    "Invalid email or password"
                )

            # Update online status
            user.is_online = True

            await user.save()

            # Security logging
            security_logger.log_login_attempt(
                email=login_data.email,
                success=True,
            )

            # Generate token
            access_token = create_access_token(
                data={"sub": str(user.id)}
            )

            logger.info(
                f"User logged in successfully: {user.email}"
            )

            return TokenResponse(
                access_token=access_token,
                token_type="bearer",
                user=user.to_dict_safe(),
            )

        except AuthenticationError:
            security_logger.log_login_attempt(
                email=login_data.email,
                success=False,
                error="Invalid credentials",
            )

            raise

        except Exception as e:
            logger.error(f"Login error: {str(e)}")

            security_logger.log_login_attempt(
                email=login_data.email,
                success=False,
                error=str(e),
            )

            raise AuthenticationError("Login failed")

    @staticmethod
    async def get_current_user(
        current_user: User
    ) -> UserResponse:
        """Get current user"""

        try:
            user_dict = current_user.to_dict_safe()

            return UserResponse(**user_dict)

        except Exception as e:
            logger.error(
                f"Get current user error: {str(e)}"
            )

            raise ValidationError(
                "Failed to get user profile"
            )

    @staticmethod
    async def logout(current_user: User) -> dict:
        """Logout user"""

        try:
            current_user.is_online = False

            await current_user.save()

            logger.info(
                f"User logged out: {current_user.email}"
            )

            return {
                "message": "Logout successful"
            }

        except Exception as e:
            logger.error(f"Logout error: {str(e)}")

            raise ValidationError("Logout failed")

    @staticmethod
    async def change_password(
        password_data: PasswordChange,
        current_user: User,
    ) -> dict:
        """Change password"""

        try:
            if not current_user.verify_password(
                password_data.current_password
            ):
                raise AuthenticationError(
                    "Current password is incorrect"
                )

            current_user.set_password(
                password_data.new_password
            )

            await current_user.save()

            logger.info(
                f"Password changed for user: {current_user.email}"
            )

            return {
                "message": "Password changed successfully"
            }

        except AuthenticationError:
            raise

        except Exception as e:
            logger.error(
                f"Change password error: {str(e)}"
            )

            raise ValidationError(
                "Failed to change password"
            )