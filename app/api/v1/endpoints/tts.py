from fastapi import APIRouter, HTTPException, Body
from fastapi.responses import StreamingResponse
from app.services.elevenlabs_service import ElevenLabsService
import logging
import io

router = APIRouter()
logger = logging.getLogger(__name__)

# Instanciar o serviço fora da função do endpoint para reutilização
try:
    elevenlabs_service = ElevenLabsService()
except ValueError as e:
    logger.error(f"Não foi possível inicializar o ElevenLabsService: {e}")
    elevenlabs_service = None

@router.post("/generate-audio", response_class=StreamingResponse)
async def generate_audio_endpoint(text: str = Body(..., embed=True, description="O texto a ser convertido em áudio.")):
    """
    Converte o texto fornecido em áudio usando a API da ElevenLabs e devolve-o como um stream.
    """
    if not elevenlabs_service:
        raise HTTPException(
            status_code=503, 
            detail="O serviço de TTS não está disponível devido a um erro de configuração."
        )

    if not text or not text.strip():
        raise HTTPException(status_code=400, detail="O texto não pode estar vazio.")

    try:
        audio_bytes = elevenlabs_service.generate_audio(text)
        
        # Devolve os bytes do áudio como um stream de resposta
        return StreamingResponse(io.BytesIO(audio_bytes), media_type="audio/mpeg")

    except Exception as e:
        logger.error(f"Erro ao gerar áudio: {e}")
        raise HTTPException(status_code=500, detail=str(e))
