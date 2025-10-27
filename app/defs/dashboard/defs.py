from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncConnection
from sqlalchemy import select

from app.models.database import User, Note

class Dashboard:
    def __init__(self, db_conn: AsyncConnection) -> None:
        self.db = db_conn

    async def new_note(self, user_id: int, title: str, body: str):
        """Create a new note"""
        user = (await self.db.execute(select(User).where(User.id == int(user_id)))).scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="По зарегистрированному email пользователь не найден.")
        
        if not title:
            title = body[:50]

        new_note = Note(
            title=title,
            content=body,
            user_id=user.id
        )

        self.db.add(new_note)
        await self.db.commit()
        await self.db.refresh(new_note)

        return new_note
    
    async def get_notes(self, user: User):
        pass