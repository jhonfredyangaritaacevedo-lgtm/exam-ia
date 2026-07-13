import uuid
from sqlalchemy import Column, String, Text
from sqlalchemy.dialects.postgresql import UUID
from pgvector.sqlalchemy import Vector
from core.database import Base


class EbcChunk(Base):
    __tablename__ = "ebc_chunks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    area = Column(String, nullable=False)
    grado = Column(String, nullable=False)
    competencia = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    embedding = Column(Vector(768), nullable=True)

    def __repr__(self):
        return f"<EbcChunk(id={self.id}, area={self.area}, grado={self.grado})>"
