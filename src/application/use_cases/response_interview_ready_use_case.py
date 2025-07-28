
from application.dto.create_interview_response_dto import CreateInterviewResponseDTO
from application.use_cases.base_interview_ready_use_case import BaseInterviewReadyUseCase
from datetime import datetime, timezone
class ResponseInterviewReadyUseCase(BaseInterviewReadyUseCase):
    async def execute(self, id: str, user_response: str, user_id: str) -> CreateInterviewResponseDTO:
        try:
            print(f"Executing ResponseInterviewReadyUseCase with id: {id}, user_response: {user_response}, user_id: {user_id}")
            
            interview = await self.interview_ready_repository.find_by_id(id)
            
            # Validaciones básicas
            if interview.status != "in_progress":
                raise ValueError("Interview is not in progress")
            
            if user_id != interview.userId:
                raise ValueError("User ID does not match the interview's user ID")
            
            # VALIDACIÓN CRÍTICA: Verificar que actual_question existe
            if interview.actual_question is None:
                raise ValueError("No current question available")
            
            print(f"Processing response for question ID: {interview.actual_question.id}, User Response: {user_response}")
            
           
            interview.actual_question.answer = user_response
            
            
            gemini_response = await self.gemini_service.generate_feedback(
                question=interview.actual_question.question,
                user_response=user_response,
                seniority=interview.user_seniority,
                specialization=interview.user_specialization,
                interview_type=interview.type
            )
            
            feedback = gemini_response.get('feedback', '')
            good_question=gemini_response.get("good_question",False)
            interview.actual_question.feedback = feedback
            
            for q in interview.questions:
                if q.id == interview.actual_question.id:
                    q.answer = user_response
                    q.feedback = feedback
                    break
            interview.previus_question = interview.actual_question
            

            
            if True :

                
            
            
                current_question_id = interview.actual_question.id
                next_question_found = False
            
                for i, question in enumerate(interview.questions):
                    if question.id == current_question_id:
                    # Verificar si hay una siguiente pregunta
                        if i + 1 < len(interview.questions):
                            interview.actual_question = interview.questions[i + 1]
                            next_question_found = True
                            print(f"Moving to next question: {interview.actual_question.id}")
                        break
            
            # Si no hay más preguntas, completar la entrevista
                if not next_question_found:
                    interview.status = "completed"
                    interview.end_at = datetime.now(timezone.utc)
                # IMPORTANTE: Mantener actual_question con la última pregunta
                # NO asignar None aquí
                    print("Interview completed")
            else:
                interview.actual_question=interview.actual_question
            
            # Actualizar en la base de datos
            updated_interview = await self.interview_ready_repository.update(interview)
            print(f"InterviewReady updated successfully with ID: {updated_interview.id}")
            
            # Construir respuesta según el estado
            if updated_interview.status == "completed":
                return CreateInterviewResponseDTO(
                    id=str(updated_interview.id),
                    user_id=updated_interview.userId,
                    current_question=updated_interview.previus_question,
                    type=updated_interview.type,
                    next_question=None,  # No hay siguiente pregunta
                    init_at=str(updated_interview.init_at),
                    status=updated_interview.status,
                    question_number=updated_interview.question_number,
                    actual_question=updated_interview.previus_question.id,
                    feedback=updated_interview.previus_question.feedback,
                    message="Interview completed successfully"
                )
            else:
                return CreateInterviewResponseDTO(
                    id=str(updated_interview.id),
                    user_id=updated_interview.userId,
                    type=updated_interview.type,
                    current_question=updated_interview.previus_question,
                    next_question=updated_interview.actual_question,
                    init_at=str(updated_interview.init_at),
                    status=updated_interview.status,
                    question_number=updated_interview.question_number,
                    actual_question=updated_interview.actual_question.id,
                    feedback=updated_interview.previus_question.feedback
                )
            
        except Exception as e:
            import traceback
            print(f"Error in execute method: {e}")
            print(f"Full traceback: {traceback.format_exc()}")
            raise ValueError(f"An error occurred while executing the use case: {str(e)}")