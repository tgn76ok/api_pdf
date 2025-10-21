import requests
from typing import Optional
import logging
from app.core.config import settings
from app.services.text_preprocessor_service import TextPreprocessorService # <-- IMPORTAR O NOVO SERVIÇO

logger = logging.getLogger(__name__)

class ElevenLabsService:
    """
    Serviço para interagir com a API de Text-to-Speech da ElevenLabs.
    """
    def __init__(self):
        if not settings.ELEVENLABS_API_KEY:
            raise ValueError("A chave da API da ElevenLabs (ELEVENLABS_API_KEY) não foi definida.")
        
        self.api_key = settings.ELEVENLABS_API_KEY
        self.base_url = "https://api.elevenlabs.io/v1"
        self.preprocessor = TextPreprocessorService() # <-- INSTANCIAR O PRÉ-PROCESSADOR

    def generate_audio(self, text: str, voice_id: Optional[str] = None) -> bytes:
        """
        Gera o áudio a partir do texto fornecido, após limpá-lo.
        """
        target_voice_id = voice_id or settings.ELEVENLABS_VOICE_ID

        # --- NOVO PASSO DE TRATAMENTO ---
        # Limpa e prepara o texto antes de o enviar para a API.
        logger.info("A pré-processar o texto para o TTS...")
        cleaned_text = self.preprocessor.clean_text_for_tts(text)
        # --------------------------------

        tts_url = f"{self.base_url}/text-to-speech/{target_voice_id}"

        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": self.api_key
        }

        data = {
            "text": cleaned_text, # <-- USAR O TEXTO LIMPO
            "model_id": "eleven_multilingual_v2",
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.75,
                "style": 0.0,
                "use_speaker_boost": True,
                "speed": 1.3,
            }
        }

        try:
            logger.info(f"A enviar {len(cleaned_text)} caracteres para a ElevenLabs para a voz {target_voice_id}...")
            response = requests.post(tts_url, json=data, headers=headers)
            response.raise_for_status()
            logger.info("Áudio recebido com sucesso da ElevenLabs.")
            return response.content
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro na comunicação com a API da ElevenLabs: {e}")
            raise Exception(f"Falha ao gerar áudio: {e.response.text if e.response else e}")

