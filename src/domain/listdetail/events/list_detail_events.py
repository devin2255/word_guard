"""名单详情领域事件"""
from dataclasses import dataclass
from typing import List, Any
from src.shared.events.domain_event import DomainEvent


@dataclass
class ListDetailCreatedEvent(DomainEvent):
    """名单详情创建事件"""
    
    detail: Any  # ListDetail实体
    
    def __post_init__(self):
        super().__init__()
        self.event_type = "ListDetailCreated"


@dataclass  
class ListDetailUpdatedEvent(DomainEvent):
    """名单详情更新事件"""
    
    detail: Any  # ListDetail实体
    field_name: str
    old_value: Any
    new_value: Any
    
    def __post_init__(self):
        super().__init__()
        self.event_type = "ListDetailUpdated"


@dataclass
class ListDetailActivatedEvent(DomainEvent):
    """名单详情激活事件"""
    
    detail: Any  # ListDetail实体
    
    def __post_init__(self):
        super().__init__()
        self.event_type = "ListDetailActivated"


@dataclass
class ListDetailDeactivatedEvent(DomainEvent):
    """名单详情停用事件"""
    
    detail: Any  # ListDetail实体
    
    def __post_init__(self):
        super().__init__()
        self.event_type = "ListDetailDeactivated"


@dataclass
class ListDetailBatchProcessedEvent(DomainEvent):
    """名单详情批量处理事件"""
    
    wordlist_id: int
    processed_count: int
    success_count: int
    failure_count: int
    details: List[Any]  # ListDetail实体列表
    
    def __post_init__(self):
        super().__init__()
        self.event_type = "ListDetailBatchProcessed"