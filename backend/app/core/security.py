"""
Security Utilities — JWT tokens, password hashing, and cookie management

This module handles all authentication security:
1. Password hashing with bcrypt — never store plain text passwords
2. JWT token creation and validation — stateless session management
3. httpOnly cookie setting — prevents XSS attacks from stealing tokens

Interview talking point:
"I use httpOnly cookies instead of localStorage because JavaScript cannot
read httpOnly cookies. If an attacker injects malicious JS (XSS), they
cannot steal the token. With localStorage, any JS on the page can read it."
"""

from datetime import datetime, timedelta

from fastapi import Response
from jose import jwt, JWTError, ExpiredSignatureError
import bcrypt

from app.core.config import settings




# JWT configuration constants
JWT_ALGORITHM = "HS256"  # Symmetric — same key signs and verifies
COOKIE_NAME = "access_token"  # Name of the httpOnly cookie


def hash_password(plain_password: str) -> str:
    """
    Hash a plain text password using bcrypt.
    bcrypt automatically handles salt generation — each hash is unique
    even for the same password. Never store plain text passwords.

    Args:
        plain_password: The raw password from user input

    Returns:
        Bcrypt hash string (starts with $2b$)
    """
    pwd_bytes = plain_password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed_bytes = bcrypt.hashpw(pwd_bytes, salt)
    return hashed_bytes.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Compare a plain text password with its bcrypt hash.
    Returns True if they match, False otherwise.
    Used during login to validate user credentials.

    Args:
        plain_password: Raw password submitted in login form
        hashed_password: Stored bcrypt hash from database

    Returns:
        True if password matches, False otherwise
    """
    pwd_bytes = plain_password.encode('utf-8')
    hashed_bytes = hashed_password.encode('utf-8')
    return bcrypt.checkpw(pwd_bytes, hashed_bytes)


def create_access_token(user_id: str) -> str:
    """
    Create a JWT token containing the user's ID.
    Token expires after TOKEN_EXPIRY_HOURS (default 24 hours).

    Algorithm: HS256 — symmetric, single secret key for sign and verify.
    HS256 is perfect here since only our backend signs and verifies tokens.
    RS256 would be needed if multiple services verified tokens independently.

    Args:
        user_id: UUID string of the authenticated user

    Returns:
        Encoded JWT token string
    """
    expire = datetime.utcnow() + timedelta(hours=settings.TOKEN_EXPIRY_HOURS)
    payload = {
        "sub": user_id,       # Subject — the user this token belongs to
        "exp": expire,        # Expiration — token becomes invalid after this
        "iat": datetime.utcnow(),  # Issued at — when this token was created
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=JWT_ALGORITHM)


def decode_access_token(token: str) -> dict:
    """
    Decode and validate a JWT token.
    Returns payload dict containing user_id under 'sub' key.

    Raises:
        ValueError: If token is expired, tampered with, or malformed

    Args:
        token: The JWT token string from the cookie

    Returns:
        Decoded payload dict with 'sub' (user_id) key
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[JWT_ALGORITHM],
        )
        return payload
    except ExpiredSignatureError:
        raise ValueError("Token has expired. Please login again.")
    except JWTError:
        raise ValueError("Invalid token. Please login again.")


def set_auth_cookie(response: Response, token: str) -> None:
    """
    Set JWT as an httpOnly cookie on the HTTP response.

    Security settings explained:
    - httponly=True: JavaScript cannot read this cookie (XSS protection)
    - samesite='lax': Prevents CSRF attacks while allowing OAuth redirects
    - secure=False in dev: Must be True in production with HTTPS
    - max_age: Cookie expires with the JWT token

    Args:
        response: FastAPI Response object to set cookie on
        token: JWT token string to store in cookie
    """
    response.set_cookie(
        key=COOKIE_NAME,
        value=token,
        httponly=True,           # JS cannot access this cookie — XSS protection
        samesite="none",          # Blocks cross-site requests but allows OAuth redirects
        secure=True,  # True in production (requires HTTPS)
        max_age=settings.TOKEN_EXPIRY_HOURS * 3600,  # Convert hours to seconds
        path="/",                # Cookie available on all routes
    )


def clear_auth_cookie(response: Response) -> None:
    """
    Clear the auth cookie by setting max_age to 0.
    Called on logout to invalidate the session.
    The browser immediately removes cookies with max_age=0.

    Args:
        response: FastAPI Response object to clear cookie from
    """
    response.delete_cookie(
        key=COOKIE_NAME,
        httponly=True,
        samesite="none",
        secure=True,
        path="/",
    )
