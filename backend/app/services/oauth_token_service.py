"""
OAuth Token Service — Store and invalidate OAuth tokens in SQL + MongoDB
"""

from datetime import datetime, timedelta, timezone

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.oauth_token import OAuthToken


def _token_expires_at(token: dict) -> datetime | None:
    """Normalize OAuth token expiry into a UTC datetime."""
    if not token:
        return None

    if token.get("expires_at"):
        try:
            return datetime.fromtimestamp(float(token["expires_at"]), tz=timezone.utc)
        except (TypeError, ValueError):
            return None

    if token.get("expires_in"):
        try:
            return datetime.now(tz=timezone.utc) + timedelta(
                seconds=int(token["expires_in"])
            )
        except (TypeError, ValueError):
            return None

    return None


async def save_oauth_token_sql(
    db: AsyncSession,
    user_id: str,
    provider: str,
    token: dict,
) -> OAuthToken:
    """Upsert OAuth token for a user/provider in SQL."""
    result = await db.execute(
        select(OAuthToken).where(
            OAuthToken.user_id == user_id,
            OAuthToken.provider == provider,
        )
    )
    existing = result.scalar_one_or_none()

    expires_at = _token_expires_at(token)

    if existing:
        existing.access_token = token.get("access_token", existing.access_token)
        existing.refresh_token = token.get("refresh_token")
        existing.token_type = token.get("token_type")
        existing.expires_at = expires_at
        await db.commit()
        await db.refresh(existing)
        return existing

    new_token = OAuthToken(
        user_id=user_id,
        provider=provider,
        access_token=token.get("access_token", ""),
        refresh_token=token.get("refresh_token"),
        token_type=token.get("token_type"),
        expires_at=expires_at,
    )
    db.add(new_token)
    await db.commit()
    await db.refresh(new_token)
    return new_token


async def delete_oauth_tokens_sql(
    db: AsyncSession,
    user_id: str,
    provider: str | None = None,
) -> None:
    """Delete OAuth tokens from SQL for a user (optionally provider-scoped)."""
    stmt = delete(OAuthToken).where(OAuthToken.user_id == user_id)
    if provider:
        stmt = stmt.where(OAuthToken.provider == provider)
    await db.execute(stmt)
    await db.commit()


async def save_oauth_token_mongo(
    mongo_db,
    user_id: str,
    provider: str,
    token: dict,
) -> None:
    """Upsert OAuth token for a user/provider in MongoDB."""
    expires_at = _token_expires_at(token)
    await mongo_db.oauth_tokens.update_one(
        {"user_id": user_id, "provider": provider},
        {
            "$set": {
                "access_token": token.get("access_token"),
                "refresh_token": token.get("refresh_token"),
                "token_type": token.get("token_type"),
                "expires_at": expires_at,
                "updated_at": datetime.now(tz=timezone.utc),
            },
            "$setOnInsert": {"created_at": datetime.now(tz=timezone.utc)},
        },
        upsert=True,
    )


async def delete_oauth_tokens_mongo(
    mongo_db,
    user_id: str,
    provider: str | None = None,
) -> None:
    """Delete OAuth tokens from MongoDB for a user (optionally provider-scoped)."""
    query = {"user_id": user_id}
    if provider:
        query["provider"] = provider
    await mongo_db.oauth_tokens.delete_many(query)
