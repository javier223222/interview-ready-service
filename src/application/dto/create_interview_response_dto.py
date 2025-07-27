from pydantic import BaseModel, field_validator
from typing import Optional
from domain.entities.interview_ready import Question
from utils.sanitization import InputSanitizer

class CreateInterviewResponseDTO(BaseModel):
    id: str
    user_id: str
    interview_type: str
    current_question: Question
    next_question: Optional[Question] = None
    init_at: str
    status: str
    question_number: int
    actual_question: int
    feedback: Optional[str] = None
    good_question: Optional[bool] = None
    message: Optional[str] = None
    
    @field_validator('user_id', mode='before')
    @classmethod
    def sanitize_user_id(cls, v):
        if v is None:
            raise ValueError("User ID is required")
        return InputSanitizer.sanitize_user_id(str(v))
    
    @field_validator('feedback', mode='before')
    @classmethod
    def sanitize_feedback(cls, v):
        if v is None:
            return v
        if isinstance(v, str) and v.strip():
            return InputSanitizer.sanitize_text(str(v), max_length=500)
        return v
    
    @field_validator('message', mode='before')
    @classmethod
    def sanitize_message(cls, v):
        if v is None:
            return v
        if isinstance(v, str) and v.strip():
            return InputSanitizer.sanitize_text(str(v), max_length=200)
        return v

# Mantenemos compatibilidad con el nombre anterior
class CreateInterviewReadyResponseDTO(CreateInterviewResponseDTO):
    """Alias para compatibilidad con código existente"""
    pass
    


 
   