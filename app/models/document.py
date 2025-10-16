# app/models/document.py
import enum
import uuid

from sqlalchemy import String, DateTime, ForeignKey, Enum as SQLAlchemyEnum , Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID 
from typing import List
from datetime import datetime

from .base import Base

class ProcessingStatus(str, enum.Enum):
    """
    Enum para os estados de processamento de um documento.
    """
    PENDING = "PENDING"
    TEXT_EXTRACTED = "TEXT_EXTRACTED"
    Approve = "Approve"
    IN_ANALYSIS = "IN_ANALYSIS"
    REJECTED = "REJECTED"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    ARCHIVED = "ARCHIVED"
    AVAILABLE = "AVAILABLE"


class Document(Base):
    """
    Modelo SQLAlchemy que representa a tabela 'documents' na base de dados.
    """
    __tablename__ = "books"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(300), nullable=True)
    pdfUrl: Mapped[str] = mapped_column(String(255), nullable=False)
    cover_file_key: Mapped[str] = mapped_column(String(255), nullable=False)
    coverImage: Mapped[str] = mapped_column(String(255), nullable=False)
    page_count: Mapped[int] = mapped_column(Integer, nullable=False)
    pdf_file_key: Mapped[str] = mapped_column(String(255), nullable=False)
    pdf_file_name: Mapped[str] = mapped_column(String(255), nullable=False)

    status: Mapped[ProcessingStatus] = mapped_column(
        SQLAlchemyEnum(ProcessingStatus, name="processing_status_enum"), 
        nullable=False, 
        default=ProcessingStatus.PENDING
    )

    date_added: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    
    # Relacionamento com a tabela 'users'
    owner_id: Mapped[uuid.UUID] = mapped_column(
            UUID(as_uuid=True),
            ForeignKey("users.id", ondelete="CASCADE"), 
            nullable=False
        )
    owner: Mapped["User"] = relationship(back_populates="books")

    # Relacionamento com a tabela 'audio_segments'
    # cascade="all, delete-orphan" garante que ao deletar um Document,
    # todos os seus AudioSegments também sejam deletados
    segments: Mapped[List["AudioSegment"]] = relationship(
        back_populates="document",
        cascade="all, delete-orphan"
    )
