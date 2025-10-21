from sqlalchemy import String, Integer, ForeignKey, Text, BigInteger
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base


class AudioSegment(Base):
    """
    Modelo SQLAlchemy que representa a tabela 'audio_segments'.
    ⚠️ IMPORTANTE: A FK no banco se chama 'book_id', não 'document_id'!
    """
    __tablename__ = "audio_segments"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    
    # ===== CORRIGIDO: Usar book_id =====
    book_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("books.id", ondelete="CASCADE"),
        nullable=False
    )
    
    # ===== RELACIONAMENTO =====
    document: Mapped["Document"] = relationship(
        back_populates="segments",
        foreign_keys=[book_id]
    )
    
    # ===== CAMPOS DO SEGMENTO =====
    segment_index: Mapped[int] = mapped_column(Integer, nullable=False)
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    text_content: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    # ===== CAMPOS DE ÁUDIO =====
    audio_file_key: Mapped[str | None] = mapped_column(String(512), nullable=True)
    audio_file_size: Mapped[str | None] = mapped_column(BigInteger, nullable=True)

