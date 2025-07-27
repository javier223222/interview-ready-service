from typing import Dict, Optional, List
from domain.entities.interview_ready import InterviewReady
from domain.repositories.base_repository import BaseRepository
from datetime import datetime

class InterviewReadyRepository(BaseRepository[InterviewReady]):
    def __init__(self):
        super().__init__(InterviewReady)

    async def update(self, entity):
        return await super().update(entity)
    
    async def find_by_id(self, id: str) -> Optional[InterviewReady]:
        return await self.model_class.get(id)

    async def find_by_user_id(self, user_id: str) -> Optional[InterviewReady]:
        """Encuentra una entrevista por user_id"""
        try:
            interview = await InterviewReady.find_one(InterviewReady.userId == user_id)
            return interview
        except Exception as e:
            print(f"Error in find_by_user_id: {e}")
            raise e

    async def find_all_by_user_id(self, user_id: str, limit: int = 100, skip: int = 0,status:str="completed") -> List[Dict]:

        try:
            
            pipeline = [
                {
                    "$match": {
                        "userId": user_id,
                        "status": status
                        
                    }
                },
                {
                    "$project": {
                        "questions": 0,
                        "actual_question": 0,
                        "previus_question": 0,
                        "feedback": 0
                    }
                },
                {
                    "$sort": {"init_at": -1}
                },
                {
                    "$skip": skip
                },
                {
                    "$limit": limit
                }
            ]
            
            interviews = await InterviewReady.aggregate(pipeline).to_list()
            
            # 
            for interview in interviews:
                if "_id" in interview:
                    interview["id"] = str(interview["_id"])
                    del interview["_id"]
                
                # Convertir fechas a string si es necesario
                for date_field in ["init_at", "end_at", "updated_at"]:
                    if interview.get(date_field):
                        interview[date_field] = interview[date_field].isoformat()

            return interviews
        except Exception as e:
            print(f"Error in find_all_by_user_id: {e}")
            import traceback
            traceback.print_exc()
            raise e

    async def count_by_user_id(self, user_id: str) -> int:
        """Cuenta el total de entrevistas completadas de un usuario"""
        try:
            # Usar InterviewReady.find() directamente
            count = await InterviewReady.find(
                {
                    "userId": user_id,
                    "status": "completed"  # Cambiar a completed para consistencia
                }
            ).count()
            return count
        except Exception as e:
            print(f"Error in count_by_user_id: {e}")
            raise e