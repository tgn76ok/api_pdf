# app/api/v1/schemas/pdf.py
from pydantic import BaseModel
from typing import List, Optional, Any

class Chapter(BaseModel):
    """Schema para representar um capítulo segmentado."""
    title: str
    content: str
    start_page: int

class TableOfContentsItem(BaseModel):
    """Schema para um item do sumário."""
    level: int
    title: str
    page: int

class SegmentationResponse(BaseModel):
    """Schema para a resposta da API de segmentação."""
    status: str
    message: str
    chapters: List[Chapter]
    table_of_contents: Optional[List[TableOfContentsItem]] = []

