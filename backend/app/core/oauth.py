"""
OAuth2 Client Configuration — Google and Facebook with Authlib
"""
import logging
from authlib.integrations.starlette_client import OAuth
from authlib.oauth2.rfc6749.errors import MismatchingStateException, OAuth2Error

from app.core.config import settings

logger = logging.getLogger(__name__)

# Remove custom cache entirely
# Authlib will use the request.session automatically
oauth = OAuth()

# ── Google OAuth2 ────────────────────────────────────────
oauth.register(
    name="google",
    client_id=settings.GOOGLE_CLIENT_ID,
    client_secret=settings.GOOGLE_CLIENT_SECRET,
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    redirect_uri=settings.GOOGLE_REDIRECT_URI, 
    client_kwargs={
        "scope": "openid email profile",
    },
)

# ── Facebook OAuth2 ─────────────────────────────────────
oauth.register(
    name="facebook",
    client_id=settings.FACEBOOK_CLIENT_ID,
    client_secret=settings.FACEBOOK_CLIENT_SECRET,
    access_token_url="https://graph.facebook.com/oauth/access_token",
    authorize_url="https://www.facebook.com/dialog/oauth",
    api_base_url="https://graph.facebook.com/",
    client_kwargs={
        "scope": "email public_profile",
    },
)

async def get_google_user_info(token: dict, oauth_client=None) -> dict:
    user_info = token.get("userinfo") or {}

    if not user_info.get("email") and oauth_client is not None:
        try:
            response = await oauth_client.get(
                "https://openidconnect.googleapis.com/v1/userinfo",
                token=token,
            )
            user_info = response.json()
        except Exception as error:
            logger.warning(f"Google userinfo fetch failed: {error}")
            user_info = user_info or {}

    email = user_info.get("email")
    name = user_info.get("name") or (email.split("@")[0] if email else "User")

    return {
        "email": email,
        "name": name,
        "picture": user_info.get("picture"),
        "provider_id": user_info.get("sub"),
    }

OAuthStateErrors = (MismatchingStateException, OAuth2Error)

async def get_facebook_user_info(token: dict, oauth_client) -> dict:
    response = await oauth_client.get(
        "me",
        params={"fields": "id,name,email,picture.type(large)"},
        token=token,
    )
    user_data = response.json()

    picture_url = None
    if "picture" in user_data and "data" in user_data["picture"]:
        picture_url = user_data["picture"]["data"].get("url")

    return {
        "email": user_data.get("email"),
        "name": user_data.get("name"),
        "picture": picture_url,
        "provider_id": str(user_data.get("id")), 
    }