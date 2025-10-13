from sqlalchemy.orm import Session
from typing import List

from app.models.audio_segment import AudioSegment
from app.api.v1.schemas.audio_segment import AudioSegmentCreate

def bulk_create_audio_segments(
    db: Session, *, segments_in: List[AudioSegmentCreate], document_id: int
) -> List[AudioSegment]:
    """
    Cria múltiplos registos de segmentos de áudio de uma só vez para um documento.

    Args:
        db: A sessão da base de dados.
        segments_in: Uma lista de schemas Pydantic com os dados dos segmentos.
        document_id: O ID do documento ao qual estes segmentos pertencem.

    Returns:
        A lista de objetos do modelo AudioSegment que foram criados.
    """
    db_segments = [
        AudioSegment(**segment.model_dump(), document_id=document_id)
        for segment in segments_in
    ]
    db.add_all(db_segments)
    db.commit()
    # Não há necessidade de db.refresh aqui, pois os objetos já estão atualizados
    return db_segments

def get_segments_for_document(db: Session, document_id: int) -> List[AudioSegment]:
    """
    Obtém todos os segmentos de áudio associados a um documento específico.

    Args:
        db: A sessão da base de dados.
        document_id: O ID do documento.

    Returns:
        Uma lista de objetos do modelo AudioSegment, ordenados pelo seu índice.
    """
    return (
        db.query(AudioSegment)
        .filter(AudioSegment.document_id == document_id)
        .order_by(AudioSegment.segment_index)
        .all()
    )

def update_segment_s3_url(db: Session, segment_id: int, s3_url: str) -> AudioSegment | None:
    """
    Atualiza um segmento específico com o URL do ficheiro de áudio no S3.

    Args:
        db: A sessão da base de dados.
        segment_id: O ID do segmento a ser atualizado.
        s3_url: O URL público do ficheiro de áudio no S3.

    Returns:
        O objeto do modelo AudioSegment atualizado, se encontrado.
    """
    db_segment = db.query(AudioSegment).filter(AudioSegment.id == segment_id).first()
    if db_segment:
        db_segment.s3_url = s3_url
        db.commit()
        db.refresh(db_segment)
    return db_segment

