from domain.repositories.interview_ready_repository import InterviewReadyRepository
from domain.entities.interview_ready import InterviewReady


class GetInterviewReadyByIdUseCase:
    def __init__(self, interview_ready_repository: InterviewReadyRepository):
        self.interview_ready_repository = interview_ready_repository

    async def execute(self, user_id: str, interview_id: str) -> InterviewReady:
        try:
            interview = await self.interview_ready_repository.find_by_id(interview_id)
            if interview.userId != user_id:
                raise ValueError("You are not authorized to access this interview")
            

            if not interview:
                raise ValueError("Interview not found for the given ID")
            return interview
        except Exception as e:
            print(f"Error in GetInterviewReadyByIdUseCase: {e}")
            raise Exception("Failed to execute GetInterviewReadyByIdUseCase") from e