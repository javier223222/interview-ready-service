from pydantic import BaseModel
from domain.entities.interview_ready import FeedBack

class GetInterviewReadyFeedBackDto(BaseModel):
    interview_id:str
    user_id:str
    points_earned:int
    feedback:FeedBack
    init_at:str
    finish_at:str
    

