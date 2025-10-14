# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.endpoints.pdf import router as pdf_router
from app.api.v1.endpoints.tts import router as tts_router
from app.api.v1.endpoints.audiobook import router as audiobook_router
from app.api.v1.endpoints.extractText import router as extracttext_router
from app.api.v1.endpoints.document import router as document_router  # NOVO
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Cria a instância da aplicação FastAPI
app = FastAPI(
    title="PDF to Audiobook API",
    description="API completa para conversão de PDFs em audiobooks com segmentação inteligente.",
    version="2.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, especifique as origens permitidas
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["Root"])
async def read_root():
    """Endpoint raiz que retorna informações sobre a API."""
    logger.info("Acessando o endpoint raiz.")
    return {
        "message": "Bem-vindo à API de Conversão de PDF para Audiobook!",
        "version": "2.0.0",
        "docs": "/docs",
        "endpoints": {
            "documents": "/api/v1/documents",
            "pdf_segmentation": "/api/v1/pdf",
            "text_to_speech": "/api/v1/tts",
            "audiobook_generation": "/api/v1/audiobook",
            "text_extraction": "/api/v1/extractbook"
        }
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Endpoint de verificação de saúde da aplicação."""
    return {
        "status": "healthy",
        "service": "PDF to Audiobook API"
    }


# Incluir todos os routers
app.include_router(
    document_router, 
    prefix="/api/v1/documents", 
    tags=["Documents Management"]
)

app.include_router(
    pdf_router, 
    prefix="/api/v1/pdf", 
    tags=["PDF Segmentation"]
)

app.include_router(
    tts_router, 
    prefix="/api/v1/tts", 
    tags=["Text-to-Speech"]
)

app.include_router(
    audiobook_router, 
    prefix="/api/v1/audiobook", 
    tags=["Audiobook Generation"]
)

app.include_router(
    extracttext_router, 
    prefix="/api/v1/extractbook", 
    tags=["Text Extraction"]
)
