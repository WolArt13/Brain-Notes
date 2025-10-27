from sqlalchemy.ext.asyncio import AsyncConnection
from sqlalchemy import select

from app.models.database import User, Note

class Dashboard:
    def __init__(self, db_conn: AsyncConnection) -> None:
        self.db_conn = db_conn

    async def new_note(self, db: AsyncConnection, title: str, body: str, email: str):
        """Create a new note"""
        user = (await db.execute(select(User).where(User.email == email))).scalar_one_or_none()
        if not user:
            raise 
        new_note = Note(
            title=title,
            content=body,
            user_id=user.id
        )

        await db.add(new_note)
        await db.commit()
        await db.refresh(new_note)

        return new_note