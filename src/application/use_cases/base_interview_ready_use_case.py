from domain.repositories.interview_ready_repository import InterviewReadyRepository

from infrastructure.external_services.gemini_service import GeminiService


class BaseInterviewReadyUseCase:
    def __init__(self, interview_ready_repository: InterviewReadyRepository, gemini_service: GeminiService):
        self.interview_ready_repository = interview_ready_repository
        self.gemini_service = gemini_service