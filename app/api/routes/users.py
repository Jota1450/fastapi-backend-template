import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlmodel import func, select

from app.auth import services as auth_services
from app.auth.deps import (
    CurrentUser,
    SessionDep,
    get_current_active_superuser,
)
from app.auth.models import (
    UpdatePassword,
    User,
    UserCreate,
    UserPublic,
    UserRegister,
    UserUpdate,
    UserUpdateMe,
)
from app.auth.security import get_password_hash, verify_password
from app.config.config import settings
from app.config.response import StandardResponse, error_response, success_response
from app.utils.utils import generate_new_account_email, send_email

router = APIRouter(prefix="/users", tags=["users"])


@router.get(
    "/",
    dependencies=[Depends(get_current_active_superuser)],
)
def read_users(session: SessionDep, skip: int = 0, limit: int = 100) -> StandardResponse:
    """
    Retrieve users.
    """

    count_statement = select(func.count()).select_from(User)
    count = session.exec(count_statement).one()

    statement = select(User).offset(skip).limit(limit)
    users = session.exec(statement).all()

    users_data = [UserPublic.model_validate(user).model_dump() for user in users]
    response, status_code = success_response(
        data={"items": users_data, "count": count},
        message="Users retrieved successfully",
        status_code=200,
    )
    return Response(content=response.model_dump_json(), status_code=status_code, media_type="application/json")


@router.post(
    "/", dependencies=[Depends(get_current_active_superuser)]
)
def create_user(*, session: SessionDep, user_in: UserCreate) -> StandardResponse:
    """
    Create new user.
    """
    user = auth_services.get_user_by_email(session=session, email=user_in.email)
    if user:
        response, status_code = error_response(
            message="The user with this email already exists in the system.",
            status_code=400,
        )
        return Response(content=response.model_dump_json(), status_code=status_code, media_type="application/json")

    user = auth_services.create_user(session=session, user_create=user_in)
    if settings.emails_enabled and user_in.email:
        email_data = generate_new_account_email(
            email_to=user_in.email, username=user_in.email, password=user_in.password
        )
        send_email(
            email_to=user_in.email,
            subject=email_data.subject,
            html_content=email_data.html_content,
        )
    response, status_code = success_response(
        data=UserPublic.model_validate(user).model_dump(),
        message="User created successfully",
        status_code=200,
    )
    return Response(content=response.model_dump_json(), status_code=status_code, media_type="application/json")


@router.patch("/me")
def update_user_me(
    *, session: SessionDep, user_in: UserUpdateMe, current_user: CurrentUser
) -> StandardResponse:
    """
    Update own user.
    """

    if user_in.email:
        existing_user = auth_services.get_user_by_email(session=session, email=user_in.email)
        if existing_user and existing_user.id != current_user.id:
            response, status_code = error_response(
                message="User with this email already exists",
                status_code=409,
            )
            return Response(content=response.model_dump_json(), status_code=status_code, media_type="application/json")
    
    user_data = user_in.model_dump(exclude_unset=True)
    current_user.sqlmodel_update(user_data)
    session.add(current_user)
    session.commit()
    session.refresh(current_user)
    response, status_code = success_response(
        data=UserPublic.model_validate(current_user).model_dump(),
        message="User updated successfully",
        status_code=200,
    )
    return Response(content=response.model_dump_json(), status_code=status_code, media_type="application/json")


@router.patch("/me/password")
def update_password_me(
    *, session: SessionDep, body: UpdatePassword, current_user: CurrentUser
) -> StandardResponse:
    """
    Update own password.
    """
    if not verify_password(body.current_password, current_user.hashed_password):
        response, status_code = error_response(
            message="Incorrect password",
            status_code=400,
        )
        return Response(content=response.model_dump_json(), status_code=status_code, media_type="application/json")
    
    if body.current_password == body.new_password:
        response, status_code = error_response(
            message="New password cannot be the same as the current one",
            status_code=400,
        )
        return Response(content=response.model_dump_json(), status_code=status_code, media_type="application/json")
    
    hashed_password = get_password_hash(body.new_password)
    current_user.hashed_password = hashed_password
    session.add(current_user)
    session.commit()
    response, status_code = success_response(
        data=None,
        message="Password updated successfully",
        status_code=200,
    )
    return Response(content=response.model_dump_json(), status_code=status_code, media_type="application/json")


@router.get("/me")
def read_user_me(current_user: CurrentUser) -> StandardResponse:
    """
    Get current user.
    """
    response, status_code = success_response(
        data=UserPublic.model_validate(current_user).model_dump(),
        message="User retrieved successfully",
        status_code=200,
    )
    return Response(content=response.model_dump_json(), status_code=status_code, media_type="application/json")


@router.delete("/me")
def delete_user_me(session: SessionDep, current_user: CurrentUser) -> StandardResponse:
    """
    Delete own user.
    """
    if current_user.is_superuser:
        response, status_code = error_response(
            message="Super users are not allowed to delete themselves",
            status_code=403,
        )
        return Response(content=response.model_dump_json(), status_code=status_code, media_type="application/json")
    
    session.delete(current_user)
    session.commit()
    response, status_code = success_response(
        data=None,
        message="User deleted successfully",
        status_code=200,
    )
    return Response(content=response.model_dump_json(), status_code=status_code, media_type="application/json")


@router.post("/signup", tags=["auth"])
def register_user(session: SessionDep, user_in: UserRegister) -> StandardResponse:
    """
    Create new user without the need to be logged in.
    """
    user = auth_services.get_user_by_email(session=session, email=user_in.email)
    if user:
        response, status_code = error_response(
            message="The user with this email already exists in the system",
            status_code=400,
        )
        return Response(content=response.model_dump_json(), status_code=status_code, media_type="application/json")
    
    user_create = UserCreate.model_validate(user_in)
    user = auth_services.create_user(session=session, user_create=user_create)
    response, status_code = success_response(
        data=UserPublic.model_validate(user).model_dump(),
        message="User registered successfully",
        status_code=200,
    )
    return Response(content=response.model_dump_json(), status_code=status_code, media_type="application/json")


@router.get("/{user_id}")
def read_user_by_id(
    user_id: uuid.UUID, session: SessionDep, current_user: CurrentUser
) -> StandardResponse:
    """
    Get a specific user by id.
    """
    user = session.get(User, user_id)
    if not user:
        response, status_code = error_response(
            message="User not found",
            status_code=404,
        )
        return Response(content=response.model_dump_json(), status_code=status_code, media_type="application/json")
    
    if user == current_user:
        response, status_code = success_response(
            data=UserPublic.model_validate(user).model_dump(),
            message="User retrieved successfully",
            status_code=200,
        )
        return Response(content=response.model_dump_json(), status_code=status_code, media_type="application/json")
    
    if not current_user.is_superuser:
        response, status_code = error_response(
            message="The user doesn't have enough privileges",
            status_code=403,
        )
        return Response(content=response.model_dump_json(), status_code=status_code, media_type="application/json")
    
    response, status_code = success_response(
        data=UserPublic.model_validate(user).model_dump(),
        message="User retrieved successfully",
        status_code=200,
    )
    return Response(content=response.model_dump_json(), status_code=status_code, media_type="application/json")


@router.patch(
    "/{user_id}",
    dependencies=[Depends(get_current_active_superuser)],
)
def update_user(
    *,
    session: SessionDep,
    user_id: uuid.UUID,
    user_in: UserUpdate,
) -> StandardResponse:
    """
    Update a user.
    """

    db_user = session.get(User, user_id)
    if not db_user:
        response, status_code = error_response(
            message="The user with this id does not exist in the system",
            status_code=404,
        )
        return Response(content=response.model_dump_json(), status_code=status_code, media_type="application/json")
    
    if user_in.email:
        existing_user = auth_services.get_user_by_email(session=session, email=user_in.email)
        if existing_user and existing_user.id != user_id:
            response, status_code = error_response(
                message="User with this email already exists",
                status_code=409,
            )
            return Response(content=response.model_dump_json(), status_code=status_code, media_type="application/json")

    db_user = auth_services.update_user(session=session, db_user=db_user, user_in=user_in)
    response, status_code = success_response(
        data=UserPublic.model_validate(db_user).model_dump(),
        message="User updated successfully",
        status_code=200,
    )
    return Response(content=response.model_dump_json(), status_code=status_code, media_type="application/json")


@router.delete("/{user_id}", dependencies=[Depends(get_current_active_superuser)])
def delete_user(
    session: SessionDep, current_user: CurrentUser, user_id: uuid.UUID
) -> StandardResponse:
    """
    Delete a user.
    """
    user = session.get(User, user_id)
    if not user:
        response, status_code = error_response(
            message="User not found",
            status_code=404,
        )
        return Response(content=response.model_dump_json(), status_code=status_code, media_type="application/json")
    
    if user == current_user:
        response, status_code = error_response(
            message="Super users are not allowed to delete themselves",
            status_code=403,
        )
        return Response(content=response.model_dump_json(), status_code=status_code, media_type="application/json")
    
    session.delete(user)
    session.commit()
    response, status_code = success_response(
        data=None,
        message="User deleted successfully",
        status_code=200,
    )
    return Response(content=response.model_dump_json(), status_code=status_code, media_type="application/json")
