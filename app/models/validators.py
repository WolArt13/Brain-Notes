from fastapi import HTTPException, status
from pydantic import BaseModel, EmailStr, Field, ValidationError
from typing import Optional
from datetime import datetime

from uuid import UUID

class UserBase(BaseModel):
    """Общие поля пользователя"""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    full_name: Optional[str] = None

class UserCreate(UserBase):
    password: str = Field(..., min_length=8, description="Минимум 8 символов")

class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime

    class Cofig:
        from_attributes = True

class UserInDB(UserResponse):
    hashed_password: str

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    username: Optional[str] = None

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str

class ResendVerificationRequest(BaseModel):
    email: EmailStr

class NewFolderCreate(BaseModel):
    title: str
    parent_id: Optional[UUID]

class NewFolderUpdate(BaseModel):
    title: str
    parent_id: Optional[UUID]

class NewNoteCreate(BaseModel):
    header: Optional[str] = Field(None, max_length=50)
    content: str
    folder_id: Optional[UUID] = Field(None)

class NoteUpdate(BaseModel):
    header: Optional[str] = Field(None, max_length=50)
    content: Optional[str]
    folder_id: Optional[UUID] = Field(None)

async def validate_data(data, validation_class):
    try:
        validation_class(**data)
    except ValidationError as e:
        print(e.errors())
        miss = [i['loc'][-1] for i in e.errors()]
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"ParameterError {miss}"
        )
    except TypeError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"NotJSONFormat"
        )