import enum
import uuid
from sqlalchemy import String, DateTime, ForeignKey, Enum as SQLAlchemyEnum, Integer, Text, Boolean, Date, BigInteger
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID 
from typing import List
from datetime import datetime, date
from .base import Base


class ProcessingStatus(str, enum.Enum):
    """Enum para os estados de processamento de um documento."""
    PENDING = "PENDING"
    TEXT_EXTRACTED = "TEXT_EXTRACTED"
    APPROVE = "Approve"
    IN_ANALYSIS = "IN_ANALYSIS"
    REJECTED = "REJECTED"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    ARCHIVED = "ARCHIVED"
    AVAILABLE = "AVAILABLE"


class Document(Base):
    """
    Modelo SQLAlchemy que representa a tabela 'books' na base de dados.
    ⚠️ Corresponde EXATAMENTE à entity TypeScript Book.
    """
    __tablename__ = "books"

    # ===== PRIMARY KEY =====
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    
    # ===== CAMPOS PRINCIPAIS =====
    title: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    publication_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    volume_edition: Mapped[str | None] = mapped_column(String, nullable=True)
    visit_count: Mapped[int] = mapped_column(BigInteger, default=0)
    language: Mapped[str] = mapped_column(String, nullable=False)
    visible: Mapped[bool] = mapped_column(Boolean, default=False)
    is_audio: Mapped[bool] = mapped_column(Boolean, default=False)
    page_count: Mapped[int] = mapped_column(Integer, default=0)
    
    # ===== CAMPOS DE ARQUIVOS =====
    cover_file_key: Mapped[str | None] = mapped_column(Text, nullable=True)
    cover_image_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    pdf_file_key: Mapped[str | None] = mapped_column(Text, nullable=True)
    pdf_image_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    # ===== STATUS =====
    status: Mapped[ProcessingStatus] = mapped_column(
        SQLAlchemyEnum(ProcessingStatus, name="processing_status_enum"),
        nullable=False,
        default=ProcessingStatus.PENDING
    )
    
    # ===== TIMESTAMPS =====
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # ===== RELACIONAMENTOS =====
    owner_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )
    owner: Mapped["User"] = relationship(back_populates="books")
    
    segments: Mapped[List["AudioSegment"]] = relationship(
        back_populates="document",
        cascade="all, delete-orphan"
    )
