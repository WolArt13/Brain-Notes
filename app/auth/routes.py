from typing import Annotated
from fastapi import APIRouter, Depends, Form, HTTPException, Request, status, BackgroundTasks
from fastapi.responses import HTMLResponse
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from passlib.context import CryptContext
from datetime import timedelta

from app.database import get_db
from app.config import settings
from app.models.validators import ResetPasswordRequest, UserCreate, UserResponse, Token
from app.models.database import User
from app.auth.jwt_handler import create_access_token, create_refresh_token, decode_jwt
from app.auth.email_utils import verify_email_token, generate_password_reset_token, verify_password_reset_token
from app.auth.email_service import send_password_reset_email, send_verification_email

router = APIRouter(prefix="/auth", tags=["Authentication"])

templates = Jinja2Templates(directory="templates")

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

@router.get("/register")
async def login(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(User).where(
            (User.email == user_data.email) | (User.username == user_data.username)
        )
    )
    existing_user = result.scalar_one_or_none()

    if existing_user:
        if existing_user.email == user_data.email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
    
    hashed_password = pwd_context.hash(user_data.password)

    new_user = User(
        username=user_data.username,
        email=user_data.email,
        full_name=user_data.full_name,
        hashed_password=hashed_password,
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

    return new_user

@router.get("/verify")
async def verify_email(token: str, request: Request, db: AsyncSession = Depends(get_db)):
    try:
        email = verify_email_token(token)
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
    
    if user.is_verified:
        return {"message": "Email already verified", "status": "success"}
    
    user.is_verified = True
    await db.commit()

    return templates.TemplateResponse("register_success.html", {"request": request})

@router.post("/resend-verification")
async def resend_verification_email(
    email: str,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()

    if not user:
        return {"message": "If email exists, verification link has been sent"}
    
    if user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already verified"
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

@router.post("/login", response_model=Token)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(User).where(User.username == form_data.username))
    user = result.scalar_one_or_none()

    if not user or not pwd_context.verify(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    if not user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email not verified. Please check your inbox."
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is disabled"
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=access_token_expires
    )
    refresh_token = create_refresh_token(data={"sub": user.username})

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

@router.post("/refresh", response_model=Token)
async def refresh_access_token(
    refresh_token: str,
    db: AsyncSession = Depends(get_db)
):
    payload = decode_jwt(refresh_token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Please provide a refresh token"
        )
    
    username = payload.get("sub")
    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    new_access_token = create_access_token(
        data={"sub": username},
        expires_delta=access_token_expires
    )

    return {
        "access_token": new_access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


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
        return templates.TemplateResponse("reset_password.html", {"request": request, "token": token})
    except Exception as e:
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
