from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from pydantic import EmailStr
from app.config import settings
from app.auth.email_utils import generate_verification_token

mail_config = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_STARTTLS=settings.MAIL_TLS,
    MAIL_SSL_TLS=settings.MAIL_SSL,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True
)

fastmail = FastMail(mail_config)

async def send_verification_email(email: EmailStr, username: str) -> None:
    token = generate_verification_token(email)

    verification_link = f"{settings.APP_URL}/auth/verify?token={token}"

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; 
                         border: 1px solid #ddd; border-radius: 5px; }}
            .button {{ display: inline-block; padding: 12px 24px; 
                      background-color: #007bff; color: white; 
                      text-decoration: none; border-radius: 4px; margin: 20px 0; }}
            .footer {{ margin-top: 30px; font-size: 12px; color: #666; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h2>Подтвердите ваш email</h2>
            <p>Здравствуйте, {username}!</p>
            <p>Спасибо за регистрацию в сервисе BrainNotes. Пожалуйста, подтвердите ваш email:</p>
            <a href="{verification_link}" class="button">Подтвердить Email</a>
            <p>Или скопируйте ссылку: <a href="{verification_link}">{verification_link}</a></p>
            <div class="footer">
                <p>Ссылка действительна {settings.VERIFICATION_TOKEN_EXPIRE_HOURS} часов.</p>
                <p>Если вы не регистрировались, проигнорируйте это письмо.</p>
            </div>
        </div>
    </body>
    </html>
    """

    message = MessageSchema(
        subject="Подтвердите ваш email",
        recipients=[email],
        body=html_content,
        subtype="html"
    )

    await fastmail.send_message(message)

async def send_password_reset_email(email: EmailStr, reset_token: str) -> None:
    reset_link = f"{settings.APP_URL}/auth/reset-password?token={reset_token}"

    html_content = f"""
    <div style="font-family: Arial;">
        <h2>Сброс пароля</h2>
        <p>Вы запросили сброс пароля в сервисе BrainNotes. Нажмите на кнопку:</p>
        <a href="{reset_link}" style="padding: 10px 20px; background: #007bff; 
           color: white; text-decoration: none; border-radius: 4px;">
            Сбросить пароль
        </a>
        <p>Ссылка действительна {settings.VERIFICATION_TOKEN_EXPIRE_HOURS} часов.</p>
        <p>Если вы не запрашивали сброс, проигнорируйте это письмо.</p>
    </div>
    """

    message = MessageSchema(
        subject="Сброс пароля",
        recipients=[email],
        body=html_content,
        subtype="html"
    )
    
    await fastmail.send_message(message)