import enum
from sqlalchemy import String, DateTime, ForeignKey, Enum as SQLAlchemyEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from .base import Base
from typing import List
from datetime import datetime # <-- ATUALIZAÇÃO AQUI

# --- Definição do Enum ---
# Define os possíveis estados em que um trabalho de processamento de documento pode estar.
class ProcessingStatus(str, enum.Enum):
    """
    Enum para os estados de processamento de um documento.
    """
    PENDING = "pending"               # O trabalho foi criado, mas nada aconteceu ainda.
    TEXT_EXTRACTED = "text_extracted" # A extração de texto foi concluída com sucesso.
    PROCESSING = "processing"         # A geração de áudio está em andamento.
    COMPLETED = "completed"           # O trabalho foi concluído com sucesso.
    FAILED = "failed"                 # Ocorreu um erro durante o processo.


class Document(Base):
    """
    Modelo SQLAlchemy que representa a tabela 'documents' na base de dados.
    """
    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(300), nullable=True)
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    
    # A coluna 'status' na base de dados usará os valores do Enum ProcessingStatus.
    status: Mapped[ProcessingStatus] = mapped_column(
        SQLAlchemyEnum(ProcessingStatus, name="processing_status_enum"), 
        nullable=False, 
        default=ProcessingStatus.PENDING
    )

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    
    # Relacionamento com a tabela 'users'
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    owner: Mapped["User"] = relationship(back_populates="documents")

    # Relacionamento com a tabela 'audio_segments'
    segments: Mapped[List["AudioSegment"]] = relationship(back_populates="document")

