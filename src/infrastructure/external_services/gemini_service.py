from google import genai
import os 
import logging
from typing import Optional,Dict,Any,List
import asyncio
from datetime import datetime
from infrastructure.config.app_config import config
from domain.entities.interview_ready import Question
from domain.entities.interview_ready import FeedBack
import json

import random
logger = logging.getLogger(__name__)

class GeminiService:
    def __init__(self):
        self.api_key=config.gemini_api_key
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY environment variable is not set")
        self.client=genai.Client(api_key=self.api_key)
        self.model_name=config.gemini_model
        if not self.model_name:
            raise ValueError("GEMINI_MODEL environment variable is not set")
        
        self.is_connected = False
    
    async def connect(self):
        try:
            await self.health_check()
            self.is_connected = True
            logger.info("Gemini Service conectado exitosamente")
        except Exception as e:
            logger.error(f"Error conectando a Gemini Service: {e}")
            raise

    async def health_check(self)->bool:
        try:
            response=await asyncio.to_thread(
                self.client.models.generate_content,
                model=self.model_name,
                contents="Test connection",
            )
            return response.text is not None
        except Exception as e:
            logger.info(f"Health check failed: {e}")
            return False
    
    async def generate_content(self, prompt: str, max_tokens: int = 100) -> Optional[str]:
        if not self.is_connected:
            await self.connect()
        try:
            response = await asyncio.to_thread(
                self.client.models.generate_content,
                model=self.model_name,
                contents=prompt,
                max_output_tokens=max_tokens
            )
            return response.text
        except Exception as e:
            logger.error(f"Error generating content: {e}")
            return None
        
    async def generate_questions(self, seniority: str, specialization: str, num_questions: int = 5, interview_type: str = "behavioral"):
        if not self.is_connected:
            await self.connect()
        try:
        # Mapear tipos de entrevista a descripciones específicas
            interview_types = {
            "behavioral": {
                "description": "Quick Behavioral or Introduction Questions",
                "focus": "STAR method behavioral questions focusing on past experiences, teamwork, and problem-solving situations",
                "examples": "leadership, collaboration, conflict resolution, adaptability"
            },
            "structured": {
                "description": "Structured Interview Responses", 
                "focus": "Structured behavioral questions with clear STAR framework, emphasizing measurable outcomes and specific methodologies",
                "examples": "project management, process improvement, decision-making, stakeholder management"
            },
            "technical": {
                "description": "Role-Specific or Technical Questions",
                "focus": "Technical and role-specific challenges combining behavioral aspects with technical problem-solving",
                "examples": "technical leadership, architecture decisions, code review, system design"
            },
            "simulation": {
                "description": "Full Interview Simulation",
                "focus": "Comprehensive interview simulation covering behavioral, technical, and leadership scenarios with high complexity",
                "examples": "crisis management, strategic planning, cross-functional leadership, business impact"
            }
        }
        
            interview_config = interview_types.get(interview_type, interview_types["behavioral"])
        
            response = await asyncio.to_thread(
                self.client.models.generate_content,
                model=self.model_name,
                contents=f"""
                You are a senior Human Resources professional who has run 1,000+ technical interviews for global tech companies.

                OBJECTIVE
                Generate exactly {num_questions} interview questions for a {interview_config['description']} session that follow the STAR method (Situation, Task, Action, Result).

                INTERVIEW TYPE: {interview_type.upper()}
                FOCUS: {interview_config['focus']}

                CANDIDATE CONTEXT
                - Seniority level: {seniority}
                - Specialization: {specialization}
                - Industry: Technology
                - Interview Type: {interview_config['description']}

                DESIGN RULES
                1. STAR focus – Each question must invite a STAR-structured answer.
                2. Interview type alignment – Questions must match the {interview_type} interview style:
                • behavioral = personal experiences, soft skills, team dynamics
                • structured = process-oriented, methodical approaches, clear frameworks  
                • technical = technical challenges, system design, code/architecture decisions
                • simulation = complex scenarios, multiple stakeholders, business impact
                3. Progressive difficulty –  
                • easy = straightforward, single team, clear outcome  
                • medium = cross-team, partial ambiguity, measurable impact  
                • hard = open-ended, high ambiguity, high stakes (production outage, business risk)
                4. Embed realistic, contemporary tech settings (e.g., cloud-native microservices, AI-driven products, agile at scale).  
                5. No generic fillers or duplicate wording across questions.  
                6. Target core competencies: {interview_config['examples']}
                7. Limit each `question` field to ≤ 45 words.

                DIFFICULTY DISTRIBUTION
                - {num_questions} questions total
                - If 5 questions: 2 easy, 2 medium, 1 hard
                - If 10 questions: 3 easy, 4 medium, 3 hard  
                - If 15 questions: 4 easy, 6 medium, 5 hard
                - If 30 questions: 8 easy, 12 medium, 10 hard

                OUTPUT FORMAT  
                Return only valid JSON:

                {{
                "questions": [
                    {{
                    "id": 1,
                    "question": "...",
                    "competency": "e.g., {interview_config['examples'].split(', ')[0]}",
                    "difficulty": "easy|medium|hard"
                    }}
                ]
                }}

                Think through the steps silently; print only the JSON. No extra text.
                """
              )
        
            if response and response.text:
                try:
                    json_text = response.text.strip()
                
                    if json_text.startswith('```json'):
                        json_text = json_text[7:-3]  
                    elif json_text.startswith('```'):
                        json_text = json_text[3:-3]  
                
                    questions_data = json.loads(json_text)
                    logger.info(f"Generated {interview_type} questions data: {questions_data}")
                    return questions_data

                except json.JSONDecodeError as e:
                    logger.error(f"Error parsing JSON response: {e}")
                    logger.error(f"Response text: {response.text}")
                    return None
        
            logger.warning(f"No content generated for {interview_type} interview")
            return None
        
        except Exception as e:
            logger.error(f"Error generating {interview_type} questions: {e}")
            return None
    async def generate_feedback(self, question: str,
                  user_response: str,
                  seniority: str,
                  specialization: str,
                  interview_type: str = "behavioral"):
        if not self.is_connected:
            await self.connect()
        try:
        # Map specific criteria by interview type
            feedback_criteria = {
            "behavioral": {
                "focus": "past experiences, specific situations and measurable results",
                "key_aspects": "situation clarity, actions taken, results achieved"
            },
            "structured": {
                "focus": "structured methodology, clear processes and frameworks",
                "key_aspects": "systematic thinking, stakeholder consideration, result measurement"
            },
            "technical": {
                "focus": "technical depth, trade-offs and architecture decisions",
                "key_aspects": "technical accuracy, scalability, best practices"
            },
            "simulation": {
                "focus": "comprehensive analysis, stakeholder management and strategic thinking",
                "key_aspects": "complexity handling, leadership, business impact"
            }
            }
        
            criteria = feedback_criteria.get(interview_type, feedback_criteria["behavioral"])
        
            response = await asyncio.to_thread(
                self.client.models.generate_content,
                model=self.model_name,
                contents=f"""You are an experienced interview mentor who provides constructive feedback to help professionals improve their interview performance.

OBJECTIVE
Analyze the candidate's response and provide specific, actionable feedback (≤80 words) in a personal and encouraging tone.

CONTEXT
Question: {question}
Candidate's response: {user_response}
Candidate level: {seniority} 
Specialization: {specialization}
Interview type: {interview_type}

EVALUATION CRITERIA for {interview_type} interviews:
Primary focus: {criteria['focus']}
Key evaluation aspects: {criteria['key_aspects']}

RESPONSE QUALITY ASSESSMENT
First, evaluate the response quality:
- COHERENT: Response directly addresses the question with relevant content
- PARTIALLY COHERENT: Response somewhat relates to question but lacks focus or clarity
- INCOHERENT: Response is off-topic, unclear, or doesn't address the question
- EMPTY/MINIMAL: Very short response (≤10 words) or just says "I don't know"

FEEDBACK STRATEGY by Response Type:

FOR COHERENT RESPONSES:
- Acknowledge specific strengths in their answer
- Suggest 1-2 concrete improvements (more details, metrics, structure)
- Use encouraging tone: "You demonstrated...", "Consider adding..."

FOR PARTIALLY COHERENT RESPONSES:
- Acknowledge any relevant points they made
- Guide them to focus more directly on the question
- Suggest structure improvements: "Your experience with X is valuable. To strengthen this, focus on..."

FOR INCOHERENT/OFF-TOPIC RESPONSES:
- Gently redirect without being harsh
- Provide clear guidance on what the question is asking
- Suggest approach: "This question is looking for an example of [specific situation]. Consider sharing..."

FOR EMPTY/MINIMAL RESPONSES:
- Encourage them to elaborate
- Provide framework guidance
- Be supportive: "Take your time to think of a specific example where you..."

SENIORITY-ADJUSTED EXPECTATIONS:
- Junior: Focus on learning mindset, basic examples, potential
- Mid: Expect some structured thinking, relevant examples  
- Senior: Expect clear structure, measurable impact, leadership examples
- Lead/Principal: Expect strategic thinking, organizational impact, complex scenarios

GOOD RESPONSE CRITERIA
Determine if this is a "good" response based on:
- COHERENT responses that address the question directly = true
- PARTIALLY COHERENT responses with relevant content but lacking structure = true
- INCOHERENT or OFF-TOPIC responses = false
- EMPTY/MINIMAL responses = false

FEEDBACK REQUIREMENTS:
1. Always maintain an encouraging, supportive tone
2. Provide specific, actionable suggestions
3. Keep feedback concise (≤80 words)
4. Focus on 1-2 key improvement areas
5. When possible, acknowledge something positive first

CRITICAL: Return ONLY valid JSON with this exact structure:

{{
  "feedback": "Your specific, encouraging feedback here",
  "good_question": true
}}

The "good_question" field should be:
- true: if the response is COHERENT or PARTIALLY COHERENT (shows effort and relevance)
- false: if the response is INCOHERENT, OFF-TOPIC, or EMPTY/MINIMAL

Do not include markdown formatting, code blocks, or any text outside the JSON. Analyze the response quality internally and provide appropriate feedback based on the assessment."""
                            )
        
            if response and response.text:
                try:
                    json_text = response.text.strip()
                    if json_text.startswith('```json'):
                        json_text = json_text[7:-3]  
                    elif json_text.startswith('```'):
                        json_text = json_text[3:-3]  
                
                    feedback_data = json.loads(json_text)
                    return feedback_data
                
                except json.JSONDecodeError as e:
                    logger.error(f"Error parsing JSON response: {e}")
                    logger.error(f"Response text: {response.text}")
                    return None

            return None
        
        except Exception as e:
            logger.error(f"Error generating feedback: {e}")
            return None
    async def generate_complete_feedback(self, questions: List[Question],
                  seniority: str,
                  specialization: str,
                  interview_type: str = "behavioral")-> Optional[FeedBack]:
        if not self.is_connected:
            await self.connect()
        try:
        # Map interview type to scoring criteria
            scoring_criteria = {
            "behavioral": {
                "description": "behavioral interview with STAR method focus",
                "key_competencies": "leadership, collaboration, conflict resolution, adaptability",
                "scoring_focus": "situation clarity, action specificity, measurable results"
            },
            "structured": {
                "description": "structured interview with systematic approach",
                "key_competencies": "project management, process improvement, decision-making, stakeholder management", 
                "scoring_focus": "methodology application, process thinking, outcome measurement"
            },
            "technical": {
                "description": "technical interview with role-specific challenges",
                "key_competencies": "technical leadership, architecture decisions, code review, system design",
                "scoring_focus": "technical depth, trade-offs consideration, best practices"
            },
            "simulation": {
                "description": "comprehensive interview simulation",
                "key_competencies": "crisis management, strategic planning, cross-functional leadership, business impact",
                "scoring_focus": "complexity handling, stakeholder management, strategic thinking"
            }
            }
        
            criteria = scoring_criteria.get(interview_type, scoring_criteria["behavioral"])
            questions_data = []
            for q in questions:
                questions_data.append({
                "id": q.id,
                "question": q.question,
                "answer": getattr(q, 'answer', ''),
                "feedback": getattr(q, 'feedback', ''),
                "competency": q.competency,
                "difficulty": q.difficulty
             })
        
            questions_json = json.dumps(questions_data, ensure_ascii=False)
        
            response = await asyncio.to_thread(
                self.client.models.generate_content,
                model=self.model_name,
                contents=f"""You are an experienced interview mentor providing comprehensive feedback for a {criteria['description']}.

        OBJECTIVE
        Analyze the complete interview session and provide actionable insights with a personal, encouraging tone.

        CONTEXT
        Candidate level: {seniority}
        Candidate specialization: {specialization}
        Interview type: {interview_type}
        Key competencies evaluated: {criteria['key_competencies']}
        Scoring focus: {criteria['scoring_focus']}

        SESSION DATA
        {questions_json}

        SCORING METHODOLOGY
        1. **Answer Quality Assessment** (per question):
        • Excellent response → 90 points (clear STAR structure, specific examples, measurable impact)
        • Good response → 75 points (good structure, relevant examples, some metrics)
        • Fair response → 55 points (basic structure, general examples, limited specifics)
        • Poor response → 35 points (lacks structure, vague examples, no measurable results)

        2. **Overall Score**: Average of all individual answer scores (rounded to nearest integer)

        3. **Competency Scores**: Average score per competency group

        4. **Points Earned** (based on overall performance):
        • ≥80 → 10 points (excellent performance)
        • 60-79 → 5 points (good performance) 
        • <60 → 2 points (needs improvement)

        5. **Focus Areas**: Identify up to 5 questions with scores <60 for improvement

        FEEDBACK TONE
        - Use encouraging, personal language ("You demonstrated...", "Consider strengthening...")
        - Adjust expectations for {seniority} level
        - Focus on specific, actionable improvements
        - Highlight strengths while addressing growth areas

        OUTPUT FORMAT
        Return ONLY valid JSON (no markdown, no comments):

        {{
        "overall_score": 0,
        "competency_breakdown": [
            {{
            "name": "competency_name",
            "score": 0
            }}
        ],
        "points_earned": 0,
        "focus_questions": ["question text for improvement"],
        "summary_feedback": "Personal, encouraging summary with specific recommendations"
        }}

        Analyze internally and return only the JSON."""
                )
        
            if response and response.text:
                try:
                    json_text = response.text.strip()
                    if json_text.startswith('```json'):
                        json_text = json_text[7:-3]  
                    elif json_text.startswith('```'):
                        json_text = json_text[3:-3]  

                    feedback_complete = json.loads(json_text)
                    logger.info(f"Generated complete feedback for {interview_type} interview: {feedback_complete}")
                
                    feedback_complete = FeedBack(
                        overall_score=feedback_complete.get("overall_score", 0),
                        competency_breakdown=[
                            {
                            "name": item["name"],
                            "score": item["score"]
                            } for item in feedback_complete.get("competency_breakdown", [])
                        ],
                        points_earned=feedback_complete.get("points_earned", 0),
                        focus_questions=feedback_complete.get("focus_questions", []),
                        summary_feedback=feedback_complete.get("summary_feedback", "")
                    )
                    return feedback_complete
                
                except json.JSONDecodeError as e:
                    logger.error(f"Error parsing JSON response: {e}")
                    logger.error(f"Response text: {response.text}")
                    return None

            return None
        
        except Exception as e:
            logger.error(f"Error generating complete feedback: {e}")
            return None




 
        
   