"""关联查询定义"""
from dataclasses import dataclass
from typing import Optional
from src.shared.pagination import PageRequest


@dataclass
class GetAssociationQuery:
    """获取单个关联查询"""
    association_id: int


@dataclass
class GetAssociationByAppWordlistQuery:
    """根据应用和名单获取关联查询"""
    app_id: int
    wordlist_id: int


@dataclass
class GetAssociationsQuery:
    """获取关联列表查询"""
    app_id: Optional[int] = None
    wordlist_id: Optional[int] = None
    active_only: bool = False
    page_request: Optional[PageRequest] = None


@dataclass
class GetAppAssociationsQuery:
    """获取应用关联查询"""
    app_id: int
    active_only: bool = False
    page_request: Optional[PageRequest] = None


@dataclass
class GetWordlistAssociationsQuery:
    """获取名单关联查询"""
    wordlist_id: int
    active_only: bool = False
    page_request: Optional[PageRequest] = None


@dataclass
class GetAssociationsByPriorityQuery:
    """按优先级获取关联查询"""
    app_id: Optional[int] = None
    wordlist_id: Optional[int] = None
    min_priority: int = 0
    active_only: bool = True


@dataclass
class GetAssociationStatisticsQuery:
    """获取关联统计查询"""
    pass


@dataclass
class GetPriorityOptimizationSuggestionsQuery:
    """获取优先级优化建议查询"""
    app_id: Optional[int] = None
    wordlist_id: Optional[int] = None


@dataclass
class ValidateAppDeletionQuery:
    """验证应用删除查询"""
    app_id: int


@dataclass
class ValidateWordlistDeletionQuery:
    """验证名单删除查询"""
    wordlist_id: int