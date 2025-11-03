"""
OAuth module for third-party authentication providers (Google, etc.)
All OAuth functionality is optional - the application works without it.
"""

from app.config.config import settings

# Export configuration check function
def is_google_oauth_configured() -> bool:
    """Check if Google OAuth is fully configured"""
    return settings.is_google_oauth_configured

# Conditionally export Google OAuth functions if available
if is_google_oauth_configured():
    try:
        from app.auth.oauth.google import (
            get_google_oauth_client,
            get_google_user_info,
            create_or_update_user_from_google,
            link_google_account,
        )
        __all__ = [
            "is_google_oauth_configured",
            "get_google_oauth_client",
            "get_google_user_info",
            "create_or_update_user_from_google",
            "link_google_account",
        ]
    except ImportError:
        __all__ = ["is_google_oauth_configured"]
else:
    __all__ = ["is_google_oauth_configured"]

