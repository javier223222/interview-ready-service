from pydantic_settings import BaseSettings
from dotenv import load_dotenv





load_dotenv()

class AppConfig(BaseSettings):
    
    gemini_api_key: str
    gemini_model: str 
    
    
    mongodb_url: str
    mongodb_db_name: str
    rabbitmq_url: str 
    
   
   
    
    
    profile_queue_name: str = "profile_updates"
    notifications_queue_name: str = "notifications"
    
    

    
    
  
    
    log_level: str = "INFO"
    
    class Config:
      
        env_file_encoding = "utf-8"

config = AppConfig()