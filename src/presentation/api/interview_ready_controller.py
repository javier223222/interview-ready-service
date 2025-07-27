
from fastapi import APIRouter, HTTPException, status
from pydantic import ValidationError
import logging

from application.dto.create_interview_ready_dto import CreateInterviewReadyDTO
from application.dto.user_response_dto import UserResponseDTO
from application.use_cases.create_interview_ready_use_case import CreateInterviewReadyUseCase

from domain.repositories.interview_ready_repository import InterviewReadyRepository
from application.dto.create_interview_response_dto import CreateInterviewResponseDTO
from application.dto.get_interview_ready_feedback_dto import GetInterviewReadyFeedBackDto
from application.use_cases.generate_interview_feedback_use_case import GenerateInterviewFeedbackUseCase
from application.use_cases.response_interview_ready_use_case import ResponseInterviewReadyUseCase
from application.use_cases.get_interview_ready_use_case import GetInterviewReadyUseCase
from application.use_cases.get_interview_ready_by_id_use_case import GetInterviewReadyByIdUseCase
from infrastructure.external_services.gemini_service import GeminiService
from domain.entities.interview_ready import InterviewReady
from infrastructure.messaging.rabbitmq_producer import rabbitmq_producer

logger = logging.getLogger(__name__)
interview_router = APIRouter(prefix="/interview",tags=["questions"])


@interview_router.post("/questions/generate", status_code=status.HTTP_201_CREATED,summary="Generate Interview Questions",
                       description="Generates a set of interview questions based on user seniority and specialization.",response_model=CreateInterviewResponseDTO)
async def generate_questions(dto: CreateInterviewReadyDTO):
    try:
        gemini_service = GeminiService()
        interview_ready_repository = InterviewReadyRepository()
        create_interview_ready_use_case = CreateInterviewReadyUseCase(
            interview_ready_repository=interview_ready_repository,
            gemini_service=gemini_service
        )
        questions_data = await create_interview_ready_use_case.execute(dto)
        if not questions_data:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to generate questions")

        logger.info(f"Successfully generated questions for user: {dto.user_id}")
        return questions_data
        
    except ValidationError as ve:
        logger.warning(f"Validation error in generate_questions: {ve}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Validation error: {str(ve)}"
        )
    except ValueError as ve:
        logger.error(f"Business logic error in generate_questions: {ve}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as e:
        logger.error(f"Unexpected error in generate_questions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An internal error occurred while generating questions"
        )
@interview_router.post("/questions/response/{id}", status_code=status.HTTP_200_OK,
                       summary="Submit User Response to Interview Question",
                       description="Submits the user's response to the current interview question and retrieves the next question.",
                       response_model=CreateInterviewResponseDTO)
async def answer_question(id: str, response_dto: UserResponseDTO):
    try:
        gemini_service = GeminiService()
        interview_ready_repository = InterviewReadyRepository()
        response_interview_ready_use_case = ResponseInterviewReadyUseCase(
            interview_ready_repository=interview_ready_repository,
            gemini_service=gemini_service
        )
        response = await response_interview_ready_use_case.execute(id, response_dto)

        if not response:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to process response")
            
        logger.info(f"Successfully processed response for interview: {id}")
        return response
        
    except ValidationError as ve:
        logger.warning(f"Validation error in answer_question: {ve}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Validation error: {str(ve)}"
        )
    except ValueError as ve:
        logger.error(f"Business logic error in answer_question: {ve}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as e:
        logger.error(f"Unexpected error in answer_question: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An internal error occurred while processing the response"
        )
    
@interview_router.get("/questions/feedback/{id}", status_code=status.HTTP_200_OK,response_model=GetInterviewReadyFeedBackDto,
                      summary="Get a Feeback",
                      description="Get a feedback after the interview finish")
async def get_question(id:str,user_id:str):
    try:
        
        gemini_service = GeminiService()

        interview_ready_repository = InterviewReadyRepository()
        generate_interview_feedback_use_case = GenerateInterviewFeedbackUseCase(
            interview_ready_repository=interview_ready_repository,
            gemini_service=gemini_service,
            rabbitmq_producer=rabbitmq_producer
        )
        feedback = await generate_interview_feedback_use_case.execute(id,user_id)
        
        if not feedback:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to generate feedback")
        
        logger.info(f"Successfully generated feedback for interview: {id}")
        return feedback
        
    except ValidationError as ve:
        logger.warning(f"Validation error in get_question: {ve}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Validation error: {str(ve)}"
        )
    except ValueError as ve:
        logger.error(f"Business logic error in get_question: {ve}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as e:
        logger.error(f"Unexpected error in get_question: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An internal error occurred while generating feedback"
        )

@interview_router.get("/history/{user_id}", status_code=status.HTTP_200_OK,
                      summary="Get Interview History",
                      description="Retrieves the interview history for a specific user.")
async def get_interview_history(user_id: str):
    try:
        
        interview_ready_repository = InterviewReadyRepository()
        get_interview_ready_use_case = GetInterviewReadyUseCase(
            interview_ready_repository=interview_ready_repository
        )

        history = await get_interview_ready_use_case.execute(
            user_id=user_id
        )
        logger.info(f"Retrieved interview history for user {user_id}")

        if not history:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No interview history found")

        return history
        
    except ValidationError as ve:
        logger.warning(f"Validation error in get_interview_history: {ve}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Validation error: {str(ve)}"
        )
    except ValueError as ve:
        logger.error(f"Business logic error in get_interview_history: {ve}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as e:
        logger.error(f"Unexpected error in get_interview_history: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An internal error occurred while retrieving interview history"
        )

@interview_router.get("/history/{user_id}/{interview_id}", status_code=status.HTTP_200_OK,
                      summary="Get Interview by ID",
                      response_model=InterviewReady)
async def get_interview_by_id(user_id: str, interview_id: str):
    try:
        interview_ready_repository = InterviewReadyRepository()
        get_interview_ready_by_id_use_case = GetInterviewReadyByIdUseCase(
            interview_ready_repository=interview_ready_repository
        )

        interview = await get_interview_ready_by_id_use_case.execute(
            user_id=user_id,
            interview_id=interview_id
        )
        
        if not interview:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Interview not found")

        logger.info(f"Retrieved interview {interview_id} for user {user_id}")
        return interview
        
    except ValidationError as ve:
        logger.warning(f"Validation error in get_interview_by_id: {ve}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Validation error: {str(ve)}"
        )
    except ValueError as ve:
        logger.error(f"Business logic error in get_interview_by_id: {ve}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as e:
        logger.error(f"Unexpected error in get_interview_by_id: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An internal error occurred while retrieving the interview"
        )