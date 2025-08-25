from typing import List

class Settings:
    """
    Classe para centralizar as configurações da aplicação.
    """
    # Padrões regex para identificar títulos de capítulos
    CHAPTER_PATTERNS: List[str] = [
        r'^(Capítulo|Chapter)\s+(\d+|[IVXLCDM]+)[\s\.:]*(.*)$',
        r'^(\d+)[\.\s]+(.+)$',
        r'^([IVXLCDM]+)[\.\s]+(.+)$',
        r'^(Seção|Section)\s+(\d+|[IVXLCDM]+)[\s\.:]*(.*)$',
        r'^(Parte|Part)\s+(\d+|[IVXLCDM]+)[\s\.:]*(.*)$',
        r'^(Introdução|Introduction)$',
        r'^(Conclusão|Conclusion)$',
        r'^(Bibliografia|References|Referências)$',
        r'^(Anexo|Appendix)\s*([A-Z]|\d+)?[\s\.:]*(.*)$',
        r'^([A-ZÁÉÍÓÚÇÃÕ\s]{3,})(!|\?|\.{3}|\[\d+\])?$',
        r'^([A-ZÁÉÍÓÚÇÃÕ\s.,!?-—\'’()]{3,})(?:\s*\[\d+\])?$'
        r'^(M{0,4}(CM|CD|D?C{0,3})(XC|XL|L?X{0,3})(IX|IV|V?I{0,3}))$',

        r'^(\d+|[IVXLCDM]+)[\.\s]+(.+)$',

    ]
    IGNORE_TITLES: List[str] = [
        "ÍNDICE",
        "DO AUTOR",
        "AO LEITOR"
    ]
    # Padrões para identificar cabeçalhos/rodapés e números de página
    HEADER_FOOTER_PATTERNS: List[str] = [
        r'(?i)(página|page)\s+\d+',
        r'^\s*\d+\s*$',
        r'(?i)(manual de teste|versão \d+\.\d+)',
        r'(?i)(copyright|todos os direitos reservados)',
        r'\s{2,}\d+\s{2,}$',
        r'\b\d+\s*\|\s*\w+\b'
    ]

# Instância única das configurações para ser importada em outros módulos
settings = Settings()
