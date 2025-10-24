from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
from app.config import settings

serializer = URLSafeTimedSerializer(settings.SECRET_KEY)

def generate_verification_token(email: str) -> str:
    return serializer.dumps(email, salt="email-verification")

def verify_email_token(token: str, max_age: int = None) -> str:
    if max_age is None:
        max_age = settings.VERIFICATION_TOKEN_EXPIRE_HOURS * 3600

    try:
        email = serializer.loads(
            token,
            salt="email-verification",
            max_age=max_age
        )
        return email
    except SignatureExpired:
        raise ValueError("Verification link has expired. Please request a new one.")
    except BadSignature:
        raise ValueError("Invalid verification token.")
    
def generate_password_reset_token(email: str) -> str:
    return serializer.dumps(email, salt="password-reset")

def verify_password_reset_token(token: str) -> str:
    max_age = settings.VERIFICATION_TOKEN_EXPIRE_HOURS * 3600

    try:
        email = serializer.loads(
            token,
            salt="password-reset",
            max_age=max_age
        )
        return email
    except SignatureExpired:
        raise ValueError("Password reset link has expired.")
    except BadSignature:
        raise ValueError("Invalid password reset token.")