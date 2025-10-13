from sqlalchemy.orm import Session
from app.models.document import Document, ProcessingStatus
from app.api.v1.schemas.document import DocumentCreate

def create_document(db: Session, doc: DocumentCreate, owner_id: int) -> Document:
    """
    Cria um novo registo de documento na base de dados.

    Args:
        db: A sessão da base de dados.
        doc: O schema Pydantic com os dados do documento a ser criado.
        owner_id: O ID do utilizador dono do documento.

    Returns:
        O objeto do modelo Document que foi criado.
    """
    # Desempacota o schema Pydantic e adiciona o owner_id e o status inicial
    db_document = Document(
        **doc.model_dump(), 
        owner_id=owner_id,
        status=ProcessingStatus.PENDING # Um novo documento começa sempre como pendente
    )
    db.add(db_document)
    db.commit()
    db.refresh(db_document)
    return db_document

def get_document(db: Session, document_id: int) -> Document | None:
    """
    Obtém um único documento pelo seu ID.

    Args:
        db: A sessão da base de dados.
        document_id: O ID do documento a ser procurado.

    Returns:
        O objeto do modelo Document se encontrado, caso contrário None.
    """
    return db.query(Document).filter(Document.id == document_id).first()

def update_document_status(db: Session, document_id: int, status: ProcessingStatus) -> Document | None:
    """
    Atualiza o estado de processamento de um documento.

    Args:
        db: A sessão da base de dados.
        document_id: O ID do documento a ser atualizado.
        status: O novo valor para o ProcessingStatus.

    Returns:
        O objeto do modelo Document atualizado se encontrado, caso contrário None.
    """
    db_document = get_document(db, document_id)
    if db_document:
        db_document.status = status
        db.commit()
        db.refresh(db_document)
    return db_document

