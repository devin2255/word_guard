"""领域事件基类"""
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any


class DomainEvent(ABC):
    """领域事件基类"""
    
    def __init__(self, event_id: str = None, occurred_at: datetime = None):
        self.event_id = event_id or self._generate_event_id()
        self.occurred_at = occurred_at or datetime.now()
    
    def _generate_event_id(self) -> str:
        """生成事件ID"""
        import uuid
        return str(uuid.uuid4())
    
    @property
    @abstractmethod
    def event_name(self) -> str:
        """事件名称"""
        pass
    
    @abstractmethod
    def to_dict(self) -> dict:
        """转换为字典"""
        pass