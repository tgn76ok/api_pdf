import logging
import fitz  # PyMuPDF
from sqlalchemy.orm import Session
from typing import List, Dict, Any

from app.services.pdf_segmenter import PDFSegmenterService
from app.services.text_preprocessor_service import TextPreprocessorService
from app.crud import crud_document, crud_audio_segment
from app.models.document import ProcessingStatus
from app.api.v1.schemas.audio_segment import AudioSegmentCreate

logger = logging.getLogger(__name__)

class TextExtractionService:
    """
    Serviço responsável pela primeira fase do processo: extrair, limpar,
    e guardar o texto de um PDF na base de dados.
    """

    def __init__(self):
        self.pdf_segmenter = PDFSegmenterService()
        self.preprocessor = TextPreprocessorService()

    def _segment_by_page(self, pdf_bytes: bytes) -> List[Dict[str, Any]]:
        """Usa o PyMuPDF para dividir o texto por página."""
        logger.info("A segmentar por páginas...")
        units = []
        try:
            pdf_document = fitz.open(stream=pdf_bytes, filetype="pdf")
            for page_num, page in enumerate(pdf_document):
                text = page.get_text("text").strip()
                if text:
                    units.append(
                        {
                            "index": page_num + 1,
                            "title": f"Página {page_num + 1}",
                            "content": text,
                        }
                    )
            pdf_document.close()
        except Exception as e:
            logger.error(f"Falha ao extrair texto por página: {e}")
            raise
        return units

    def _segment_by_chapter(self, pdf_bytes: bytes) -> List[Dict[str, Any]]:
        """Usa o PDFSegmenterService para dividir o texto em capítulos."""
        logger.info("A segmentar por capítulos...")
        result = self.pdf_segmenter.segment_pdf(pdf_bytes)
        # Adaptar a estrutura para o processador genérico
        return [
            {
                "index": i + 1,
                "title": chap["title"],
                "content": chap["content"],
            }
            for i, chap in enumerate(result.get("chapters", []))
        ]

    def extract_and_save_text(
        self,
        db: Session,
        *,
        pdf_bytes: bytes,
        document_id: int,
        segmentation_mode: str,
    ):
        """
        Orquestra o processo de extração e armazenamento de texto.
        Esta função é projetada para ser executada em segundo plano.
        """
        try:
            logger.info(
                f"A iniciar extração de texto para o documento ID: {document_id} com modo '{segmentation_mode}'."
            )
            crud_document.update_document_status(
                db, document_id, ProcessingStatus.PROCESSING
            )

            if segmentation_mode == "chapter":
                text_units = self._segment_by_chapter(pdf_bytes)
            else:  # Padrão é 'page'
                text_units = self._segment_by_page(pdf_bytes)

            if not text_units:
                logger.warning(
                    f"Nenhum texto encontrado para o documento ID: {document_id}."
                )
                crud_document.update_document_status(
                    db, document_id, ProcessingStatus.FAILED
                )
                return

            segments_to_create = []
            for unit in text_units:
                # Pré-processa o texto antes de o guardar
                cleaned_text = self.preprocessor.clean_text_for_tts(unit["content"])
                
                segment_data = AudioSegmentCreate(
                    segment_index=unit["index"],
                    title=unit["title"],
                    text_content=cleaned_text,
                )
                segments_to_create.append(segment_data)

            # Guarda todos os segmentos na base de dados de uma só vez
            crud_audio_segment.bulk_create_audio_segments(
                db, segments_in=segments_to_create, document_id=document_id
            )

            # Atualiza o estado do documento para indicar que a extração terminou
            crud_document.update_document_status(
                db, document_id, ProcessingStatus.TEXT_EXTRACTED
            )
            logger.info(
                f"Extração de texto para o documento ID: {document_id} concluída com sucesso."
            )

        except Exception as e:
            logger.error(
                f"Erro durante a extração de texto para o documento ID {document_id}: {e}",
                exc_info=True,
            )
            crud_document.update_document_status(
                db, document_id, ProcessingStatus.FAILED
            )

