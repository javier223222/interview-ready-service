from pydantic import BaseModel
from typing import Optional
from domain.entities.interview_ready import Question
class CreateInterviewResponseDTO(BaseModel):
    id:str
    user_id:str
    type:str
    current_question:Question
    next_question:Optional[Question]
    init_at:str
    status:str
    question_number:int
    actual_question:int
    feedback: Optional[str] = None
    message: Optional[str] = None
    


 
   