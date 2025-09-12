"""名单相关查询"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class GetWordListQuery:
    """获取单个名单查询"""
    
    wordlist_id: int


@dataclass
class GetWordListsQuery:
    """获取名单列表查询"""
    
    list_type: Optional[int] = None
    match_rule: Optional[int] = None
    status: Optional[int] = None
    include_deleted: bool = False
    page: int = 1
    page_size: int = 20