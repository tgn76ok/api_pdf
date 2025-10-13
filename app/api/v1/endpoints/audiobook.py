# app/api/v1/endpoints/audiobook.py
from fastapi import (
    APIRouter,
    File,
    UploadFile,
    HTTPException,
    Depends,
    Form,
)
from typing import Optional
import logging

# Importe todos os serviços necessários
from app.services.audiobook_generator_service import AudiobookGeneratorService
from app.services.pdf_segmenter import PDFSegmenterService
from app.services.elevenlabs_service import ElevenLabsService
from app.services.s3_service import S3Service

logger = logging.getLogger(__name__)
router = APIRouter()

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, Path
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.crud import crud_document
from app.services.audio_generation_service import AudioGenerationService

from app.api.v1.schemas.document import Document as DocumentSchema

# --- Injeção de Dependências ---
# Esta abordagem permite que o FastAPI gerencie o ciclo de vida dos serviços.
def get_audiobook_service() -> AudiobookGeneratorService:
    # Em uma aplicação real, você poderia ter lógicas mais complexas aqui.
    return AudiobookGeneratorService(
        pdf_segmenter=PDFSegmenterService(),
        elevenlabs_service=ElevenLabsService(),
        s3_service=S3Service(),
    )

@router.post("/pdf-to-audiobook")
async def create_audiobook_from_pdf(
    file: UploadFile = File(..., description="Arquivo PDF para conversão."),
    segmentation_mode: str = Form(
        "page",
        enum=["page", "chapter"],
        description="Modo de segmentação: 'page' para processar página por página, 'chapter' para usar a detecção de capítulos."
    ),
    book_title: Optional[str] = Form(None, description="Título do livro (opcional, usa o nome do arquivo se não for fornecido)."),
    service: AudiobookGeneratorService = Depends(get_audiobook_service),
):
    """
    Endpoint completo para converter um PDF em um audiobook.
    Recebe um PDF, o processa conforme o modo de segmentação, gera o áudio
    para cada segmento e faz o upload para o S3, retornando as URLs.
    """
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Formato de arquivo inválido. Apenas PDFs são aceitos.")

    try:
        pdf_bytes = await file.read()
        title = book_title or file.filename.rsplit('.', 1)[0]

        logger.info(f"Iniciando trabalho de audiobook para '{title}' com modo '{segmentation_mode}'.")
        
        # O processo pode ser demorado. Em produção, isso deveria ser uma tarefa em background (Celery, ARQ).
        results = service.generate(pdf_bytes, title, "page")
        
        return {
            "message": "Processo de geração de audiobook concluído.",
            "book_title": title,
            "segmentation_mode": segmentation_mode,
            "results": results,
        }

    except ValueError as ve:
        logger.error(f"Erro de valor durante o processamento de {file.filename}: {ve}")
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"Erro inesperado ao processar {file.filename}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Ocorreu um erro interno no servidor.")
    
def get_audio_generation_service():
    return AudioGenerationService(
        elevenlabs_service=ElevenLabsService(),
        s3_service=S3Service()
    )

@router.post("/generate-audio/{document_id}", response_model=DocumentSchema)
async def generate_audio_for_document_endpoint(
    background_tasks: BackgroundTasks,
    document_id: int = Path(..., description="O ID do documento para o qual gerar áudio."),
    db: Session = Depends(get_db),
    service: AudioGenerationService = Depends(get_audio_generation_service)
):
    """
    Inicia a geração de áudio em segundo plano para um documento existente.
    """
    db_document = crud_document.get_document(db, document_id)
    if not db_document:
        raise HTTPException(status_code=404, detail="Documento não encontrado.")

    background_tasks.add_task(
        service.generate_audio_for_document,
        db=db,
        document_id=document_id
    )

    logger.info(f"Tarefa de geração de áudio agendada para o documento ID: {document_id}.")
    
    # Retorna o estado atual do documento
    return db_document
