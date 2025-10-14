from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional
from enum import Enum
# Importa o schema do AudioSegment para poder aninhá-lo
from .audio_segment import AudioSegment

# Importa o Enum do modelo para garantir que o campo 'status' seja sempre um valor válido
from app.models.document import ProcessingStatus

class DocumentBase(BaseModel):
    """
    Schema base com os campos comuns que um documento sempre terá.
    """
    original_filename: str
    title: Optional[str] = None


class DocumentCreate(DocumentBase):
    """
    Schema usado especificamente para validar os dados ao criar um novo documento.
    Neste caso, é igual ao base, mas poderia ter campos adicionais no futuro.
    """
    pass

class Document(DocumentBase):
    """
    Schema completo usado para retornar um documento pela API.
    Inclui campos gerados pela base de dados (como id, created_at) e
    relacionamentos com outros dados (como os segmentos de áudio).
    """
    id: int
    owner_id: int
    status: ProcessingStatus  # Garante que o status seja um dos valores do Enum
    created_at: datetime
    
    # Aninha uma lista de schemas de AudioSegment, mostrando todos os
    # segmentos de áudio que pertencem a este documento.
    segments: List[AudioSegment] = []

    class Config:
        """
        Configuração do Pydantic que permite que ele funcione diretamente
        com os modelos do SQLAlchemy (ORM), convertendo-os para JSON.
        """
        orm_mode = True

class SegmentationMode(str, Enum):
    PAGE = "page"
    CHAPTER = "chapter"
