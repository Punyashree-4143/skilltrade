import bcrypt
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from fastapi import HTTPException, status

from app.config.settings import settings


def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    print(f"DEBUG: Hashing password: '{password}' (length: {len(password)})")
    print(f"DEBUG: Password bytes length: {len(password.encode('utf-8'))}")
    
    try:
        # Ensure password is a string and handle encoding properly
        if not isinstance(password, str):
            password = str(password)
        
        # Handle bcrypt 72-byte limit by truncating if necessary
        password_bytes = password.encode('utf-8')
        if len(password_bytes) > 72:
            print(f"DEBUG: Truncating password from {len(password_bytes)} to 72 bytes")
            password_bytes = password_bytes[:72]
        
        print(f"DEBUG: Final password bytes length: {len(password_bytes)}")
        
        # Generate salt and hash using bcrypt directly
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password_bytes, salt)
        
        # Convert bytes back to string for storage
        hashed_str = hashed.decode('utf-8')
        print(f"DEBUG: Successfully hashed password")
        return hashed_str
        
    except Exception as e:
        print(f"DEBUG: Error hashing password: {e}")
        print(f"DEBUG: Error type: {type(e)}")
        raise


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a hash"""
    try:
        # Handle bcrypt 72-byte limit by truncating if necessary (same as hashing)
        password_bytes = plain_password.encode('utf-8')
        if len(password_bytes) > 72:
            password_bytes = password_bytes[:72]
        
        # Convert stored hash back to bytes for verification
        hashed_bytes = hashed_password.encode('utf-8')
        
        # Verify using bcrypt directly
        return bcrypt.checkpw(password_bytes, hashed_bytes)
        
    except Exception as e:
        print(f"DEBUG: Error verifying password: {e}")
        print(f"DEBUG: Error type: {type(e)}")
        return False


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.jwt_expire_minutes)
    
    to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(
        to_encode, 
        settings.jwt_secret, 
        algorithm=settings.jwt_algorithm
    )
    return str(encoded_jwt) if isinstance(encoded_jwt, bytes) else encoded_jwt


def verify_token(token: str) -> Dict[str, Any]:
    """Verify and decode JWT token"""
    try:
        payload = jwt.decode(
            token, 
            settings.jwt_secret, 
            algorithms=[settings.jwt_algorithm]
        )
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


def create_password_reset_token(email: str) -> str:
    """Create password reset token"""
    delta = timedelta(hours=1)  # Reset token expires in 1 hour
    now = datetime.utcnow()
    expires = now + delta
    exp = expires.timestamp()
    encoded_jwt = jwt.encode(
        {"exp": exp, "nbf": now, "sub": email},
        settings.jwt_secret,
        algorithm=settings.jwt_algorithm,
    )
    return str(encoded_jwt) if isinstance(encoded_jwt, bytes) else encoded_jwt


def verify_password_reset_token(token: str) -> str:
    """Verify password reset token and return email"""
    try:
        decoded_token = jwt.decode(
            token, 
            settings.jwt_secret, 
            algorithms=[settings.jwt_algorithm]
        )
        return decoded_token["sub"]
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_400_BADAIL,
            detail="Invalid reset token"
        )


def generate_password() -> str:
    """Generate a random password"""
    import secrets
    import string
    
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    password = ''.join(secrets.choice(alphabet) for _ in range(12))
    return password


def validate_password_strength(password: str) -> bool:
    """Validate password strength requirements"""
    if len(password) < 8:
        return False
    
    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_special = any(c in "!@#$%^&*" for c in password)
    
    return has_upper and has_lower and has_digit and has_special


def get_password_hash_info(password_hash: str) -> Dict[str, Any]:
    """Get information about password hash"""
    try:
        # Extract algorithm info from bcrypt hash
        if password_hash.startswith("$2b$"):
            parts = password_hash.split("$")
            return {
                "algorithm": parts[1],
                "rounds": parts[2],
                "salt": parts[3][:22] if len(parts) > 3 else None
            }
    except Exception:
        pass
    
    return {"algorithm": "unknown", "rounds": "unknown", "salt": None}
