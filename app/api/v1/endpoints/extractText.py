from fastapi import (
    APIRouter, File, Path, UploadFile, HTTPException, Depends, Form, BackgroundTasks
)
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.v1.schemas.document import DocumentCreate, Document as DocumentSchema
from app.crud import crud_document
from app.services.s3_service import S3Service
from app.services.text_extraction_service import TextExtractionService
from app.services.pdf_segmenter import PDFSegmenterService
from app.services.text_preprocessor_service import TextPreprocessorService
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

def get_text_extraction_service():
    return TextExtractionService(pdf_segmenter=PDFSegmenterService(),preprocessor=TextPreprocessorService())

# @router.post("/extract-text")
# async def extract_text_from_pdf(
#     background_tasks: BackgroundTasks,
#     db: Session = Depends(get_db),
#     service: TextExtractionService = Depends(get_text_extraction_service)
# ):
#     """
#     Recebe um PDF, cria um registo de Documento e inicia a extração de texto em segundo plano.
#     """

#     # 1. Cria o registo do documento na base de dados
#     doc_create = DocumentCreate(title=title, pdf_file_name=file.filename)
#     db_document = crud_document.create_document(db=db, document=doc_create)
    
#     pdf_bytes = await file.rea

#     # 2. Adiciona a tarefa de longa duração para ser executada em segundo plano
#     background_tasks.add_task(
#         service.extract_and_save_text,
#         db=db,
#         document_id=db_document.id,
#         pdf_bytes=pdf_bytes,
#         segmentation_mode="page"
#     )
    
#     logger.info(f"Tarefa de extração de texto agendada para o documento '{title}' (ID: {db_document.id}).")
    
#     return db_document


def get_text_extraction_service():
    return TextExtractionService(pdf_segmenter=PDFSegmenterService(),preprocessor=TextPreprocessorService())

@router.post("/documents/{document_id}/extract-text", response_model=DocumentSchema)
async def extract_text_from_existing_document(
    background_tasks: BackgroundTasks,
    document_id: int = Path(..., description="O ID do livro que já existe no banco de dados."),
    db: Session = Depends(get_db),
    service: TextExtractionService = Depends(get_text_extraction_service)
):
    """
    Recebe um ID de um livro existente e um PDF, e inicia a extração de texto 
    para esse livro em segundo plano.
    """
    # 1. Busca o livro no banco de dados usando o ID fornecido.
    db_document = crud_document.get_document(db=db, document_id=document_id)
    if not db_document:
        raise HTTPException(status_code=404, detail="Livro não encontrado com o ID fornecido.")
    if not db_document.pdf_file_key:
        raise HTTPException(status_code=400, detail="Documento não possui uma chave de ficheiro PDF associada para a extração.")
    # 2. Adiciona a tarefa de extração para ser executada em segundo plano.
    background_tasks.add_task(
        service.extract_and_save_text,
        db=db,
        pdf_file_key=db_document.pdf_file_key,  # Mantido como bytes vazios conforme o código original
        document_id=db_document.id,
        segmentation_mode="page" # Mantido conforme o código original
    )
    
    logger.info(f"Tarefa de extração de texto agendada para o livro '{db_document.title}' (ID: {db_document.id}).")
    
    # 3. Retorna os dados do livro que foi encontrado e para o qual a tarefa foi agendada.
    return db_document
@router.post("/documents/{document_id}/generate-audio")
async def extract_text_from_existing_document(
    background_tasks: BackgroundTasks,
    document_id: int = Path(..., description="O ID do livro que já existe no banco de dados."),
    db: Session = Depends(get_db),
    service: TextExtractionService = Depends(get_text_extraction_service)
):
    """
    Recebe um ID de um livro existente e um PDF, e inicia a extração de texto 
    para esse livro em segundo plano.
    """
    # 1. Busca o livro no banco de dados usando o ID fornecido.
    db_document = crud_document.get_document(db=db, document_id=document_id)
    if not db_document:
        raise HTTPException(status_code=404, detail="Livro não encontrado com o ID fornecido.")
    if not db_document.pdf_file_key:
        raise HTTPException(status_code=400, detail="Documento não possui uma chave de ficheiro PDF associada para a extração.")
    # 2. Adiciona a tarefa de extração para ser executada em segundo plano.
    background_tasks.add_task(
        service.extract_and_save_text,
        db=db,
        pdf_file_key=db_document.pdf_file_key,  # Mantido como bytes vazios conforme o código original
        document_id=db_document.id,
        segmentation_mode="page" # Mantido conforme o código original
    )
    
    logger.info(f"Tarefa de extração de texto agendada para o livro '{db_document.title}' (ID: {db_document.id}).")
    
    # 3. Retorna os dados do livro que foi encontrado e para o qual a tarefa foi agendada.
    return db_document