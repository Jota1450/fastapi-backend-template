from datetime import timedelta
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.responses import HTMLResponse
from fastapi.security import OAuth2PasswordRequestForm

from app.auth import services as auth_services
from app.auth.deps import CurrentUser, SessionDep, get_current_active_superuser
from app.auth.security import create_access_token, get_password_hash
from app.auth.models import NewPassword, Token, UserPublic
from app.config.config import settings
from app.config.response import StandardResponse, error_response, success_response
from app.utils.utils import (
    generate_password_reset_token,
    generate_reset_password_email,
    send_email,
    verify_password_reset_token,
)

router = APIRouter(tags=["auth"])


@router.post("/login/access-token")
def login_access_token(
    session: SessionDep, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
) -> StandardResponse:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    user = auth_services.authenticate(
        session=session, email=form_data.username, password=form_data.password
    )
    if not user:
        response, status_code = error_response(
            message="Incorrect email or password",
            status_code=401,
        )
        return Response(content=response.model_dump_json(), status_code=status_code, media_type="application/json")
    elif not user.is_active:
        response, status_code = error_response(
            message="Inactive user",
            status_code=400,
        )
        return Response(content=response.model_dump_json(), status_code=status_code, media_type="application/json")
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    token = Token(
        access_token=create_access_token(
            user.id, expires_delta=access_token_expires
        )
    )
    response, status_code = success_response(
        data=token.model_dump(),
        message="Login successful",
        status_code=200,
    )
    return Response(content=response.model_dump_json(), status_code=status_code, media_type="application/json")


@router.post("/login/test-token")
def test_token(current_user: CurrentUser) -> StandardResponse:
    """
    Test access token
    """
    response, status_code = success_response(
        data=UserPublic.model_validate(current_user).model_dump(),
        message="Token is valid",
        status_code=200,
    )
    return Response(content=response.model_dump_json(), status_code=status_code, media_type="application/json")


@router.post("/password-recovery/{email}")
def recover_password(email: str, session: SessionDep) -> StandardResponse:
    """
    Password Recovery
    """
    user = auth_services.get_user_by_email(session=session, email=email)

    if not user:
        response, status_code = error_response(
            message="The user with this email does not exist in the system.",
            status_code=404,
        )
        return Response(content=response.model_dump_json(), status_code=status_code, media_type="application/json")
    
    password_reset_token = generate_password_reset_token(email=email)
    email_data = generate_reset_password_email(
        email_to=user.email, email=email, token=password_reset_token
    )
    send_email(
        email_to=user.email,
        subject=email_data.subject,
        html_content=email_data.html_content,
    )
    response, status_code = success_response(
        data=None,
        message="Password recovery email sent",
        status_code=200,
    )
    return Response(content=response.model_dump_json(), status_code=status_code, media_type="application/json")


@router.post("/reset-password/")
def reset_password(session: SessionDep, body: NewPassword) -> StandardResponse:
    """
    Reset password
    """
    email = verify_password_reset_token(token=body.token)
    if not email:
        response, status_code = error_response(
            message="Invalid token",
            status_code=400,
        )
        return Response(content=response.model_dump_json(), status_code=status_code, media_type="application/json")
    
    user = auth_services.get_user_by_email(session=session, email=email)
    if not user:
        response, status_code = error_response(
            message="The user with this email does not exist in the system.",
            status_code=404,
        )
        return Response(content=response.model_dump_json(), status_code=status_code, media_type="application/json")
    elif not user.is_active:
        response, status_code = error_response(
            message="Inactive user",
            status_code=400,
        )
        return Response(content=response.model_dump_json(), status_code=status_code, media_type="application/json")
    
    hashed_password = get_password_hash(password=body.new_password)
    user.hashed_password = hashed_password
    session.add(user)
    session.commit()
    response, status_code = success_response(
        data=None,
        message="Password updated successfully",
        status_code=200,
    )
    return Response(content=response.model_dump_json(), status_code=status_code, media_type="application/json")


@router.post(
    "/password-recovery-html-content/{email}",
    dependencies=[Depends(get_current_active_superuser)],
    response_class=HTMLResponse,
)
def recover_password_html_content(email: str, session: SessionDep) -> Any:
    """
    HTML Content for Password Recovery
    """
    user = auth_services.get_user_by_email(session=session, email=email)

    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this username does not exist in the system.",
        )
    password_reset_token = generate_password_reset_token(email=email)
    email_data = generate_reset_password_email(
        email_to=user.email, email=email, token=password_reset_token
    )

    return HTMLResponse(
        content=email_data.html_content, headers={"subject:": email_data.subject}
    )
