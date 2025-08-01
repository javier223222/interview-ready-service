import logging
from motor.motor_asyncio import AsyncIOMotorClient
from infrastructure.config.app_config import config 
from beanie import init_beanie
from domain.entities.interview_ready import InterviewReady


logger = logging.getLogger(__name__)

class MongoConnection:
    def __init__(self):
        self.client = None
        self.database = None
        self.logger = logging.getLogger(__name__)
    
    async def connect(self):
        
        try:
            self.client = AsyncIOMotorClient(config.mongodb_url)
            self.database = self.client[config.mongodb_db_name]
            await init_beanie(database=self.database, document_models=[
                InterviewReady
                
            ]
                              )
            
            self.logger.info("MongoDB connection established successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to connect to MongoDB: {e}")
            raise Exception(f"Database connection failed: {e}")
    
    async def disconnect(self):
        """Cerrar conexión a MongoDB"""
        if self.client:
            self.client.close()
            self.logger.info("MongoDB connection closed")
    
    async def health_check(self) -> bool:
        """Verificar estado de la conexión"""
        try:
            await self.client.admin.command('ping')
            return True
        except Exception as e:
            self.logger.error(f"Database health check failed: {e}")
            return False


mongo_connection = MongoConnection()