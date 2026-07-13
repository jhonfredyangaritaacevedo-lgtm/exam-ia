from sqlalchemy.orm import Session
from models.rag_document import RagDocument
import uuid
from typing import List

class RagDocumentRepository:
    def __init__(self, db: Session):
        self.db = db

    def add_document(self, user_id: uuid.UUID, filename: str, s3_key: str) -> RagDocument:
        doc = RagDocument(
            id=uuid.uuid4(),
            uploaded_by=user_id,
            filename=filename,
            s3_key=s3_key,
            status="processed"
        )
        self.db.add(doc)
        self.db.commit()
        return doc

    def list_documents(self) -> List[RagDocument]:
        return self.db.query(RagDocument).all()
