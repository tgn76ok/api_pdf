import fitz
import pandas as pd
import logging
from typing import List, Dict, Any
from app.services.feature_extractor import FeatureExtractor
from app.services.chapter_validator import ChapterValidator

logger = logging.getLogger(__name__)

class PDFSegmenterService:
    def __init__(self):
        self.feature_extractor = FeatureExtractor()
        self.chapter_validator = ChapterValidator()

    def _is_title_candidate(self, row: pd.Series, median_font_size: float) -> bool:
        """
        --- NOVA LÓGICA DE DECISÃO INTELIGENTE ---
        Analisa as características de um bloco de texto para determinar se é um título.
        Combina várias pistas visuais para uma decisão mais robusta.
        """
        # Condição 1: Fonte significativamente maior que o texto normal.
        cond_large_font = row['relative_font_size'] > 1.2 and row['word_count'] < 15

        # Condição 2: Texto em negrito e ligeiramente maior.
        cond_bold_and_larger = row['is_bold'] and row['relative_font_size'] > 1.1

        # Condição 3: Texto em maiúsculas, com poucos caracteres e alinhado ao centro.
        cond_all_caps = (row['is_all_caps'] and 
                         row['word_count'] < 10 and 
                         row['char_count'] > 2 and # Evita capturar apenas "I", "V", etc. isoladamente aqui
                         row['alignment'] == 'center')

        # Condição 4: Espaçamento vertical significativo após o bloco.
        # Um espaço maior que 1.5x o tamanho da fonte do parágrafo é um bom indicador.
        cond_spacing = row['vertical_spacing_after'] > (median_font_size * 1.5)

        # Um bloco é um forte candidato a título se tiver uma formatação de destaque
        # E for seguido por um espaço em branco significativo.
        return (cond_large_font or cond_bold_and_larger or cond_all_caps) and cond_spacing

    def _identify_chapters_from_features(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Identifica e extrai capítulos com base no DataFrame de características.
        """
        if df.empty:
            return []

        chapters = []
        current_content = ""
        current_title = "Início do Documento"
        start_page = 1

        # Calcula o tamanho de fonte mediano para usar como referência
        paragraph_blocks = df[df['word_count'] > 5]
        median_font_size = paragraph_blocks['avg_font_size'].median() if not paragraph_blocks.empty else 10.0
        
        for index, row in df.iterrows():
            if self._is_title_candidate(row, median_font_size):
                # Se encontramos um novo título, guardamos o capítulo anterior
                if current_content.strip():
                    chapters.append({
                        "title": current_title,
                        "content": current_content.strip(),
                        "start_page": start_page
                    })
                
                # Inicia o novo capítulo
                current_title = row['text']
                start_page = row['page_num']
                current_content = ""
            else:
                # Se não for um título, adiciona o texto ao conteúdo atual
                current_content += row['text'] + "\n"

        # Adiciona o último capítulo que estava a ser processado
        if current_content.strip():
            chapters.append({
                "title": current_title,
                "content": current_content.strip(),
                "start_page": start_page
            })

        return chapters

    def segment_pdf(self, pdf_bytes: bytes) -> Dict[str, Any]:
        """
        Orquestra o processo completo de segmentação do PDF.
        """
        try:
            pdf_document = fitz.open(stream=pdf_bytes, filetype="pdf")
        except Exception as e:
            logger.error(f"Erro ao abrir o stream do PDF: {e}")
            raise ValueError("Arquivo PDF inválido ou corrompido.")

        # 1. Extrai um DataFrame limpo e rico em características
        features_df = self.feature_extractor.extract_features_as_dataframe(pdf_document)

        # 2. Identifica os capítulos brutos com base nas características
        raw_chapters = self._identify_chapters_from_features(features_df)

        # 3. Valida e refina os capítulos (ex: funde subtítulos)
        final_chapters = self.chapter_validator.validate_and_merge(raw_chapters)
        
        toc = [] # A extração de TOC pode ser adicionada aqui se necessário

        pdf_document.close()

        if not final_chapters:
             return {
                "status": "success",
                "message": "Nenhum capítulo encontrado. O documento foi processado como um único bloco.",
                "chapters": [{
                    "title": "Documento Completo",
                    "content": " ".join(features_df['text'].tolist()),
                    "start_page": 1
                }],
                "table_of_contents": toc
            }

        return {
            "status": "success",
            "message": f"PDF processado com sucesso. {len(final_chapters)} capítulo(s) encontrado(s).",
            "chapters": final_chapters,
            "table_of_contents": toc
        }

