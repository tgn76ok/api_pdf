from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.sql import func
from datetime import datetime

class Base(DeclarativeBase):
    """
    Classe base declarativa para os modelos SQLAlchemy.
    
    Todos os outros modelos da aplicação (User, Document, etc.) herdarão
    desta classe. O SQLAlchemy usa esta base para mapear as classes Python
    para tabelas na base de dados e para gerir os metadados.
    """
    pass

