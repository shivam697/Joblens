"""
FastAPI Dependencies — Reusable dependency injection functions

These functions are injected into route handlers using FastAPI's Depends() system.
They handle cross-cutting concerns like database sessions, auth validation,
and MongoDB access so route handlers can focus on business logic.
"""

from typing import AsyncGenerator

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.mysql import async_session_factory
from app.db.mongodb import get_mongo_database
from app.db.models.user import User
from app.core.security import decode_access_token, COOKIE_NAME


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency that provides an async MySQL session.
    Automatically closes session when request is complete.

    Usage in route:
        async def my_route(db: AsyncSession = Depends(get_db)):

    The 'yield' pattern ensures the session is properly closed even if
    an exception occurs during request processing.
    """
    async with async_session_factory() as session:
        yield session


def get_mongo_db():
    """
    FastAPI dependency that returns the MongoDB database instance.
    Motor handles connection pooling internally — no session management needed.

    Usage in route:
        async def my_route(mongo = Depends(get_mongo_db)):
    """
    return get_mongo_database()


async def get_current_user(
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    FastAPI dependency that validates the session and returns current user.

    Steps:
    1. Read 'access_token' from httpOnly cookie in request
    2. If no cookie found, raise 401 — user is not logged in
    3. Decode JWT using decode_access_token()
    4. Extract user_id from token payload['sub']
    5. Query MySQL for user by id
    6. If user not found or inactive, raise 401
    7. Return user object — available in all protected route functions

    This dependency is added to every protected endpoint:
        current_user: User = Depends(get_current_user)

    Args:
        request: FastAPI Request containing cookies
        db: Async MySQL session (auto-injected)

    Returns:
        User object from database

    Raises:
        HTTPException 401: If not authenticated or token invalid
    """
    # Step 1: Read JWT from httpOnly cookie
    token = request.cookies.get(COOKIE_NAME)

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Please login to continue.",
        )

    # Step 2: Decode and validate the JWT token
    try:
        payload = decode_access_token(token)
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(error),
        )

    # Step 3: Extract user_id from token payload
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload.",
        )

    # Step 4: Fetch user from database
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    # Step 5: Validate user exists and is active
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found. Please login again.",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account is deactivated. Contact support.",
        )

    return user


async def get_current_user_optional(
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> User | None:
    """
    Best-effort auth lookup. Returns None when no valid session is present.
    Useful for logout flows where we want to clear stored tokens if possible.
    """
    token = request.cookies.get(COOKIE_NAME)
    if not token:
        return None

    try:
        payload = decode_access_token(token)
    except ValueError:
        return None

    user_id = payload.get("sub")
    if not user_id:
        return None

    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()
