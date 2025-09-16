"""敏感词检查日志仓储接口"""
from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional, Dict, Any

from src.domain.moderation.entities.moderation_log import ModerationLog


class ModerationLogRepository(ABC):
    """敏感词检查日志仓储接口"""
    
    @abstractmethod
    async def save(self, log: ModerationLog) -> ModerationLog:
        """保存日志"""
        pass
    
    @abstractmethod
    async def find_by_id(self, log_id: int) -> Optional[ModerationLog]:
        """根据ID查找日志"""
        pass
    
    @abstractmethod
    async def find_by_request_id(self, request_id: str) -> Optional[ModerationLog]:
        """根据请求ID查找日志"""
        pass
    
    @abstractmethod
    async def find_by_user_id(
        self, 
        user_id: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100
    ) -> List[ModerationLog]:
        """根据用户ID查找日志"""
        pass
    
    @abstractmethod
    async def find_by_app_id(
        self,
        app_id: int,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100
    ) -> List[ModerationLog]:
        """根据应用ID查找日志"""
        pass
    
    @abstractmethod
    async def find_violations(
        self,
        app_id: Optional[int] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100
    ) -> List[ModerationLog]:
        """查找违规记录"""
        pass
    
    @abstractmethod
    async def get_statistics(
        self,
        app_id: Optional[int] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """获取统计信息"""
        pass
    
    @abstractmethod
    async def count_by_conditions(
        self,
        app_id: Optional[int] = None,
        user_id: Optional[str] = None,
        is_violation: Optional[bool] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> int:
        """根据条件统计数量"""
        pass
    
    @abstractmethod
    async def delete_old_logs(self, days: int) -> int:
        """删除旧日志"""
        pass