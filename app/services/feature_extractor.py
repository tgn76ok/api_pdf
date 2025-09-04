import fitz  # PyMuPDF
import pandas as pd
import re
from typing import List, Dict, Any
from statistics import mean, StatisticsError

class FeatureExtractor:
    """
    Implementa a extração e validação granular de características de um documento PDF,
    conforme detalhado na Secção 1 do relatório, com uma camada adicional de limpeza.
    """

    def _get_page_blocks(self, page: fitz.Page) -> List[Dict[str, Any]]:
        """Extrai todos os blocos de texto de uma página com as suas propriedades."""
        return page.get_text("dict", flags=fitz.TEXTFLAGS_SEARCH).get("blocks", [])

    def _decode_flags(self, flags: int) -> Dict[str, bool]:
        """Descodifica os flags de estilo de um span em características booleanas."""
        return {
            "is_bold": bool(flags & 2**4),
            "is_italic": bool(flags & 2**1),
            "is_serif": bool(flags & 2**0),
            "is_monospace": bool(flags & 2**3),
        }

    def _is_potential_junk(self, block_features: Dict[str, Any]) -> bool:
        """
        Valida se um bloco de texto é provavelmente ruído (cabeçalho, rodapé, número de página).
        Esta é a camada de validação que remove textos inúteis.
        """
        # Regra 1: Posição na página (muito no topo ou muito no fundo)
        if block_features["normalized_y0"] < 0.08 or block_features["normalized_y0"] > 0.92:
            # Regra 2: Conteúdo curto e/ou numérico
            if block_features["word_count"] < 5 or block_features["text"].isdigit():
                return True
        
        # Regra 3: Linhas que contêm "página" ou "page" (comum em rodapés)
        text_lower = block_features["text"].lower()
        if "página" in text_lower or "page" in text_lower:
            return True
            
        return False

    def _aggregate_block_features(self, block: Dict[str, Any], page_height: float, page_width: float) -> Dict[str, Any]:
        """
        Agrega as características dos spans a nível de bloco.
        """
        if block.get("type") != 0 or not block.get("lines"):
            return None

        all_spans = [span for line in block["lines"] for span in line["spans"]]
        if not all_spans:
            return None

        block_text = " ".join(s["text"].strip() for s in all_spans).strip()
        if not block_text:
            return None
        
        # Limpa o texto de referências numéricas comuns em títulos
        cleaned_text = re.sub(r'\s*\[\d+\]$', '', block_text).strip()

        word_count = len(cleaned_text.split())
        
        # A chave correta da biblioteca é 'size', não 'font_size'.
        try:
            font_sizes = [s["size"] for s in all_spans]
            avg_font_size = mean(font_sizes) if font_sizes else 0
            max_font_size = max(font_sizes) if font_sizes else 0
        except (StatisticsError, KeyError):
            avg_font_size = 0
            max_font_size = 0

        is_bold = any(self._decode_flags(s["flags"])["is_bold"] for s in all_spans)
        
        bbox = block["bbox"]
        normalized_y0 = bbox[1] / page_height
        
        block_center = (bbox[0] + bbox[2]) / 2
        page_center = page_width / 2
        alignment_threshold = 0.1 * page_width
        if abs(block_center - page_center) < alignment_threshold:
            alignment = "center"
        elif block_center < page_center:
            alignment = "left"
        else:
            alignment = "right"

        return {
            "text": cleaned_text,
            "word_count": word_count,
            "char_count": len(cleaned_text),
            "avg_font_size": avg_font_size,
            "max_font_size": max_font_size,
            "is_bold": is_bold,
            "is_all_caps": cleaned_text.isupper() and word_count > 0,
            "bbox": bbox,
            "normalized_y0": normalized_y0,
            "alignment": alignment,
        }

    def extract_features_as_dataframe(self, pdf_document: fitz.Document) -> pd.DataFrame:
        """
        Processa o documento, extrai características, valida-as e retorna um DataFrame limpo.
        """
        all_blocks_features = []
        for page_num, page in enumerate(pdf_document):
            page_blocks = self._get_page_blocks(page)
            page_height = page.rect.height
            page_width = page.rect.width
            
            for block in page_blocks:
                features = self._aggregate_block_features(block, page_height, page_width)
                if features:
                    # Aplica a validação para filtrar ruído
                    if not self._is_potential_junk(features):
                        features["page_num"] = page_num + 1
                        all_blocks_features.append(features)

        if not all_blocks_features:
            return pd.DataFrame()

        df = pd.DataFrame(all_blocks_features)

        # Engenharia de Características Contextuais
        df['vertical_spacing_after'] = df['bbox'].apply(lambda b: b[1]).shift(-1) - df['bbox'].apply(lambda b: b[3])
        df['vertical_spacing_after'] = df['vertical_spacing_after'].fillna(0)
        
        # Tamanho de fonte relativo
        paragraph_blocks = df[df['word_count'] > 5]
        if not paragraph_blocks.empty:
            median_font_size = paragraph_blocks['avg_font_size'].median()
        else:
            median_font_size = df['avg_font_size'].median() if not df.empty else 10

        if pd.notna(median_font_size) and median_font_size > 0:
            df['relative_font_size'] = df['max_font_size'] / median_font_size
        else:
            df['relative_font_size'] = 1.0
            
        return df

