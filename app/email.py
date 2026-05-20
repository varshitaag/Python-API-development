from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from .config import settings


def get_mail_config():
    """Create email configuration dynamically to handle optional mail settings"""
    return ConnectionConfig(
        MAIL_USERNAME=settings.mail_username,
        MAIL_PASSWORD=settings.mail_password,
        MAIL_FROM=settings.mail_from,
        MAIL_PORT=settings.mail_port,
        MAIL_SERVER=settings.mail_server,
        MAIL_STARTTLS=True,
        MAIL_SSL_TLS=False,
        USE_CREDENTIALS=True,
    )


async def send_verification_email(email: str, token: str):
    # This is the link the user will click
    verify_url = f"http://localhost:8000/users/verify?token={token}"

    message = MessageSchema(
        subject="Verify your email address",
        recipients=[email],
        body=f"""
        <h2>Welcome! Please verify your email.</h2>
        <p>Click the link below to activate your account:</p>
        <a href="{verify_url}">Verify my account</a>
        <p>This link is valid for 24 hours.</p>
        """,
        subtype=MessageType.html,
    )

    conf = get_mail_config()
    fm = FastMail(conf)
    await fm.send_message(message)