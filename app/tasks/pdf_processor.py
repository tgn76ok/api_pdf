# app/tasks/pdf_processor.py

from sqlalchemy.orm import Session
from app.services.pdf_segmenter import PDFSegmenterService
from app.services.text_preprocessor_service import TextPreprocessorService
from app.services.text_extraction_service import TextExtractionService
from app.api.v1.schemas.document import SegmentationMode
from app.db.session import SessionLocal # Importante para criar uma nova sessão de DB

def process_pdf_task(doc_id: int, pdf_bytes: bytes, mode: SegmentationMode):
    """
    Esta função é executada em segundo plano.
    Ela cria sua própria sessão de banco de dados para garantir que seja independente.
    """
    print(f"Iniciando tarefa em segundo plano para o documento ID: {doc_id}")
    
    # Cada tarefa em segundo plano deve gerir sua própria sessão de DB
    db: Session = SessionLocal()
    
    try:
        # Crie as dependências aqui
        pdf_segmenter = PDFSegmenterService()
        preprocessor = TextPreprocessorService()
        
        # Injete as dependências ao criar o serviço
        text_extractor = TextExtractionService(
            pdf_segmenter=pdf_segmenter, 
            preprocessor=preprocessor
        )
        
        # Chame o método principal
        text_extractor.extract_and_save_text(
            db=db,
            pdf_bytes=pdf_bytes,
            document_id=doc_id,
            segmentation_mode=mode
        )
        print(f"Tarefa para o documento ID: {doc_id} concluída com sucesso.")
    except Exception as e:
        print(f"Erro na tarefa para o documento ID: {doc_id}: {e}")
        # Aqui você pode adicionar lógica para atualizar o status do documento para FALHA
    finally:
        # Garanta que a sessão do banco de dados seja sempre fechada
        db.close()