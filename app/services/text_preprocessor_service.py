import re
import unicodedata
from typing import List
import spacy

# Carrega modelo de NLP para segmentação de sentenças (opcional)
nlp = spacy.load('pt_core_news_sm')


class TextPreprocessorService:
    """
    Serviço para limpar e pré-processar o texto antes de o enviar para um motor de TTS.
    O objetivo é remover artefatos de formatação de PDF e normalizar o texto
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
        text = self._remove_headers_footers(text)
        text = self._remove_references_and_footnotes(text)
        text = self._dehyphenate_and_join(text)
        text = self._remove_urls_emails(text)
        # text = self._normalize_unicode(text)
        text = self._normalize_whitespace_and_punctuation(text)
        # Opcional: reconstrução de sentenças para coerência
        text = self._reconstruct_sentences(text)
        return text.strip()

    def _remove_headers_footers(self, text: str) -> str:
        """Remove cabeçalhos, rodapés e números de página."""
        # Remove linhas compostas apenas por números (páginas)
        text = re.sub(r'(?m)^\s*\d+\s*$', '', text)
        # Remove marcas como "Página 10", "page 10" (case-insensitive)
        text = re.sub(r'(?i)(^|\s)(página|page)\s+\d+(\s|$)', ' ', text)
        # Remove textos fixos de rodapé/head
        patterns = [
            r'(?i)copyright.*',
            r'(?i)versão\s*\d+(\.\d+)?',
            r'(?i)todos os direitos reservados'
        ]
        for pat in patterns:
            text = re.sub(pat, '', text)
        return text

    def _remove_references_and_footnotes(self, text: str) -> str:
        """Remove referências numéricas e marcadores de notas de rodapé."""
        # Remove referências entre colchetes [1], [23]
        text = re.sub(r'\[\d+\]', '', text)
        # Remove marcadores numerados no início de parágrafo "1. Texto"
        text = re.sub(r'(?m)^\s*\d+\.\s+', '', text)
        return text

    def _dehyphenate_and_join(self, text: str) -> str:
        """
        Junta palavras hifenizadas no fim da linha e normaliza quebras de linha.
        """
        # Junta palavras hifenizadas no fim da linha
        text = re.sub(r'(?<!\w-)(\w+)-\s*\n\s*(\w+)', r'\1\2', text)
        # Une quebras de linha que não indicam parágrafo
        text = re.sub(r'(?<!\n)\n(?!\n)', ' ', text)
        # Mantém duplas quebras para delimitar parágrafo
        text = re.sub(r'\n{2,}', '\n\n', text)
        return text

    def _remove_urls_emails(self, text: str) -> str:
        """Remove URLs e endereços de e-mail."""
        # URLs http(s):// e www.
        text = re.sub(r'https?://\S+|www\.\S+', '', text)
        # Endereços de e-mail
        text = re.sub(r'\S+@\S+', '', text)
        return text

    def _normalize_unicode(self, text: str) -> str:
        """Normaliza caracteres Unicode e remove não-ASCII."""
        text = unicodedata.normalize('NFKC', text)
        return re.sub(r'[^\x00-\x7F]+', ' ', text)

    def _normalize_whitespace_and_punctuation(self, text: str) -> str:
        """
        Normaliza espaços e pontuação para fluidez de leitura.
        Remove pontuação duplicada e garante espaço após ponto final.
        """
        # Pontuação duplicada como ",." ou ".."
        text = re.sub(r'([,\.])\s*[,\.]+', r'\1', text)
        # Espaço faltante após ponto final
        text = re.sub(r'(?<=[\.])(?=[^\s])', ' ', text)
        # Reduz múltiplos espaços a um único
        return re.sub(r'\s+', ' ', text).strip()

    def _reconstruct_sentences(self, text: str) -> str:
        """
        Reconstrói sentenças usando spaCy para coerência textual.
        (Etapa opcional; habilitar se desejado.)
        """
        doc = nlp(text)
        return ' '.join(sent.text.strip() for sent in doc.sents)
