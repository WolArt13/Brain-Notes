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

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )
    updated_at = Column(
        DateTime(timezone=True),
        onupdate=func.now()
    )

    notes = relationship("Note", back_populates="user")

class Note(Base):
    __tablename__ = "notes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    title = Column(String(50))
    content = Column(String, nullable=True)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("User", back_populates="notes")