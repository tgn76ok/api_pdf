import re
from typing import List

class TextPreprocessorService:
    """
    Serviço para limpar e pré-processar o texto antes de o enviar para um motor de TTS.
    O objetivo é remover artefactos de formatação de PDF e normalizar o texto
    para uma narração mais natural.
    """

    def clean_text_for_tts(self, text: str) -> str:
        """
        Orquestra a limpeza completa do texto.

        Args:
            text: O texto bruto extraído de um capítulo.

        Returns:
            O texto limpo e pronto para ser enviado para a ElevenLabs.
        """
        # A ordem das operações é importante.
        processed_text = self._remove_reference_numbers(text)
        processed_text = self._dehyphenate(processed_text)
        processed_text = self._normalize_whitespace_for_speech(processed_text)
        return processed_text.strip()

    def _remove_reference_numbers(self, text: str) -> str:
        """Remove referências numéricas como [1], [25], etc."""
        # Remove colchetes e os números dentro deles.
        return re.sub(r'\[\d+\]', '', text)

    def _dehyphenate(self, text: str) -> str:
        """
        Encontra e junta palavras que foram hifenizadas no final das linhas.
        Exemplo: "pala-\nvra" -> "palavra"
        """
        # Encontra uma palavra (letras), seguida por um hífen, uma quebra de linha opcional,
        # e depois continua com mais letras na linha seguinte.
        return re.sub(r'(\w+)-\s*\n\s*(\w+)', r'\1\2', text)

    def _normalize_whitespace_for_speech(self, text: str) -> str:
        """
        Converte quebras de linha e espaços em pontuação para guiar a narração do TTS.
        Isto é mais eficaz do que simplesmente remover as quebras de linha.
        """
        # Substitui duas ou mais quebras de linha (parágrafos) por um ponto final e um espaço,
        # para criar uma pausa mais longa.
        processed_text = re.sub(r'\n{2,}', '. ', text)
        
        # Substitui quebras de linha únicas (versos de poema) por uma vírgula e um espaço,
        # para criar uma pausa curta e natural.
        processed_text = re.sub(r'\n', ', ', processed_text)
        
        # Remove múltiplos espaços que possam ter sido criados
        processed_text = re.sub(r'\s+', ' ', processed_text)
        
        # Garante que a pontuação não fique duplicada (ex: ", ." ou "..")
        processed_text = re.sub(r'[,\.]\s*[,.]', '.', processed_text)

        return processed_text
