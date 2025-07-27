from pydantic import BaseModel, field_validator, Field
from typing import Literal
from domain.value_objects.question_count import QuestionCount
from utils.sanitization import InputSanitizer

class CreateInterviewReadyDTO(BaseModel):
    user_id: str = Field(..., description="ID único del usuario")
    user_seniority: str = Field(..., description="Nivel de seniority del usuario")
    user_specialization: str = Field(..., description="Especialización del usuario")
    interview_type: Literal["behavioral", "structured", "technical", "simulation"] = Field(
        default="behavioral", 
        description="Tipo de entrevista a realizar"
    )
    question_number: QuestionCount = Field(..., description="Número de preguntas a generar")
    
    @field_validator('user_id', mode='before')
    @classmethod
    def sanitize_user_id(cls, v):
        if v is None:
            raise ValueError("User ID is required")
        return InputSanitizer.sanitize_user_id(str(v))
    
    @field_validator('user_seniority', mode='before')
    @classmethod
    def validate_and_sanitize_seniority(cls, v):
        if v is None:
            raise ValueError("User seniority is required")
        
        v = str(v).strip().lower()
        allowed_seniorities = ['junior', 'mid', 'senior', 'lead', 'principal']
        if v not in allowed_seniorities:
            raise ValueError(f"Seniority must be one of: {allowed_seniorities}")
        return v
    
    @field_validator('user_specialization', mode='before')
    @classmethod
    def sanitize_specialization(cls, v):
        if v is None:
            raise ValueError("User specialization is required")
        return InputSanitizer.sanitize_specialization(str(v))
    
    @field_validator('interview_type', mode='before')
    @classmethod
    def validate_interview_type(cls, v):
        if v is None:
            v = "behavioral"  # valor por defecto
        return str(v).lower()
    
    def model_post_init(self, __context):
        """Validaciones contextuales después de la inicialización"""
        # Validar combinación seniority + interview_type
        InputSanitizer.validate_seniority_context(
            self.user_seniority, 
            self.interview_type
        )
        
        # Validar combinación question_count + interview_type
        InputSanitizer.validate_question_count_for_type(
            self.question_number.value, 
            self.interview_type
        )
          
    

