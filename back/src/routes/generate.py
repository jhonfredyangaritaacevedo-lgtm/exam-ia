from fastapi import APIRouter, Depends, status, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from core.database import get_db
from core.auth import get_current_active_user
from schemas.exam import (
    GenerateExamRequest,
    ExamResponse,
    PresignUploadRequest,
    PresignUploadResponse,
)
from repositories.exam_repository import ExamRepository
from services.async_exam_service import async_exam_service
from services.r2_service import r2_service
from typing import List
import uuid
import os

router = APIRouter(prefix="/generate", tags=["Generation"])


@router.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_exam_files(
    files: List[UploadFile] = File(...),
    current_user: dict = Depends(get_current_active_user),
):
    """
    Uploads teacher documents to R2 under a shared folder.
    Returns the files_uuid to link with the exam generation request.
    """
    allowed = {".pdf", ".docx", ".pptx", ".xlsx"}
    files_uuid = str(uuid.uuid4())
    uploaded = []

    for file in files:
        ext = os.path.splitext(file.filename or "")[1].lower()
        if ext not in allowed:
            raise HTTPException(status_code=400, detail=f"Tipo de archivo no permitido: {ext}")
        content = await file.read()
        r2_service.upload_exam_file(content, files_uuid, file.filename)
        uploaded.append(file.filename)

    return {"files_uuid": files_uuid, "files": uploaded}

@router.post("/presign", response_model=PresignUploadResponse, status_code=status.HTTP_201_CREATED)
async def presign_exam_uploads(
    request: PresignUploadRequest,
    current_user: dict = Depends(get_current_active_user),
):
    """
    Returns presigned PUT URLs so the browser uploads files directly to R2,
    bypassing the API Gateway/Lambda 6MB payload limit.
    Shares a single files_uuid to link with the exam generation request.
    """
    allowed = {".pdf", ".docx", ".pptx", ".xlsx"}
    files_uuid = str(uuid.uuid4())
    presigned = []

    for filename in request.filenames:
        ext = os.path.splitext(filename or "")[1].lower()
        if ext not in allowed:
            raise HTTPException(status_code=400, detail=f"Tipo de archivo no permitido: {ext}")
        presigned.append(r2_service.generate_presigned_upload_url(files_uuid, filename))

    return {"files_uuid": files_uuid, "files": presigned}


@router.post("/exam", response_model=ExamResponse, status_code=status.HTTP_202_ACCEPTED)
async def generate_exam(
    request: GenerateExamRequest,
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Starts asynchronous exam generation.
    Returns the exam object with PENDING status.
    """
    exam_repo = ExamRepository(db)
    
    # 1. Create entry in DB
    # Convert question_types list of objects to dict for JSONB storage
    q_types_dict = {qt.type.value: qt.quantity for qt in request.question_types}
    
    exam = exam_repo.create(
        user_id=uuid.UUID(current_user["user_id"]),
        title=request.title or "Nuevo Examen",
        area=request.area,
        grado=request.grado,
        prompt=request.prompt or "",
        num_questions=request.num_questions,
        question_types=q_types_dict,
        files_uuid=str(request.files_uuid) if request.files_uuid else None
    )
    
    # 2. Trigger background process
    async_exam_service.start_exam_generation(exam.id, request)
    
    return exam
