from fastapi import APIRouter

from app.api.routes import login, private, users, utils
from app.config.config import settings

api_router = APIRouter()
api_router.include_router(login.router)
api_router.include_router(users.router)
api_router.include_router(utils.router)

# Conditionally register OAuth routes if Google OAuth is configured
if settings.is_google_oauth_configured:
    try:
        from app.auth.oauth.routes import router as oauth_router
        api_router.include_router(oauth_router)
    except ImportError:
        # OAuth not available, skip silently
        pass


if settings.ENVIRONMENT == "local":
    api_router.include_router(private.router)
