from pydantic import BaseModel, Field, field_validator
from typing import Literal


class QuestionCount(BaseModel):
    """Value Object que representa el número de preguntas permitidas en una entrevista."""
    
    value: Literal[5, 10, 15, 30] = Field(
        description="Número de preguntas permitidas",
        example=10
    )

    @field_validator('value')
    def validate_question_count(cls, v):
        allowed_values = [5, 10, 15, 30]
        if v not in allowed_values:
            raise ValueError(f"El número de preguntas debe ser uno de: {allowed_values}")
        return v
    
    def __str__(self) -> str:
        return str(self.value)
    
    def __int__(self) -> int:
        return self.value
    
    def __eq__(self, other) -> bool:
        if isinstance(other, QuestionCount):
            return self.value == other.value
        return False
    
    def __hash__(self) -> int:
        return hash(self.value)
    
    @classmethod
    def create(cls, count: int) -> 'QuestionCount':
        """Factory method para crear una instancia de QuestionCount."""
        return cls(value=count)
    
    class Config:
        frozen = True  
        allow_reuse = True