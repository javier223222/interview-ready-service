
from domain.entities.interview_ready import InterviewReady,Question


from application.dto.create_interview_ready_dto import CreateInterviewReadyDTO
from application.dto.create_interview_response_dto import CreateInterviewResponseDTO
from application.use_cases.base_interview_ready_use_case import BaseInterviewReadyUseCase


class CreateInterviewReadyUseCase(BaseInterviewReadyUseCase):
  

    async def execute(self, dto: CreateInterviewReadyDTO) ->CreateInterviewResponseDTO:
     try:


        questions_data = await self.gemini_service.generate_questions(
            num_questions=dto.question_number.value,
            seniority=dto.user_seniority,
            specialization=dto.user_specialization
        )

        
        questions = []
        for i, q_data in enumerate(questions_data['questions']):
            try:
                # Asegúrate de que todos los campos requeridos estén presentes
                question_dict = {
                    'id': q_data.get('id', i + 1),
                    'question': q_data.get('question', ''),
                    'competency': q_data.get('competency', ''),
                    'difficulty': q_data.get('difficulty', 'medium')
                }
                question = Question(**question_dict)
                questions.append(question)
            except Exception as qe:
                print(f"Error creating question {i}: {qe}")
                continue


        
        interview_ready = InterviewReady(
            userId=dto.user_id,
            user_seniority=dto.user_seniority,
            user_specialization=dto.user_specialization,
            questions=questions,
            actual_question=questions[0],
            question_number=dto.question_number.value,
            type=dto.type,
        )
        print(f"Creating InterviewReady with userId: {interview_ready.userId}, question_number: {interview_ready.question_number}")

        
        res=await self.interview_ready_repository.create(interview_ready)
        print(res.actual_question)
        if not res:
            raise ValueError("Failed to create InterviewReady in the repository")
        print(f"InterviewReady created successfully with ID: {res.id}")

        return CreateInterviewResponseDTO(
            id=str(res.id),
            user_id=res.userId,
            current_question=interview_ready.questions[0],
            init_at=str(res.init_at),
            status=res.status,
            question_number=res.question_number,
            next_question=None,  # Asumiendo que no hay una siguiente pregunta al crear
            type=res.type,
            actual_question=1
        )
     except Exception as e:
        print(f"Error occurred while creating InterviewReady: {e}")
        raise ValueError(f"Failed to create interview ready: {str(e)}")
