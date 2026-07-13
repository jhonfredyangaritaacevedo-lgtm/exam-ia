from google import genai
from google.genai import types
from typing import Optional, Dict, Any, List
import json
import logging
from core.config import settings
from schemas.exam import GenerateExamRequest, QuestionType
from .document_extractor import DocumentExtractorService
from .rag_service import RagService
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

class GenAIService:
    def __init__(self, db: Session):
        self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
        self.model = settings.LLM_MODEL
        self.extractor = DocumentExtractorService()
        self.rag_service = RagService(db)

    def _create_exam_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "title": {"type": "string"},
                "instructions": {"type": "string"},
                "questions": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "type": {"type": "string", "enum": ["multiple_choice", "true_false", "short_answer", "essay"]},
                            "stem": {"type": "string"},
                            "options": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "text": {"type": "string"},
                                        "correct": {"type": "boolean"}
                                    },
                                    "required": ["text", "correct"]
                                }
                            },
                            "expected_answer": {"type": "string"},
                            "justification": {"type": "string"},
                            "difficulty": {"type": "string", "enum": ["easy", "medium", "hard"]}
                        },
                        "required": ["type", "stem", "difficulty"]
                    }
                }
            },
            "required": ["title", "instructions", "questions"]
        }

    async def generate_exam(self, exam_request: GenerateExamRequest, document_content: str = "") -> Dict[str, Any]:
        # 1. Get RAG Context (EBC MEN)
        topic = exam_request.prompt or exam_request.title or "General"
        rag_context = self.rag_service.build_rag_context(
            area=exam_request.area,
            grado=exam_request.grado,
            topic=topic
        )

        # 2. Build Prompt
        dist = ", ".join(f"{qt.quantity} de tipo '{qt.type.value}'" for qt in exam_request.question_types)
        system_instruction = f"""Eres un experto creador de exámenes para educación media en Colombia.
Tu tarea es generar un examen riguroso y alineado con los estándares oficiales.

REQUISITOS DEL EXAMEN:
- Total de preguntas: {exam_request.num_questions}
- Distribución: {dist}

REGLAS PARA LAS OPCIONES:
- En preguntas de tipo 'multiple_choice': genera exactamente 4 opciones en el campo "options". Marca con "correct: true" SOLO la opción correcta.
- En preguntas de tipo 'true_false': genera exactamente 2 opciones: "Verdadero" y "Falso". Marca la correcta.
- En preguntas de tipo 'short_answer' o 'essay': NO incluyas "options". Usa "expected_answer" con la respuesta modelo.
- En todos los tipos: incluye "justification" explicando por qué la respuesta es correcta.

CONTEXTO EBC (LINEAMIENTOS OFICIALES):
{rag_context}

Responde siempre en ESPAÑOL.
"""

        user_prompt = f"""Área: {exam_request.area} | Grado: {exam_request.grado}

Contenido del docente:
{document_content or '(Sin contenido adjunto)'}

Instrucciones adicionales: {exam_request.prompt or 'Ninguna'}
"""

        # 3. Call Gemini
        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=user_prompt,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    response_mime_type="application/json",
                    response_schema=self._create_exam_schema(),
                    temperature=0.3
                )
            )
            
            return json.loads(response.text)
        except Exception as e:
            logger.error(f"Error calling Gemini: {str(e)}")
            raise
