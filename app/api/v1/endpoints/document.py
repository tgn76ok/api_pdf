# app/api/v1/endpoints/document.py
from fastapi import APIRouter, HTTPException, Depends, Query, Path
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.crud import crud_document
from app.api.v1.schemas.document import Document as DocumentSchema
from app.models.document import ProcessingStatus
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/", response_model=List[DocumentSchema])
async def get_all_documents(
    skip: int = Query(0, ge=0, description="Número de registos a saltar (paginação)"),
    limit: int = Query(100, ge=1, le=500, description="Número máximo de registos a retornar"),
    status: Optional[ProcessingStatus] = Query(None, description="Filtrar por status de processamento"),
    db: Session = Depends(get_db)
):
    """
    Retorna todos os documentos (livros) cadastrados no sistema.
    
    Suporta:
    - Paginação (skip/limit)
    - Filtro por status de processamento
    """
    try:
        logger.info(f"Buscando documentos: skip={skip}, limit={limit}, status={status}")
        
        documents = crud_document.get_all_documents(
            db=db, 
            skip=skip, 
            limit=limit,
            status=status
        )
        
        logger.info(f"Encontrados {len(documents)} documentos.")
        return documents
    
    except Exception as e:
        logger.error(f"Erro ao buscar documentos: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Erro ao buscar documentos.")


@router.get("/{document_id}", response_model=DocumentSchema)
async def get_document_by_id(
    document_id: int = Path(..., description="ID do documento a ser retornado"),
    db: Session = Depends(get_db)
):
    """
    Retorna um documento específico pelo seu ID, incluindo todos os seus segmentos de áudio.
    """
    try:
        logger.info(f"Buscando documento com ID: {document_id}")
        
        document = crud_document.get_document(db=db, document_id=document_id)
        
        if not document:
            logger.warning(f"Documento com ID {document_id} não encontrado.")
            raise HTTPException(status_code=404, detail="Documento não encontrado.")
        
        logger.info(f"Documento encontrado: '{document.title}'")
        return document
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao buscar documento {document_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Erro ao buscar documento.")


@router.delete("/{document_id}")
async def delete_document(
    document_id: int = Path(..., description="ID do documento a ser deletado"),
    db: Session = Depends(get_db)
):
    """
    Deleta um documento e todos os seus segmentos de áudio associados.
    """
    try:
        logger.info(f"Tentando deletar documento com ID: {document_id}")
        
        document = crud_document.get_document(db=db, document_id=document_id)
        
        if not document:
            logger.warning(f"Documento com ID {document_id} não encontrado.")
            raise HTTPException(status_code=404, detail="Documento não encontrado.")
        
        success = crud_document.delete_document(db=db, document_id=document_id)
        
        if success:
            logger.info(f"Documento {document_id} deletado com sucesso.")
            return {
                "message": f"Documento '{document.title}' deletado com sucesso.",
                "document_id": document_id
            }
        else:
            raise HTTPException(status_code=500, detail="Falha ao deletar documento.")
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao deletar documento {document_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Erro ao deletar documento.")


@router.get("/stats/summary")
async def get_documents_summary(db: Session = Depends(get_db)):
    """
    Retorna estatísticas gerais sobre os documentos no sistema.
    """
    try:
        logger.info("Buscando estatísticas de documentos.")
        
        stats = crud_document.get_documents_stats(db=db)
        
        logger.info("Estatísticas obtidas com sucesso.")
        return stats
    
    except Exception as e:
        logger.error(f"Erro ao buscar estatísticas: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Erro ao buscar estatísticas.")