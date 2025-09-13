"""查询构建器"""
from typing import Any, Dict, List, Optional, Tuple
from tortoise.queryset import QuerySet
from tortoise.models import Model
from tortoise.expressions import Q

from .page_request import PageRequest, QueryRequest, FilterCriteria, SortDirection


class TortoiseQueryBuilder:
    """Tortoise ORM 查询构建器"""
    
    @staticmethod
    def build_filter_query(
        queryset: QuerySet, 
        filters: List[FilterCriteria]
    ) -> QuerySet:
        """构建过滤查询"""
        
        for filter_criteria in filters:
            field = filter_criteria.field
            operator = filter_criteria.operator
            value = filter_criteria.value
            
            # 构建查询条件
            if operator == "eq":
                queryset = queryset.filter(**{field: value})
            elif operator == "ne":
                queryset = queryset.exclude(**{field: value})
            elif operator == "gt":
                queryset = queryset.filter(**{f"{field}__gt": value})
            elif operator == "gte":
                queryset = queryset.filter(**{f"{field}__gte": value})
            elif operator == "lt":
                queryset = queryset.filter(**{f"{field}__lt": value})
            elif operator == "lte":
                queryset = queryset.filter(**{f"{field}__lte": value})
            elif operator == "like":
                queryset = queryset.filter(**{f"{field}__icontains": value})
            elif operator == "in":
                if isinstance(value, (list, tuple)):
                    queryset = queryset.filter(**{f"{field}__in": value})
            elif operator == "not_in":
                if isinstance(value, (list, tuple)):
                    queryset = queryset.exclude(**{f"{field}__in": value})
            elif operator == "is_null":
                queryset = queryset.filter(**{f"{field}__isnull": True})
            elif operator == "is_not_null":
                queryset = queryset.filter(**{f"{field}__isnull": False})
            elif operator == "starts_with":
                queryset = queryset.filter(**{f"{field}__startswith": value})
            elif operator == "ends_with":
                queryset = queryset.filter(**{f"{field}__endswith": value})
        
        return queryset
    
    @staticmethod
    def build_search_query(
        queryset: QuerySet,
        search_fields: List[str],
        search_keyword: str
    ) -> QuerySet:
        """构建搜索查询"""
        if not search_keyword or not search_fields:
            return queryset
        
        # 使用Q对象进行OR查询
        search_query = Q()
        for field in search_fields:
            search_query |= Q(**{f"{field}__icontains": search_keyword})
        
        return queryset.filter(search_query)
    
    @staticmethod
    def build_sort_query(
        queryset: QuerySet,
        page_request: PageRequest
    ) -> QuerySet:
        """构建排序查询"""
        if not page_request.sorts:
            return queryset
        
        order_by_fields = []
        for sort_field in page_request.sorts:
            field = sort_field.field
            if sort_field.direction == SortDirection.DESC:
                field = f"-{field}"
            order_by_fields.append(field)
        
        return queryset.order_by(*order_by_fields)
    
    @staticmethod
    def build_pagination_query(
        queryset: QuerySet,
        page_request: PageRequest
    ) -> QuerySet:
        """构建分页查询"""
        return queryset.offset(page_request.offset).limit(page_request.limit)
    
    @staticmethod
    async def execute_query_with_pagination(
        queryset: QuerySet,
        query_request: QueryRequest,
        search_fields: List[str] = None
    ) -> Tuple[List[Model], int]:
        """执行带分页的查询"""
        
        # 应用过滤条件
        if query_request.filters:
            queryset = TortoiseQueryBuilder.build_filter_query(
                queryset, 
                query_request.filters
            )
        
        # 应用搜索条件
        if query_request.search_keyword and search_fields:
            queryset = TortoiseQueryBuilder.build_search_query(
                queryset,
                search_fields,
                query_request.search_keyword
            )
        
        # 获取总数（在分页和排序之前）
        total_count = await queryset.count()
        
        # 应用排序
        queryset = TortoiseQueryBuilder.build_sort_query(
            queryset,
            query_request.page_request
        )
        
        # 应用分页
        queryset = TortoiseQueryBuilder.build_pagination_query(
            queryset,
            query_request.page_request
        )
        
        # 执行查询
        results = await queryset
        
        return results, total_count


class QueryOptimizer:
    """查询优化器"""
    
    @staticmethod
    def optimize_select_related(
        queryset: QuerySet,
        related_fields: List[str]
    ) -> QuerySet:
        """优化关联查询"""
        if related_fields:
            return queryset.select_related(*related_fields)
        return queryset
    
    @staticmethod
    def optimize_prefetch_related(
        queryset: QuerySet,
        prefetch_fields: List[str]
    ) -> QuerySet:
        """优化预取查询"""
        if prefetch_fields:
            return queryset.prefetch_related(*prefetch_fields)
        return queryset
    
    @staticmethod
    def optimize_only_fields(
        queryset: QuerySet,
        only_fields: List[str]
    ) -> QuerySet:
        """只查询指定字段"""
        if only_fields:
            return queryset.only(*only_fields)
        return queryset
    
    @staticmethod
    def optimize_defer_fields(
        queryset: QuerySet,
        defer_fields: List[str]
    ) -> QuerySet:
        """延迟加载指定字段"""
        if defer_fields:
            return queryset.defer(*defer_fields)
        return queryset