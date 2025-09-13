"""关联处理器"""
from __future__ import annotations
from typing import List, Optional, Dict, Any

from src.domain.association.entities import AppWordListAssociation
from src.domain.association.repositories import AssociationRepository
from src.domain.association.services import AssociationDomainService
from src.shared.pagination import PageRequest, PageResponse
from src.shared.exceptions.application_exceptions import (
    CommandHandlerError,
    QueryHandlerError
)
from src.application.commands.association_commands import (
    CreateAssociationCommand,
    UpdateAssociationCommand,
    DeleteAssociationCommand,
    DeleteAssociationByAppWordlistCommand,
    BatchCreateAssociationsCommand,
    BatchUpdateAssociationsCommand,
    ActivateAssociationCommand,
    DeactivateAssociationCommand,
    CleanupAppAssociationsCommand,
    CleanupWordlistAssociationsCommand
)
from src.application.queries.association_queries import (
    GetAssociationQuery,
    GetAssociationByAppWordlistQuery,
    GetAssociationsQuery,
    GetAppAssociationsQuery,
    GetWordlistAssociationsQuery,
    GetAssociationsByPriorityQuery,
    GetAssociationStatisticsQuery,
    GetPriorityOptimizationSuggestionsQuery,
    ValidateAppDeletionQuery,
    ValidateWordlistDeletionQuery
)
from src.application.dto.association_dto import (
    AssociationDTO,
    AssociationStatisticsDTO,
    BatchOperationResultDTO,
    PriorityOptimizationDTO
)


class AssociationCommandHandler:
    """关联命令处理器"""
    
    def __init__(
        self,
        repository: AssociationRepository,
        domain_service: AssociationDomainService
    ):
        self._repository = repository
        self._domain_service = domain_service
    
    async def handle_create(self, command: CreateAssociationCommand) -> AssociationDTO:
        """处理创建关联命令"""
        try:
            association = await self._domain_service.create_association(
                app_id=command.app_id,
                wordlist_id=command.wordlist_id,
                priority=command.priority,
                memo=command.memo,
                associated_by=command.associated_by
            )
            
            return AssociationDTO(**association.to_dict())
        
        except Exception as e:
            raise CommandHandlerError(
                "AssociationCommandHandler",
                "CreateAssociationCommand",
                str(e),
                e
            )
    
    async def handle_update(self, command: UpdateAssociationCommand) -> AssociationDTO:
        """处理更新关联命令"""
        try:
            association = await self._domain_service.update_association(
                association_id=command.association_id,
                priority=command.priority,
                memo=command.memo,
                is_active=command.is_active,
                updated_by=command.updated_by
            )
            
            return AssociationDTO(**association.to_dict())
        
        except Exception as e:
            raise CommandHandlerError(
                "AssociationCommandHandler",
                "UpdateAssociationCommand",
                str(e),
                e
            )
    
    async def handle_delete(self, command: DeleteAssociationCommand) -> bool:
        """处理删除关联命令"""
        try:
            return await self._domain_service.delete_association(
                association_id=command.association_id,
                deleted_by=command.deleted_by
            )
        
        except Exception as e:
            raise CommandHandlerError(
                "AssociationCommandHandler",
                "DeleteAssociationCommand",
                str(e),
                e
            )
    
    async def handle_delete_by_app_wordlist(
        self, 
        command: DeleteAssociationByAppWordlistCommand
    ) -> bool:
        """处理根据应用和名单删除关联命令"""
        try:
            return await self._domain_service.delete_association_by_app_and_wordlist(
                app_id=command.app_id,
                wordlist_id=command.wordlist_id,
                deleted_by=command.deleted_by
            )
        
        except Exception as e:
            raise CommandHandlerError(
                "AssociationCommandHandler",
                "DeleteAssociationByAppWordlistCommand",
                str(e),
                e
            )
    
    async def handle_batch_create(
        self, 
        command: BatchCreateAssociationsCommand
    ) -> BatchOperationResultDTO:
        """处理批量创建关联命令"""
        try:
            result = await self._domain_service.batch_create_associations(
                app_id=command.app_id,
                wordlist_ids=command.wordlist_ids,
                default_priority=command.default_priority,
                memo=command.memo,
                associated_by=command.associated_by
            )
            
            return BatchOperationResultDTO(**result)
        
        except Exception as e:
            raise CommandHandlerError(
                "AssociationCommandHandler",
                "BatchCreateAssociationsCommand",
                str(e),
                e
            )
    
    async def handle_batch_update(
        self, 
        command: BatchUpdateAssociationsCommand
    ) -> BatchOperationResultDTO:
        """处理批量更新关联命令"""
        try:
            result = await self._domain_service.batch_update_associations(
                association_ids=command.association_ids,
                priority=command.priority,
                is_active=command.is_active,
                memo=command.memo,
                updated_by=command.updated_by
            )
            
            return BatchOperationResultDTO(**result)
        
        except Exception as e:
            raise CommandHandlerError(
                "AssociationCommandHandler",
                "BatchUpdateAssociationsCommand",
                str(e),
                e
            )
    
    async def handle_activate(self, command: ActivateAssociationCommand) -> AssociationDTO:
        """处理激活关联命令"""
        try:
            association = await self._domain_service.update_association(
                association_id=command.association_id,
                is_active=True,
                updated_by=command.updated_by
            )
            
            return AssociationDTO(**association.to_dict())
        
        except Exception as e:
            raise CommandHandlerError(
                "AssociationCommandHandler",
                "ActivateAssociationCommand",
                str(e),
                e
            )
    
    async def handle_deactivate(self, command: DeactivateAssociationCommand) -> AssociationDTO:
        """处理停用关联命令"""
        try:
            association = await self._domain_service.update_association(
                association_id=command.association_id,
                is_active=False,
                updated_by=command.updated_by
            )
            
            return AssociationDTO(**association.to_dict())
        
        except Exception as e:
            raise CommandHandlerError(
                "AssociationCommandHandler",
                "DeactivateAssociationCommand",
                str(e),
                e
            )
    
    async def handle_cleanup_app_associations(
        self, 
        command: CleanupAppAssociationsCommand
    ) -> int:
        """处理清理应用关联命令"""
        try:
            return await self._domain_service.cleanup_app_associations(
                app_id=command.app_id,
                deleted_by=command.deleted_by
            )
        
        except Exception as e:
            raise CommandHandlerError(
                "AssociationCommandHandler",
                "CleanupAppAssociationsCommand",
                str(e),
                e
            )
    
    async def handle_cleanup_wordlist_associations(
        self, 
        command: CleanupWordlistAssociationsCommand
    ) -> int:
        """处理清理名单关联命令"""
        try:
            return await self._domain_service.cleanup_wordlist_associations(
                wordlist_id=command.wordlist_id,
                deleted_by=command.deleted_by
            )
        
        except Exception as e:
            raise CommandHandlerError(
                "AssociationCommandHandler",
                "CleanupWordlistAssociationsCommand",
                str(e),
                e
            )


class AssociationQueryHandler:
    """关联查询处理器"""
    
    def __init__(
        self,
        repository: AssociationRepository,
        domain_service: AssociationDomainService
    ):
        self._repository = repository
        self._domain_service = domain_service
    
    async def handle_get_association(self, query: GetAssociationQuery) -> Optional[AssociationDTO]:
        """处理获取单个关联查询"""
        try:
            association = await self._repository.find_by_id(query.association_id)
            if not association:
                return None
            
            return AssociationDTO(**association.to_dict())
        
        except Exception as e:
            raise QueryHandlerError(
                "AssociationQueryHandler",
                "GetAssociationQuery",
                str(e),
                e
            )
    
    async def handle_get_association_by_app_wordlist(
        self, 
        query: GetAssociationByAppWordlistQuery
    ) -> Optional[AssociationDTO]:
        """处理根据应用和名单获取关联查询"""
        try:
            association = await self._repository.find_by_app_and_wordlist(
                query.app_id, query.wordlist_id
            )
            if not association:
                return None
            
            return AssociationDTO(**association.to_dict())
        
        except Exception as e:
            raise QueryHandlerError(
                "AssociationQueryHandler",
                "GetAssociationByAppWordlistQuery",
                str(e),
                e
            )
    
    async def handle_get_associations(
        self, 
        query: GetAssociationsQuery
    ) -> PageResponse[AssociationDTO]:
        """处理获取关联列表查询"""
        try:
            page_request = query.page_request or PageRequest()
            
            result = await self._repository.find_with_pagination(
                app_id=query.app_id,
                wordlist_id=query.wordlist_id,
                active_only=query.active_only,
                page_request=page_request
            )
            
            # 转换为DTO
            dto_content = [AssociationDTO(**association.to_dict()) for association in result.content]
            
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
                "AssociationQueryHandler",
                "GetAssociationsQuery",
                str(e),
                e
            )
    
    async def handle_get_app_associations(
        self, 
        query: GetAppAssociationsQuery
    ) -> PageResponse[AssociationDTO]:
        """处理获取应用关联查询"""
        try:
            result = await self._domain_service.get_app_associations(
                app_id=query.app_id,
                active_only=query.active_only,
                page_request=query.page_request
            )
            
            # 转换为DTO
            dto_content = [AssociationDTO(**association.to_dict()) for association in result.content]
            
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
                "AssociationQueryHandler",
                "GetAppAssociationsQuery",
                str(e),
                e
            )
    
    async def handle_get_wordlist_associations(
        self, 
        query: GetWordlistAssociationsQuery
    ) -> PageResponse[AssociationDTO]:
        """处理获取名单关联查询"""
        try:
            result = await self._domain_service.get_wordlist_associations(
                wordlist_id=query.wordlist_id,
                active_only=query.active_only,
                page_request=query.page_request
            )
            
            # 转换为DTO
            dto_content = [AssociationDTO(**association.to_dict()) for association in result.content]
            
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
                "AssociationQueryHandler",
                "GetWordlistAssociationsQuery",
                str(e),
                e
            )
    
    async def handle_get_associations_by_priority(
        self, 
        query: GetAssociationsByPriorityQuery
    ) -> List[AssociationDTO]:
        """处理按优先级获取关联查询"""
        try:
            associations = await self._domain_service.get_associations_by_priority(
                app_id=query.app_id,
                wordlist_id=query.wordlist_id,
                min_priority=query.min_priority,
                active_only=query.active_only
            )
            
            return [AssociationDTO(**association.to_dict()) for association in associations]
        
        except Exception as e:
            raise QueryHandlerError(
                "AssociationQueryHandler",
                "GetAssociationsByPriorityQuery",
                str(e),
                e
            )
    
    async def handle_get_statistics(
        self, 
        query: GetAssociationStatisticsQuery
    ) -> AssociationStatisticsDTO:
        """处理获取关联统计查询"""
        try:
            stats = await self._domain_service.get_association_statistics()
            return AssociationStatisticsDTO(**stats)
        
        except Exception as e:
            raise QueryHandlerError(
                "AssociationQueryHandler",
                "GetAssociationStatisticsQuery",
                str(e),
                e
            )
    
    async def handle_get_priority_optimization_suggestions(
        self, 
        query: GetPriorityOptimizationSuggestionsQuery
    ) -> PriorityOptimizationDTO:
        """处理获取优先级优化建议查询"""
        try:
            suggestions = await self._domain_service.suggest_priority_optimization(
                app_id=query.app_id,
                wordlist_id=query.wordlist_id
            )
            return PriorityOptimizationDTO(**suggestions)
        
        except Exception as e:
            raise QueryHandlerError(
                "AssociationQueryHandler",
                "GetPriorityOptimizationSuggestionsQuery",
                str(e),
                e
            )
    
    async def handle_validate_app_deletion(self, query: ValidateAppDeletionQuery) -> bool:
        """处理验证应用删除查询"""
        try:
            return await self._domain_service.validate_association_before_delete_app(query.app_id)
        
        except Exception as e:
            raise QueryHandlerError(
                "AssociationQueryHandler",
                "ValidateAppDeletionQuery",
                str(e),
                e
            )
    
    async def handle_validate_wordlist_deletion(self, query: ValidateWordlistDeletionQuery) -> bool:
        """处理验证名单删除查询"""
        try:
            return await self._domain_service.validate_association_before_delete_wordlist(query.wordlist_id)
        
        except Exception as e:
            raise QueryHandlerError(
                "AssociationQueryHandler",
                "ValidateWordlistDeletionQuery",
                str(e),
                e
            )