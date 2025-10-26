from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.auth.jwt_handler import decode_jwt
from app.models.database import User
from app.database import get_db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

async def get_current_user(
        token: Annotated[str, Depends(oauth2_scheme)],
        db: AsyncSession = Depends(get_db)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"}
    )

    payload = decode_jwt(token)
    if payload is None:
        raise credentials_exception
    
    username: str = payload.get("sub")
    if username is None:
        raise credentials_exception
    
    token_type = payload.get("type")
    if token_type != "access":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Pleace provide an access token, not a refresh token"
        )
    
    result = await db.execute(select(User).where(User.username == username))
    user = result.scalar_one_or_none()

    if user is None:
        raise credentials_exception
    
    return user

async def get_current_active_user(
        current_user: Annotated[User, Depends(get_current_user)]
) -> User:
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    
    if not current_user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email not verified"
        )
    
    return current_user