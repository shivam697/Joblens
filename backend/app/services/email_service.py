"""
Email Service — Interview reminder emails via Gmail SMTP

Uses FastAPI-Mail with aiosmtplib for fully async email sending.
Configured for Gmail with App Password authentication.
"""

import logging

from fastapi_mail import FastMail, MessageSchema, MessageType, ConnectionConfig

from app.core.config import settings

logger = logging.getLogger(__name__)

# Gmail SMTP configuration
# Requires Gmail App Password — regular password won't work
# See OAUTH_SETUP.md for setup instructions
email_config = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_FROM_NAME=settings.MAIL_FROM_NAME,
    MAIL_PORT=587,                    # Gmail TLS port
    MAIL_SERVER="smtp.gmail.com",
    MAIL_STARTTLS=True,               # Enable TLS encryption
    MAIL_SSL_TLS=False,               # Don't use SSL (we use STARTTLS instead)
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
)

mail_client = FastMail(email_config)


async def send_interview_reminder_email(
    user_name: str,
    user_email: str,
    company_name: str,
    interview_time: str,
    interview_mode: str | None,
    interview_platform: str | None,
    interview_link: str | None,
    interview_notes: str | None,
    job_id: str,
) -> None:
    """
    Send a friendly and informative interview reminder email.

    Email includes:
    - Personalized greeting with user's first name
    - Company name prominently displayed
    - Interview time formatted nicely
    - Interview mode, platform, and link if available
    - Interview notes the user saved
    - Direct link to job detail in JobLense

    Args:
        user_name: User's full name
        user_email: User's email address
        company_name: Company they're interviewing with
        interview_time: Formatted interview datetime string
        interview_mode: Online / In Person / Phone
        interview_platform: Zoom, Google Meet, etc.
        interview_link: Meeting URL
        interview_notes: User's preparation notes
        job_id: Job application UUID for deep link
    """
    first_name = user_name.split()[0] if user_name else "there"

    # Build interview details section
    details_html = ""
    if interview_mode:
        mode_display = interview_mode.replace("_", " ").title()
        details_html += f"<p><strong>Mode:</strong> {mode_display}</p>"
    if interview_platform:
        details_html += f"<p><strong>Platform:</strong> {interview_platform}</p>"
    if interview_link:
        details_html += f'<p><strong>Join Link:</strong> <a href="{interview_link}" style="color: #6366F1;">{interview_link}</a></p>'
    if interview_notes:
        details_html += f'<p><strong>Your Notes:</strong></p><p style="background: #F1F5F9; padding: 12px; border-radius: 8px; color: #334155;">{interview_notes}</p>'

    # Build the full email HTML
    html_body = f"""
    <div style="font-family: 'DM Sans', Arial, sans-serif; max-width: 600px; margin: 0 auto; background: #0F172A; color: #F1F5F9; padding: 32px; border-radius: 16px;">
        <div style="text-align: center; margin-bottom: 24px;">
            <h1 style="font-family: 'Sora', sans-serif; color: #6366F1; margin: 0;">JobLense</h1>
            <p style="color: #94A3B8; margin: 4px 0;">Interview Reminder</p>
        </div>

        <div style="background: #1E293B; border-radius: 12px; padding: 24px; border: 1px solid #334155;">
            <h2 style="margin-top: 0; color: #F1F5F9;">Hi {first_name}! 👋</h2>

            <p>You have an interview coming up today!</p>

            <div style="background: #0F172A; border-radius: 8px; padding: 16px; margin: 16px 0; border-left: 4px solid #6366F1;">
                <h3 style="margin: 0 0 8px 0; color: #818CF8;">{company_name}</h3>
                <p style="margin: 0; font-size: 18px; color: #F1F5F9;"><strong>{interview_time}</strong></p>
            </div>

            {details_html}

            <div style="margin-top: 24px; text-align: center;">
                <a href="{settings.FRONTEND_URL}/jobs/{job_id}"
                   style="display: inline-block; background: #6366F1; color: white; padding: 12px 24px;
                          border-radius: 8px; text-decoration: none; font-weight: 600;">
                    View in JobLense →
                </a>
            </div>
        </div>

        <div style="text-align: center; margin-top: 24px; color: #64748B; font-size: 13px;">
            <p>You've got this! 🚀 Good luck with your interview!</p>
            <p>— The JobLense Team</p>
        </div>
    </div>
    """

    try:
        message = MessageSchema(
            subject=f"🔔 Interview Today: {company_name}",
            recipients=[user_email],
            body=html_body,
            subtype=MessageType.html,
        )
        await mail_client.send_message(message)
        logger.info(f"Interview reminder sent to {user_email} for {company_name}")

    except Exception as error:
        # Don't crash the cron job if one email fails — continue with others
        logger.error(f"Failed to send reminder to {user_email}: {error}")
