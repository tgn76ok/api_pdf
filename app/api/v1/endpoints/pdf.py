# app/api/v1/endpoints/pdf.py
from fastapi import APIRouter, File, UploadFile, HTTPException, Depends
from fastapi.responses import JSONResponse
from app.services.pdf_segmenter import PDFSegmenterService
from app.api.v1.schemas.pdf import SegmentationResponse
import logging

# Configuração do logger para este módulo
logger = logging.getLogger(__name__)

# Cria um router para agrupar os endpoints relacionados a PDF
router = APIRouter()

# Função de dependência para injetar o serviço
def get_segmenter_service():
    """Cria e retorna uma instância do serviço de segmentação."""
    return PDFSegmenterService()

@router.post("/segment", response_model=SegmentationResponse)
async def segment_pdf_endpoint(
    file: UploadFile = File(..., description="Arquivo PDF para ser segmentado."),
    service: PDFSegmenterService = Depends(get_segmenter_service)
):
    """
    Recebe um arquivo PDF, o segmenta em capítulos e retorna o resultado.
    """
    if not file.filename.lower().endswith(".pdf"):
        logger.warning(f"Tentativa de upload de arquivo não-PDF: {file.filename}")
        raise HTTPException(status_code=400, detail="Formato de arquivo inválido. Apenas PDFs são aceitos.")
    
    try:
        logger.info(f"Iniciando segmentação do arquivo: {file.filename}")
        pdf_bytes = await file.read()
        
        if not pdf_bytes:
            logger.warning(f"Arquivo PDF vazio recebido: {file.filename}")
            raise HTTPException(status_code=400, detail="O arquivo PDF não pode estar vazio.")

        # Chama o serviço para processar o PDF
        result = service.segment_pdf(pdf_bytes)
        
        logger.info(f"Segmentação concluída com sucesso para o arquivo: {file.filename}")
        return JSONResponse(content=result, status_code=200)

    except ValueError as ve:
        logger.error(f"Erro de valor durante o processamento de {file.filename}: {ve}")
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"Erro inesperado ao processar {file.filename}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Ocorreu um erro interno no servidor.")
