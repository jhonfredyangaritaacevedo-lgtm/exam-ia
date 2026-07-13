from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.responses import Response
from sqlalchemy.orm import Session
from core.database import get_db
from core.auth import get_current_active_user
from schemas.exam import ExamResponse
from repositories.exam_repository import ExamRepository
from services.pdf_service import pdf_service
from services.word_service import word_service
from services.r2_service import r2_service
import uuid
import re
from typing import List

router = APIRouter(prefix="/exams", tags=["Exams"])

@router.get("", response_model=List[ExamResponse])
async def list_exams(
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    exam_repo = ExamRepository(db)
    return exam_repo.list_by_user(uuid.UUID(current_user["user_id"]))

@router.get("/{exam_id}", response_model=ExamResponse)
async def get_exam(
    exam_id: uuid.UUID,
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    exam_repo = ExamRepository(db)
    exam = exam_repo.get_by_id(exam_id)
    
    if not exam:
        raise HTTPException(status_code=404, detail="Examen no encontrado")
        
    if str(exam.user_id) != current_user["user_id"]:
        raise HTTPException(status_code=403, detail="No tienes permiso para ver este examen")
        
    return exam

def _get_owned_exam(exam_id: uuid.UUID, current_user: dict, db: Session):
    exam_repo = ExamRepository(db)
    exam = exam_repo.get_by_id(exam_id)

    if not exam:
        raise HTTPException(status_code=404, detail="Examen no encontrado")

    if str(exam.user_id) != current_user["user_id"]:
        raise HTTPException(status_code=403, detail="No tienes permiso para ver este examen")

    return exam


def _get_owned_exam_with_result(exam_id: uuid.UUID, current_user: dict, db: Session):
    exam = _get_owned_exam(exam_id, current_user, db)

    if not exam.result:
        raise HTTPException(status_code=400, detail="El examen no tiene contenido para exportar")

    return exam


@router.get("/{exam_id}/files")
async def list_exam_files(
    exam_id: uuid.UUID,
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    exam = _get_owned_exam(exam_id, current_user, db)

    if not exam.files_uuid:
        return []

    files = r2_service.list_files_in_folder(f"files_for_exam/{exam.files_uuid}/")
    return [f["filename"] for f in files]


@router.get("/{exam_id}/files/{filename}")
async def download_exam_file(
    exam_id: uuid.UUID,
    filename: str,
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    exam = _get_owned_exam(exam_id, current_user, db)

    if not exam.files_uuid:
        raise HTTPException(status_code=404, detail="El examen no tiene archivos adjuntos")

    key = f"files_for_exam/{exam.files_uuid}/{filename}"
    try:
        file_bytes = r2_service.download_file(key)
    except Exception:
        raise HTTPException(status_code=404, detail="Archivo no encontrado")

    return Response(
        content=file_bytes,
        media_type="application/octet-stream",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


def _safe_filename(title: str) -> str:
    safe = re.sub(r'[^\w\s-]', '', (title or 'examen').encode('ascii', 'ignore').decode('ascii')).strip()
    return re.sub(r'[-\s]+', '_', safe) or 'examen'


@router.get("/{exam_id}/pdf")
async def export_exam_pdf(
    exam_id: uuid.UUID,
    include_solutions: bool = False,
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    exam = _get_owned_exam_with_result(exam_id, current_user, db)

    pdf_content = pdf_service.generate_exam_pdf(exam, include_solutions)

    suffix = "_con_soluciones" if include_solutions else "_sin_resolver"
    filename = f"{_safe_filename(exam.title)}{suffix}.pdf"

    return Response(
        content=pdf_content,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


@router.get("/{exam_id}/word")
async def export_exam_word(
    exam_id: uuid.UUID,
    include_solutions: bool = False,
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    exam = _get_owned_exam_with_result(exam_id, current_user, db)

    word_content = word_service.generate_exam_word(exam, include_solutions)

    suffix = "_con_soluciones" if include_solutions else "_sin_resolver"
    filename = f"{_safe_filename(exam.title)}{suffix}.docx"

    return Response(
        content=word_content,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


@router.delete("/{exam_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_exam(
    exam_id: uuid.UUID,
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    exam_repo = ExamRepository(db)
    exam = exam_repo.get_by_id(exam_id)

    if not exam:
        raise HTTPException(status_code=404, detail="Examen no encontrado")

    if str(exam.user_id) != current_user["user_id"]:
        raise HTTPException(status_code=403, detail="No tienes permiso para eliminar este examen")

    exam_repo.soft_delete(exam_id)


@router.get("/{exam_id}/status")
async def get_exam_status(
    exam_id: uuid.UUID,
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    exam_repo = ExamRepository(db)
    exam = exam_repo.get_by_id(exam_id)
    
    if not exam:
        raise HTTPException(status_code=404, detail="Examen no encontrado")
        
    if str(exam.user_id) != current_user["user_id"]:
        raise HTTPException(status_code=403, detail="No tienes permiso")
        
    return {"status": exam.status}
