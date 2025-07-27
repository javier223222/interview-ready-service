
from domain.entities.interview_ready import InterviewReady, Question
from application.dto.create_interview_ready_dto import CreateInterviewReadyDTO
from application.dto.create_interview_response_dto import CreateInterviewResponseDTO
from application.use_cases.base_interview_ready_use_case import BaseInterviewReadyUseCase
from utils.sanitization import ValidationHelper
import logging

logger = logging.getLogger(__name__)

class CreateInterviewReadyUseCase(BaseInterviewReadyUseCase):

    async def execute(self, dto: CreateInterviewReadyDTO) -> CreateInterviewResponseDTO:
        try:
            logger.info(f"Creating interview for user {dto.user_id}, type: {dto.interview_type}")

            # Generar preguntas con el tipo de entrevista
            questions_data = await self.gemini_service.generate_questions(
                num_questions=dto.question_number.value,
                seniority=dto.user_seniority,
                specialization=dto.user_specialization,
                interview_type=dto.interview_type
            )

            if not questions_data or 'questions' not in questions_data:
                raise ValueError("Failed to generate questions from Gemini service")

            # Crear preguntas con validación mejorada
            questions = []
            for i, q_data in enumerate(questions_data['questions']):
                try:
                    question_dict = {
                        'id': q_data.get('id', i + 1),
                        'question': q_data.get('question', ''),
                        'competency': q_data.get('competency', ''),
                        'difficulty': q_data.get('difficulty', 'medium')
                    }
                    
                    # Validar que la pregunta tenga contenido mínimo
                    if len(question_dict['question'].strip()) < 10:
                        logger.warning(f"Question {i} too short, skipping")
                        continue
                        
                    question = Question(**question_dict)
                    questions.append(question)
                except Exception as qe:
                    logger.error(f"Error creating question {i}: {qe}")
                    continue

            if not questions:
                raise ValueError("No valid questions were created")

            # Determinar siguiente pregunta
            next_question = questions[1] if len(questions) > 1 else None

            # Crear entrevista con validaciones mejoradas
            interview_ready = InterviewReady(
                userId=dto.user_id,
                user_seniority=dto.user_seniority,
                user_specialization=dto.user_specialization,
                interview_type=dto.interview_type,
                questions=questions,
                actual_question=questions[0],
                question_number=dto.question_number.value,
            )

            logger.info(f"Creating InterviewReady with userId: {interview_ready.userId}, question_number: {interview_ready.question_number}")

            # Guardar en repositorio
            res = await self.interview_ready_repository.create(interview_ready)
            if not res:
                raise ValueError("Failed to create InterviewReady in the repository")
                
            logger.info(f"InterviewReady created successfully with ID: {res.id}")

            # Crear respuesta con validación de completitud
            return CreateInterviewResponseDTO(
                id=str(res.id),
                user_id=res.userId,
                interview_type=res.interview_type,
                current_question=questions[0],
                next_question=next_question,
                init_at=str(res.init_at),
                status=res.status,
                question_number=res.question_number,
                actual_question=1
            )
            
        except ValueError as ve:
            logger.error(f"Validation error in CreateInterviewReadyUseCase: {ve}")
            raise ve
        except Exception as e:
            logger.error(f"Unexpected error in CreateInterviewReadyUseCase: {e}")
            raise ValueError(f"Failed to create interview ready: {str(e)}")
