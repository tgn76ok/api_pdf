# app/services/audiobook_generator_service.py
import fitz  # PyMuPDF
import re
import logging
from typing import List, Dict, Any

# Importe os serviços que você já criou
from app.services.pdf_segmenter import PDFSegmenterService
from app.services.elevenlabs_service import ElevenLabsService
from app.services.s3_service import S3Service

logger = logging.getLogger(__name__)

class AudiobookGeneratorService:
    """
    Orquestra o processo completo de conversão de PDF para audiobook,
    integrando segmentação, geração de áudio e upload para S3.
    """
    def __init__(
        self,
        pdf_segmenter: PDFSegmenterService,
        elevenlabs_service: ElevenLabsService,
        s3_service: S3Service,
    ):
        self.pdf_segmenter = pdf_segmenter
        self.elevenlabs_service = elevenlabs_service
        self.s3_service = s3_service

    def _sanitize_filename(self, text: str) -> str:
        """Limpa texto para ser usado em nomes de arquivos ou pastas."""
        text = re.sub(r'[\\/*?:"<>|]', "", text)
        text = text.replace(" ", "_").lower()
        return text[:100]

    def generate(
        self,
        pdf_bytes: bytes,
        book_title: str,
        segmentation_mode: str = "page", # "page" ou "chapter"
    ) -> List[Dict[str, Any]]:
        """
        Executa o fluxo completo de geração do audiobook.
        """
        if segmentation_mode not in ["page", "chapter"]:
            raise ValueError("O modo de segmentação deve ser 'page' ou 'chapter'.")

        logger.info(f"Iniciando geração de audiobook para '{book_title}' com modo '{segmentation_mode}'.")
        
        if segmentation_mode == "chapter":
            units = self._segment_by_chapter(pdf_bytes)
        else: # Padrão é 'page'
            units = self._segment_by_page(pdf_bytes)

        if not units:
            logger.warning("Nenhuma unidade (página/capítulo) com conteúdo foi encontrada.")
            return []

        return self._process_units(units, book_title)

    def _segment_by_chapter(self, pdf_bytes: bytes) -> List[Dict[str, Any]]:
        """Usa o PDFSegmenterService para dividir o texto em capítulos."""
        logger.info("Segmentando por capítulos...")
        result = self.pdf_segmenter.segment_pdf(pdf_bytes)
        # Adaptar a estrutura para o processador genérico
        return [{"id": i + 1, "title": chap["title"], "text": chap["content"]} for i, chap in enumerate(result.get("chapters", []))]

    def _segment_by_page(self, pdf_bytes: bytes) -> List[Dict[str, Any]]:
        """Usa o PyMuPDF para dividir o texto por página."""
        logger.info("Segmentando por páginas...")
        units = []
        try:
            pdf_document = fitz.open(stream=pdf_bytes, filetype="pdf")
            for page_num, page in enumerate(pdf_document):
                text = page.get_text("text").strip()
                if text:
                    units.append({"id": page_num + 1, "title": f"Página {page_num + 1}", "text": text})
            pdf_document.close()
        except Exception as e:
            logger.error(f"Falha ao extrair texto por página: {e}")
            raise
        return units

    def _process_units(self, units: List[Dict[str, Any]], book_title: str) -> List[Dict[str, Any]]:
        """Itera sobre as unidades (páginas/capítulos), gera áudio e faz upload."""
        processed_results = []
        safe_book_title = self._sanitize_filename(book_title)

        for unit in units:
            unit_id = unit["id"]
            unit_title = unit["title"]
            unit_text = unit["text"]
            
            logger.info(f"Processando Unidade {unit_id}: '{unit_title}'...")

            try:
                # O ElevenLabsService já usa o TextPreprocessor internamente
                audio_bytes = self.elevenlabs_service.generate_audio(unit_text)

                safe_unit_title = self._sanitize_filename(unit_title)
                filename = f"{safe_book_title}/{unit_id:04d}_{safe_unit_title}.mp3"

                audio_url = self.s3_service.upload_audio(audio_bytes, filename)
                
                processed_results.append({
                    "unit_id": unit_id,
                    "title": unit_title,
                    "audio_url": audio_url,
                    "status": "success",
                })
                logger.info(f"Unidade {unit_id} processada com sucesso. URL: {audio_url}")

            except Exception as e:
                logger.error(f"Falha ao processar unidade {unit_id} ('{unit_title}'): {e}")
                processed_results.append({
                    "unit_id": unit_id,
                    "title": unit_title,
                    "status": "failed",
                    "error": str(e),
                })
        
        return processed_results