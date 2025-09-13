"""应用-名单关联聚合根实体"""
from datetime import datetime
from typing import Optional
from dataclasses import dataclass

from src.shared.patterns import AggregateRoot
from src.shared.exceptions.domain_exceptions import AssociationValidationError
from src.domain.association.value_objects import AssociationPriority
from src.domain.association.events import (
    AssociationCreatedEvent,
    AssociationUpdatedEvent,
    AssociationActivatedEvent,
    AssociationDeactivatedEvent
)


@dataclass
class AppWordListAssociation(AggregateRoot):
    """应用-名单关联聚合根"""
    
    # 基本信息
    id: Optional[int] = None
    app_id: int = 0
    wordlist_id: int = 0
    
    # 关联属性
    is_active: bool = True
    priority: AssociationPriority = AssociationPriority.NORMAL
    memo: Optional[str] = None
    
    # 审计信息
    associated_at: Optional[datetime] = None
    associated_by: Optional[str] = None
    create_time: Optional[datetime] = None
    update_time: Optional[datetime] = None
    delete_time: Optional[datetime] = None
    create_by: Optional[str] = None
    update_by: Optional[str] = None
    delete_by: Optional[str] = None
    
    def __post_init__(self):
        """初始化后验证"""
        super().__init__()
        self._validate()
    
    def _validate(self) -> None:
        """验证关联数据"""
        if self.app_id <= 0:
            raise AssociationValidationError("app_id", self.app_id, "应用ID必须大于0")
        
        if self.wordlist_id <= 0:
            raise AssociationValidationError("wordlist_id", self.wordlist_id, "名单ID必须大于0")
        
        if self.memo and len(self.memo) > 200:
            raise AssociationValidationError("memo", self.memo, "备注长度不能超过200字符")
    
    @classmethod
    def create(
        cls,
        app_id: int,
        wordlist_id: int,
        priority: int = 0,
        memo: str = None,
        associated_by: str = None
    ) -> "AppWordListAssociation":
        """创建应用-名单关联"""
        
        association = cls(
            app_id=app_id,
            wordlist_id=wordlist_id,
            is_active=True,
            priority=AssociationPriority(priority),
            memo=memo,
            associated_at=datetime.now(),
            associated_by=associated_by,
            create_time=datetime.now(),
            create_by=associated_by
        )
        
        # 添加领域事件
        association.add_domain_event(AssociationCreatedEvent(association))
        
        return association
    
    def update_priority(self, new_priority: int, updated_by: str = None) -> None:
        """更新优先级"""
        old_priority = self.priority.value
        self.priority = AssociationPriority(new_priority)
        self.update_time = datetime.now()
        self.update_by = updated_by
        
        # 添加领域事件
        self.add_domain_event(AssociationUpdatedEvent(
            self, "priority", old_priority, new_priority
        ))
    
    def update_memo(self, new_memo: str, updated_by: str = None) -> None:
        """更新备注"""
        old_memo = self.memo or ""
        self.memo = new_memo
        self.update_time = datetime.now()
        self.update_by = updated_by
        
        # 添加领域事件
        self.add_domain_event(AssociationUpdatedEvent(
            self, "memo", old_memo, new_memo
        ))
    
    def activate(self, updated_by: str = None) -> None:
        """激活关联"""
        if self.is_active:
            return  # 已经激活，无需操作
        
        self.is_active = True
        self.update_time = datetime.now()
        self.update_by = updated_by
        
        # 添加领域事件
        self.add_domain_event(AssociationActivatedEvent(self))
    
    def deactivate(self, updated_by: str = None) -> None:
        """停用关联"""
        if not self.is_active:
            return  # 已经停用，无需操作
        
        self.is_active = False
        self.update_time = datetime.now()
        self.update_by = updated_by
        
        # 添加领域事件
        self.add_domain_event(AssociationDeactivatedEvent(self))
    
    def soft_delete(self, deleted_by: str = None) -> None:
        """软删除关联"""
        self.delete_time = datetime.now()
        self.delete_by = deleted_by
        self.is_active = False
    
    def is_deleted(self) -> bool:
        """是否已删除"""
        return self.delete_time is not None
    
    def can_be_used(self) -> bool:
        """关联是否可用（激活且未删除）"""
        return self.is_active and not self.is_deleted()
    
    def get_priority_score(self) -> int:
        """获取优先级分数"""
        return self.priority.value
    
    def is_higher_priority_than(self, other: "AppWordListAssociation") -> bool:
        """是否比另一个关联优先级更高"""
        return self.priority.value > other.priority.value
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "id": self.id,
            "app_id": self.app_id,
            "wordlist_id": self.wordlist_id,
            "is_active": self.is_active,
            "priority": self.priority.value,
            "memo": self.memo,
            "associated_at": self.associated_at,
            "associated_by": self.associated_by,
            "create_time": self.create_time,
            "update_time": self.update_time,
            "create_by": self.create_by,
            "update_by": self.update_by
        }