from typing import Any, Dict, List
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncConnection
from sqlalchemy import delete, select, update
from sqlalchemy.orm import selectinload

from app.models.database import Folder, User, Note

class Dashboard:
    def __init__(self, db_conn: AsyncConnection) -> None:
        self.db: AsyncConnection = db_conn

    async def new_note(self, user_id: int, title: str, content: str, folder_id = None):
        """Create a new note"""
        user = (await self.db.execute(select(User).where(User.id == int(user_id)))).scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="По зарегистрированному email пользователь не найден.")
        
        if not title:
            title = content[:50]

        new_note = Note(
            title=title,
            content=content,
            user_id=user.id,
            folder_id=folder_id
        )

        self.db.add(new_note)
        await self.db.commit()
        await self.db.refresh(new_note)

        return new_note
    
    async def update_note(self, user: User, source_id, **kwargs):
        title = kwargs.get('title')
        body = kwargs.get('body')
        folder_id = kwargs.get('folder_id')

        values = {}
        if title:
            values['title'] = title
        if body:
            values['content'] = body
        if folder_id:
            values['folder_id'] = folder_id

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
    
    async def new_folder(self, user: User, **kwargs):
        title = kwargs.get('title')
        parent_id = kwargs.get('folder_id')

        new_folder = Folder(
            title=title,
            user_id=user.id,
            parent_id=parent_id
        )

        self.db.add(new_folder)
        await self.db.commit()
        await self.db.refresh(new_folder)

        return new_folder
    
    async def update_folder(self, folder_id, user: User, **kwargs):
        title = kwargs.get('title')
        parent_id = kwargs.get('parent_id')

        folder = (await self.db.execute(select(Folder).where(Folder.id == folder_id, Folder.user_id == user.id))).scalar_one_or_none()

        if folder:
            if title:
                folder.title = title
            if parent_id:
                folder.parent_id = parent_id

            await self.db.commit()
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Folder not found")
        
        return {
            "message": "Folder successfully updated"
        }
    
    async def delete_folder(self, folder_id, user: User):
        res = (await self.db.execute(
            delete(Folder)
            .where(Folder.id == folder_id, Folder.user_id == user.id)
            .returning(Folder.id)
        )).scalar_one_or_none()

        if not res:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Folder not found")
        
        return {
            "message": "Folder successfully deleted"
        }
    
    async def get_tree(self, user: User) -> List[Dict[str, Any]]:
        """Получить древовидную структуру папок и заметок"""
    
        # 1. Получаем все корневые папки (parent_id = None) с их дочерними элементами
        root_folders_query = select(Folder).where(
            Folder.user_id == user.id,
            Folder.parent_id == None
        ).options(
            selectinload(Folder.children),  # предзагрузка дочерних папок
            selectinload(Folder.notes)      # предзагрузка заметок в папке
        )
        
        result = await self.db.execute(root_folders_query)
        root_folders = result.scalars().all()
        
        # 2. Получаем заметки без папки (корневые заметки)
        root_notes_query = select(Note).where(
            Note.user_id == user.id,
            Note.folder_id == None
        )
        
        result = await self.db.execute(root_notes_query)
        root_notes = result.scalars().all()
        
        # 3. Рекурсивно строим дерево
        def build_folder_tree(folder: Folder) -> Dict[str, Any]:
            return {
                "id": str(folder.id),
                "title": folder.title,
                "type": "folder",
                "created_at": folder.created_at.isoformat() if folder.created_at else None,
                "updated_at": folder.updated_at.isoformat() if folder.updated_at else None,
                "children": [
                    *[build_folder_tree(child) for child in folder.children],
                    *[build_note_item(note) for note in folder.notes]
                ]
            }
        
        def build_note_item(note: Note) -> Dict[str, Any]:
            return {
                "id": str(note.id),
                "title": note.title,
                "content": note.content,
                "type": "note",
                "created_at": note.created_at.isoformat() if note.created_at else None,
                "updated_at": note.updated_at.isoformat() if note.updated_at else None
            }
        
        # 4. Формируем итоговое дерево
        tree = [
            *[build_folder_tree(folder) for folder in root_folders],
            *[build_note_item(note) for note in root_notes]
        ]
        
        return tree