import uuid
import enum
from sqlalchemy import Column, String, Integer, Boolean, DateTime, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from core.database import Base


class ExamStatus(str, enum.Enum):
    PENDING = 'pending'
    PROCESSING = 'processing'
    SUCCESSFUL = 'successful'
    FAILED = 'failed'


class Exam(Base):
    __tablename__ = "exams"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=False)
    area = Column(String, nullable=False)
    grado = Column(String, nullable=False)
    prompt = Column(String, nullable=False)
    num_questions = Column(Integer, nullable=False)
    question_types = Column(JSONB, nullable=False)
    files_uuid = Column(String, nullable=True)
    result = Column(JSONB, nullable=True)
    status = Column(
        Enum('pending', 'processing', 'successful', 'failed', name='exam_status'),
        nullable=False,
        default='pending',
    )
    tokens_in = Column(Integer, nullable=True)
    tokens_out = Column(Integer, nullable=True)
    duration_seconds = Column(Integer, nullable=True)
    model_used = Column(String, nullable=True)
    deleted = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<Exam(id={self.id}, title={self.title}, status={self.status})>"
