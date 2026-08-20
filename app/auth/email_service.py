import os

from dotenv import load_dotenv
from fastapi_mail import (
    FastMail,
    MessageSchema,
    ConnectionConfig,
)

load_dotenv()


# ============================================================
# Email Configuration
# ============================================================

conf = ConnectionConfig(
    MAIL_USERNAME=os.getenv("MAIL_USERNAME"),
    MAIL_PASSWORD=os.getenv("MAIL_PASSWORD"),
    MAIL_FROM=os.getenv("MAIL_FROM"),
    MAIL_SERVER=os.getenv("MAIL_SERVER", "smtp.gmail.com"),
    MAIL_PORT=int(os.getenv("MAIL_PORT", "587")),

    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,

    USE_CREDENTIALS=True,
)


BACKEND_URL = os.getenv(
    "BACKEND_URL",
    "http://127.0.0.1:8000"
)


# ============================================================
# Send Verification Email
# ============================================================

async def send_verification_email(
    email: str,
    token: str
):
    verification_link = (
        f"{BACKEND_URL}/auth/verify-email"
        f"?token={token}"
    )

    message = MessageSchema(
        subject="Verify Your Email",
        recipients=[email],
        body=f"""
Hello,

Thank you for creating an account.

Please verify your email address by clicking the link below:

{verification_link}

This verification link will expire in 15 minutes.

If you did not create this account, you can safely ignore this email.

Regards,
YT + PDF Chat
""",
        subtype="plain",
    )

    fm = FastMail(conf)

    await fm.send_message(message)


# ============================================================
# Send Password Reset Email
# ============================================================

async def send_reset_email(
    email: str,
    token: str
):
    # For now this points to the backend endpoint.
    # Later, when your Streamlit reset-password page exists,
    # we can change this to the frontend URL.

    reset_link = (
        f"{BACKEND_URL}/auth/reset-password"
        f"?token={token}"
    )

    message = MessageSchema(
        subject="Reset Your Password",
        recipients=[email],
        body=f"""
Hello,

We received a request to reset your password.

Click the link below to continue:

{reset_link}

This link will expire in 15 minutes.

If you did not request a password reset, you can safely ignore this email.

Regards,
YT + PDF Chat
""",
        subtype="plain",
    )

    fm = FastMail(conf)

    await fm.send_message(message)