import re
from typing import List, Dict, Any
from statistics import mean

class ChapterValidator:
    """
    Aplica regras semânticas e estruturais de alto nível para validar, 
    fundir e refinar uma lista de capítulos brutos, simulando uma análise de PLN.
    """

    def _is_sub_chapter_title(self, title: str) -> bool:
        """Verifica se um título é um provável subtítulo (ex: algarismo romano)."""
        roman_numeral_pattern = r'^[IVXLCDM]+$'
        return bool(re.fullmatch(roman_numeral_pattern, title.strip()))

    def _content_has_poem_structure(self, content: str) -> bool:
        """
        Heurística de PLN: Verifica se o conteúdo tem uma estrutura de poema.
        Um poema genuíno terá uma média de palavras por linha baixa.
        """
        lines = content.strip().split('\n')
        if not lines or len(lines) < 2:
            return False # Conteúdo com menos de 2 linhas provavelmente não é um poema
        
        # Tratamento de erro para o caso de não haver linhas com conteúdo
        try:
            avg_words_per_line = mean(len(line.split()) for line in lines if line.strip())
        except ZeroDivisionError:
            return False
        
        # Se a média de palavras por linha for inferior a 10, é muito provável que seja um poema.
        return avg_words_per_line < 10

    def validate_and_merge(self, chapters: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Método principal que orquestra a validação, fusão e filtragem de capítulos.
        """
        if not chapters:
            return []

        # 1. Primeira Passagem: Fundir sub-capítulos
        merged_chapters = []
        if chapters:
            previous_chapter = chapters[0]
            for i in range(1, len(chapters)):
                current_chapter = chapters[i]
                # Se o título atual for um subtítulo, funde-o com o capítulo anterior.
                if self._is_sub_chapter_title(current_chapter['title']):
                    previous_chapter['content'] += f"\n\n{current_chapter['title']}\n{current_chapter['content']}"
                else:
                    merged_chapters.append(previous_chapter)
                    previous_chapter = current_chapter
            merged_chapters.append(previous_chapter)

        # 2. Segunda Passagem: Filtrar e Validar os capítulos já fundidos
        final_chapters = []
        for chapter in merged_chapters:
            content = chapter.get("content", "").strip()
            # Validação: O capítulo deve ter conteúdo. Para documentos gerais, a verificação da estrutura do poema é removida.
            # A heurística _content_has_poem_structure pode ser reativada se o foco for apenas poesia.
            if content:
                final_chapters.append(chapter)

        return final_chapters

