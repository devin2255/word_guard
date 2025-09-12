"""名单仓储接口"""
from abc import ABC, abstractmethod
from typing import List, Optional

from src.domain.wordlist.entities import WordList
from src.shared.enums.list_enums import ListTypeEnum, MatchRuleEnum


class WordListRepository(ABC):
    """名单仓储接口"""
    
    @abstractmethod
    async def save(self, wordlist: WordList) -> WordList:
        """保存名单"""
        pass
    
    @abstractmethod
    async def find_by_id(self, wordlist_id: int) -> Optional[WordList]:
        """根据ID查找名单"""
        pass
    
    @abstractmethod
    async def find_by_name(self, name: str) -> Optional[WordList]:
        """根据名称查找名单"""
        pass
    
    @abstractmethod
    async def find_all(self, include_deleted: bool = False) -> List[WordList]:
        """查找所有名单"""
        pass
    
    @abstractmethod
    async def find_by_type(self, list_type: ListTypeEnum, include_deleted: bool = False) -> List[WordList]:
        """根据类型查找名单"""
        pass
    
    @abstractmethod
    async def find_by_match_rule(self, match_rule: MatchRuleEnum, include_deleted: bool = False) -> List[WordList]:
        """根据匹配规则查找名单"""
        pass
    
    @abstractmethod
    async def find_active_lists(self) -> List[WordList]:
        """查找激活的名单"""
        pass
    
    @abstractmethod
    async def delete(self, wordlist_id: int) -> bool:
        """删除名单"""
        pass
    
    @abstractmethod
    async def exists_by_name(self, name: str, exclude_id: int = None) -> bool:
        """检查名称是否存在"""
        pass
    
    @abstractmethod
    async def count_by_type(self, list_type: ListTypeEnum) -> int:
        """按类型统计数量"""
        pass