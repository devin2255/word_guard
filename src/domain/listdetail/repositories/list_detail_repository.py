"""名单详情仓储接口"""
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any

from src.domain.listdetail.entities import ListDetail
from src.shared.pagination import PageRequest, PageResponse


class ListDetailRepository(ABC):
    """名单详情仓储接口"""
    
    @abstractmethod
    async def save(self, list_detail: ListDetail) -> ListDetail:
        """保存名单详情"""
        pass
    
    @abstractmethod
    async def save_batch(self, list_details: List[ListDetail]) -> List[ListDetail]:
        """批量保存名单详情"""
        pass
    
    @abstractmethod
    async def find_by_id(self, detail_id: int) -> Optional[ListDetail]:
        """根据ID查找名单详情"""
        pass
    
    @abstractmethod
    async def find_by_wordlist_id(
        self, 
        wordlist_id: int,
        include_deleted: bool = False,
        active_only: bool = True
    ) -> List[ListDetail]:
        """根据名单ID查找所有详情"""
        pass
    
    @abstractmethod
    async def find_by_wordlist_id_with_pagination(
        self,
        wordlist_id: int,
        page_request: PageRequest,
        include_deleted: bool = False,
        active_only: bool = True
    ) -> PageResponse[ListDetail]:
        """根据名单ID分页查找详情"""
        pass
    
    @abstractmethod
    async def find_by_text_hash(
        self,
        text_hash: str,
        include_deleted: bool = False
    ) -> List[ListDetail]:
        """根据文本哈希查找详情"""
        pass
    
    @abstractmethod
    async def find_by_processed_text(
        self,
        wordlist_id: int,
        processed_text: str,
        include_deleted: bool = False
    ) -> List[ListDetail]:
        """根据处理后文本查找详情"""
        pass
    
    @abstractmethod
    async def search_by_content(
        self,
        wordlist_id: int = None,
        search_text: str = None,
        page_request: PageRequest = None,
        include_deleted: bool = False,
        active_only: bool = True
    ) -> PageResponse[ListDetail]:
        """根据内容搜索详情"""
        pass
    
    @abstractmethod
    async def exists_by_text_hash(
        self,
        wordlist_id: int,
        text_hash: str,
        exclude_id: int = None
    ) -> bool:
        """检查文本哈希是否存在"""
        pass
    
    @abstractmethod
    async def count_by_wordlist_id(
        self,
        wordlist_id: int,
        active_only: bool = True
    ) -> int:
        """统计名单详情数量"""
        pass
    
    @abstractmethod
    async def get_statistics_by_wordlist_id(
        self,
        wordlist_id: int
    ) -> Dict[str, Any]:
        """获取名单详情统计信息"""
        pass
    
    @abstractmethod
    async def delete_by_wordlist_id(
        self,
        wordlist_id: int,
        deleted_by: str = None
    ) -> int:
        """根据名单ID软删除所有详情"""
        pass
    
    @abstractmethod
    async def hard_delete_by_wordlist_id(self, wordlist_id: int) -> int:
        """根据名单ID硬删除所有详情"""
        pass
    
    @abstractmethod
    async def activate_batch(
        self,
        detail_ids: List[int],
        updated_by: str = None
    ) -> int:
        """批量激活"""
        pass
    
    @abstractmethod
    async def deactivate_batch(
        self,
        detail_ids: List[int],
        updated_by: str = None
    ) -> int:
        """批量停用"""
        pass
    
    @abstractmethod
    async def find_duplicates_by_wordlist_id(
        self,
        wordlist_id: int
    ) -> List[List[ListDetail]]:
        """查找重复的名单详情（按文本哈希分组）"""
        pass
    
    @abstractmethod
    async def get_active_texts_for_matching(
        self,
        wordlist_id: int
    ) -> List[str]:
        """获取用于匹配的激活文本列表"""
        pass