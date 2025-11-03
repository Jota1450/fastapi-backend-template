from fastapi import APIRouter, Depends, Response
from pydantic.networks import EmailStr

from app.api.deps import get_current_active_superuser
from app.config.response import StandardResponse, success_response
from app.utils.utils import generate_test_email, send_email

router = APIRouter(prefix="/utils", tags=["utils"])


@router.post(
    "/test-email/",
    dependencies=[Depends(get_current_active_superuser)],
)
def test_email(email_to: EmailStr) -> StandardResponse:
    """
    Test emails.
    """
    email_data = generate_test_email(email_to=email_to)
    send_email(
        email_to=email_to,
        subject=email_data.subject,
        html_content=email_data.html_content,
    )
    response, status_code = success_response(
        data=None,
        message="Test email sent",
        status_code=201,
    )
    return Response(content=response.model_dump_json(), status_code=status_code, media_type="application/json")


@router.get("/health-check/")
async def health_check() -> StandardResponse:
    response, status_code = success_response(
        data={"status": "healthy"},
        message="Service is healthy",
        status_code=200,
    )
    return Response(content=response.model_dump_json(), status_code=status_code, media_type="application/json")
