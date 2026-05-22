"""
Auth Service — Business logic for user registration, login, and OAuth

This service layer handles all authentication logic:
- Creating new users with hashed passwords
- Validating login credentials
- Finding or creating OAuth users (Google/Facebook)

The router layer only handles HTTP — all business logic lives here.
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.user import User
from app.core.security import hash_password, verify_password


async def register_user(
    db: AsyncSession,
    full_name: str,
    email: str,
    password: str,
) -> User:
    """
    Create a new user with a bcrypt-hashed password.

    Args:
        db: Async MySQL session
        full_name: User's display name
        email: User's email (must be unique)
        password: Plain text password (will be hashed before storage)

    Returns:
        Created User object

    Note:
        Email uniqueness is checked in the router before calling this.
        We hash the password here — plain text NEVER touches the database.
    """
    user = User(
        full_name=full_name.strip(),
        email=email.lower().strip(),
        password_hash=hash_password(password),
        auth_provider="local",
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    """
    Find a user by email address.
    Returns None if no user exists with this email.

    Args:
        db: Async MySQL session
        email: Email to search for (case-insensitive)

    Returns:
        User object or None
    """
    result = await db.execute(
        select(User).where(User.email == email.lower().strip())
    )
    return result.scalar_one_or_none()


async def find_or_create_oauth_user(
    db: AsyncSession,
    email: str,
    full_name: str,
    avatar_url: str | None,
    provider: str,
    provider_id: str,
) -> User:
    """
    Find existing user by email OR create new OAuth user.

    This handles both Google and Facebook with the same function.

    Logic:
    1. Query: SELECT user WHERE email = email
    2. If found:
       - Update avatar_url if changed (user may have updated their Google photo)
       - Update auth_provider and provider_id if this is a new OAuth provider
       - Return existing user
    3. If not found:
       - Create new User with auth_provider=provider, password_hash=None
       - Set avatar_url from OAuth profile picture
       - Return new user

    Why same email = same user:
    If someone registered with email/password and now logs in with Google using
    the same email, we link the accounts automatically. This is the standard
    behavior in most modern apps (GitHub, Notion, etc. all do this).

    Args:
        db: Async MySQL session
        email: Email from OAuth provider
        full_name: Display name from OAuth provider
        avatar_url: Profile picture URL from OAuth provider
        provider: 'google' or 'facebook'
        provider_id: Unique ID from the OAuth provider

    Returns:
        Existing or newly created User object
    """
    # Check if user already exists with this email
    existing_user = await get_user_by_email(db, email)

    if existing_user:
        # Update profile info from OAuth provider
        # User might have changed their Google/Facebook profile picture
        if avatar_url:
            existing_user.avatar_url = avatar_url
        if provider_id:
            existing_user.provider_id = provider_id
        # If they originally signed up locally, update to show they've used OAuth too
        if existing_user.auth_provider == "local":
            existing_user.auth_provider = provider

        await db.commit()
        await db.refresh(existing_user)
        return existing_user

    # Create new user — no password since they authenticated via OAuth
    new_user = User(
        full_name=full_name,
        email=email.lower().strip(),
        password_hash=None,  # OAuth users don't have a local password
        avatar_url=avatar_url,
        auth_provider=provider,
        provider_id=provider_id,
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user
