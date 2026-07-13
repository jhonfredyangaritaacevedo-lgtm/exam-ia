from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from core.database import Base


class ReindexStatus(Base):
    __tablename__ = "reindex_status"

    # Fila singleton (id siempre = 1)
    id = Column(Integer, primary_key=True, default=1)
    running = Column(Boolean, default=False, nullable=False)
    progress = Column(String, default="Sin ejecutar", nullable=False)
    error = Column(String, nullable=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
