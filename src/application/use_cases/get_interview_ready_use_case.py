from domain.repositories.interview_ready_repository import InterviewReadyRepository
from application.dto.get_interview_ready_dto import GetInterviewReadyDto,InterviewReadyDto

class GetInterviewReadyUseCase():
    def __init__(self, interview_ready_repository: InterviewReadyRepository):
        self.interview_ready_repository = interview_ready_repository
    async def execute(self, user_id: str,limit: int = 100, skip: int = 0) -> GetInterviewReadyDto:
      try:
          interview = await self.interview_ready_repository.find_all_by_user_id(
              user_id=user_id,
              limit=limit, 
              skip=skip 
          )
          print(f"Found {interview} interviews for user ID: {user_id}")
          interview_ready_dto = [InterviewReadyDto(
              user_id=interview_data["userId"],
              user_seniority=interview_data["user_seniority"],
              user_specialization=interview_data["user_specialization"],
              init_at=str(interview_data["init_at"]),
              end_at=str(interview_data["end_at"]) ,
              status=interview_data["status"],
              questions_number=interview_data["question_number"],
              type=interview_data["type"] if "type" in interview_data else "",
              points_earned=interview_data["points_earned"],
              updated_at=str(interview_data["updated_at"]) if "updated_at" in interview_data else "",
              id=interview_data["id"]
          ) for interview_data in interview]
          get_interview_ready_dto = GetInterviewReadyDto(
              interviews=interview_ready_dto,
              total=len(interview_ready_dto),
              limit=limit,
              skip=skip
          )
          if not get_interview_ready_dto.interviews:
                raise ValueError("No interviews found for the given user ID")
          if not interview:
              raise ValueError("Interview not found for the given user ID")
          return get_interview_ready_dto
      except Exception as e:
          print(f"Error in GetInterviewReadyUseCase: {e}")
          raise Exception("Failed to execute GetInterviewReadyUseCase")
