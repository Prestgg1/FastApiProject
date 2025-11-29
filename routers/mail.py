# routers/mail_router.py
"""
Mail Router

Public endpoints for sending emails (contact form, etc.)
"""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr, Field

from services.mail_service import MailService


router = APIRouter(prefix="/mail", tags=["Mail"])


# ==========================================
# SCHEMAS
# ==========================================

class ContactRequest(BaseModel):
    """Contact form request schema."""
    
    name: str = Field(..., min_length=2, max_length=100, description="Sender name")
    email: EmailStr = Field(..., description="Sender email address")
    message: str = Field(..., min_length=10, max_length=1000, description="Message content")
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "Aysel Məmmədova",
                    "email": "aysel@example.com",
                    "message": "Salam, həkimlə görüş təyin etmək istəyirəm."
                }
            ]
        }
    }


class ContactResponse(BaseModel):
    """Contact form response schema."""
    
    success: bool = Field(..., description="Operation success status")
    message: str = Field(..., description="Response message")


class AppointmentConfirmationRequest(BaseModel):
    """Appointment confirmation email request."""
    
    patient_email: EmailStr = Field(..., description="Patient email")
    patient_name: str = Field(..., min_length=2, max_length=100)
    doctor_name: str = Field(..., min_length=2, max_length=100)
    appointment_date: str = Field(..., description="Appointment date (e.g., '15 Yanvar 2025')")
    appointment_time: str = Field(..., description="Appointment time (e.g., '14:30')")


class PasswordResetRequest(BaseModel):
    """Password reset email request."""
    
    email: EmailStr = Field(..., description="User email")
    user_name: str = Field(..., min_length=2, max_length=100)
    reset_link: str = Field(..., description="Password reset link")


class EmailResponse(BaseModel):
    """Generic email response."""
    
    success: bool
    message: str


# ==========================================
# ENDPOINTS
# ==========================================

@router.post(
    "/contact",
    response_model=ContactResponse,
    status_code=status.HTTP_200_OK,
    summary="Send contact form message",
    description="Send a message through the contact form. Email will be sent to admin.",
)
async def send_contact_message(data: ContactRequest) -> ContactResponse:
    """
    Send contact form message to admin.
    
    - **name**: Sender's full name (2-100 characters)
    - **email**: Sender's email address
    - **message**: Message content (10-1000 characters)
    
    Returns success status and message.
    """
    try:
        success = await MailService.send_contact_form(
            name=data.name,
            email=data.email,
            message=data.message,
        )
        
        if success:
            return ContactResponse(
                success=True,
                message="Mesajınız uğurla göndərildi. Tezliklə sizinlə əlaqə saxlanılacaq."
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Email göndərilə bilmədi. Zəhmət olmasa yenidən cəhd edin."
            )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Xəta baş verdi: {str(e)}"
        )


@router.post(
    "/appointment-confirmation",
    response_model=EmailResponse,
    status_code=status.HTTP_200_OK,
    summary="Send appointment confirmation email",
    description="Send appointment confirmation email to patient.",
)
async def send_appointment_confirmation(
    data: AppointmentConfirmationRequest
) -> EmailResponse:
    """
    Send appointment confirmation email to patient.
    
    This endpoint is typically called internally after appointment creation.
    """
    try:
        success = await MailService.send_appointment_confirmation(
            to_email=data.patient_email,
            patient_name=data.patient_name,
            doctor_name=data.doctor_name,
            appointment_date=data.appointment_date,
            appointment_time=data.appointment_time,
        )
        
        if success:
            return EmailResponse(
                success=True,
                message="Görüş təsdiqi emaili göndərildi."
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Email göndərilə bilmədi."
            )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Xəta baş verdi: {str(e)}"
        )


@router.post(
    "/password-reset",
    response_model=EmailResponse,
    status_code=status.HTTP_200_OK,
    summary="Send password reset email",
    description="Send password reset link to user's email.",
)
async def send_password_reset_email(data: PasswordResetRequest) -> EmailResponse:
    """
    Send password reset email.
    
    This endpoint is typically called when user requests password reset.
    """
    try:
        success = await MailService.send_password_reset(
            to_email=data.email,
            user_name=data.user_name,
            reset_link=data.reset_link,
        )
        
        if success:
            return EmailResponse(
                success=True,
                message="Şifrə sıfırlama linki emailinizə göndərildi."
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Email göndərilə bilmədi."
            )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Xəta baş verdi: {str(e)}"
        )


@router.get(
    "/health",
    response_model=dict,
    summary="Check email service health",
    description="Check if email service is configured correctly.",
)
async def check_email_health() -> dict:
    """
    Check email service health and configuration.
    
    Returns configuration status (without exposing sensitive data).
    """
    from services.mail_service import MailConfig
    
    is_configured = MailConfig.validate()
    
    return {
        "service": "email",
        "status": "operational" if is_configured else "not_configured",
        "configured": is_configured,
        "smtp_host": MailConfig.SMTP_HOST if MailConfig.SMTP_HOST else "not_set",
        "smtp_port": MailConfig.SMTP_PORT,
        "from_name": MailConfig.SMTP_FROM_NAME,
    }