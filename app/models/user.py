
import uuid
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID 
from typing import List
from .base import Base

class User(Base):
    __tablename__ = "users"

    # --- ID como UUID ---
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),  # Tipo da coluna no DB
        primary_key=True,
        default=uuid.uuid4  # Gera um novo UUID para cada novo usuário
    )
    # ---------------------
    documents: Mapped[List["books"]] = relationship(back_populates="owner")