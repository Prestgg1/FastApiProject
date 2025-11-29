# services/mail_service.py
"""
Mail Service Module

Professional email service with HTML support, templates, and error handling.
Supports both plain text and HTML emails with attachments.
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import Optional, List
from pathlib import Path
import os
import logging

from pydantic import EmailStr

# Configure logging
logger = logging.getLogger(__name__)


class MailConfig:
    """
    Email configuration from environment variables.
    
    Environment Variables:
        SMTP_HOST: SMTP server host (e.g., smtp.gmail.com)
        SMTP_PORT: SMTP server port (default: 587)
        SMTP_USER: SMTP username/email
        SMTP_PASS: SMTP password/app password
        SMTP_FROM_NAME: Sender display name (default: "ŞefaTapp")
        SMTP_ADMIN_EMAIL: Admin email for contact forms
    """
    
    SMTP_HOST: str = os.getenv("SMTP_HOST", "")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USER: str = os.getenv("SMTP_USER", "")
    SMTP_PASS: str = os.getenv("SMTP_PASS", "")
    SMTP_FROM_NAME: str = os.getenv("SMTP_FROM_NAME", "ŞefaTapp")
    SMTP_ADMIN_EMAIL: str = os.getenv("SMTP_ADMIN_EMAIL", "admin@sefatapp.az")
    
    @classmethod
    def validate(cls) -> bool:
        """Validate that required configuration is present."""
        required = [cls.SMTP_HOST, cls.SMTP_USER, cls.SMTP_PASS]
        return all(required)


class EmailTemplate:
    """
    Email template builder with common templates.
    """
    
    @staticmethod
    def contact_form(name: str, email: str, message: str) -> tuple[str, str]:
        """
        Generate contact form email (plain text and HTML).
        
        Returns:
            tuple: (plain_text_body, html_body)
        """
        plain_text = f"""
Yeni əlaqə formu mesajı

Ad Soyad: {name}
Email: {email}

Mesaj:
{message}

---
Bu mesaj ŞefaTapp əlaqə formasından göndərilib.
        """
        
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                   color: white; padding: 20px; border-radius: 8px 8px 0 0; }}
        .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 8px 8px; }}
        .info-row {{ margin: 15px 0; padding: 10px; background: white; border-radius: 5px; }}
        .label {{ font-weight: bold; color: #667eea; }}
        .message-box {{ background: white; padding: 20px; border-left: 4px solid #667eea; 
                        margin-top: 20px; border-radius: 5px; }}
        .footer {{ text-align: center; color: #999; margin-top: 20px; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h2>🔔 Yeni Əlaqə Mesajı</h2>
        </div>
        <div class="content">
            <div class="info-row">
                <span class="label">👤 Ad Soyad:</span> {name}
            </div>
            <div class="info-row">
                <span class="label">📧 Email:</span> {email}
            </div>
            <div class="message-box">
                <p class="label">💬 Mesaj:</p>
                <p>{message.replace(chr(10), '<br>')}</p>
            </div>
            <div class="footer">
                <p>Bu mesaj ŞefaTapp əlaqə formasından göndərilib</p>
            </div>
        </div>
    </div>
</body>
</html>
        """
        
        return plain_text.strip(), html.strip()
    
    @staticmethod
    def appointment_confirmation(
        patient_name: str,
        doctor_name: str,
        appointment_date: str,
        appointment_time: str
    ) -> tuple[str, str]:
        """
        Generate appointment confirmation email.
        
        Returns:
            tuple: (plain_text_body, html_body)
        """
        plain_text = f"""
Hörmətli {patient_name},

Görüşünüz təsdiqləndi!

Həkim: Dr. {doctor_name}
Tarix: {appointment_date}
Saat: {appointment_time}

Görüş vaxtından 15 dəqiqə əvvəl klinikada olmanızı xahiş edirik.

Hörmətlə,
ŞefaTapp Komandası
        """
        
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: #4CAF50; color: white; padding: 20px; border-radius: 8px 8px 0 0; text-align: center; }}
        .content {{ background: #f9f9f9; padding: 30px; }}
        .appointment-details {{ background: white; padding: 20px; border-radius: 8px; margin: 20px 0; }}
        .detail-row {{ padding: 10px 0; border-bottom: 1px solid #eee; }}
        .detail-row:last-child {{ border-bottom: none; }}
        .label {{ font-weight: bold; color: #4CAF50; }}
        .footer {{ text-align: center; color: #666; margin-top: 20px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h2>✅ Görüşünüz Təsdiqləndi</h2>
        </div>
        <div class="content">
            <p>Hörmətli <strong>{patient_name}</strong>,</p>
            <p>Görüşünüz uğurla təsdiqləndi:</p>
            
            <div class="appointment-details">
                <div class="detail-row">
                    <span class="label">👨‍⚕️ Həkim:</span> Dr. {doctor_name}
                </div>
                <div class="detail-row">
                    <span class="label">📅 Tarix:</span> {appointment_date}
                </div>
                <div class="detail-row">
                    <span class="label">🕐 Saat:</span> {appointment_time}
                </div>
            </div>
            
            <p><strong>⚠️ Xahiş:</strong> Görüş vaxtından 15 dəqiqə əvvəl klinikada olmanızı xahiş edirik.</p>
            
            <div class="footer">
                <p>Hörmətlə,<br><strong>ŞefaTapp Komandası</strong></p>
            </div>
        </div>
    </div>
</body>
</html>
        """
        
        return plain_text.strip(), html.strip()
    
    @staticmethod
    def password_reset(reset_link: str, user_name: str) -> tuple[str, str]:
        """
        Generate password reset email.
        
        Returns:
            tuple: (plain_text_body, html_body)
        """
        plain_text = f"""
Hörmətli {user_name},

Şifrənizi sıfırlamaq üçün aşağıdaki linkə daxil olun:

{reset_link}

Bu link 1 saat ərzində etibarlıdır.

Əgər bu tələbi siz göndərməmisinizsə, bu emaili nəzərə almayın.

Hörmətlə,
ŞefaTapp Komandası
        """
        
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: #FF9800; color: white; padding: 20px; border-radius: 8px 8px 0 0; text-align: center; }}
        .content {{ background: #f9f9f9; padding: 30px; }}
        .button {{ display: inline-block; padding: 15px 30px; background: #FF9800; 
                   color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
        .warning {{ background: #fff3cd; border: 1px solid #ffc107; padding: 15px; 
                    border-radius: 5px; margin: 20px 0; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h2>🔐 Şifrə Sıfırlama</h2>
        </div>
        <div class="content">
            <p>Hörmətli <strong>{user_name}</strong>,</p>
            <p>Şifrənizi sıfırlamaq üçün aşağıdaki düyməyə klikləyin:</p>
            
            <a href="{reset_link}" class="button">Şifrəni Sıfırla</a>
            
            <div class="warning">
                <strong>⚠️ Diqqət:</strong> Bu link yalnız 1 saat ərzində etibarlıdır.
            </div>
            
            <p>Əgər bu tələbi siz göndərməmisinizsə, bu emaili nəzərə almayın.</p>
            
            <p>Hörmətlə,<br><strong>ŞefaTapp Komandası</strong></p>
        </div>
    </div>
</body>
</html>
        """
        
        return plain_text.strip(), html.strip()


class MailService:
    """
    Professional mail service with error handling and logging.
    """
    
    def __init__(self):
        """Initialize mail service and validate configuration."""
        if not MailConfig.validate():
            logger.warning("SMTP configuration is incomplete. Email functionality may not work.")
    
    @staticmethod
    async def send_email(
        to_email: str | EmailStr,
        subject: str,
        plain_body: str,
        html_body: Optional[str] = None,
        from_name: Optional[str] = None,
        attachments: Optional[List[tuple[str, bytes]]] = None,
    ) -> bool:
        """
        Send email with optional HTML and attachments.
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            plain_body: Plain text email body
            html_body: Optional HTML email body
            from_name: Optional sender display name
            attachments: Optional list of (filename, file_bytes) tuples
            
        Returns:
            bool: True if email sent successfully, False otherwise
            
        Example:
            ```python
            success = await MailService.send_email(
                to_email="user@example.com",
                subject="Welcome!",
                plain_body="Welcome to our platform",
                html_body="<h1>Welcome to our platform</h1>"
            )
            ```
        """
        try:
            # Validate configuration
            if not MailConfig.validate():
                logger.error("Cannot send email: SMTP configuration is incomplete")
                return False
            
            # Create message
            msg = MIMEMultipart("alternative")
            msg["From"] = f"{from_name or MailConfig.SMTP_FROM_NAME} <{MailConfig.SMTP_USER}>"
            msg["To"] = str(to_email)
            msg["Subject"] = subject
            
            # Attach plain text
            msg.attach(MIMEText(plain_body, "plain", "utf-8"))
            
            # Attach HTML if provided
            if html_body:
                msg.attach(MIMEText(html_body, "html", "utf-8"))
            
            # Attach files if provided
            if attachments:
                for filename, file_bytes in attachments:
                    part = MIMEBase("application", "octet-stream")
                    part.set_payload(file_bytes)
                    encoders.encode_base64(part)
                    part.add_header(
                        "Content-Disposition",
                        f"attachment; filename= {filename}",
                    )
                    msg.attach(part)
            
            # Send email
            with smtplib.SMTP(MailConfig.SMTP_HOST, MailConfig.SMTP_PORT) as server:
                server.starttls()
                server.login(MailConfig.SMTP_USER, MailConfig.SMTP_PASS)
                server.sendmail(MailConfig.SMTP_USER, str(to_email), msg.as_string())
            
            logger.info(f"Email sent successfully to {to_email}")
            return True
            
        except smtplib.SMTPAuthenticationError:
            logger.error("SMTP authentication failed. Check credentials.")
            return False
        except smtplib.SMTPException as e:
            logger.error(f"SMTP error occurred: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error sending email: {str(e)}")
            return False
    
    @staticmethod
    async def send_contact_form(name: str, email: str, message: str) -> bool:
        """
        Send contact form email to admin.
        
        Args:
            name: Sender name
            email: Sender email
            message: Message content
            
        Returns:
            bool: True if sent successfully
            
        Example:
            ```python
            success = await MailService.send_contact_form(
                name="John Doe",
                email="john@example.com",
                message="I have a question..."
            )
            ```
        """
        subject = f"ŞefaTapp Əlaqə Forması - {name}"
        plain_body, html_body = EmailTemplate.contact_form(name, email, message)
        
        return await MailService.send_email(
            to_email=MailConfig.SMTP_ADMIN_EMAIL,
            subject=subject,
            plain_body=plain_body,
            html_body=html_body,
        )
    
    @staticmethod
    async def send_appointment_confirmation(
        to_email: str,
        patient_name: str,
        doctor_name: str,
        appointment_date: str,
        appointment_time: str,
    ) -> bool:
        """
        Send appointment confirmation email to patient.
        
        Args:
            to_email: Patient email
            patient_name: Patient name
            doctor_name: Doctor name
            appointment_date: Appointment date
            appointment_time: Appointment time
            
        Returns:
            bool: True if sent successfully
        """
        subject = "ŞefaTapp - Görüş Təsdiqi"
        plain_body, html_body = EmailTemplate.appointment_confirmation(
            patient_name, doctor_name, appointment_date, appointment_time
        )
        
        return await MailService.send_email(
            to_email=to_email,
            subject=subject,
            plain_body=plain_body,
            html_body=html_body,
        )
    
    @staticmethod
    async def send_password_reset(
        to_email: str,
        user_name: str,
        reset_link: str,
    ) -> bool:
        """
        Send password reset email.
        
        Args:
            to_email: User email
            user_name: User name
            reset_link: Password reset link
            
        Returns:
            bool: True if sent successfully
        """
        subject = "ŞefaTapp - Şifrə Sıfırlama"
        plain_body, html_body = EmailTemplate.password_reset(reset_link, user_name)
        
        return await MailService.send_email(
            to_email=to_email,
            subject=subject,
            plain_body=plain_body,
            html_body=html_body,
        )
    
    @staticmethod
    async def send_bulk_email(
        recipients: List[str],
        subject: str,
        plain_body: str,
        html_body: Optional[str] = None,
    ) -> dict[str, int]:
        """
        Send email to multiple recipients.
        
        Args:
            recipients: List of email addresses
            subject: Email subject
            plain_body: Plain text body
            html_body: Optional HTML body
            
        Returns:
            dict: {"success": count, "failed": count}
        """
        success_count = 0
        failed_count = 0
        
        for email in recipients:
            result = await MailService.send_email(
                to_email=email,
                subject=subject,
                plain_body=plain_body,
                html_body=html_body,
            )
            if result:
                success_count += 1
            else:
                failed_count += 1
        
        logger.info(f"Bulk email completed: {success_count} success, {failed_count} failed")
        return {"success": success_count, "failed": failed_count}