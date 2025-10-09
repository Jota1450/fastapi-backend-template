from collections.abc import Generator
from typing import Annotated

from fastapi import Depends
from sqlmodel import Session

from app.auth.deps import CurrentUser, SessionDep, get_current_active_superuser
from app.config.db import engine


def get_db() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session


# Re-export auth dependencies for backward compatibility
__all__ = ["get_db", "SessionDep", "CurrentUser", "get_current_active_superuser"]
