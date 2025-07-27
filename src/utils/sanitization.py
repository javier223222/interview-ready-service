"""
Input sanitization utilities for Interview Ready Service
"""
import html
import re
from typing import Any, List
import logging

logger = logging.getLogger(__name__)

class InputSanitizer:
    """Utility class for sanitizing and validating input data"""
    
    # Patrones peligrosos que deben ser removidos o escapados
    DANGEROUS_PATTERNS = [
        r'<script[^>]*>.*?</script>',
        r'javascript:',
        r'data:',
        r'vbscript:',
        r'on\w+\s*=',  # onclick, onload, etc.
        r'<iframe',
        r'<object',
        r'<embed',
        r'<form',
    ]
    
    # Caracteres especiales que necesitan ser escapados
    DANGEROUS_CHARS = ['<', '>', '"', "'", '&', '\\', ';']
    
    @staticmethod
    def sanitize_text(text: str, max_length: int = 2000, allow_html: bool = False) -> str:
        """
        Sanitiza texto de entrada general
        
        Args:
            text: Texto a sanitizar
            max_length: Longitud máxima permitida
            allow_html: Si se permite HTML básico
            
        Returns:
            Texto sanitizado
            
        Raises:
            ValueError: Si el texto es inválido
        """
        if not isinstance(text, str):
            raise ValueError("Input must be string")
        
        # Trim espacios
        text = text.strip()
        
        # Validar longitud
        if len(text) > max_length:
            raise ValueError(f"Text too long (max {max_length} characters)")
        
        if len(text) == 0:
            return text
        
        # Remover patrones peligrosos
        for pattern in InputSanitizer.DANGEROUS_PATTERNS:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE)
        
        if not allow_html:
            # Escapar HTML
            text = html.escape(text)
        else:
            # Solo remover caracteres especialmente peligrosos
            for char in ['<script', '<iframe', '<object']:
                text = text.replace(char, '')
        
        return text
    
    @staticmethod
    def sanitize_user_response(response: str) -> str:
        """
        Sanitiza respuestas de usuarios en entrevistas
        
        Args:
            response: Respuesta del usuario
            
        Returns:
            Respuesta sanitizada
            
        Raises:
            ValueError: Si la respuesta es inválida
        """
        if not isinstance(response, str):
            raise ValueError("User response must be string")
        
        # Trim espacios
        response = response.strip()
        
        # Validar longitud mínima y máxima
        if len(response) < 10:
            raise ValueError("Response too short (minimum 10 characters)")
        
        if len(response) > 3000:
            raise ValueError("Response too long (maximum 3000 characters)")
        
        # Verificar que contenga texto significativo
        if not re.search(r'[a-zA-Z]', response):
            raise ValueError("Response must contain meaningful text")
        
        # Sanitizar contenido
        response = InputSanitizer.sanitize_text(response, max_length=3000)
        
        return response
    
    @staticmethod
    def sanitize_user_id(user_id: str) -> str:
        """
        Sanitiza user_id
        
        Args:
            user_id: ID del usuario
            
        Returns:
            User ID sanitizado
            
        Raises:
            ValueError: Si el user_id es inválido
        """
        if not isinstance(user_id, str):
            raise ValueError("User ID must be string")
        
        user_id = user_id.strip()
        
        # Solo números y letras, mínimo 1 carácter
        if not re.match(r'^[a-zA-Z0-9]+$', user_id):
            raise ValueError("Invalid user_id format (only alphanumeric characters allowed)")
        
        if len(user_id) < 1 or len(user_id) > 50:
            raise ValueError("User ID must be between 1 and 50 characters")
        
        return user_id
    
    @staticmethod
    def sanitize_specialization(specialization: str) -> str:
        """
        Sanitiza especialización profesional
        
        Args:
            specialization: Especialización del usuario
            
        Returns:
            Especialización sanitizada
            
        Raises:
            ValueError: Si la especialización es inválida
        """
        if not isinstance(specialization, str):
            raise ValueError("Specialization must be string")
        
        specialization = specialization.strip()
        
        # Permitir letras, números, espacios, guiones, puntos y algunos caracteres especiales
        if not re.match(r'^[a-zA-Z0-9\s\-\.\+#/&()]+$', specialization):
            raise ValueError("Specialization contains invalid characters")
        
        if len(specialization) < 2 or len(specialization) > 100:
            raise ValueError("Specialization must be between 2 and 100 characters")
        
        # Capitalizar primera letra de cada palabra
        specialization = ' '.join(word.capitalize() for word in specialization.split())
        
        return specialization
    
    @staticmethod
    def validate_seniority_context(seniority: str, interview_type: str) -> None:
        """
        Valida que el tipo de entrevista sea apropiado para el nivel de seniority
        
        Args:
            seniority: Nivel de seniority
            interview_type: Tipo de entrevista
            
        Raises:
            ValueError: Si la combinación no es válida
        """
        # Junior no debería hacer simulation interviews
        if seniority == 'junior' and interview_type == 'simulation':
            logger.warning(f"Junior attempting simulation interview")
            # No bloqueamos, solo loggeamos
        
        # Principal debería hacer entrevistas más avanzadas
        if seniority == 'principal' and interview_type == 'behavioral':
            logger.info(f"Principal doing basic behavioral interview")
    
    @staticmethod
    def validate_question_count_for_type(question_count: int, interview_type: str) -> None:
        """
        Valida que el número de preguntas sea apropiado para el tipo de entrevista
        
        Args:
            question_count: Número de preguntas
            interview_type: Tipo de entrevista
            
        Raises:
            ValueError: Si la combinación no es válida
        """
        # Simulation interviews deberían tener más preguntas
        if interview_type == 'simulation' and question_count < 10:
            raise ValueError("Simulation interviews should have at least 10 questions")
        
        # Behavioral interviews pueden ser más cortas
        if interview_type == 'behavioral' and question_count > 15:
            logger.info(f"Long behavioral interview requested: {question_count} questions")


class ValidationHelper:
    """Helper class for common validation patterns"""
    
    @staticmethod
    def validate_interview_state_transition(current_status: str, new_status: str) -> bool:
        """
        Valida transiciones de estado válidas para entrevistas
        
        Args:
            current_status: Estado actual
            new_status: Nuevo estado
            
        Returns:
            True si la transición es válida
        """
        valid_transitions = {
            'in_progress': ['completed'],
            'completed': [],  # No se puede cambiar desde completed
        }
        
        return new_status in valid_transitions.get(current_status, [])
    
    @staticmethod
    def validate_question_sequence(current_question_id: int, total_questions: int) -> bool:
        """
        Valida que la secuencia de preguntas sea lógica
        
        Args:
            current_question_id: ID de la pregunta actual
            total_questions: Total de preguntas
            
        Returns:
            True si la secuencia es válida
        """
        return 1 <= current_question_id <= total_questions
    
    @staticmethod
    def validate_response_completeness(questions: List[dict]) -> dict:
        """
        Valida la completitud de las respuestas en una entrevista
        
        Args:
            questions: Lista de preguntas con respuestas
            
        Returns:
            Diccionario con estadísticas de completitud
        """
        total = len(questions)
        answered = sum(1 for q in questions if q.get('answer') and q.get('answer').strip())
        
        return {
            'total_questions': total,
            'answered_questions': answered,
            'completion_rate': (answered / total * 100) if total > 0 else 0,
            'is_complete': answered == total
        }
