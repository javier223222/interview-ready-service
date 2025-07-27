from abc import ABC
from typing import TypeVar,Generic,Optional,List
from beanie import Document
from datetime import datetime
T = TypeVar('T', bound=Document)

class BaseRepository(Generic[T], ABC):
    
    
    def __init__(self, model_class: type[T]):
        self.model_class = model_class
    
    async def create(self, entity: T) -> T:
        
        await entity.insert()
        return entity
    
    async def find_by_id(self, entity_id: str) -> Optional[T]:
        
        return await self.model_class.get(entity_id)
    
    async def find_all(self, limit: int = 100, skip: int = 0) -> List[T]:
       
        return await self.model_class.find().skip(skip).limit(limit).to_list()
    
    async def update(self, entity: T) -> T:
       
        entity.updated_at = datetime.utcnow()
        await entity.save()
        return entity
    
    async def delete_by_id(self, entity_id: str) -> bool:
        
        entity = await self.find_by_id(entity_id)
        if entity:
            await entity.delete()
            return True
        return False
    
    async def delete(self, entity: T) -> bool:
        
        await entity.delete()
        return True
    
    async def count(self) -> int:
        
        return await self.model_class.count()
    
    async def exists(self, entity_id: str) -> bool:
        
        entity = await self.find_by_id(entity_id)
        return entity is not None
