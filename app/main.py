from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.endpoints.pdf import router as pdf_router
from app.api.v1.endpoints.tts import router as tts_router  # <-- IMPORTAR O NOVO ROUTER
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Cria a instância da aplicação FastAPI
app = FastAPI(
    title="PDF Segmentation API",
    description="API para segmentar PDFs em capítulos com base em títulos e sumários.",
    version="1.0.0"
)

# Configurar CORS para permitir acesso de qualquer origem
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, restrinja a origens específicas
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Adiciona um endpoint raiz para verificação de saúde
@app.get("/", tags=["Root"])
async def read_root():
    """Endpoint raiz que retorna uma mensagem de boas-vindas."""
    logger.info("Acessando o endpoint raiz.")
    return {"message": "Bem-vindo à API de Segmentação de PDFs! Acesse /docs para a documentação."}

# Inclui as rotas definidas no módulo de PDF
# O prefixo /api/v1 ajuda a versionar a API
app.include_router(pdf_router, prefix="/api/v1", tags=["PDF Segmentation"])
app.include_router(tts_router, prefix="/api/v1/tts", tags=["Text-to-Speech"]) # <-- ADICIONAR O NOVO ROUTER
