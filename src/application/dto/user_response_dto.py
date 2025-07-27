from pydantic import BaseModel, field_validator, Field
from utils.sanitization import InputSanitizer

class UserResponseDTO(BaseModel):
    """DTO para manejar respuestas de usuarios a preguntas de entrevista"""
    
    user_response: str = Field(..., description="Respuesta del usuario a la pregunta")
    user_id: str = Field(..., description="ID del usuario que responde")
    
    @field_validator('user_response', mode='before')
    @classmethod
    def sanitize_user_response(cls, v):
        if v is None:
            raise ValueError("User response is required")
        return InputSanitizer.sanitize_user_response(str(v))
    
    @field_validator('user_id', mode='before')
    @classmethod
    def sanitize_user_id(cls, v):
        if v is None:
            raise ValueError("User ID is required")
        return InputSanitizer.sanitize_user_id(str(v))
