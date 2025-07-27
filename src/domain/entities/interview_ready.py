from beanie import Document
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Literal
from datetime import datetime, timezone
from utils.sanitization import InputSanitizer, ValidationHelper


class CompetencyBreakdown(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    score: int = Field(..., ge=0, le=100)

    class Config:
        arbitrary_types_allowed = True


class FeedBack(BaseModel):
    overall_score: int = Field(..., ge=0, le=100)
    competency_breakdown: List[CompetencyBreakdown] = Field(default_factory=list)
    points_earned: int = Field(default=0, ge=0)
    focus_questions: List[str] = Field(default_factory=list)
    summary_feedback: str = Field(default="", max_length=1000)

    class Config:
        arbitrary_types_allowed = True


class Question(BaseModel):
    id: int = Field(..., gt=0)
    question: str = Field(..., min_length=10, max_length=500)
    answer: Optional[str] = Field(None, max_length=3000)
    feedback: Optional[str] = Field(None, max_length=500)
    competency: Optional[str] = Field(None, max_length=100)
    difficulty: Optional[Literal["easy", "medium", "hard"]] = Field(None)

    @field_validator('question', mode='before')
    @classmethod
    def sanitize_question(cls, v):
        if v is None:
            raise ValueError("Question text is required")
        return InputSanitizer.sanitize_text(str(v), max_length=500)
    
    @field_validator('answer', mode='before')
    @classmethod
    def sanitize_answer(cls, v):
        if v is None:
            return v
        if isinstance(v, str) and v.strip():
            return InputSanitizer.sanitize_user_response(str(v))
        return v
    
    @field_validator('feedback', mode='before')
    @classmethod
    def sanitize_feedback(cls, v):
        if v is None:
            return v
        if isinstance(v, str) and v.strip():
            return InputSanitizer.sanitize_text(str(v), max_length=500)
        return v

    class Config:
        arbitrary_types_allowed = True
        validate_assignment = True


class InterviewReady(Document):
    userId: str = Field(..., min_length=1, max_length=50)
    interview_type: Literal["behavioral", "structured", "technical", "simulation"] = Field(default="behavioral")
    user_seniority: Literal["junior", "mid", "senior", "lead", "principal"] = Field(...)
    user_specialization: str = Field(..., min_length=2, max_length=100)
    questions: List[Question] = Field(default_factory=list)
    init_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    end_at: Optional[datetime] = None
    status: Literal["in_progress", "completed"] = Field(default="in_progress")
    question_number: int = Field(..., gt=0)
    actual_question: Optional[Question] = None
    previus_question: Optional[Question] = None
    points_earned: int = Field(default=0, ge=0)
    feedback: Optional[FeedBack] = None
    updated_at: Optional[datetime] = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    @field_validator('userId', mode='before')
    @classmethod
    def sanitize_user_id(cls, v):
        if v is None:
            raise ValueError("User ID is required")
        return InputSanitizer.sanitize_user_id(str(v))
    
    @field_validator('user_specialization', mode='before')
    @classmethod
    def sanitize_specialization(cls, v):
        if v is None:
            raise ValueError("User specialization is required")
        return InputSanitizer.sanitize_specialization(str(v))
    
    @field_validator('questions')
    @classmethod
    def validate_questions_list(cls, v, info):
        question_number = info.data.get('question_number', 0)
        if len(v) > 0 and len(v) != question_number:
            # Log warning but don't fail - puede estar en construcción
            pass
        return v
    
    def model_post_init(self, __context):
        """Validaciones contextuales después de la inicialización"""
        # Actualizar timestamp
        self.updated_at = datetime.now(timezone.utc)
        
        # Validar transición de estados
        if hasattr(self, '_original_status'):
            if not ValidationHelper.validate_interview_state_transition(
                self._original_status, self.status
            ):
                raise ValueError(f"Invalid status transition from {self._original_status} to {self.status}")
    
    class Settings:
        collection = "interview_ready"
        use_state_management = True
        validate_on_save = True
    
    class Config:
        arbitrary_types_allowed = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None,
        }
        validate_assignment = True
        allow_population_by_field_name = True
   
        
    



    