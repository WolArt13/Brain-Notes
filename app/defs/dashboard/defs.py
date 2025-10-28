from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncConnection
from sqlalchemy import delete, select, update

from app.models.database import User, Note

class Dashboard:
    def __init__(self, db_conn: AsyncConnection) -> None:
        self.db: AsyncConnection = db_conn

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
    
    async def update_note(self, user: User, source_id, **kwargs):
        title = kwargs.get('title')
        body = kwargs.get('body')

        values = {}
        if title:
            values['title'] = title
        if body:
            values['content'] = body

        try:
            res = (await self.db.execute(
                update(Note)
                .where(Note.id == str(source_id), Note.user_id == int(user.id))
                .values(**values)
                .returning(Note.id)
            )).scalar_one_or_none()
        except Exception as e:
            print(str(e))
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")
        
        await self.db.commit()

        if not res:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")
        
        return {"status": "ok", "message": "Note successfully updated"}
    
    async def delete_note(self, user: Note, source_id):
        try:
            res = (await self.db.execute(
                delete(Note)
                .where(Note.id == str(source_id), Note.user_id == int(user.id))
                .returning(Note.id)
            )).scalar_one_or_none()
        except Exception as e:
            print(str(e))
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")
        
        await self.db.commit()

        if not res:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Note does not exists")
        
        return {"status": "ok", "message": "Note successfully deleted"}