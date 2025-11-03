"""
Google OAuth2 implementation
All functions handle gracefully when OAuth is not configured (return None, don't raise exceptions)
"""

import json
from typing import Any, Optional

import httpx
from authlib.integrations.httpx_client import AsyncOAuth2Client

from app.auth.models import User, UserCreate
from app.auth.services import create_user, get_user_by_email
from app.config.config import settings
from sqlmodel import Session


def is_google_oauth_configured() -> bool:
    """Check if Google OAuth is fully configured"""
    return settings.is_google_oauth_configured


def get_google_oauth_client() -> Optional[AsyncOAuth2Client]:
    """
    Get Google OAuth2 client instance.
    Returns None if Google OAuth is not configured.
    """
    if not is_google_oauth_configured():
        return None

    return AsyncOAuth2Client(
        client_id=settings.GOOGLE_CLIENT_ID,
        client_secret=settings.GOOGLE_CLIENT_SECRET,
        redirect_uri=settings.GOOGLE_REDIRECT_URI,
        scope="openid email profile",
    )


async def get_google_user_info(access_token: str) -> Optional[dict[str, Any]]:
    """
    Get user information from Google using access token.
    Returns None if OAuth is not configured or if the request fails.
    """
    if not is_google_oauth_configured():
        return None

    try:
        # Use Google's userinfo endpoint
        async with httpx.AsyncClient() as http_client:
            resp = await http_client.get(
                "https://www.googleapis.com/oauth2/v2/userinfo",
                headers={"Authorization": f"Bearer {access_token}"},
            )
            resp.raise_for_status()
            return resp.json()
    except Exception:
        return None


def create_or_update_user_from_google(
    *, session: Session, google_user_info: dict[str, Any]
) -> Optional[User]:
    """
    Create or update user from Google OAuth data.
    Creates new user if email doesn't exist, updates if it does.
    Returns None if OAuth is not configured.
    """
    if not is_google_oauth_configured():
        return None

    try:
        email = google_user_info.get("email")
        if not email:
            return None

        # Check if user already exists
        existing_user = get_user_by_email(session=session, email=email)

        # Prepare OAuth data as JSON string
        oauth_data = json.dumps(google_user_info)

        if existing_user:
            # Update existing user with Google data
            existing_user.avatar_url = google_user_info.get("picture")
            existing_user.full_name = google_user_info.get("name") or existing_user.full_name
            existing_user.oauth_provider_data = oauth_data
            session.add(existing_user)
            session.commit()
            session.refresh(existing_user)
            return existing_user
        else:
            # Create new user from Google data
            user_create = UserCreate(
                email=email,
                password=None,  # OAuth users don't have password
                full_name=google_user_info.get("name"),
            )
            user = create_user(session=session, user_create=user_create)

            # Update with OAuth-specific data
            user.avatar_url = google_user_info.get("picture")
            user.oauth_provider_data = oauth_data
            session.add(user)
            session.commit()
            session.refresh(user)
            return user
    except Exception:
        return None


def link_google_account(*, session: Session, user: User, google_user_info: dict[str, Any]) -> Optional[User]:
    """
    Link Google account to existing user.
    Updates user with Google OAuth data.
    Returns None if OAuth is not configured.
    """
    if not is_google_oauth_configured():
        return None

    try:
        # Prepare OAuth data as JSON string
        oauth_data = json.dumps(google_user_info)

        # Update user with Google data
        if not user.avatar_url:
            user.avatar_url = google_user_info.get("picture")
        if not user.full_name:
            user.full_name = google_user_info.get("name")
        user.oauth_provider_data = oauth_data

        session.add(user)
        session.commit()
        session.refresh(user)
        return user
    except Exception:
        return None

