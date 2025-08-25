# app/services/pdf_segmenter.py
import fitz
import re
import logging
from typing import List, Dict, Any
from app.core.config import settings

logger = logging.getLogger(__name__)

class PDFSegmenterService:
    def __init__(self):
        self.chapter_patterns = settings.CHAPTER_PATTERNS
        self.header_footer_patterns = settings.HEADER_FOOTER_PATTERNS
        self.ignore_titles = settings.IGNORE_TITLES

    def _clean_text(self, text: str) -> str:
        """Remove cabeçalhos/rodapés e números de página do texto."""
        cleaned_lines = []
        for line in text.split('\n'):
            is_header_footer = any(re.search(p, line.strip(), re.IGNORECASE) for p in self.header_footer_patterns)
            if not is_header_footer:
                cleaned_lines.append(line)
        return '\n'.join(cleaned_lines)

    def _extract_raw_pages(self, pdf_document: fitz.Document) -> List[Dict[str, Any]]:
        """Extrai o texto limpo de cada página."""
        pages_content = []
        for page_num, page in enumerate(pdf_document):
            raw_text = page.get_text()
            cleaned_text = self._clean_text(raw_text)
            pages_content.append({"page_num": page_num + 1, "text": cleaned_text})
        return pages_content
    
    def _clean_chapter_content(self, content: str) -> str:
        """
        --- NOVA FUNÇÃO ---
        Remove metadados e linhas de citação do início do conteúdo de um capítulo.
        """
        lines = content.strip().split('\n')
        cleaned_lines = []
        content_started = False
        
        # Padrões para identificar metadados/citações iniciais
        meta_patterns = [
            r'^\(.*\)$', # Linhas entre parênteses (ex: (Imitação de...))
            r'^\d{1,2}\s\w{3}\.\s\d{4}$', # Datas (ex: 29 jun. 1855)
            r'^[A-ZÁÉÍÓÚÇÃÕ\s.,]+$', # Linhas só com maiúsculas (ex: A UMA ITALIANA)
            r'^RJ,.*$', # Linhas que começam com RJ,
            r'^\[.*\]$', # Linhas entre colchetes
        ]

        for line in lines:
            stripped_line = line.strip()
            if not content_started:
                # Se a linha parece ser metadado, ignora
                is_meta = any(re.match(p, stripped_line) for p in meta_patterns)
                # Também ignora citações curtas ou dedicatórias
                is_short_line = len(stripped_line.split()) < 10

                if is_meta or (is_short_line and not stripped_line.endswith('.')):
                    continue
                else:
                    content_started = True
            
            if content_started:
                cleaned_lines.append(line)
                
        return '\n'.join(cleaned_lines).strip()

    def _identify_chapters_by_pattern(self, pages_content: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        --- LÓGICA REFINADA ---
        Identifica capítulos com lógica aprimorada para lidar com subtítulos e metadados.
        """
        chapters = []
        current_chapter = None

        for page_data in pages_content:
            lines = page_data["text"].split('\n')
            for line in lines:
                clean_line = line.strip()

                if not clean_line:
                    continue

                # Verifica se a linha limpa corresponde a um padrão de título
                is_chapter_title = any(re.fullmatch(p, clean_line) for p in self.chapter_patterns)
                
                # Verifica se o título deve ser ignorado
                is_ignored = any(ignore_word in clean_line.upper() for ignore_word in self.ignore_titles)

                if is_chapter_title and not is_ignored:
                    # Se já existe um capítulo, guarda-o antes de começar um novo
                    if current_chapter:
                        if current_chapter["content"].strip():
                            chapters.append(current_chapter)
                    
                    # Inicia um novo capítulo
                    current_chapter = {
                        "title": clean_line,
                        "content": "",
                        "start_page": page_data["page_num"]
                    }
                
                # Se a linha não é um título, adiciona ao conteúdo do capítulo atual
                elif current_chapter:
                    current_chapter["content"] += line + "\n"
    
        # Adiciona o último capítulo se existir
        if current_chapter and current_chapter["content"].strip():
            chapters.append(current_chapter)
        
        # --- NOVO PASSO: Limpeza do conteúdo de cada capítulo ---
        for chapter in chapters:
            chapter["content"] = self._clean_chapter_content(chapter["content"])

        return [ch for ch in chapters if ch["content"]] # Retorna apenas capítulos com conteúdo

    def _extract_table_of_contents(self, pdf_document: fitz.Document) -> List[Dict[str, Any]]:
        """Extrai o sumário (TOC) do PDF, se disponível."""
        try:
            toc = pdf_document.get_toc()
            return [{"level": item[0], "title": item[1], "page": item[2]} for item in toc] if toc else []
        except Exception:
            logger.warning("Não foi possível extrair o sumário (TOC) do PDF.")
            return []

    def _segment_by_toc(self, pdf_document: fitz.Document, toc: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Segmenta o PDF com base no sumário (TOC)."""
        chapters = []
        for i, item in enumerate(toc):
            start_page = item["page"] - 1
            end_page = toc[i + 1]["page"] - 2 if i + 1 < len(toc) else len(pdf_document) - 1
            content = ""
            for page_num in range(start_page, end_page + 1):
                if 0 <= page_num < len(pdf_document):
                    content += self._clean_text(pdf_document[page_num].get_text()) + "\n"
            chapters.append({"title": item["title"], "content": content.strip(), "start_page": start_page + 1})
        return chapters

    def segment_pdf(self, pdf_bytes: bytes) -> Dict[str, Any]:
        """Orquestra o processo de segmentação do PDF."""
        try:
            pdf_document = fitz.open(stream=pdf_bytes, filetype="pdf")
        except Exception as e:
            logger.error(f"Erro ao abrir o stream do PDF: {e}")
            raise ValueError("Arquivo PDF inválido ou corrompido.")

        toc = self._extract_table_of_contents(pdf_document)
        chapters = []
        
        # Para este tipo de documento, a análise de texto é mais confiável que o TOC
        logger.info("Usando a correspondência de padrões de texto para maior precisão.")
        pages_content = self._extract_raw_pages(pdf_document)
        chapters = self._identify_chapters_by_pattern(pages_content)
            
        if not chapters:
            # Fallback para o TOC se a análise de texto falhar
            if len(toc) > 5:
                logger.info(f"Análise de texto falhou. Usando o sumário (TOC) com {len(toc)} itens.")
                chapters = self._segment_by_toc(pdf_document, toc)
            else:
                logger.info("Nenhum capítulo encontrado. Tratando o documento como um único capítulo.")
                full_text = ""
                for page in pdf_document:
                    full_text += page.get_text()
                chapters = [{"title": "Documento Completo", "content": full_text.strip(), "start_page": 1}]
        
        pdf_document.close()

        return {
            "status": "success",
            "message": f"PDF processado com sucesso. {len(chapters)} capítulo(s) encontrado(s).",
            "chapters": chapters,
            "table_of_contents": toc
        }
