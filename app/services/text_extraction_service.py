# app/services/text_extraction_service.py

import logging
import fitz  # PyMuPDF
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Callable

from app.services.pdf_segmenter import PDFSegmenterService
from app.services.text_preprocessor_service import TextPreprocessorService
from app.crud import crud_document, crud_audio_segment
from app.models.document import ProcessingStatus
from app.api.v1.schemas.audio_segment import AudioSegmentCreate
# Supondo que você criou o Enum
from app.api.v1.schemas.document import SegmentationMode 

logger = logging.getLogger(__name__)

class TextExtractionService:
    """
    Serviço responsável pela extração de texto de PDFs.
    As dependências são injetadas para maior flexibilidade e testabilidade.
    """

    def __init__(
        self,
        pdf_segmenter: PDFSegmenterService,
        preprocessor: TextPreprocessorService,
    ):
        # 1. Injeção de Dependência: recebemos as instâncias em vez de criá-las.
        self.pdf_segmenter = pdf_segmenter
        self.preprocessor = preprocessor
        
        # 2. Padrão Strategy: Mapeia o modo de segmentação para a função correspondente.
        self._segmentation_strategies: Dict[SegmentationMode, Callable] = {
            SegmentationMode.PAGE: self._segment_by_page,
            SegmentationMode.CHAPTER: self._segment_by_chapter,
        }

    def _segment_by_page(self, pdf_bytes: bytes) -> List[Dict[str, Any]]:
        """Usa o PyMuPDF para dividir o texto por página."""
        logger.info("A segmentar por páginas...")
        units = []
        try:
            # 3. Gerenciamento de Recursos com 'with'
            with fitz.open(stream=pdf_bytes, filetype="pdf") as pdf_document:
                for page_num, page in enumerate(pdf_document):
                    text = page.get_text("text").strip()
                    if text:
                        units.append({
                            "index": page_num + 1,
                            "title": f"Página {page_num + 1}",
                            "content": text,
                        })
        except Exception as e:
            logger.error(f"Falha ao extrair texto por página: {e}")
            raise
        return units

    def _segment_by_chapter(self, pdf_bytes: bytes) -> List[Dict[str, Any]]:
        """Usa o PDFSegmenterService para dividir o texto em capítulos."""
        logger.info("A segmentar por capítulos...")
        result = self.pdf_segmenter.segment_pdf(pdf_bytes)
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
        segmentation_mode: SegmentationMode, # 4. Usando o Enum
    ):
        """Orquestra o processo de extração e armazenamento de texto."""
        try:
            logger.info(
                f"A iniciar extração de texto para o documento ID: {document_id} com modo '{segmentation_mode.value}'."
            )
            crud_document.update_document_status(db, document_id, ProcessingStatus.PROCESSING)

            # Seleciona a estratégia de segmentação a partir do dicionário
            segment_strategy = self._segmentation_strategies.get(segmentation_mode)
            if not segment_strategy:
                raise ValueError(f"Modo de segmentação desconhecido: {segmentation_mode}")
            
            text_units = segment_strategy(pdf_bytes)

            if not text_units:
                logger.warning(f"Nenhum texto encontrado para o documento ID: {document_id}.")
                crud_document.update_document_status(db, document_id, ProcessingStatus.FAILED)
                return

            segments_to_create = [
                AudioSegmentCreate(
                    segment_index=unit["index"],
                    title=unit["title"],
                    text_content=self.preprocessor.clean_text_for_tts(unit["content"]),
                )
                for unit in text_units
            ]

            crud_audio_segment.bulk_create_audio_segments(
                db, segments_in=segments_to_create, document_id=document_id
            )

            crud_document.update_document_status(db, document_id, ProcessingStatus.TEXT_EXTRACTED)
            logger.info(f"Extração de texto para o documento ID: {document_id} concluída com sucesso.")

        except Exception as e:
            logger.error(f"Erro durante a extração de texto para o documento ID {document_id}: {e}", exc_info=True)
            crud_document.update_document_status(db, document_id, ProcessingStatus.FAILED)