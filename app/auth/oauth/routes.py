"""
OAuth routes for third-party authentication (Google, etc.)
All endpoints validate configuration before executing.
"""

from datetime import timedelta
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from fastapi.responses import RedirectResponse
from sqlmodel import Session

from app.auth.deps import SessionDep
from app.auth.models import Token
from app.auth.oauth import (
    create_or_update_user_from_google,
    get_google_oauth_client,
    get_google_user_info,
    is_google_oauth_configured,
    link_google_account,
)
from app.auth.security import create_access_token
from app.auth import services as auth_services
from app.config.config import settings
from app.config.response import StandardResponse, success_response

router = APIRouter(prefix="/oauth", tags=["auth", "oauth"])


@router.get("/google/login")
async def google_login() -> RedirectResponse:
    """
    Initiate Google OAuth2 login flow.
    Redirects to Google's authorization page.
    """
    if not is_google_oauth_configured():
        raise HTTPException(
            status_code=503,
            detail="Google OAuth is not configured. Please configure GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, and GOOGLE_REDIRECT_URI",
        )

    client = get_google_oauth_client()
    if not client:
        raise HTTPException(
            status_code=503,
            detail="Google OAuth client could not be created",
        )

    # Generate authorization URL
    authorization_url, state = await client.create_authorization_url(
        "https://accounts.google.com/o/oauth2/v2/auth",
    )

    # Store state in session or return it for verification
    # For simplicity, we'll include it in the redirect
    return RedirectResponse(url=authorization_url)


@router.get("/google/callback")
async def google_callback(
    session: SessionDep,
    code: str = Query(...),
    state: str = Query(None),
) -> StandardResponse:
    """
    Handle Google OAuth2 callback.
    Creates or updates user and returns access token.
    """
    if not is_google_oauth_configured():
        raise HTTPException(
            status_code=503,
            detail="Google OAuth is not configured",
        )

    client = get_google_oauth_client()
    if not client:
        raise HTTPException(
            status_code=503,
            detail="Google OAuth client could not be created",
        )

    try:
        # Exchange authorization code for access token
        token_response = await client.fetch_token(
            "https://oauth2.googleapis.com/token",
            code=code,
        )

        access_token = token_response.get("access_token")
        if not access_token:
            raise HTTPException(status_code=400, detail="Failed to get access token from Google")

        # Get user info from Google
        google_user_info = await get_google_user_info(access_token)
        if not google_user_info:
            raise HTTPException(status_code=400, detail="Failed to get user info from Google")

        email = google_user_info.get("email")
        if not email:
            raise HTTPException(status_code=400, detail="Email not provided by Google")

        # Check if user already exists
        existing_user = auth_services.get_user_by_email(session=session, email=email)

        if existing_user:
            # Link Google account to existing user (if email matches)
            user = link_google_account(
                session=session,
                user=existing_user,
                google_user_info=google_user_info,
            )
        else:
            # Create new user from Google data
            user = create_or_update_user_from_google(
                session=session,
                google_user_info=google_user_info,
            )

        if not user:
            raise HTTPException(status_code=400, detail="Failed to create or update user")

        if not user.is_active:
            raise HTTPException(status_code=400, detail="User is inactive")

        # Generate JWT token for our API
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        api_token = create_access_token(user.id, expires_delta=access_token_expires)

        token_data = Token(access_token=api_token, token_type="bearer")
        response, status_code = success_response(
            data=token_data.model_dump(),
            message="Google OAuth login successful",
            status_code=200,
        )
        return Response(content=response.model_dump_json(), status_code=status_code, media_type="application/json")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"OAuth callback failed: {str(e)}")

