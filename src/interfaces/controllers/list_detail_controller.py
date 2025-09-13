"""名单详情控制器"""
from __future__ import annotations
from typing import List, Optional, Dict, Any
from fastapi import HTTPException, status, Query

from src.application.handlers.list_detail_handlers import (
    ListDetailCommandHandler,
    ListDetailQueryHandler
)
from src.application.commands.list_detail_commands import (
    CreateListDetailCommand,
    UpdateListDetailCommand,
    DeleteListDetailCommand,
    ActivateListDetailCommand,
    DeactivateListDetailCommand,
    BatchCreateListDetailsCommand,
    BatchUpdateListDetailsCommand,
    CleanupDuplicatesCommand,
    ReprocessTextsCommand
)
from src.application.queries.list_detail_queries import (
    GetListDetailQuery,
    GetListDetailsQuery,
    SearchListDetailsQuery,
    GetListDetailStatisticsQuery,
    AnalyzeListDetailQualityQuery,
    AnalyzeListDetailDuplicatesQuery,
    GetOptimizationSuggestionsQuery
)
from src.application.dto.list_detail_dto import (
    ListDetailDTO,
    CreateListDetailRequest,
    UpdateListDetailRequest,
    BatchCreateListDetailsRequest,
    BatchUpdateListDetailsRequest,
    ListDetailStatisticsDTO,
    QualityAnalysisDTO,
    DuplicateAnalysisDTO,
    OptimizationSuggestionsDTO,
    BatchProcessingResultDTO
)
from src.shared.pagination import PageRequest, PageResponse, SortDirection
from src.shared.exceptions.base_exceptions import BaseException


class ListDetailController:
    """名单详情控制器"""
    
    def __init__(
        self,
        command_handler: ListDetailCommandHandler,
        query_handler: ListDetailQueryHandler
    ):
        self._command_handler = command_handler
        self._query_handler = query_handler
    
    async def create_detail(
        self,
        request: CreateListDetailRequest
    ) -> ListDetailDTO:
        """创建名单详情"""
        try:
            command = CreateListDetailCommand(
                wordlist_id=request.wordlist_id,
                original_text=request.original_text,
                processed_text=request.processed_text,
                memo=request.memo,
                created_by=request.created_by
            )
            
            return await self._command_handler.handle_create(command)
        
        except BaseException as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=e.to_dict()
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"创建名单详情失败: {str(e)}"
            )
    
    async def get_detail(self, detail_id: int) -> ListDetailDTO:
        """获取单个名单详情"""
        try:
            query = GetListDetailQuery(detail_id=detail_id)
            detail = await self._query_handler.handle_get_detail(query)
            
            if not detail:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"名单详情 {detail_id} 不存在"
                )
            
            return detail
        
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"获取名单详情失败: {str(e)}"
            )
    
    async def get_details(
        self,
        wordlist_id: Optional[int] = Query(None, description="名单ID"),
        search_text: Optional[str] = Query(None, description="搜索文本"),
        is_active: Optional[bool] = Query(None, description="是否激活"),
        include_deleted: bool = Query(False, description="是否包含已删除"),
        page: int = Query(1, ge=1, description="页码"),
        page_size: int = Query(20, ge=1, le=100, description="每页大小"),
        sort_field: str = Query("create_time", description="排序字段"),
        sort_direction: str = Query("desc", description="排序方向")
    ) -> PageResponse[ListDetailDTO]:
        """获取名单详情列表"""
        try:
            # 构建分页请求
            page_request = PageRequest(page=page, page_size=page_size)
            direction = SortDirection.DESC if sort_direction.lower() == "desc" else SortDirection.ASC
            page_request.add_sort(sort_field, direction)
            
            query = GetListDetailsQuery(
                wordlist_id=wordlist_id,
                search_text=search_text,
                is_active=is_active,
                include_deleted=include_deleted,
                page_request=page_request
            )
            
            return await self._query_handler.handle_get_details(query)
        
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"获取名单详情列表失败: {str(e)}"
            )
    
    async def search_details(
        self,
        search_text: str = Query(..., description="搜索文本"),
        wordlist_id: Optional[int] = Query(None, description="名单ID"),
        is_active: Optional[bool] = Query(True, description="是否激活"),
        page: int = Query(1, ge=1, description="页码"),
        page_size: int = Query(20, ge=1, le=100, description="每页大小")
    ) -> PageResponse[ListDetailDTO]:
        """搜索名单详情"""
        try:
            page_request = PageRequest(page=page, page_size=page_size)
            
            query = SearchListDetailsQuery(
                wordlist_id=wordlist_id,
                search_text=search_text,
                is_active=is_active,
                page_request=page_request
            )
            
            return await self._query_handler.handle_search_details(query)
        
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"搜索名单详情失败: {str(e)}"
            )
    
    async def update_detail(
        self,
        detail_id: int,
        request: UpdateListDetailRequest
    ) -> ListDetailDTO:
        """更新名单详情"""
        try:
            command = UpdateListDetailCommand(
                detail_id=detail_id,
                original_text=request.original_text,
                processed_text=request.processed_text,
                memo=request.memo,
                updated_by=request.updated_by
            )
            
            return await self._command_handler.handle_update(command)
        
        except BaseException as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=e.to_dict()
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"更新名单详情失败: {str(e)}"
            )
    
    async def delete_detail(
        self,
        detail_id: int,
        deleted_by: Optional[str] = Query(None, description="删除人")
    ) -> Dict[str, Any]:
        """删除名单详情"""
        try:
            command = DeleteListDetailCommand(
                detail_id=detail_id,
                deleted_by=deleted_by
            )
            
            success = await self._command_handler.handle_delete(command)
            
            return {
                "success": success,
                "message": "名单详情删除成功"
            }
        
        except BaseException as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=e.to_dict()
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"删除名单详情失败: {str(e)}"
            )
    
    async def activate_detail(
        self,
        detail_id: int,
        updated_by: Optional[str] = Query(None, description="更新人")
    ) -> Dict[str, Any]:
        """激活名单详情"""
        try:
            command = ActivateListDetailCommand(
                detail_id=detail_id,
                updated_by=updated_by
            )
            
            success = await self._command_handler.handle_activate(command)
            
            return {
                "success": success,
                "message": "名单详情激活成功"
            }
        
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"激活名单详情失败: {str(e)}"
            )
    
    async def deactivate_detail(
        self,
        detail_id: int,
        updated_by: Optional[str] = Query(None, description="更新人")
    ) -> Dict[str, Any]:
        """停用名单详情"""
        try:
            command = DeactivateListDetailCommand(
                detail_id=detail_id,
                updated_by=updated_by
            )
            
            success = await self._command_handler.handle_deactivate(command)
            
            return {
                "success": success,
                "message": "名单详情停用成功"
            }
        
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"停用名单详情失败: {str(e)}"
            )
    
    async def batch_create_details(
        self,
        request: BatchCreateListDetailsRequest
    ) -> BatchProcessingResultDTO:
        """批量创建名单详情"""
        try:
            command = BatchCreateListDetailsCommand(
                wordlist_id=request.wordlist_id,
                texts=request.texts,
                processing_level=request.processing_level,
                created_by=request.created_by
            )
            
            return await self._command_handler.handle_batch_create(command)
        
        except BaseException as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=e.to_dict()
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"批量创建名单详情失败: {str(e)}"
            )
    
    async def batch_update_details(
        self,
        request: BatchUpdateListDetailsRequest
    ) -> Dict[str, Any]:
        """批量更新名单详情"""
        try:
            command = BatchUpdateListDetailsCommand(
                detail_ids=request.detail_ids,
                is_active=request.is_active,
                memo=request.memo,
                updated_by=request.updated_by
            )
            
            return await self._command_handler.handle_batch_update(command)
        
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"批量更新名单详情失败: {str(e)}"
            )
    
    async def get_statistics(self, wordlist_id: int) -> ListDetailStatisticsDTO:
        """获取统计信息"""
        try:
            query = GetListDetailStatisticsQuery(wordlist_id=wordlist_id)
            return await self._query_handler.handle_get_statistics(query)
        
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"获取统计信息失败: {str(e)}"
            )
    
    async def analyze_quality(self, wordlist_id: int) -> QualityAnalysisDTO:
        """分析数据质量"""
        try:
            query = AnalyzeListDetailQualityQuery(wordlist_id=wordlist_id)
            return await self._query_handler.handle_analyze_quality(query)
        
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"分析数据质量失败: {str(e)}"
            )
    
    async def analyze_duplicates(self, wordlist_id: int) -> DuplicateAnalysisDTO:
        """分析重复内容"""
        try:
            query = AnalyzeListDetailDuplicatesQuery(wordlist_id=wordlist_id)
            return await self._query_handler.handle_analyze_duplicates(query)
        
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"分析重复内容失败: {str(e)}"
            )
    
    async def get_optimization_suggestions(
        self,
        wordlist_id: int
    ) -> OptimizationSuggestionsDTO:
        """获取优化建议"""
        try:
            query = GetOptimizationSuggestionsQuery(wordlist_id=wordlist_id)
            return await self._query_handler.handle_get_optimization_suggestions(query)
        
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"获取优化建议失败: {str(e)}"
            )
    
    async def cleanup_duplicates(
        self,
        wordlist_id: int,
        keep_strategy: str = Query("earliest", description="保留策略"),
        deleted_by: Optional[str] = Query(None, description="删除人")
    ) -> Dict[str, Any]:
        """清理重复内容"""
        try:
            command = CleanupDuplicatesCommand(
                wordlist_id=wordlist_id,
                keep_strategy=keep_strategy,
                deleted_by=deleted_by
            )
            
            return await self._command_handler.handle_cleanup_duplicates(command)
        
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"清理重复内容失败: {str(e)}"
            )
    
    async def reprocess_texts(
        self,
        wordlist_id: int,
        processing_level: str = Query("standard", description="处理级别"),
        updated_by: Optional[str] = Query(None, description="更新人")
    ) -> Dict[str, Any]:
        """重新处理文本"""
        try:
            command = ReprocessTextsCommand(
                wordlist_id=wordlist_id,
                processing_level=processing_level,
                updated_by=updated_by
            )
            
            return await self._command_handler.handle_reprocess_texts(command)
        
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"重新处理文本失败: {str(e)}"
            )