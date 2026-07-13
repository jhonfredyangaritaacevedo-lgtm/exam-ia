from sqlalchemy.orm import Session
from models.exam import Exam, ExamStatus
import uuid
from typing import List, Optional

class ExamRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, user_id: uuid.UUID, title: str, area: str, grado: str, prompt: str, num_questions: int, question_types: dict, files_uuid: Optional[uuid.UUID] = None) -> Exam:
        db_exam = Exam(
            id=uuid.uuid4(),
            user_id=user_id,
            title=title,
            area=area,
            grado=grado,
            prompt=prompt,
            num_questions=num_questions,
            question_types=question_types,
            files_uuid=files_uuid,
            status=ExamStatus.PENDING,
            deleted=False
        )
        self.db.add(db_exam)
        self.db.commit()
        self.db.refresh(db_exam)
        return db_exam

    def get_by_id(self, exam_id: uuid.UUID) -> Optional[Exam]:
        return self.db.query(Exam).filter(Exam.id == exam_id).first()

    def list_by_user(self, user_id: uuid.UUID) -> List[Exam]:
        return self.db.query(Exam).filter(Exam.user_id == user_id, Exam.deleted == False).order_by(Exam.created_at.desc()).all()

    def soft_delete(self, exam_id: uuid.UUID):
        self.db.query(Exam).filter(Exam.id == exam_id).update({"deleted": True})
        self.db.commit()

    def update_status(self, exam_id: uuid.UUID, status: ExamStatus):
        self.db.query(Exam).filter(Exam.id == exam_id).update({"status": status})
        self.db.commit()

    def update_result(self, exam_id: uuid.UUID, result: dict, tokens_in: int = None, tokens_out: int = None, duration: int = None, model: str = None):
        self.db.query(Exam).filter(Exam.id == exam_id).update({
            "result": result,
            "tokens_in": tokens_in,
            "tokens_out": tokens_out,
            "duration_seconds": duration,
            "model_used": model
        })
        self.db.commit()
