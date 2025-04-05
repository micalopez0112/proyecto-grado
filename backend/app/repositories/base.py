from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Optional, List

T = TypeVar('T')

class BaseRepository(ABC, Generic[T]):
    """Base abstract class for all repositories."""
    
    def __init__(self, collection):
        self.collection = collection

    @abstractmethod
    async def find_by_id(self, id: str) -> Optional[T]:
        pass

    @abstractmethod
    async def create(self, entity: T) -> str:
        pass

    @abstractmethod
    async def update(self, id: str, entity: T) -> bool:
        pass

    @abstractmethod
    async def delete(self, id: str) -> bool:
        pass
