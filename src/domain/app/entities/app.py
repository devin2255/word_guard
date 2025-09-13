"""应用实体"""
from datetime import datetime
from typing import Optional, Set
from dataclasses import dataclass, field

from src.shared.exceptions import AppAlreadyExistsError


@dataclass
class App:
    """应用实体"""
    
    id: Optional[int] = None
    app_name: str = ""
    app_id: str = ""
    username: Optional[str] = None
    
    # 审计信息
    create_time: Optional[datetime] = None
    update_time: Optional[datetime] = None
    delete_time: Optional[datetime] = None
    create_by: Optional[str] = None
    update_by: Optional[str] = None
    delete_by: Optional[str] = None
    
    # 关联的名单ID集合（不持久化到数据库，用于内存中的关系管理）
    _associated_wordlist_ids: Set[int] = field(default_factory=set, init=False)
    
    def __post_init__(self):
        """初始化后验证"""
        if not self.app_name:
            raise ValueError("应用名称不能为空")
        
        if not self.app_id:
            raise ValueError("应用ID不能为空")
        
        if len(self.app_name) > 100:
            raise ValueError("应用名称长度不能超过100字符")
        
        if len(self.app_id) > 50:
            raise ValueError("应用ID长度不能超过50字符")
    
    @classmethod
    def create(
        cls, 
        app_name: str,
        app_id: str,
        username: str = None,
        created_by: str = None
    ) -> "App":
        """创建新应用"""
        
        return cls(
            app_name=app_name.strip(),
            app_id=app_id.strip(),
            username=username,
            create_time=datetime.now(),
            create_by=created_by
        )
    
    def update_name(self, new_name: str, updated_by: str = None) -> None:
        """更新应用名称"""
        self.app_name = new_name.strip()
        self.update_time = datetime.now()
        self.update_by = updated_by
    
    def update_username(self, new_username: str, updated_by: str = None) -> None:
        """更新负责人"""
        self.username = new_username
        self.update_time = datetime.now()
        self.update_by = updated_by
    
    def soft_delete(self, deleted_by: str = None) -> None:
        """软删除"""
        self.delete_time = datetime.now()
        self.delete_by = deleted_by
    
    def is_deleted(self) -> bool:
        """是否已删除"""
        return self.delete_time is not None
    
    def add_associated_wordlist(self, wordlist_id: int) -> None:
        """添加关联名单（内存操作）"""
        self._associated_wordlist_ids.add(wordlist_id)
    
    def remove_associated_wordlist(self, wordlist_id: int) -> None:
        """移除关联名单（内存操作）"""
        self._associated_wordlist_ids.discard(wordlist_id)
    
    def is_associated_with_wordlist(self, wordlist_id: int) -> bool:
        """是否与指定名单关联"""
        return wordlist_id in self._associated_wordlist_ids
    
    def get_associated_wordlist_ids(self) -> Set[int]:
        """获取关联的名单ID集合"""
        return self._associated_wordlist_ids.copy()
    
    def has_any_associations(self) -> bool:
        """是否有任何名单关联"""
        return len(self._associated_wordlist_ids) > 0
    
    def can_be_deleted(self) -> bool:
        """是否可以删除（没有名单关联时才能删除）"""
        return not self.has_any_associations() and not self.is_deleted()
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "id": self.id,
            "app_name": self.app_name,
            "app_id": self.app_id,
            "username": self.username,
            "create_time": self.create_time,
            "update_time": self.update_time,
            "create_by": self.create_by,
            "update_by": self.update_by,
        }