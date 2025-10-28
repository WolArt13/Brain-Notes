from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from pydantic import EmailStr
from app.config import settings
from app.defs.auth.mail_templates_defs import get_verification_email_html, get_password_reset_email_html, get_welcome_email_html, get_change_email_html
from app.defs.auth.email_utils import generate_verification_token

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
    """
    Отправка письма для подтверждения email при регистрации.
    """
    # Генерируем токен верификации
    token = generate_verification_token(email)
    verification_link = f"{settings.APP_URL}/auth/verify?token={token}"

    # Получаем стилизованный HTML шаблон
    html_content = get_verification_email_html(username, verification_link)

    # Создаём сообщение
    message = MessageSchema(
        subject="Подтверждение регистрации - Brain Notes",
        recipients=[email],
        body=html_content,
        subtype="html"
    )

    # Отправляем письмо
    await fastmail.send_message(message)


async def send_password_reset_email(email: EmailStr, reset_token: str, username: str = None) -> None:
    """
    Отправка письма для сброса пароля.
    """
    # Формируем ссылку для сброса пароля
    reset_link = f"{settings.APP_URL}/auth/reset-password?token={reset_token}"

    # Если username не передан, используем часть email
    if not username:
        username = email.split('@')[0]

    # Время истечения токена (по умолчанию 24 часа)
    expire_hours = getattr(settings, 'PASSWORD_RESET_TOKEN_EXPIRE_HOURS', 24)

    # Получаем стилизованный HTML шаблон
    html_content = get_password_reset_email_html(
        username=username,
        reset_link=reset_link,
        expire_hours=expire_hours
    )

    # Создаём сообщение
    message = MessageSchema(
        subject="Сброс пароля - Brain Notes",
        recipients=[email],
        body=html_content,
        subtype="html"
    )

    # Отправляем письмо
    await fastmail.send_message(message)

async def send_change_mail_email(email: EmailStr, username: str = None) -> None:
    """
    Отправка письма для смены email
    """
    token = generate_verification_token(email)

    reset_link = f"{settings.APP_URL}/auth/change-email?token={token}"

    if not username:
        username = email.split('@')[0]

    expire_hours = getattr(settings, 'EMAIL_CHANGE_TOKEN_EXPIRE_HOURS', 24)

    # Получаем стилизованный HTML шаблон
    html_content = get_password_reset_email_html(
        username=username,
        reset_link=reset_link,
        expire_hours=expire_hours
    )

    # Создаём сообщение
    message = MessageSchema(
        subject="Смена email - Brain Notes",
        recipients=[email],
        body=html_content,
        subtype="html"
    )

    # Отправляем письмо
    await fastmail.send_message(message)

async def send_welcome_email(email: EmailStr, username: str) -> None:
    """
    Опциональное приветственное письмо после успешной верификации email.
    """
    # URL для кнопки "Начать работу"
    dashboard_url = f"{settings.APP_URL}/dashboard"

    # Получаем стилизованный HTML шаблон
    html_content = get_welcome_email_html(username, dashboard_url)

    # Создаём сообщение
    message = MessageSchema(
        subject="Добро пожаловать в Brain Notes! 🎉",
        recipients=[email],
        body=html_content,
        subtype="html"
    )

    # Отправляем письмо
    await fastmail.send_message(message)