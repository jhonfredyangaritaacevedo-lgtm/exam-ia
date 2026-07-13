import logging
import os
import sys

# El código de src/ usa imports relativos a esa carpeta (from core..., from services...)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from mangum import Mangum
from main import app

# Configure logging level for Lambda
logging.basicConfig(level=logging.INFO)
logging.getLogger().setLevel(logging.INFO)
logger = logging.getLogger(__name__)

_mangum = Mangum(app, lifespan="off")


def handler(event, context):
    # Tareas disparadas por auto-invocación asíncrona
    if isinstance(event, dict) and event.get("task"):
        task = event["task"]

        if task == "generate_exam":
            import uuid
            from schemas.exam import GenerateExamRequest
            from services.async_exam_service import async_exam_service

            logger.info(f"Generación de examen {event['exam_id']} disparada por auto-invocación")
            async_exam_service.run_generation(
                uuid.UUID(event["exam_id"]),
                GenerateExamRequest(**event["exam_request"]),
            )
            return {"statusCode": 200, "body": "exam generation completed"}

        if task == "reindex":
            from routes.admin import run_reindex

            logger.info("Re-indexación RAG disparada por auto-invocación")
            run_reindex()
            return {"statusCode": 200, "body": "reindex completed"}

        if task == "reindex_single":
            import uuid as _uuid
            from routes.admin import run_reindex_single

            logger.info(f"Re-indexación de documento {event['doc_id']} disparada por auto-invocación")
            run_reindex_single(_uuid.UUID(event["doc_id"]))
            return {"statusCode": 200, "body": "reindex_single completed"}

    return _mangum(event, context)
