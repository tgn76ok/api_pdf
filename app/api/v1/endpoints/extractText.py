from fastapi import (
    APIRouter, File, UploadFile, HTTPException, Depends, Form, BackgroundTasks
)
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.v1.schemas.document import DocumentCreate, Document as DocumentSchema
from app.crud import crud_document
from app.services.text_extraction_service import TextExtractionService
from app.services.pdf_segmenter import PDFSegmenterService
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

def get_text_extraction_service():
    return TextExtractionService(pdf_segmenter=PDFSegmenterService())

@router.post("/extract-text", response_model=DocumentSchema)
async def extract_text_from_pdf(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(..., description="Arquivo PDF para extração."),
    book_title: str = Form(None, description="Título do livro."),
    db: Session = Depends(get_db),
    service: TextExtractionService = Depends(get_text_extraction_service)
):
    """
    Recebe um PDF, cria um registo de Documento e inicia a extração de texto em segundo plano.
    """
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Apenas PDFs são aceitos.")

    title = book_title or file.filename.rsplit('.', 1)[0]
    
    # 1. Cria o registo do documento na base de dados
    doc_create = DocumentCreate(title=title, original_filename=file.filename)
    db_document = crud_document.create_document(db=db, document=doc_create)
    
    pdf_bytes = await file.read()

    # 2. Adiciona a tarefa de longa duração para ser executada em segundo plano
    background_tasks.add_task(
        service.extract_and_save_text,
        db=db,
        document_id=db_document.id,
        pdf_bytes=pdf_bytes,
        segmentation_mode="page"
    )
    
    logger.info(f"Tarefa de extração de texto agendada para o documento '{title}' (ID: {db_document.id}).")
    
    return db_document
