import asyncio
import json
import threading
import uuid
import logging
import os
import tempfile
from core.database import get_db
from repositories.exam_repository import ExamRepository
from models.exam import Exam, ExamStatus
from services.genai_service import GenAIService
from services.document_extractor import DocumentExtractorService
from services.r2_service import r2_service
from schemas.exam import GenerateExamRequest

logger = logging.getLogger(__name__)

class AsyncExamService:
    def start_exam_generation(self, exam_id: uuid.UUID, exam_request: GenerateExamRequest):
        """Starts generation in background.

        In Lambda the daemon thread dies when the handler returns, so the
        function re-invokes itself asynchronously instead (handled in lambda_handler).
        """
        if os.getenv("AWS_LAMBDA_FUNCTION_NAME"):
            self._invoke_lambda(exam_id, exam_request)
        else:
            thread = threading.Thread(
                target=self._generate_background,
                args=(exam_id, exam_request),
                daemon=True
            )
            thread.start()

    def _invoke_lambda(self, exam_id: uuid.UUID, exam_request: GenerateExamRequest):
        """Re-invokes this same Lambda asynchronously to run the generation"""
        import boto3

        client = boto3.client("lambda")
        client.invoke(
            FunctionName=os.environ["AWS_LAMBDA_FUNCTION_NAME"],
            InvocationType="Event",
            Payload=json.dumps({
                "task": "generate_exam",
                "exam_id": str(exam_id),
                "exam_request": exam_request.model_dump(mode="json"),
            }),
        )

    def run_generation(self, exam_id: uuid.UUID, exam_request: GenerateExamRequest):
        """Runs the generation synchronously (entry point for the Lambda self-invocation)"""
        self._generate_background(exam_id, exam_request)

    def _extract_documents_content(self, files_uuid: str) -> str:
        """Downloads exam files from R2 and extracts their text as Markdown."""
        extractor = DocumentExtractorService()
        parts = []

        files = r2_service.list_files_in_folder(f"files_for_exam/{files_uuid}/")
        for f in files:
            try:
                file_bytes = r2_service.download_file(f["key"])
                ext = os.path.splitext(f["filename"])[1]
                with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as tmp:
                    tmp.write(file_bytes)
                    tmp_path = tmp.name
                try:
                    md_content = extractor.extract_to_markdown(tmp_path)
                finally:
                    os.unlink(tmp_path)

                if md_content:
                    parts.append(f"=== {f['filename']} ===\n{md_content}")
                else:
                    logger.warning(f"No se extrajo contenido de {f['filename']}")
            except Exception as e:
                logger.error(f"Error extrayendo {f['filename']}: {e}")

        return "\n\n".join(parts)

    def _generate_background(self, exam_id: uuid.UUID, exam_request: GenerateExamRequest):
        db = next(get_db())
        try:
            exam_repo = ExamRepository(db)
            genai_service = GenAIService(db)

            # 1. Update status
            exam_repo.update_status(exam_id, ExamStatus.PROCESSING)

            # 2. Extract content if files provided
            document_content = ""
            if exam_request.files_uuid:
                document_content = self._extract_documents_content(str(exam_request.files_uuid))
                logger.info(f"Contenido extraído: {len(document_content)} caracteres de documentos del docente")
            
            # 3. Generate with Gemini
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            exam_result = loop.run_until_complete(
                genai_service.generate_exam(exam_request, document_content)
            )
            
            # 4. Save result
            exam_repo.update_result(exam_id, exam_result)
            exam_repo.update_status(exam_id, ExamStatus.SUCCESSFUL)
            
        except Exception as e:
            logger.error(f"Error in background generation: {str(e)}")
            # mark as failed
            db.rollback()
            db.query(Exam).filter(Exam.id == exam_id).update({"status": ExamStatus.FAILED})
            db.commit()
        finally:
            db.close()

async_exam_service = AsyncExamService()
