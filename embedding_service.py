from pydantic import BaseModel, Field, field_validator, model_validator
from typing import List, Optional, Any
from uuid import UUID
from enum import Enum

class QuestionTypeEnum(str, Enum):
    multiple_choice = "multiple_choice"
    true_false = "true_false"
    short_answer = "short_answer"
    essay = "essay"

class QuestionType(BaseModel):
    type: QuestionTypeEnum
    quantity: int = Field(gt=0, description="Number of questions of this type")

class GenerateExamRequest(BaseModel):
    prompt: Optional[str] = Field(None, description="Exam generation prompt")
    title: Optional[str] = Field(None, min_length=1, description="Exam title")
    area: str = Field(..., description="Subject area (e.g. Ciencias Naturales)")
    grado: str = Field(..., description="Grade (9, 10, 11)")
    num_questions: int = Field(gt=0, description="Total number of questions")
    files_uuid: Optional[UUID] = Field(None, description="UUID of the files folder")
    question_types: List[QuestionType] = Field(min_length=1, description="List of question types and quantities")
    
    @field_validator('question_types')
    @classmethod
    def validate_question_quantities(cls, v, info):
        if info.data and 'num_questions' in info.data:
            total_quantity = sum(qt.quantity for qt in v)
            if total_quantity != info.data['num_questions']:
                raise ValueError(f'Sum of question quantities ({total_quantity}) must equal num_questions ({info.data["num_questions"]})')
        return v

class PresignUploadRequest(BaseModel):
    filenames: List[str] = Field(..., min_length=1, description="Names of the files to upload")

class PresignedFile(BaseModel):
    filename: str
    key: str
    url: str

class PresignUploadResponse(BaseModel):
    files_uuid: str
    files: List[PresignedFile]

class ExamResponse(BaseModel):
    id: UUID
    title: str
    area: str
    grado: str
    num_questions: int
    status: str
    result: Optional[Any] = None
    files_uuid: Optional[str] = None
    created_at: Any

    class Config:
        from_attributes = True
