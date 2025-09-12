"""应用相关查询"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class GetAppQuery:
    """获取单个应用查询"""
    
    app_db_id: Optional[int] = None
    app_id: Optional[str] = None


@dataclass
class GetAppsQuery:
    """获取应用列表查询"""
    
    include_deleted: bool = False