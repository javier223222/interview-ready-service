from beanie import Document
from pydantic import BaseModel,Field
from typing import List, Optional
from datetime import datetime,timezone


class CompetencyBreakdown(BaseModel):
    name: str
    score: int

class FeedBack(BaseModel):
    overall_score:int
    competency_breakdown: List[CompetencyBreakdown] 
    points_earned: int = 0
    focus_questions: List[str] 
    summary_feedback: str = ""

class Question(BaseModel):
    id: int
    question: str
    answer: Optional[str] = None
    feedback: Optional[str] = None
    competency: str
    difficulty: str


class InterviewReady(Document):
    userId:str
    type: str

    user_seniority: str
    user_specialization: str
    questions: List[Question]
    init_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    end_at: Optional[datetime] = None
    status: str = "in_progress" 
    question_number: int
    actual_question: Optional[Question] = None
    previus_question:Optional[Question]=None
    points_earned: int = 0
    feedback: Optional[FeedBack] = None
    updated_at: Optional[datetime] = None
    
    class Settings:
        collection = "interview_ready"
   
        
    



    