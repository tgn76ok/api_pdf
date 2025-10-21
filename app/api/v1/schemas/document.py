import uuid
from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import List, Optional
from enum import Enum

from .audio_segment import AudioSegment
from app.models.document import ProcessingStatus


class SegmentationMode(str, Enum):
    """Modos de segmentação disponíveis."""
    PAGE = "page"
    CHAPTER = "chapter"


class DocumentBase(BaseModel):
    """Schema base - SOMENTE campos que o usuário pode fornecer."""
    title: Optional[str] = None


class DocumentCreate(DocumentBase):
    """Schema para criar um documento."""
    pass


class Document(BaseModel):
    """
    Schema completo para retornar um documento pela API.
    ⚠️ Corresponde EXATAMENTE aos campos do TypeScript Book entity.
    """
    # ===== CAMPOS OBRIGATÓRIOS =====
    id: int
    owner_id: uuid.UUID
    status: ProcessingStatus
    created_at: datetime
    
    # ===== CAMPOS OPCIONAIS =====
    title: str
    description: Optional[str] = None
    publication_date: Optional[datetime] = None
    volume_edition: Optional[str] = None
    visit_count: int = 0
    language: str
    visible: bool = False
    is_audio: bool = False
    page_count: int = 0
    
    # ===== CAMPOS DE ARQUIVOS =====
    cover_file_key: Optional[str] = None
    pdf_file_key: Optional[str] = None
    cover_image_url: Optional[str] = None
    pdf_image_url: Optional[str] = None
    
    # ===== RELACIONAMENTOS =====
    segments: List[AudioSegment] = []

    model_config = ConfigDict(from_attributes=True)

