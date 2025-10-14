# app/models/document.py
import enum
from sqlalchemy import String, DateTime, ForeignKey, Enum as SQLAlchemyEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from .base import Base
from typing import List
from datetime import datetime


class ProcessingStatus(str, enum.Enum):
    """
    Enum para os estados de processamento de um documento.
    """
    PENDING = "pending"
    TEXT_EXTRACTED = "text_extracted"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class Document(Base):
    """
    Modelo SQLAlchemy que representa a tabela 'documents' na base de dados.
    """
    __tablename__ = "books"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(300), nullable=True)
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    
    status: Mapped[ProcessingStatus] = mapped_column(
        SQLAlchemyEnum(ProcessingStatus, name="processing_status_enum"), 
        nullable=False, 
        default=ProcessingStatus.PENDING
    )

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    
    # Relacionamento com a tabela 'users'
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    owner: Mapped["User"] = relationship(back_populates="books")

    # Relacionamento com a tabela 'audio_segments'
    # cascade="all, delete-orphan" garante que ao deletar um Document,
    # todos os seus AudioSegments também sejam deletados
    segments: Mapped[List["AudioSegment"]] = relationship(
        back_populates="document",
        cascade="all, delete-orphan"
    )
