from application.use_cases.base_interview_ready_use_case import BaseInterviewReadyUseCase
from application.dto.get_interview_ready_feedback_dto import GetInterviewReadyFeedBackDto
from infrastructure.messaging.rabbitmq_producer import RabbitMQProducer
from datetime import datetime
class GenerateInterviewFeedbackUseCase(BaseInterviewReadyUseCase):
    def __init__(self, interview_ready_repository, gemini_service,rabbitmq_producer:RabbitMQProducer):
        self.rabbitmq_producer = rabbitmq_producer
        super().__init__(interview_ready_repository, gemini_service)

    async def execute(self, interview_id: str,user_id: str)->GetInterviewReadyFeedBackDto :
        try:
            print(f"Generating feedback for interview ID: {interview_id}")

            interview = await self.interview_ready_repository.find_by_id(interview_id)
            if interview.status=="in_progress":
                raise ValueError("Interview is still in progress, cannot generate feedback")
            if interview.feedback is not None:
                await self.rabbitmq_producer.publish_message(
                 message={
                    "event": "Interview Ready Finished",
                    "type": "Interview Ready",
                    "created_at": str(datetime.utcnow()),
                    "points_earned": 10,
                     "user_id": user_id,
            },
            queue_name="any",
            priority=5

        )
                return GetInterviewReadyFeedBackDto(
                interview_id=interview_id,
                user_id=user_id,
                points_earned=interview.points_earned,
                feedback=interview.feedback,
                init_at=str(interview.init_at),
                finish_at=str(interview.end_at))
                
            if interview.userId != user_id:
                raise ValueError("You are not able to answer this")
            if not interview:
                raise ValueError("Interview not found")

            
            
            
            feedback = await self.gemini_service.generate_complete_feedback(
                questions=interview.questions,
                seniority=interview.user_seniority,
                specialization=interview.user_specialization,
                interview_type=interview.type
            )
            interview.feedback=feedback
            interview.points_earned=feedback.points_earned
            updated_interview=await self.interview_ready_repository.update(interview)
            if not updated_interview:
                raise ValueError("Failed to update interview with feedback")
            print(f"Feedback generated successfully for interview ID: {interview_id}")
            print(f"Generated feedback: {feedback}")
            await self.rabbitmq_producer.publish_message(
                 message={
                    "event": "Interview Ready Finished",
                    "type": "Interview Ready",
                    "created_at": str(datetime.utcnow()),
                    "points_earned": 10,
                     "user_id": user_id,
            },
            queue_name="any",
            priority=5

        )
            return GetInterviewReadyFeedBackDto(
                interview_id=interview_id,
                user_id=user_id,
                points_earned=updated_interview.points_earned,
                feedback=updated_interview.feedback,
                init_at=str(interview.init_at),
                finish_at=str(interview.end_at))
        
        
        except Exception as e:
            print(f"Error occurred while generating interview feedback: {e}")
            raise ValueError(f"Failed to generate interview feedback: {str(e)}")
