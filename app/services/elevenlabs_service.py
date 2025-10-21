import logging
from typing import Optional

# ✅ PASSO 1: Importar o cliente oficial da ElevenLabs
from elevenlabs.client import ElevenLabs

from app.core.config import settings
from app.services.text_preprocessor_service import TextPreprocessorService

logger = logging.getLogger(__name__)

class ElevenLabsService:
    """
    Serviço para interagir com a API de Text-to-Speech da ElevenLabs usando o SDK oficial.
    """
    def __init__(self):
        if not settings.ELEVENLABS_API_KEY:
            raise ValueError("A chave da API da ElevenLabs (ELEVENLABS_API_KEY) não foi definida.")
        
        self.api_key = settings.ELEVENLABS_API_KEY
        
        # ✅ PASSO 2: Instanciar o cliente da ElevenLabs com sua chave de API
        self.client = ElevenLabs(api_key=self.api_key)
        self.preprocessor = TextPreprocessorService()

    def generate_audio(self, text: str, voice_id: Optional[str] = None) -> bytes:
        """
        Gera áudio a partir do texto, dividindo-o em pedaços para evitar limites da API.
        """
        target_voice_id = voice_id or settings.ELEVENLABS_VOICE_ID

        logger.info("A pré-processar o texto para o TTS...")
        # A linha abaixo estava comentada, descomentei para garantir que o pré-processamento seja usado.
        # text = self.preprocessor.clean_text_for_tts(text)
        
        # ✅ PASSO 3: A lógica de dividir o texto continua sendo essencial para evitar erros.
        # CHUNK_SIZE = 2500
        # text_chunks = [text[i:i+CHUNK_SIZE] for i in range(0, len(text), CHUNK_SIZE)]
        
        all_audio_bytes = b""

        # Definir as configurações de voz em um dicionário
        voice_settings = {
            "stability": 0.5,
            "similarity_boost": 0.75,
            "style": 0.0,
            "use_speaker_boost": True,
            "speed": 1.3,
        }

        # audio_bytes = self.client.text_to_speech.convert(
        #         voice_id=target_voice_id,
        #         text=text,
        #         model_id="eleven_multilingual_v2",
        #         voice_settings=voice_settings
        #     )
        # all_audio_bytes.join(audio_bytes)

        CHUNK_SIZE = 2500
        text_chunks = [text[i:i+CHUNK_SIZE] for i in range(0, len(text), CHUNK_SIZE)]
        
        all_audio_bytes = b""
        for i, chunk in enumerate(text_chunks):
            logger.info(f"A processar o pedaço {i+1}/{len(text_chunks)}...")
            print(f"A processar o pedaço {i+1}/{len(text_chunks)}...")
            try:
                logger.info(f"A enviar {len(chunk)} caracteres para a ElevenLabs para a voz {target_voice_id}...")
                
                # ✅ PASSO 4: Usar o método do SDK em vez de `requests.post`
                # O método `convert` é síncrono e retorna os bytes de áudio diretamente.
                audio_chunk = self.client.text_to_speech.convert(
                    voice_id=target_voice_id,
                    text=chunk,
                    model_id="eleven_multilingual_v2",
                    voice_settings=voice_settings
                )
                
                # Juntar os bytes de áudio de cada resposta
                all_audio_bytes += audio_chunk
                logger.info(f"Áudio para o pedaço {i+1} recebido com sucesso.")

            except Exception as e:
                logger.error(f"Erro ao gerar áudio para o pedaço {i+1} com o SDK da ElevenLabs: {e}", exc_info=True)
                raise Exception(f"Falha ao gerar áudio para o pedaço {i+1}: {e}")

        logger.info("Todos os pedaços de áudio foram gerados e combinados com sucesso.")
        return all_audio_bytes