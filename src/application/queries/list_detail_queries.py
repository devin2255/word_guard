"""名单详情查询"""
from dataclasses import dataclass
from typing import Optional

from src.shared.pagination import PageRequest


@dataclass  
class GetListDetailQuery:
    """获取单个名单详情查询"""
    detail_id: int


@dataclass
class GetListDetailsQuery:
    """获取名单详情列表查询"""
    wordlist_id: Optional[int] = None
    search_text: Optional[str] = None
    is_active: Optional[bool] = None
    include_deleted: bool = False
    page_request: Optional[PageRequest] = None


@dataclass
class SearchListDetailsQuery:
    """搜索名单详情查询"""
    wordlist_id: Optional[int] = None
    search_text: Optional[str] = None
    is_active: Optional[bool] = True
    include_deleted: bool = False  
    page_request: Optional[PageRequest] = None


@dataclass
class GetListDetailStatisticsQuery:
    """获取名单详情统计查询"""
    wordlist_id: int


@dataclass
class AnalyzeListDetailQualityQuery:
    """分析名单详情质量查询"""
    wordlist_id: int


@dataclass
class AnalyzeListDetailDuplicatesQuery:
    """分析名单详情重复内容查询"""
    wordlist_id: int


@dataclass
class GetOptimizationSuggestionsQuery:
    """获取优化建议查询"""
    wordlist_id: int