from sqlalchemy import exists, select
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi import APIRouter, BackgroundTasks, Body, Cookie, Depends, HTTPException, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from passlib.context import CryptContext

from app.database import get_db
from app.defs.auth.service_defs import send_change_mail_email
from app.models.database import User
from app.models.validators import validate_data
from app.defs.auth.dependencies import get_current_active_user

router = APIRouter(prefix="/profile", tags=["Profile"])
templates = Jinja2Templates(directory="templates/profile")

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

@router.get("", response_class=HTMLResponse)
async def open_profile(request: Request, user: User = Depends(get_current_active_user)):
    return templates.TemplateResponse(
            "profile.html",
            {"request": request}
        )

@router.post("/update")
async def update_profile(background_tasks: BackgroundTasks, request: Request, data = Body(), db: AsyncSession = Depends(get_db), user: User = Depends(get_current_active_user)):
    full_name = data.get("full_name")
    old_password = data.get("old_password")
    new_password = data.get("new_password")
    email = data.get("email")

    if email:
        email_already_in_use = (await db.execute(
            select(exists().where(User.email == email))
        )).scalar()

        if email_already_in_use:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Данный email уже используется")
        
        background_tasks.add_task(
            send_change_mail_email,
            email=email,
            username=user.username
        )

        return {
            "message": "Successful. Check your email for verification.",
            "email": email
        }

    if new_password:
        if not  old_password or not pwd_context.verify(old_password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Неверные учетные данные"
            )
        
        new_password = pwd_context.hash(new_password)

        user.hashed_password = new_password

        await db.commit()

        return {
            "message": "Password successfully changed"
        }

    if full_name:
        user.full_name = full_name

        await db.commit()

        return {
            "message": "Full name successfully changed"
        }

