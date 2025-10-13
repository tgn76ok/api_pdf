from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from typing import Generator
import os
from dotenv import load_dotenv

# --- CONFIGURAÇÃO PARA POSTGRESQL COM DOTENV ---
# Carrega as variáveis de ambiente do ficheiro .env
# Certifique-se de que tem a biblioteca instalada: pip install python-dotenv
load_dotenv()

# Carrega as credenciais da base de dados a partir das variáveis de ambiente
DB_USER = os.getenv("POSTGRES_USER", "default_user")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "default_password")
DB_SERVER = os.getenv("POSTGRES_SERVER", "localhost")
DB_PORT = os.getenv("POSTGRES_PORT", "5432")
DB_NAME = os.getenv("POSTGRES_DB", "audiobook_db")

# Constrói a URL de conexão a partir das variáveis carregadas
SQLALCHEMY_DATABASE_URL = (
    f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_SERVER}:{DB_PORT}/{DB_NAME}"
)

# O 'engine' é o ponto de entrada para o banco de dados.
# Nota: Certifique-se de que tem o driver do PostgreSQL instalado:
# pip install psycopg2-binary
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Cada instância de SessionLocal será uma sessão de banco de dados.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db() -> Generator:
    """
    Função de dependência do FastAPI para obter uma sessão de banco de dados por pedido.
    Garante que a sessão seja sempre fechada após o uso.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

