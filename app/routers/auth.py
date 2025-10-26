from typing import Annotated
from fastapi import APIRouter, Depends, Form, HTTPException, Request, Response, status, BackgroundTasks
from fastapi.responses import HTMLResponse
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from passlib.context import CryptContext
from datetime import timedelta

from app.database import get_db
from app.config import settings
from app.models.validators import ResendVerificationRequest
from app.models.database import User
from app.defs.auth.jwt_handler import create_access_token, create_refresh_token, decode_jwt
from app.defs.auth.email_utils import verify_email_token, generate_password_reset_token, verify_password_reset_token
from app.defs.auth.service_defs import send_password_reset_email, send_verification_email, send_welcome_email

router = APIRouter(prefix="/auth", tags=["Authentication"])

templates = Jinja2Templates(directory="templates/auth")

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

@router.get("/register")
async def register_get(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@router.post("/register")
async def register(
    response: Response,
    background_tasks: BackgroundTasks,
    username: str = Form(...),
    email: str = Form(...),
    full_name: str = Form(...),
    password: str = Form(...),
    db: AsyncSession = Depends(get_db)
):
    """
    Регистрация нового пользователя. Отправляет email для подтверждения.
    """
    # Проверяем, не существует ли уже такой пользователь
    result = await db.execute(select(User).where(User.email == email))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email уже зарегистрирован"
        )

    # Создаем нового пользователя
    new_user = User(
        username=username,
        email=email,
        full_name=full_name,
        hashed_password=pwd_context.hash(password),
        is_verified=False
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    background_tasks.add_task(
        send_verification_email,
        email=new_user.email,
        username=new_user.username
    )

    return {
        "message": "Registration successful. Check your email for verification.",
        "email": email
    }

@router.get("/verify")
async def verify_email(
    token: str,
    request: Request,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """
    Подтверждение email по ссылке из письма.
    """
    try:
        email = verify_email_token(token)
    except ValueError as e:
        return templates.TemplateResponse(
            "403.html",
            {"request": request},
            status_code=status.HTTP_400_BAD_REQUEST
        )

    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()

    if not user:
        return templates.TemplateResponse(
            "404.html",
            {"request": request},
            status_code=status.HTTP_404_NOT_FOUND
        )

    if user.is_verified:
        return templates.TemplateResponse("already_registered.html", {"request": request})

    # Подтверждаем email
    user.is_verified = True
    await db.commit()

    background_tasks.add_task(
        send_welcome_email,
        email=user.email,
        username=user.username
    )

    return templates.TemplateResponse("register_success.html", {"request": request})

@router.get("/me")
async def get_current_user(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    Получить текущего залогиненного пользователя.
    Читает токен из cookies.
    """
    access_token = request.cookies.get("access_token")

    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )

    try:
        payload = decode_jwt(access_token)
        username = payload.get("sub")

        if not username:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

    result = await db.execute(select(User).where(User.username == username))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return {
        "username": user.username,
        "email": user.email,
        "full_name": user.full_name,
        "is_verified": user.is_verified
    }

@router.post("/logout")
async def logout(response: Response):
    """
    Выход пользователя. Удаляет cookies.
    """
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")

    return {"message": "Logout successful"}

@router.post("/resend-verification")
async def resend_verification_email(
    request: ResendVerificationRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(User).where(User.email == request.email))
    user = result.scalar_one_or_none()

    if not user:
        return {"message": "If email exists, verification link has been sent"}
    
    if user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email уже подтверждён"
        )
    
    background_tasks.add_task(
        send_verification_email,
        email=user.email,
        username=user.username
    )

    return {"message": "Verification email sent"}

@router.get("/login")
async def login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.post("/login")
async def login(
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """
    Вход пользователя. Устанавливает HTTP-only cookies с токенами.
    """
    # Проверяем учетные данные
    result = await db.execute(select(User).where(User.username == form_data.username))
    user = result.scalar_one_or_none()

    if not user or not pwd_context.verify(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверные учетные данные"
        )

    if not user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email не подтверждён"
        )

    # Создаем токены
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=timedelta(minutes=30)
    )
    refresh_token = create_refresh_token(
        data={"sub": user.username}
    )

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,      # Защита от XSS
        secure=False,        # Только HTTPS (в продакшене)
        samesite="lax",     # Защита от CSRF
        max_age=1800        # 30 минут
    )

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=2592000     # 30 дней
    )

    return {
        "message": "Login successful",
        "user": {
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name
        }
    }

@router.post("/refresh")
async def refresh_token(
    response: Response,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    Обновление access token используя refresh token.
    """
    refresh_token_value = request.cookies.get("refresh_token")

    if not refresh_token_value:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token not found"
        )

    try:
        payload = decode_jwt(refresh_token_value)
        username = payload.get("sub")
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )

    # Создаем новый access token
    new_access_token = create_access_token(
        data={"sub": username},
        expires_delta=timedelta(minutes=30)
    )

    response.set_cookie(
        key="access_token",
        value=new_access_token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=1800
    )

    return {"message": "Token refreshed"}


@router.get("/forgot-password")
async def forgot_password_get(request: Request):
    return templates.TemplateResponse("forgot-password.html", {"request": request})

@router.post("/forgot-password")
async def forgot_password(
    email: str,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()

    if not user:
        return {"message": "If email exists, password reset link has been sent"}
    
    reset_token = generate_password_reset_token(user.email)

    background_tasks.add_task(
        send_password_reset_email,
        email=user.email,
        reset_token=reset_token
    )

    return {"message": "Password reset link sent"}

@router.get("/reset-password", response_class=HTMLResponse)
async def reset_password_form(request: Request, token: str):
    try: 
        verify_password_reset_token(token)
        return templates.TemplateResponse("reset-password.html", {"request": request, "token": token})
    except Exception as e:
        print(str(e))
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    
@router.post("/reset-password")
async def reset_password(
    token: str = Form(...),
    new_password: str = Form(...),
    db: AsyncSession = Depends(get_db)
):

    try:
        email = verify_password_reset_token(token)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user.hashed_password = pwd_context.hash(new_password)
    await db.commit()

    return {"message": "Password successfully reset"}
