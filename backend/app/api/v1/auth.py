"""
Auth API Routes — Registration, Login, Logout, Google OAuth, Facebook OAuth

Authentication flow:
1. User registers with name, email, password → account created
2. On login, bcrypt.verify compares submitted password with stored hash
3. If valid, create JWT token with user_id, set in httpOnly cookie
4. Every protected request reads cookie → decodes JWT → gets user
5. On logout, clear the cookie (max_age=0)

OAuth flow (Google/Facebook):
1. Frontend redirects user to GET /auth/{provider}/login
2. User approves on provider's consent screen
3. Provider redirects to our callback with auth code
4. We exchange code for token, get user profile
5. Find or create user in database
6. Set JWT cookie, redirect to frontend
"""

import logging
from urllib.parse import quote

from authlib.integrations.base_client.errors import MismatchingStateError, OAuthError
from authlib.oauth2.rfc6749.errors import MismatchingStateException, OAuth2Error
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse, RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db, get_current_user, get_current_user_optional, get_mongo_db
from app.core.security import (
    create_access_token,
    set_auth_cookie,
    clear_auth_cookie,
    verify_password,
)
from app.core.oauth import (
    oauth,
    get_google_user_info,
    get_facebook_user_info,
    #google_console_redirect_uris,
)
from app.core.config import settings
from app.db.models.user import User
from app.schemas.auth import RegisterSchema, LoginSchema, UserResponse
from app.services.auth_service import (
    register_user,
    get_user_by_email,
    find_or_create_oauth_user,
)
from app.services.oauth_token_service import (
    save_oauth_token_sql,
    save_oauth_token_mongo,
    delete_oauth_tokens_sql,
    delete_oauth_tokens_mongo,
)

logger = logging.getLogger(__name__)

router = APIRouter()


# ── Helper: Standard JSON response ──────────────────────
def success_response(message: str, data=None, status_code: int = 200):
    """Create a standard success response with consistent format."""
    return JSONResponse(
        status_code=status_code,
        content={
            "success": True,
            "message": message,
            "data": data,
        },
    )


def error_response(message: str, status_code: int = 400):
    """Create a standard error response with consistent format."""
    return JSONResponse(
        status_code=status_code,
        content={
            "success": False,
            "message": message,
            "data": None,
        },
    )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# LOCAL AUTH ENDPOINTS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


@router.post("/register")
async def register(body: RegisterSchema, db: AsyncSession = Depends(get_db)):
    """
    Register a new user with email and password.
    Returns user data and sets httpOnly auth cookie.
    """
    try:
        # Check if email is already taken
        existing = await get_user_by_email(db, body.email)
        if existing:
            return error_response("Email already registered. Please login instead.")

        # Create user with hashed password
        user = await register_user(db, body.full_name, body.email, body.password)

        # Create JWT and set in httpOnly cookie
        token = create_access_token(user.id)
        user_data = UserResponse.model_validate(user).model_dump(mode="json")

        response = success_response(
            "Account created successfully",
            data=user_data,
            status_code=201,
        )
        set_auth_cookie(response, token)
        return response

    except Exception as error:
        logger.error(f"Registration failed: {error}")
        return error_response("Registration failed. Please try again.", 500)


@router.post("/login")
async def login(body: LoginSchema, db: AsyncSession = Depends(get_db)):
    """
    Login with email and password.
    Validates credentials, creates JWT, sets httpOnly cookie.
    """
    try:
        # Find user by email — use same error message for email/password
        # to prevent attackers from knowing which emails are registered
        user = await get_user_by_email(db, body.email)

        if not user:
            return error_response("Invalid email or password.", 401)

        # Check if this user registered via OAuth (no local password)
        if user.auth_provider != "local" and not user.password_hash:
            provider = user.auth_provider.capitalize()
            return error_response(
                f"This email is registered with {provider}. "
                f"Please use {provider} login.",
                400,
            )

        # Verify password with bcrypt
        if not verify_password(body.password, user.password_hash):
            return error_response("Invalid email or password.", 401)

        # Create JWT and set cookie
        token = create_access_token(user.id)
        user_data = UserResponse.model_validate(user).model_dump(mode="json")

        response = success_response("Login successful", data=user_data)
        set_auth_cookie(response, token)
        return response

    except Exception as error:
        logger.error(f"Login failed: {error}")
        return error_response("Login failed. Please try again.", 500)


@router.post("/logout")
async def logout(
    request: Request,
    db: AsyncSession = Depends(get_db),
    mongo_db=Depends(get_mongo_db),
    current_user: User | None = Depends(get_current_user_optional),
):
    """
    Logout by clearing the httpOnly auth cookie.
    Setting max_age=0 tells the browser to remove the cookie immediately.
    """
    if current_user:
        await delete_oauth_tokens_sql(db, current_user.id)
        await delete_oauth_tokens_mongo(mongo_db, current_user.id)

    # Clear OAuth state and session data
    request.session.clear()

    response = success_response(
        "Logged out successfully",
        data={"clear_client_storage": True},
    )
    clear_auth_cookie(response)
    return response


@router.get("/me")
async def get_me(current_user: User = Depends(get_current_user)):
    """
    Get current authenticated user's profile.
    Used by frontend on page load to restore auth state from cookie.
    """
    user_data = UserResponse.model_validate(current_user).model_dump(mode="json")
    return success_response("User fetched", data=user_data)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# GOOGLE OAUTH ENDPOINTS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


@router.get("/google/oauth-config")
async def google_oauth_config(request: Request):
    return success_response(
        "Add this exact URI under Credentials → OAuth 2.0 Client → Authorized redirect URIs",
        data={
            "exact_redirect_uri_required": settings.GOOGLE_REDIRECT_URI,
            "authorized_javascript_origin": settings.FRONTEND_URL.rstrip("/"),
            "login_url": f"{settings.BACKEND_URL}/api/v1/auth/google/login",
        },
    )


@router.get("/google/login")
async def google_login(request: Request):
    if not settings.GOOGLE_CLIENT_ID or not settings.GOOGLE_CLIENT_SECRET:
        logger.error("Google OAuth: missing client ID or secret in .env")
        return RedirectResponse(f"{settings.FRONTEND_URL}/login?error=oauth_not_configured")

    # Use the static URI directly from settings
    redirect_uri = settings.GOOGLE_REDIRECT_URI.rstrip("/")
    return await oauth.google.authorize_redirect(request, redirect_uri)


@router.get("/google/callback")
async def google_callback(
    request: Request,
    db: AsyncSession = Depends(get_db),
    mongo_db=Depends(get_mongo_db),
):
    """
    Handle Google's OAuth callback after user approves.

    Flow:
    1. Authlib exchanges auth code for access token (server-to-server)
    2. Extract user info from Google's ID token
    3. Find existing user or create new one
    4. Set JWT cookie and redirect to frontend
    """
    try:
        # Authlib reads redirect_uri + state from the session cookie set at /google/login
        logger.info(
            "Google OAuth callback: state=%s session_keys=%s",
            request.query_params.get("state"),
            list(request.session.keys()),
        )
        token = await oauth.google.authorize_access_token(request)
        user_info = await get_google_user_info(token, oauth.google)

        if not user_info.get("email"):
            logger.error("Google OAuth: no email returned")
            return RedirectResponse(f"{settings.FRONTEND_URL}/login?error=no_email")

        # Find or create user in our database
        user = await find_or_create_oauth_user(
            db=db,
            email=user_info["email"],
            full_name=user_info.get("name", ""),
            avatar_url=user_info.get("picture"),
            provider="google",
            provider_id=user_info.get("provider_id", ""),
        )

        # Replace any stale OAuth tokens before saving the fresh one
        await delete_oauth_tokens_sql(db, user.id, provider="google")
        await delete_oauth_tokens_mongo(mongo_db, user.id, provider="google")
        await save_oauth_token_sql(db, user.id, "google", token)
        await save_oauth_token_mongo(mongo_db, user.id, "google", token)

        # Create JWT and set cookie, then redirect to frontend
        jwt_token = create_access_token(user.id)
        response = RedirectResponse(f"{settings.FRONTEND_URL}/auth/callback")
        set_auth_cookie(response, jwt_token)
        return response

    except (MismatchingStateError, MismatchingStateException):
        logger.error(
            "Google OAuth: state missing — retry sign-in without restarting the API"
        )
        return RedirectResponse(
            f"{settings.FRONTEND_URL}/login?error=oauth_state_lost"
        )
    except (OAuthError, OAuth2Error) as error:
        logger.error(f"Google OAuth provider error: {error}")
        err_code = getattr(error, "error", None) or "oauth_denied"
        detail = quote(str(getattr(error, "description", None) or err_code)[:200])
        if err_code == "redirect_uri_mismatch":
            return RedirectResponse(
                f"{settings.FRONTEND_URL}/login?error=redirect_uri_mismatch"
            )
        return RedirectResponse(
            f"{settings.FRONTEND_URL}/login?error=oauth_denied&detail={detail}"
        )
    except Exception as error:
        logger.error(f"Google OAuth callback failed: {error}", exc_info=True)
        detail = quote(str(error)[:200])
        return RedirectResponse(
            f"{settings.FRONTEND_URL}/login?error=oauth_failed&detail={detail}"
        )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# FACEBOOK OAUTH ENDPOINTS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


@router.get("/facebook/login")
async def facebook_login(request: Request):
    """
    Redirect user to Facebook's OAuth consent screen.
    Identical pattern to Google — Authlib abstracts the differences.
    """
    redirect_uri = settings.FACEBOOK_REDIRECT_URI
    return await oauth.facebook.authorize_redirect(request, redirect_uri)


@router.get("/facebook/callback")
async def facebook_callback(
    request: Request,
    db: AsyncSession = Depends(get_db),
    mongo_db=Depends(get_mongo_db),
):
    """
    Handle Facebook's OAuth callback after user approves.

    Same flow as Google callback but uses Facebook Graph API
    to fetch user profile information.
    """
    try:
        # Exchange auth code for token
        token = await oauth.facebook.authorize_access_token(request)

        # Fetch profile from Facebook Graph API (requires separate API call)
        user_info = await get_facebook_user_info(token, oauth.facebook)

        if not user_info.get("email"):
            logger.error("Facebook OAuth: no email returned")
            return RedirectResponse(f"{settings.FRONTEND_URL}/login?error=no_email")

        # Find or create user
        user = await find_or_create_oauth_user(
            db=db,
            email=user_info["email"],
            full_name=user_info.get("name", ""),
            avatar_url=user_info.get("picture"),
            provider="facebook",
            provider_id=user_info.get("provider_id", ""),
        )

        # Replace any stale OAuth tokens before saving the fresh one
        await delete_oauth_tokens_sql(db, user.id, provider="facebook")
        await delete_oauth_tokens_mongo(mongo_db, user.id, provider="facebook")
        await save_oauth_token_sql(db, user.id, "facebook", token)
        await save_oauth_token_mongo(mongo_db, user.id, "facebook", token)

        # Set cookie and redirect
        jwt_token = create_access_token(user.id)
        response = RedirectResponse(f"{settings.FRONTEND_URL}/auth/callback")
        set_auth_cookie(response, jwt_token)
        return response

    except Exception as error:
        logger.error(f"Facebook OAuth callback failed: {error}")
        return RedirectResponse(f"{settings.FRONTEND_URL}/login?error=oauth_failed")
