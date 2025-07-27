from pydantic import BaseModel
from typing import List



class InterviewReadyDto(BaseModel):
    user_id: str
    user_seniority: str
    type:str
    user_specialization: str
    init_at: str
    end_at: str
    status: str
    questions_number:int
    points_earned:int
    updated_at: str
    id: str
class GetInterviewReadyDto(BaseModel):
    interviews: List[InterviewReadyDto]
    total: int
    limit: int
    skip: int

