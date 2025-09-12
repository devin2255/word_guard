"""应用仓储接口"""
from abc import ABC, abstractmethod
from typing import List, Optional

from src.domain.app.entities import App


class AppRepository(ABC):
    """应用仓储接口"""
    
    @abstractmethod
    async def save(self, app: App) -> App:
        """保存应用"""
        pass
    
    @abstractmethod
    async def find_by_id(self, app_db_id: int) -> Optional[App]:
        """根据数据库ID查找应用"""
        pass
    
    @abstractmethod
    async def find_by_app_id(self, app_id: str) -> Optional[App]:
        """根据应用ID查找应用"""
        pass
    
    @abstractmethod
    async def find_all(self, include_deleted: bool = False) -> List[App]:
        """查找所有应用"""
        pass
    
    @abstractmethod
    async def delete(self, app_id: str) -> bool:
        """删除应用"""
        pass
    
    @abstractmethod
    async def exists_by_app_id(self, app_id: str, exclude_db_id: int = None) -> bool:
        """检查应用ID是否存在"""
        pass