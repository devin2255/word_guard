"""关联仓储接口"""
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import List, Optional, Set
from src.domain.association.entities import AppWordListAssociation
from src.shared.pagination import PageRequest, PageResponse


class AssociationRepository(ABC):
    """应用-名单关联仓储接口"""
    
    @abstractmethod
    async def save(self, association: AppWordListAssociation) -> AppWordListAssociation:
        """保存关联"""
        pass
    
    @abstractmethod
    async def find_by_id(self, association_id: int) -> Optional[AppWordListAssociation]:
        """根据ID查找关联"""
        pass
    
    @abstractmethod
    async def find_by_app_and_wordlist(self, app_id: int, wordlist_id: int) -> Optional[AppWordListAssociation]:
        """根据应用ID和名单ID查找关联"""
        pass
    
    @abstractmethod
    async def find_by_app_id(self, app_id: int, active_only: bool = False) -> List[AppWordListAssociation]:
        """查找应用的所有关联"""
        pass
    
    @abstractmethod
    async def find_by_wordlist_id(self, wordlist_id: int, active_only: bool = False) -> List[AppWordListAssociation]:
        """查找名单的所有关联"""
        pass
    
    @abstractmethod
    async def find_with_pagination(
        self,
        app_id: Optional[int] = None,
        wordlist_id: Optional[int] = None,
        active_only: bool = False,
        page_request: Optional[PageRequest] = None
    ) -> PageResponse[AppWordListAssociation]:
        """分页查询关联"""
        pass
    
    @abstractmethod
    async def exists(self, app_id: int, wordlist_id: int) -> bool:
        """检查关联是否存在"""
        pass
    
    @abstractmethod
    async def delete(self, association: AppWordListAssociation) -> bool:
        """删除关联"""
        pass
    
    @abstractmethod
    async def delete_by_app_id(self, app_id: int) -> int:
        """删除应用的所有关联，返回删除数量"""
        pass
    
    @abstractmethod
    async def delete_by_wordlist_id(self, wordlist_id: int) -> int:
        """删除名单的所有关联，返回删除数量"""
        pass
    
    @abstractmethod
    async def activate_batch(self, association_ids: List[int], updated_by: str = None) -> int:
        """批量激活关联，返回更新数量"""
        pass
    
    @abstractmethod
    async def deactivate_batch(self, association_ids: List[int], updated_by: str = None) -> int:
        """批量停用关联，返回更新数量"""
        pass
    
    @abstractmethod
    async def get_app_associated_wordlist_ids(self, app_id: int, active_only: bool = True) -> Set[int]:
        """获取应用关联的名单ID集合"""
        pass
    
    @abstractmethod
    async def get_wordlist_associated_app_ids(self, wordlist_id: int, active_only: bool = True) -> Set[int]:
        """获取名单关联的应用ID集合"""
        pass
    
    @abstractmethod
    async def get_association_statistics(self) -> dict:
        """获取关联统计信息"""
        pass
    
    @abstractmethod
    async def get_associations_by_priority(
        self, 
        app_id: Optional[int] = None,
        wordlist_id: Optional[int] = None,
        min_priority: int = 0,
        active_only: bool = True
    ) -> List[AppWordListAssociation]:
        """按优先级查询关联"""
        pass