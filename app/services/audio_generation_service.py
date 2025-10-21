import logging
import re
from sqlalchemy.orm import Session
from app.services.elevenlabs_service import ElevenLabsService
from app.services.s3_service import S3Service
from app.crud import crud_document, crud_audio_segment  # ✅ Adicionar import
from app.models.document import ProcessingStatus, Document

logger = logging.getLogger(__name__)


class AudioGenerationService:
    def __init__(self, elevenlabs_service: ElevenLabsService, s3_service: S3Service):
        self.elevenlabs_service = elevenlabs_service
        self.s3_service = s3_service

    def _sanitize_filename(self, text: str) -> str:
        text = re.sub(r'[\\/*?:"<>|]', "", text)
        text = text.replace(" ", "_").lower()
        return text[:100]

    def generate_audio_for_document(self, db: Session, document_id: int):
        """Gera áudio para todos os segmentos de texto de um documento."""
        try:
            document = crud_document.get_document(db, document_id)
            if not document:
                raise ValueError(f"Documento com ID {document_id} não encontrado.")

            if document.status not in [ProcessingStatus.TEXT_EXTRACTED, ProcessingStatus.FAILED]:
                logger.warning(
                    f"Documento {document_id} está em '{document.status.value}'. "
                    f"Ideal: 'text_extracted'"
                )

            crud_document.update_document_status(db, document_id, ProcessingStatus.PROCESSING)
            logger.info(f"Iniciando geração de áudio para Documento ID {document_id}.")
            
            self._process_segments(db, document)

            crud_document.update_document_status(db, document_id, ProcessingStatus.COMPLETED)
            logger.info(f"Geração de áudio para Documento ID {document_id} concluída.")

        except Exception as e:
            logger.error(f"Falha na geração de áudio para Documento ID {document_id}: {e}", exc_info=True)
            crud_document.update_document_status(db, document_id, ProcessingStatus.FAILED)

    def _process_segments(self, db: Session, document: Document):
        safe_book_title = self._sanitize_filename(document.title)
        
        # ✅ CORRIGIDO: Usar audio_file_key em vez de s3_url
        segments_to_process = [seg for seg in document.segments if not seg.audio_file_key]

        if not segments_to_process:
            logger.info(f"Não há segmentos para processar para Documento ID {document.id}.")
            return

        for segment in segments_to_process:
            logger.info(f"Processando segmento {segment.segment_index} do Documento ID {document.id}...")
            
            audio_bytes = self.elevenlabs_service.generate_audio(segment.text_content)
            
            safe_unit_title = self._sanitize_filename(segment.title)
            filename = f"{safe_book_title}/{document.id}_{segment.segment_index:04d}_{safe_unit_title}.mp3"
            
            audio_url = self.s3_service.upload_audio(audio_bytes, filename)
            
            # ✅ CORRIGIDO: Usar update_segment_audio_url (que agora salva em audio_file_key)
            crud_audio_segment.update_segment_audio_url(db, segment_id=segment.id, audio_url=audio_url)
            logger.info(f"Segmento {segment.segment_index} salvo. URL: {audio_url}")
