# app/crud/crud_document.py
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from app.models.document import Document, ProcessingStatus
from app.models.audio_segment import AudioSegment
from app.api.v1.schemas.document import DocumentCreate

def create_document(db: Session, document: DocumentCreate, owner_id: int) -> Document:
    """
    Cria um novo registo de documento na base de dados.
    """
    db_document = Document(
        **document.model_dump(), 
        owner_id=owner_id,
        status=ProcessingStatus.PENDING
    )
    db.add(db_document)
    db.commit()
    db.refresh(db_document)
    return db_document


def get_document(db: Session, document_id: int) -> Optional[Document]:
    """
    Obtém um único documento pelo seu ID.
    """
    return db.query(Document).filter(Document.id == document_id).first()


def get_all_documents(
    db: Session, 
    skip: int = 0, 
    limit: int = 100,
    status: Optional[ProcessingStatus] = None
) -> List[Document]:
    """
    Obtém todos os documentos com suporte a paginação e filtro por status.
    
    Args:
        db: A sessão da base de dados.
        skip: Número de registos a saltar (para paginação).
        limit: Número máximo de registos a retornar.
        status: Filtro opcional por status de processamento.
    
    Returns:
        Lista de objetos Document.
    """
    query = db.query(Document)
    
    if status:
        query = query.filter(Document.status == status)
    
    return query.order_by(Document.created_at.desc()).offset(skip).limit(limit).all()


def update_document_status(
    db: Session, 
    document_id: int, 
    status: ProcessingStatus
) -> Optional[Document]:
    """
    Atualiza o estado de processamento de um documento.
    """
    db_document = get_document(db, document_id)
    if db_document:
        db_document.status = status
        db.commit()
        db.refresh(db_document)
    return db_document


def delete_document(db: Session, document_id: int) -> bool:
    """
    Deleta um documento e todos os seus segmentos de áudio associados.
    
    Args:
        db: A sessão da base de dados.
        document_id: O ID do documento a ser deletado.
    
    Returns:
        True se deletado com sucesso, False caso contrário.
    """
    db_document = get_document(db, document_id)
    
    if not db_document:
        return False
    
    # SQLAlchemy vai deletar os segmentos automaticamente se a relação 
    # estiver configurada com cascade="all, delete-orphan"
    db.delete(db_document)
    db.commit()
    return True


def get_documents_stats(db: Session) -> dict:
    """
    Retorna estatísticas gerais sobre os documentos no sistema.
    
    Returns:
        Dicionário com contagens por status e total.
    """
    total = db.query(func.count(Document.id)).scalar()
    
    stats_by_status = (
        db.query(Document.status, func.count(Document.id))
        .group_by(Document.status)
        .all()
    )
    
    status_counts = {status.value: count for status, count in stats_by_status}
    
    # Total de segmentos de áudio gerados
    total_segments = db.query(func.count(AudioSegment.id)).scalar()
    segments_with_audio = (
        db.query(func.count(AudioSegment.id))
        .filter(AudioSegment.s3_url.isnot(None))
        .scalar()
    )
    
    return {
        "total_documents": total,
        "by_status": status_counts,
        "total_audio_segments": total_segments,
        "segments_with_audio": segments_with_audio
    }


def get_documents_by_owner(
    db: Session, 
    owner_id: int, 
    skip: int = 0, 
    limit: int = 100
) -> List[Document]:
    """
    Obtém todos os documentos de um proprietário específico.
    """
    return (
        db.query(Document)
        .filter(Document.owner_id == owner_id)
        .order_by(Document.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def count_documents(db: Session, owner_id: Optional[int] = None) -> int:
    """
    Conta o número total de documentos, opcionalmente filtrado por proprietário.
    """
    query = db.query(func.count(Document.id))
    
    if owner_id:
        query = query.filter(Document.owner_id == owner_id)
    
    return query.scalar()