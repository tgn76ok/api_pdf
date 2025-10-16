from sqlalchemy import String, Integer, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base

class AudioSegment(Base):
    """
    Modelo SQLAlchemy que representa a tabela 'audio_segments'.
    """
    __tablename__ = "audio_segments"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    
    # Garante que a chave estrangeira aponta para a tabela 'documents'
    document_id: Mapped[int] = mapped_column(ForeignKey("books.id"), nullable=False)
    document: Mapped["Document"] = relationship(back_populates="segments")
    
    segment_index: Mapped[int] = mapped_column(Integer, nullable=False)
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    text_content: Mapped[str] = mapped_column(Text, nullable=True)
    
    # --- CORREÇÃO: Removido o campo 's3_url' que não existe na base de dados ---
    # s3_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    
    # Mantidos os outros campos de áudio que devem existir na BD
    audio_file_key: Mapped[str | None] = mapped_column(String(512),  nullable=True)
    audio_url: Mapped[str | None] = mapped_column(String(512),  nullable=True)
    audio_file_name: Mapped[str | None] = mapped_column(String(255),  nullable=True)
    audio_file_size: Mapped[str | None] = mapped_column(String(255),  nullable=True)

