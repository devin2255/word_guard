"""分页请求"""
from dataclasses import dataclass
from typing import Optional, Dict, Any, List
from enum import Enum


class SortDirection(Enum):
    """排序方向"""
    ASC = "asc"
    DESC = "desc"


@dataclass
class SortField:
    """排序字段"""
    field: str
    direction: SortDirection = SortDirection.ASC
    
    def to_dict(self) -> Dict[str, str]:
        return {
            "field": self.field,
            "direction": self.direction.value
        }


@dataclass
class PageRequest:
    """分页请求"""
    page: int = 1
    page_size: int = 20
    sorts: List[SortField] = None
    
    def __post_init__(self):
        if self.page < 1:
            raise ValueError("页码必须大于0")
        if self.page_size < 1 or self.page_size > 1000:
            raise ValueError("每页大小必须在1-1000之间")
        if self.sorts is None:
            self.sorts = []
    
    @property
    def offset(self) -> int:
        """计算偏移量"""
        return (self.page - 1) * self.page_size
    
    @property
    def limit(self) -> int:
        """获取限制数量"""
        return self.page_size
    
    def add_sort(self, field: str, direction: SortDirection = SortDirection.ASC) -> 'PageRequest':
        """添加排序字段"""
        self.sorts.append(SortField(field, direction))
        return self
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "page": self.page,
            "page_size": self.page_size,
            "offset": self.offset,
            "limit": self.limit,
            "sorts": [sort.to_dict() for sort in self.sorts]
        }


@dataclass
class PageResponse:
    """分页响应"""
    content: List[Any]
    page: int
    page_size: int
    total_elements: int
    total_pages: int
    has_next: bool
    has_previous: bool
    
    @classmethod
    def create(
        cls, 
        content: List[Any], 
        page_request: PageRequest, 
        total_elements: int
    ) -> 'PageResponse':
        """创建分页响应"""
        total_pages = (total_elements + page_request.page_size - 1) // page_request.page_size
        has_next = page_request.page < total_pages
        has_previous = page_request.page > 1
        
        return cls(
            content=content,
            page=page_request.page,
            page_size=page_request.page_size,
            total_elements=total_elements,
            total_pages=total_pages,
            has_next=has_next,
            has_previous=has_previous
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "content": self.content,
            "pagination": {
                "page": self.page,
                "page_size": self.page_size,
                "total_elements": self.total_elements,
                "total_pages": self.total_pages,
                "has_next": self.has_next,
                "has_previous": self.has_previous
            }
        }


@dataclass
class FilterCriteria:
    """过滤条件"""
    field: str
    operator: str  # eq, ne, gt, gte, lt, lte, like, in, not_in
    value: Any
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "field": self.field,
            "operator": self.operator,
            "value": self.value
        }


@dataclass
class QueryRequest:
    """查询请求"""
    page_request: PageRequest
    filters: List[FilterCriteria] = None
    search_keyword: Optional[str] = None
    
    def __post_init__(self):
        if self.filters is None:
            self.filters = []
    
    def add_filter(
        self, 
        field: str, 
        operator: str, 
        value: Any
    ) -> 'QueryRequest':
        """添加过滤条件"""
        self.filters.append(FilterCriteria(field, operator, value))
        return self
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "page_request": self.page_request.to_dict(),
            "filters": [f.to_dict() for f in self.filters],
            "search_keyword": self.search_keyword
        }