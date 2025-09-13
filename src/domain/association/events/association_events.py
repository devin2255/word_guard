"""关联领域事件"""
from datetime import datetime
from typing import TYPE_CHECKING, Any
from dataclasses import dataclass

from src.shared.events.domain_event import DomainEvent

if TYPE_CHECKING:
    from src.domain.association.entities import AppWordListAssociation


@dataclass
class AssociationCreatedEvent(DomainEvent):
    """关联创建事件"""
    
    association: "AppWordListAssociation"
    
    def __post_init__(self):
        if not hasattr(super(), '__post_init_called__'):
            super().__post_init__()
    
    @property
    def event_data(self) -> dict[str, Any]:
        """事件数据"""
        return {
            "association_id": self.association.id,
            "app_id": self.association.app_id,
            "wordlist_id": self.association.wordlist_id,
            "priority": self.association.priority.value,
            "associated_by": self.association.associated_by
        }


@dataclass  
class AssociationUpdatedEvent(DomainEvent):
    """关联更新事件"""
    
    association: "AppWordListAssociation"
    field_name: str
    old_value: Any
    new_value: Any
    
    def __post_init__(self):
        if not hasattr(super(), '__post_init_called__'):
            super().__post_init__()
    
    @property
    def event_data(self) -> dict[str, Any]:
        """事件数据"""
        return {
            "association_id": self.association.id,
            "app_id": self.association.app_id,
            "wordlist_id": self.association.wordlist_id,
            "field_name": self.field_name,
            "old_value": self.old_value,
            "new_value": self.new_value,
            "updated_by": self.association.update_by
        }


@dataclass
class AssociationActivatedEvent(DomainEvent):
    """关联激活事件"""
    
    association: "AppWordListAssociation"
    
    def __post_init__(self):
        if not hasattr(super(), '__post_init_called__'):
            super().__post_init__()
    
    @property
    def event_data(self) -> dict[str, Any]:
        """事件数据"""
        return {
            "association_id": self.association.id,
            "app_id": self.association.app_id,
            "wordlist_id": self.association.wordlist_id,
            "activated_by": self.association.update_by
        }


@dataclass
class AssociationDeactivatedEvent(DomainEvent):
    """关联停用事件"""
    
    association: "AppWordListAssociation"
    
    def __post_init__(self):
        if not hasattr(super(), '__post_init_called__'):
            super().__post_init__()
    
    @property
    def event_data(self) -> dict[str, Any]:
        """事件数据"""
        return {
            "association_id": self.association.id,
            "app_id": self.association.app_id,
            "wordlist_id": self.association.wordlist_id,
            "deactivated_by": self.association.update_by
        }