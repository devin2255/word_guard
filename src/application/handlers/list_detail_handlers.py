"""名单详情处理器"""
from __future__ import annotations
from typing import List, Optional, Dict, Any

from src.domain.listdetail.entities import ListDetail
from src.domain.listdetail.repositories import ListDetailRepository
from src.domain.listdetail.services import ListDetailDomainService, TextProcessingService
from src.domain.listdetail.services.text_processing_service import TextProcessingLevel
from src.shared.pagination import PageRequest, PageResponse
from src.shared.exceptions.domain_exceptions import WordListNotFoundError
from src.shared.exceptions.application_exceptions import (
    CommandHandlerError,
    QueryHandlerError
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
    ListDetailStatisticsDTO,
    QualityAnalysisDTO,
    DuplicateAnalysisDTO,
    OptimizationSuggestionsDTO,
    BatchProcessingResultDTO
)


class ListDetailCommandHandler:
    """名单详情命令处理器"""
    
    def __init__(
        self,
        repository: ListDetailRepository,
        domain_service: ListDetailDomainService
    ):
        self._repository = repository
        self._domain_service = domain_service
    
    async def handle_create(self, command: CreateListDetailCommand) -> ListDetailDTO:
        """处理创建名单详情命令"""
        try:
            # 验证业务规则
            await self._domain_service.validate_new_detail(
                command.wordlist_id,
                command.original_text,
                command.processed_text
            )
            
            # 创建实体
            detail = ListDetail.create(
                wordlist_id=command.wordlist_id,
                original_text=command.original_text,
                processed_text=command.processed_text,
                memo=command.memo,
                created_by=command.created_by
            )
            
            # 保存到仓储
            saved_detail = await self._repository.save(detail)
            
            # 转换为DTO
            return ListDetailDTO(**saved_detail.to_dict())
        
        except Exception as e:
            raise CommandHandlerError(
                "ListDetailCommandHandler",
                "CreateListDetailCommand",
                str(e),
                e
            )
    
    async def handle_update(self, command: UpdateListDetailCommand) -> ListDetailDTO:
        """处理更新名单详情命令"""
        try:
            # 查找实体
            detail = await self._repository.find_by_id(command.detail_id)
            if not detail:
                raise WordListNotFoundError(command.detail_id)
            
            # 更新内容
            detail.update_content(
                original_text=command.original_text,
                processed_text=command.processed_text,
                memo=command.memo,
                updated_by=command.updated_by
            )
            
            # 保存到仓储
            saved_detail = await self._repository.save(detail)
            
            return ListDetailDTO(**saved_detail.to_dict())
        
        except Exception as e:
            raise CommandHandlerError(
                "ListDetailCommandHandler",
                "UpdateListDetailCommand",
                str(e),
                e
            )
    
    async def handle_delete(self, command: DeleteListDetailCommand) -> bool:
        """处理删除名单详情命令"""
        try:
            detail = await self._repository.find_by_id(command.detail_id)
            if not detail:
                raise WordListNotFoundError(command.detail_id)
            
            # 软删除
            detail.soft_delete(command.deleted_by)
            await self._repository.save(detail)
            
            return True
        
        except Exception as e:
            raise CommandHandlerError(
                "ListDetailCommandHandler",
                "DeleteListDetailCommand",
                str(e),
                e
            )
    
    async def handle_activate(self, command: ActivateListDetailCommand) -> bool:
        """处理激活名单详情命令"""
        try:
            detail = await self._repository.find_by_id(command.detail_id)
            if not detail:
                raise WordListNotFoundError(command.detail_id)
            
            detail.activate(command.updated_by)
            await self._repository.save(detail)
            
            return True
        
        except Exception as e:
            raise CommandHandlerError(
                "ListDetailCommandHandler",
                "ActivateListDetailCommand",
                str(e),
                e
            )
    
    async def handle_deactivate(self, command: DeactivateListDetailCommand) -> bool:
        """处理停用名单详情命令"""
        try:
            detail = await self._repository.find_by_id(command.detail_id)
            if not detail:
                raise WordListNotFoundError(command.detail_id)
            
            detail.deactivate(command.updated_by)
            await self._repository.save(detail)
            
            return True
        
        except Exception as e:
            raise CommandHandlerError(
                "ListDetailCommandHandler", 
                "DeactivateListDetailCommand",
                str(e),
                e
            )
    
    async def handle_batch_create(
        self, 
        command: BatchCreateListDetailsCommand
    ) -> BatchProcessingResultDTO:
        """处理批量创建名单详情命令"""
        try:
            # 解析处理级别
            level_map = {
                "basic": TextProcessingLevel.BASIC,
                "standard": TextProcessingLevel.STANDARD,
                "advanced": TextProcessingLevel.ADVANCED,
                "strict": TextProcessingLevel.STRICT
            }
            processing_level = level_map.get(command.processing_level, TextProcessingLevel.STANDARD)
            
            # 批量处理
            result = await self._domain_service.batch_process_texts(
                command.wordlist_id,
                command.texts,
                processing_level,
                command.created_by
            )
            
            return BatchProcessingResultDTO(
                total_count=result.total_count,
                success_count=result.success_count,
                failure_count=result.failure_count,
                duplicates_found=result.duplicates_found,
                processing_time_ms=result.processing_time_ms,
                message=f"批量创建完成：成功 {result.success_count}，失败 {result.failure_count}"
            )
        
        except Exception as e:
            raise CommandHandlerError(
                "ListDetailCommandHandler",
                "BatchCreateListDetailsCommand", 
                str(e),
                e
            )
    
    async def handle_batch_update(
        self,
        command: BatchUpdateListDetailsCommand
    ) -> Dict[str, Any]:
        """处理批量更新名单详情命令"""
        try:
            updated_count = 0
            
            if command.is_active is not None:
                if command.is_active:
                    updated_count = await self._repository.activate_batch(
                        command.detail_ids,
                        command.updated_by
                    )
                else:
                    updated_count = await self._repository.deactivate_batch(
                        command.detail_ids,
                        command.updated_by
                    )
            
            return {
                "success": True,
                "updated_count": updated_count,
                "message": f"成功更新 {updated_count} 条记录"
            }
        
        except Exception as e:
            raise CommandHandlerError(
                "ListDetailCommandHandler",
                "BatchUpdateListDetailsCommand",
                str(e),
                e
            )
    
    async def handle_cleanup_duplicates(
        self,
        command: CleanupDuplicatesCommand
    ) -> Dict[str, Any]:
        """处理清理重复内容命令"""
        try:
            result = await self._domain_service.cleanup_duplicates(
                command.wordlist_id,
                command.keep_strategy,
                command.deleted_by
            )
            
            return result
        
        except Exception as e:
            raise CommandHandlerError(
                "ListDetailCommandHandler",
                "CleanupDuplicatesCommand",
                str(e),
                e
            )
    
    async def handle_reprocess_texts(
        self,
        command: ReprocessTextsCommand
    ) -> Dict[str, Any]:
        """处理重新处理文本命令"""
        try:
            level_map = {
                "basic": TextProcessingLevel.BASIC,
                "standard": TextProcessingLevel.STANDARD,
                "advanced": TextProcessingLevel.ADVANCED,
                "strict": TextProcessingLevel.STRICT
            }
            processing_level = level_map.get(command.processing_level, TextProcessingLevel.STANDARD)
            
            result = await self._domain_service.batch_update_processing(
                command.wordlist_id,
                processing_level,
                command.updated_by
            )
            
            return result
        
        except Exception as e:
            raise CommandHandlerError(
                "ListDetailCommandHandler",
                "ReprocessTextsCommand",
                str(e),
                e
            )


class ListDetailQueryHandler:
    """名单详情查询处理器"""
    
    def __init__(
        self,
        repository: ListDetailRepository,
        domain_service: ListDetailDomainService
    ):
        self._repository = repository
        self._domain_service = domain_service
    
    async def handle_get_detail(self, query: GetListDetailQuery) -> Optional[ListDetailDTO]:
        """处理获取单个名单详情查询"""
        try:
            detail = await self._repository.find_by_id(query.detail_id)
            if not detail:
                return None
            
            return ListDetailDTO(**detail.to_dict())
        
        except Exception as e:
            raise QueryHandlerError(
                "ListDetailQueryHandler",
                "GetListDetailQuery",
                str(e),
                e
            )
    
    async def handle_get_details(
        self, 
        query: GetListDetailsQuery
    ) -> PageResponse[ListDetailDTO]:
        """处理获取名单详情列表查询"""
        try:
            page_request = query.page_request or PageRequest()
            
            if query.wordlist_id:
                result = await self._repository.find_by_wordlist_id_with_pagination(
                    query.wordlist_id,
                    page_request,
                    query.include_deleted,
                    query.is_active
                )
            else:
                result = await self._repository.search_by_content(
                    search_text=query.search_text,
                    page_request=page_request,
                    include_deleted=query.include_deleted,
                    active_only=query.is_active
                )
            
            # 转换为DTO
            dto_content = [ListDetailDTO(**detail.to_dict()) for detail in result.content]
            
            return PageResponse(
                content=dto_content,
                page=result.page,
                page_size=result.page_size,
                total_elements=result.total_elements,
                total_pages=result.total_pages,
                has_next=result.has_next,
                has_previous=result.has_previous
            )
        
        except Exception as e:
            raise QueryHandlerError(
                "ListDetailQueryHandler",
                "GetListDetailsQuery",
                str(e),
                e
            )
    
    async def handle_search_details(
        self,
        query: SearchListDetailsQuery
    ) -> PageResponse[ListDetailDTO]:
        """处理搜索名单详情查询"""
        try:
            page_request = query.page_request or PageRequest()
            
            result = await self._repository.search_by_content(
                wordlist_id=query.wordlist_id,
                search_text=query.search_text,
                page_request=page_request,
                include_deleted=query.include_deleted,
                active_only=query.is_active
            )
            
            # 转换为DTO
            dto_content = [ListDetailDTO(**detail.to_dict()) for detail in result.content]
            
            return PageResponse(
                content=dto_content,
                page=result.page,
                page_size=result.page_size,
                total_elements=result.total_elements,
                total_pages=result.total_pages,
                has_next=result.has_next,
                has_previous=result.has_previous
            )
        
        except Exception as e:
            raise QueryHandlerError(
                "ListDetailQueryHandler",
                "SearchListDetailsQuery",
                str(e),
                e
            )
    
    async def handle_get_statistics(
        self,
        query: GetListDetailStatisticsQuery
    ) -> ListDetailStatisticsDTO:
        """处理获取统计信息查询"""
        try:
            stats = await self._repository.get_statistics_by_wordlist_id(query.wordlist_id)
            return ListDetailStatisticsDTO(**stats)
        
        except Exception as e:
            raise QueryHandlerError(
                "ListDetailQueryHandler",
                "GetListDetailStatisticsQuery",
                str(e),
                e
            )
    
    async def handle_analyze_quality(
        self,
        query: AnalyzeListDetailQualityQuery
    ) -> QualityAnalysisDTO:
        """处理质量分析查询"""
        try:
            analysis = await self._domain_service.analyze_quality(query.wordlist_id)
            return QualityAnalysisDTO(
                total_items=analysis.total_items,
                active_items=analysis.active_items,
                quality_score=analysis.quality_score,
                issues=analysis.issues,
                suggestions=analysis.suggestions,
                statistics=analysis.statistics
            )
        
        except Exception as e:
            raise QueryHandlerError(
                "ListDetailQueryHandler",
                "AnalyzeListDetailQualityQuery",
                str(e),
                e
            )
    
    async def handle_analyze_duplicates(
        self,
        query: AnalyzeListDetailDuplicatesQuery
    ) -> DuplicateAnalysisDTO:
        """处理重复分析查询"""
        try:
            analysis = await self._domain_service.analyze_duplicates(query.wordlist_id)
            
            duplicate_groups_dto = None
            if analysis.duplicate_groups:
                duplicate_groups_dto = [
                    [ListDetailDTO(**detail.to_dict()) for detail in group]
                    for group in analysis.duplicate_groups
                ]
            
            return DuplicateAnalysisDTO(
                has_duplicates=analysis.has_duplicates,
                total_duplicates=analysis.total_duplicates,
                duplicate_groups_count=len(analysis.duplicate_groups),
                recommendations=analysis.recommendations,
                duplicate_groups=duplicate_groups_dto
            )
        
        except Exception as e:
            raise QueryHandlerError(
                "ListDetailQueryHandler",
                "AnalyzeListDetailDuplicatesQuery",
                str(e),
                e
            )
    
    async def handle_get_optimization_suggestions(
        self,
        query: GetOptimizationSuggestionsQuery
    ) -> OptimizationSuggestionsDTO:
        """处理获取优化建议查询"""
        try:
            suggestions = await self._domain_service.suggest_optimizations(query.wordlist_id)
            
            return OptimizationSuggestionsDTO(
                quality_analysis=QualityAnalysisDTO(**suggestions["quality_analysis"]),
                duplicate_analysis=DuplicateAnalysisDTO(**suggestions["duplicate_analysis"]),
                optimizations=suggestions["optimizations"]
            )
        
        except Exception as e:
            raise QueryHandlerError(
                "ListDetailQueryHandler",
                "GetOptimizationSuggestionsQuery",
                str(e),
                e
            )