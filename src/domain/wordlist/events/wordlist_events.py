"""名单相关领域事件"""
from datetime import datetime
from typing import Any, TYPE_CHECKING

from src.shared.events import DomainEvent

if TYPE_CHECKING:
    from src.domain.wordlist.entities import WordList


class WordListCreatedEvent(DomainEvent):
    """名单创建事件"""
    
    def __init__(self, wordlist: "WordList", event_id: str = None, occurred_at: datetime = None):
        super().__init__(event_id, occurred_at)
        self.wordlist = wordlist
    
    @property
    def event_name(self) -> str:
        return "wordlist.created"
    
    def to_dict(self) -> dict:
        return {
            "event_id": self.event_id,
            "event_name": self.event_name,
            "occurred_at": self.occurred_at.isoformat(),
            "wordlist_id": self.wordlist.id,
            "list_name": str(self.wordlist.list_name),
            "list_type": self.wordlist.list_type.value,
            "created_by": self.wordlist.create_by
        }


class WordListUpdatedEvent(DomainEvent):
    """名单更新事件"""
    
    def __init__(self, wordlist: "WordList", field_name: str, old_value: Any, new_value: Any, 
                 event_id: str = None, occurred_at: datetime = None):
        super().__init__(event_id, occurred_at)
        self.wordlist = wordlist
        self.field_name = field_name
        self.old_value = old_value
        self.new_value = new_value
    
    @property
    def event_name(self) -> str:
        return "wordlist.updated"
    
    def to_dict(self) -> dict:
        return {
            "event_id": self.event_id,
            "event_name": self.event_name,
            "occurred_at": self.occurred_at.isoformat(),
            "wordlist_id": self.wordlist.id,
            "field_name": self.field_name,
            "old_value": self.old_value,
            "new_value": self.new_value,
            "updated_by": self.wordlist.update_by
        }


class WordListDeletedEvent(DomainEvent):
    """名单删除事件"""
    
    def __init__(self, wordlist_id: int, deleted_by: str, 
                 event_id: str = None, occurred_at: datetime = None):
        super().__init__(event_id, occurred_at)
        self.wordlist_id = wordlist_id
        self.deleted_by = deleted_by
    
    @property
    def event_name(self) -> str:
        return "wordlist.deleted"
    
    def to_dict(self) -> dict:
        return {
            "event_id": self.event_id,
            "event_name": self.event_name,
            "occurred_at": self.occurred_at.isoformat(),
            "wordlist_id": self.wordlist_id,
            "deleted_by": self.deleted_by
        }