
from application.dto.create_interview_response_dto import CreateInterviewResponseDTO
from application.dto.user_response_dto import UserResponseDTO
from application.use_cases.base_interview_ready_use_case import BaseInterviewReadyUseCase
from utils.sanitization import InputSanitizer, ValidationHelper
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)

class ResponseInterviewReadyUseCase(BaseInterviewReadyUseCase):
    async def execute(self, id: str, user_response: str, user_id: str) -> CreateInterviewResponseDTO:
        try:
            logger.info(f"Processing response for interview {id}, user {user_id}")
            
            # Validar y sanitizar entrada usando el DTO
            response_dto = UserResponseDTO(
                user_response=user_response,
                user_id=user_id
            )
            
            interview = await self.interview_ready_repository.find_by_id(id)
            if not interview:
                raise ValueError("Interview not found")
            
            # Validaciones de estado
            if interview.status != "in_progress":
                raise ValueError("Interview is not in progress")
            
            if response_dto.user_id != interview.userId:
                raise ValueError("User ID does not match the interview's user ID")
            
            if interview.actual_question is None:
                raise ValueError("No current question available")
            
            logger.info(f"Processing response for question ID: {interview.actual_question.id}")
            
            # Asignar respuesta sanitizada
            interview.actual_question.answer = response_dto.user_response
            
            # Generar feedback con tipo de entrevista
            gemini_response = await self.gemini_service.generate_feedback(
                question=interview.actual_question.question,
                user_response=response_dto.user_response,
                seniority=interview.user_seniority,
                specialization=interview.user_specialization,
                interview_type=getattr(interview, 'interview_type', 'behavioral')
            )
            
            feedback = gemini_response.get('feedback', '')
            good_question = gemini_response.get("good_question", False)
            interview.actual_question.feedback = feedback
            
            # Actualizar pregunta en la lista
            for q in interview.questions:
                if q.id == interview.actual_question.id:
                    q.answer = response_dto.user_response
                    q.feedback = feedback
                    break
            
            # Guardar pregunta anterior
            interview.previus_question = interview.actual_question
            
            # Lógica de avance basada en calidad de respuesta
            if good_question:
                # Buscar siguiente pregunta
                current_question_id = interview.actual_question.id
                next_question_found = False
                
                for i, question in enumerate(interview.questions):
                    if question.id == current_question_id:
                        # Verificar si hay siguiente pregunta
                        if i + 1 < len(interview.questions):
                            # Validar secuencia de preguntas
                            if ValidationHelper.validate_question_sequence(i + 2, len(interview.questions)):
                                interview.actual_question = interview.questions[i + 1]
                                next_question_found = True
                                logger.info(f"Moving to next question: {interview.actual_question.id}")
                        break
                
                # Si no hay más preguntas, completar entrevista
                if not next_question_found:
                    interview.status = "completed"
                    interview.end_at = datetime.now(timezone.utc)
                    logger.info("Interview completed - all questions answered")
                    
            else:
                # Respuesta de mala calidad - mantener en la misma pregunta
                logger.info("Poor quality response - staying on same question")
                # interview.actual_question permanece igual
            
            # Actualizar timestamp
            interview.updated_at = datetime.now(timezone.utc)
            
            # Guardar cambios
            updated_interview = await self.interview_ready_repository.update(interview)
            if not updated_interview:
                raise ValueError("Failed to update interview")
                
            logger.info(f"InterviewReady updated successfully with ID: {updated_interview.id}")
            
            # Construir respuesta según estado
            interview_type = getattr(updated_interview, 'interview_type', 'behavioral')
            
            if updated_interview.status == "completed":
                return CreateInterviewResponseDTO(
                    id=str(updated_interview.id),
                    user_id=updated_interview.userId,
                    interview_type=interview_type,
                    current_question=updated_interview.previus_question,
                    next_question=None,
                    init_at=str(updated_interview.init_at),
                    status=updated_interview.status,
                    question_number=updated_interview.question_number,
                    actual_question=updated_interview.previus_question.id,
                    feedback=feedback,
                    good_question=good_question,
                    message="Interview completed successfully"
                )
            else:
                return CreateInterviewResponseDTO(
                    id=str(updated_interview.id),
                    user_id=updated_interview.userId,
                    interview_type=interview_type,
                    current_question=updated_interview.previus_question,
                    next_question=updated_interview.actual_question,
                    init_at=str(updated_interview.init_at),
                    status=updated_interview.status,
                    question_number=updated_interview.question_number,
                    actual_question=updated_interview.actual_question.id,
                    feedback=feedback,
                    good_question=good_question
                )
                
        except ValueError as ve:
            logger.error(f"Validation error in ResponseInterviewReadyUseCase: {ve}")
            raise ve
        except Exception as e:
            logger.error(f"Unexpected error in ResponseInterviewReadyUseCase: {e}")
            import traceback
            logger.error(f"Full traceback: {traceback.format_exc()}")
            raise ValueError(f"An error occurred while executing the use case: {str(e)}")