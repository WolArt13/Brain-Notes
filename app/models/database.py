import uuid
from sqlalchemy import UUID, Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    full_name = Column(String(100), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    notes = relationship(
        "Note", 
        back_populates="user",
        cascade="all, delete-orphan"
    )
    folders = relationship(
        "Folder", 
        back_populates="user",
        cascade="all, delete-orphan"
    )


class Folder(Base):
    __tablename__ = "folders"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    title = Column(String(50))

    parent_id = Column(UUID(as_uuid=True), ForeignKey("folders.id", ondelete="CASCADE"), nullable=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Отношение к пользователю
    user = relationship("User", back_populates="folders")
    
    # Отношение к заметкам в этой папке
    notes = relationship(
        "Note", 
        back_populates="folder",
        cascade="all, delete-orphan",
        foreign_keys="Note.folder_id"
    )

    # Отношение для вложенных папок - с single_parent=True
    children = relationship(
        "Folder",
        backref="parent",
        remote_side=[id],
        cascade="all, delete-orphan",  # Это теперь работает
        single_parent=True,  # ← ДОБАВИЛ ЭТО
        foreign_keys=[parent_id]
    )


class Note(Base):
    __tablename__ = "notes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    title = Column(String(50))
    content = Column(String, nullable=False)

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    folder_id = Column(UUID(as_uuid=True), ForeignKey("folders.id", ondelete="CASCADE"), nullable=True, index=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("User", back_populates="notes")
    folder = relationship("Folder", back_populates="notes")
