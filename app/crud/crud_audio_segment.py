from sqlalchemy.orm import Session
from typing import List
from app.models.audio_segment import AudioSegment
from app.api.v1.schemas.audio_segment import AudioSegmentCreate


def bulk_create_audio_segments(
    db: Session, 
    *, 
    segments_in: List[AudioSegmentCreate], 
    document_id: int
) -> List[AudioSegment]:
    """
    Cria múltiplos registos de segmentos de áudio.
    """
    db_segments = [
        AudioSegment(
            **segment.model_dump(),
            book_id=document_id  # ✅ CORRIGIDO: Mudou para book_id
        )
        for segment in segments_in
    ]
    db.add_all(db_segments)
    db.commit()
    return db_segments


def get_segments_for_document(db: Session, document_id: int) -> List[AudioSegment]:
    """Obtém todos os segmentos de áudio associados a um documento."""
    return (
        db.query(AudioSegment)
        .filter(AudioSegment.book_id == document_id)  # ✅ CORRIGIDO
        .order_by(AudioSegment.segment_index)
        .all()
    )
    
def delete_audio_segments_by_document(db: Session, document_id: int) -> None:
    """Exclui todos os segmentos de áudio associados a um documento."""
    db.query(AudioSegment).filter(AudioSegment.book_id == document_id).delete()  # ✅ CORRIGIDO
    db.commit()


def update_segment_audio_url(
    db: Session, 
    segment_id: int, 
    audio_url: str
) -> AudioSegment | None:
    """
    Atualiza um segmento com o URL do áudio.
    NOTA: Como não existe audio_url no banco, use audio_file_key.
    """
    db_segment = db.query(AudioSegment).filter(AudioSegment.id == segment_id).first()
    if db_segment:
        db_segment.audio_file_key = audio_url  # ✅ Usar audio_file_key
        db.commit()
        db.refresh(db_segment)
    return db_segment
