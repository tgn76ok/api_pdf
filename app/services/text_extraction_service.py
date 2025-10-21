# app/services/text_extraction_service.py

import logging
import fitz  # PyMuPDF
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Callable

from app.services.pdf_segmenter import PDFSegmenterService
from app.services.s3_service import S3Service
from app.services.text_preprocessor_service import TextPreprocessorService
from app.crud import crud_document, crud_audio_segment
from app.models.document import ProcessingStatus
from app.api.v1.schemas.audio_segment import AudioSegmentCreate
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
        # Injeção de Dependência: recebemos as instâncias em vez de criá-las.
        self.pdf_segmenter = pdf_segmenter
        self.preprocessor = preprocessor

        # Padrão Strategy: mapeia modo de segmentação à função correspondente.
        self._segmentation_strategies: Dict[SegmentationMode, Callable] = {
            SegmentationMode.PAGE: self._segment_by_page,
            SegmentationMode.CHAPTER: self._segment_by_chapter,
        }

    def _segment_by_page(self, pdf_bytes: bytes) -> List[Dict[str, Any]]:
        """Usa o PyMuPDF para dividir o texto por página."""
        logger.info("Segmentando por páginas...")
        units: List[Dict[str, Any]] = []
        try:
            doc = fitz.open(stream=pdf_bytes, filetype="pdf")
            with doc as pdf_document:
                for page_num, page in enumerate(pdf_document):
                    raw_text = page.get_text("text")
                    text = raw_text.strip() if raw_text else ""
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
        logger.info("Segmentando por capítulos...")
        result = self.pdf_segmenter.segment_pdf(pdf_bytes)
        chapters = result.get("chapters", [])
        return [
            {
                "index": i + 1,
                "title": chap["title"],
                "content": chap["content"],
            }
            for i, chap in enumerate(chapters)
        ]

    def extract_and_save_text(
        self,
        db: Session,
        *,
        pdf_file_key: str,
        document_id: int,
        segmentation_mode: SegmentationMode,
    ):
        """
        Orquestra o processo de extração e armazenamento de texto.
        Atualiza o status do documento em cada etapa.
        """
        try:
            logger.info(
                f"Iniciando extração de texto para documento ID {document_id} com modo {segmentation_mode}."
            )
            crud_document.update_document_status(db, document_id, ProcessingStatus.PROCESSING)

            # Busca o PDF no S3
            s3 = S3Service()
            pdf_bytes = s3.get_file(filename=pdf_file_key, db=db, document_id=document_id)

            # Seleciona a estratégia de segmentação
            segment_strategy = self._segmentation_strategies.get(segmentation_mode)
            if not segment_strategy:
                raise ValueError(f"Modo de segmentação desconhecido: {segmentation_mode}")

            text_units = segment_strategy(pdf_bytes)

            if not text_units:
                logger.warning(f"Nenhum texto extraído para documento ID {document_id}.")
                crud_document.update_document_status(db, document_id, ProcessingStatus.FAILED)
                return

            # Limpa o texto e prepara AudioSegmentCreate para cada unidade
            segments_to_create: List[AudioSegmentCreate] = []
            for unit in text_units:
                cleaned = self.preprocessor.clean_text_for_tts(unit["content"])
                segments_to_create.append(
                    AudioSegmentCreate(
                        segment_index=unit["index"],
                        title=unit["title"],
                        text_content=cleaned,
                    )
                )
            crud_audio_segment.delete_audio_segments_by_document(db, document_id)
            # Cria registros de segmentos de áudio em batch
            crud_audio_segment.bulk_create_audio_segments(
                db, segments_in=segments_to_create, document_id=document_id
            )
            # crud_document.update_document_countPage(db, document_id, ProcessingStatus.PROCESSING)
            

            # Atualiza status para TEXT_EXTRACTED
            crud_document.update_document_status(db, document_id, ProcessingStatus.TEXT_EXTRACTED)
            logger.info(f"Extração de texto concluída para documento ID {document_id}.")

        except Exception as e:
            logger.error(
                f"Erro na extração de texto para documento ID {document_id}: {e}",
                exc_info=True
            )
            crud_document.update_document_status(db, document_id, ProcessingStatus.FAILED)
