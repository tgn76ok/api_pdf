from pydantic import BaseModel, ConfigDict, Field
from typing import Optional


class AudioSegmentBase(BaseModel):
    """Schema base com os campos que definem um segmento de áudio."""
    title: str
    segment_index: int
    text_content: Optional[str] = None


class AudioSegmentCreate(AudioSegmentBase):
    """Schema usado ao criar um novo segmento na base de dados."""
    pass


class AudioSegment(AudioSegmentBase):
    """
    Schema completo usado para retornar um segmento de áudio pela API.
    """
    id: int
    book_id: int  # ✅ CORRIGIDO: Mudou de document_id para book_id
    
    # Campos de áudio
    audio_file_key: Optional[str] = None
    audio_file_size: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
