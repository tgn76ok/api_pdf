from pydantic import BaseModel
from typing import Optional

class AudioSegmentBase(BaseModel):
    """
    Schema base com os campos que definem um segmento de áudio.
    """
    title: str
    segment_index: int
    text_content: Optional[str] = None


class AudioSegmentCreate(AudioSegmentBase):
    """
    Schema usado ao criar um novo segmento na base de dados.
    """
    pass


class AudioSegment(AudioSegmentBase):
    """
    Schema completo usado para retornar um segmento de áudio pela API.
    Inclui o ID e a URL do S3 depois de o áudio ser gerado.
    """
    id: int
    document_id: int
    s3_url: Optional[str] = None

    class Config:
        """
        Permite que o Pydantic leia os dados diretamente de um modelo SQLAlchemy.
        """
        from_attributes = True

