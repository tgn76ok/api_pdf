# app/models/audio_segment.py
from sqlalchemy import String, Integer, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base


class AudioSegment(Base):
    """
    Modelo SQLAlchemy que representa a tabela 'audio_segments' na base de dados.
    Cada segmento representa uma parte do documento (página ou capítulo) que será convertida em áudio.
    """
    __tablename__ = "audio_segments"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    
    # Relacionamento com Document
    document_id: Mapped[int] = mapped_column(ForeignKey("books.id"), nullable=False)
    document: Mapped["Document"] = relationship(back_populates="segments")
    
    # Índice do segmento dentro do documento (1, 2, 3...)
    segment_index: Mapped[int] = mapped_column(Integer, nullable=False)
    
    # Título do segmento (ex: "Capítulo 1", "Página 5")
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    
    # Conteúdo de texto extraído e pré-processado
    text_content: Mapped[str] = mapped_column(Text, nullable=True)
    
    # URL do ficheiro de áudio no S3 (null enquanto não for gerado)
    s3_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
