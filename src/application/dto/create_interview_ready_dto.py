from pydantic import BaseModel,field_validator


from domain.value_objects.question_count import QuestionCount
class CreateInterviewReadyDTO(BaseModel):
     user_id: str
     user_seniority: str
     user_specialization: str
     type:str
     question_number: QuestionCount
     @field_validator('user_seniority')
     def validate_seniority(cls, v):
        allowed_seniorities = ['junior', 'mid', 'senior', 'lead', 'principal']
        if v.lower() not in allowed_seniorities:
            raise ValueError(f"Seniority debe ser uno de: {allowed_seniorities}")
        return v.lower()
     @field_validator("type")
     def validate_interview_types(cls,v):
         allowed_interviews=["behavioral","structured","technical","simulation"]
         if v.lower() not in allowed_interviews:
            raise ValueError(f"Seniority debe ser uno de: {allowed_interviews}")
         return v.lower()
          
    

