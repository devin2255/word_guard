"""关联控制器"""
from __future__ import annotations
from typing import List, Optional, Dict, Any
from fastapi import HTTPException, status, Query

from src.application.handlers.association_handlers import (
    AssociationCommandHandler,
    AssociationQueryHandler
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
    CreateAssociationRequest,
    UpdateAssociationRequest,
    BatchCreateAssociationsRequest,
    BatchUpdateAssociationsRequest,
    AssociationStatisticsDTO,
    BatchOperationResultDTO,
    PriorityOptimizationDTO
)
from src.shared.pagination import PageRequest, PageResponse, SortDirection
from src.shared.exceptions.base_exceptions import BaseException


class AssociationController:
    """关联控制器"""
    
    def __init__(
        self,
        command_handler: AssociationCommandHandler,
        query_handler: AssociationQueryHandler
    ):
        self._command_handler = command_handler
        self._query_handler = query_handler
    
    async def create_association(
        self,
        request: CreateAssociationRequest
    ) -> AssociationDTO:
        """创建关联"""
        try:
            command = CreateAssociationCommand(
                app_id=request.app_id,
                wordlist_id=request.wordlist_id,
                priority=request.priority,
                memo=request.memo,
                associated_by=request.associated_by
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
                detail=f"创建关联失败: {str(e)}"
            )
    
    async def get_association(self, association_id: int) -> AssociationDTO:
        """获取单个关联"""
        try:
            query = GetAssociationQuery(association_id=association_id)
            association = await self._query_handler.handle_get_association(query)
            
            if not association:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"关联 {association_id} 不存在"
                )
            
            return association
        
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"获取关联失败: {str(e)}"
            )
    
    async def get_association_by_app_wordlist(
        self, 
        app_id: int, 
        wordlist_id: int
    ) -> AssociationDTO:
        """根据应用和名单获取关联"""
        try:
            query = GetAssociationByAppWordlistQuery(
                app_id=app_id, 
                wordlist_id=wordlist_id
            )
            association = await self._query_handler.handle_get_association_by_app_wordlist(query)
            
            if not association:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"应用 {app_id} 与名单 {wordlist_id} 的关联不存在"
                )
            
            return association
        
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"获取关联失败: {str(e)}"
            )
    
    async def get_associations(
        self,
        app_id: Optional[int] = Query(None, description="应用ID"),
        wordlist_id: Optional[int] = Query(None, description="名单ID"),
        active_only: bool = Query(False, description="仅显示激活的关联"),
        page: int = Query(1, ge=1, description="页码"),
        page_size: int = Query(20, ge=1, le=100, description="每页大小"),
        sort_field: str = Query("priority", description="排序字段"),
        sort_direction: str = Query("desc", description="排序方向")
    ) -> PageResponse[AssociationDTO]:
        """获取关联列表"""
        try:
            # 构建分页请求
            page_request = PageRequest(page=page, page_size=page_size)
            direction = SortDirection.DESC if sort_direction.lower() == "desc" else SortDirection.ASC
            page_request.add_sort(sort_field, direction)
            
            query = GetAssociationsQuery(
                app_id=app_id,
                wordlist_id=wordlist_id,
                active_only=active_only,
                page_request=page_request
            )
            
            return await self._query_handler.handle_get_associations(query)
        
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"获取关联列表失败: {str(e)}"
            )
    
    async def get_app_associations(
        self,
        app_id: int,
        active_only: bool = Query(False, description="仅显示激活的关联"),
        page: int = Query(1, ge=1, description="页码"),
        page_size: int = Query(20, ge=1, le=100, description="每页大小")
    ) -> PageResponse[AssociationDTO]:
        """获取应用的关联"""
        try:
            page_request = PageRequest(page=page, page_size=page_size)
            
            query = GetAppAssociationsQuery(
                app_id=app_id,
                active_only=active_only,
                page_request=page_request
            )
            
            return await self._query_handler.handle_get_app_associations(query)
        
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"获取应用关联失败: {str(e)}"
            )
    
    async def get_wordlist_associations(
        self,
        wordlist_id: int,
        active_only: bool = Query(False, description="仅显示激活的关联"),
        page: int = Query(1, ge=1, description="页码"),
        page_size: int = Query(20, ge=1, le=100, description="每页大小")
    ) -> PageResponse[AssociationDTO]:
        """获取名单的关联"""
        try:
            page_request = PageRequest(page=page, page_size=page_size)
            
            query = GetWordlistAssociationsQuery(
                wordlist_id=wordlist_id,
                active_only=active_only,
                page_request=page_request
            )
            
            return await self._query_handler.handle_get_wordlist_associations(query)
        
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"获取名单关联失败: {str(e)}"
            )
    
    async def get_associations_by_priority(
        self,
        app_id: Optional[int] = Query(None, description="应用ID"),
        wordlist_id: Optional[int] = Query(None, description="名单ID"),
        min_priority: int = Query(0, description="最小优先级"),
        active_only: bool = Query(True, description="仅显示激活的关联")
    ) -> List[AssociationDTO]:
        """按优先级获取关联"""
        try:
            query = GetAssociationsByPriorityQuery(
                app_id=app_id,
                wordlist_id=wordlist_id,
                min_priority=min_priority,
                active_only=active_only
            )
            
            return await self._query_handler.handle_get_associations_by_priority(query)
        
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"按优先级获取关联失败: {str(e)}"
            )
    
    async def update_association(
        self,
        association_id: int,
        request: UpdateAssociationRequest
    ) -> AssociationDTO:
        """更新关联"""
        try:
            command = UpdateAssociationCommand(
                association_id=association_id,
                priority=request.priority,
                memo=request.memo,
                is_active=request.is_active,
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
                detail=f"更新关联失败: {str(e)}"
            )
    
    async def delete_association(
        self,
        association_id: int,
        deleted_by: Optional[str] = Query(None, description="删除人")
    ) -> Dict[str, Any]:
        """删除关联"""
        try:
            command = DeleteAssociationCommand(
                association_id=association_id,
                deleted_by=deleted_by
            )
            
            success = await self._command_handler.handle_delete(command)
            
            return {
                "success": success,
                "message": "关联删除成功"
            }
        
        except BaseException as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=e.to_dict()
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"删除关联失败: {str(e)}"
            )
    
    async def delete_association_by_app_wordlist(
        self,
        app_id: int,
        wordlist_id: int,
        deleted_by: Optional[str] = Query(None, description="删除人")
    ) -> Dict[str, Any]:
        """根据应用和名单删除关联"""
        try:
            command = DeleteAssociationByAppWordlistCommand(
                app_id=app_id,
                wordlist_id=wordlist_id,
                deleted_by=deleted_by
            )
            
            success = await self._command_handler.handle_delete_by_app_wordlist(command)
            
            return {
                "success": success,
                "message": "关联删除成功" if success else "关联不存在"
            }
        
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"删除关联失败: {str(e)}"
            )
    
    async def activate_association(
        self,
        association_id: int,
        updated_by: Optional[str] = Query(None, description="更新人")
    ) -> Dict[str, Any]:
        """激活关联"""
        try:
            command = ActivateAssociationCommand(
                association_id=association_id,
                updated_by=updated_by
            )
            
            association = await self._command_handler.handle_activate(command)
            
            return {
                "success": True,
                "message": "关联激活成功",
                "association": association.dict()
            }
        
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"激活关联失败: {str(e)}"
            )
    
    async def deactivate_association(
        self,
        association_id: int,
        updated_by: Optional[str] = Query(None, description="更新人")
    ) -> Dict[str, Any]:
        """停用关联"""
        try:
            command = DeactivateAssociationCommand(
                association_id=association_id,
                updated_by=updated_by
            )
            
            association = await self._command_handler.handle_deactivate(command)
            
            return {
                "success": True,
                "message": "关联停用成功",
                "association": association.dict()
            }
        
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"停用关联失败: {str(e)}"
            )
    
    async def batch_create_associations(
        self,
        request: BatchCreateAssociationsRequest
    ) -> BatchOperationResultDTO:
        """批量创建关联"""
        try:
            command = BatchCreateAssociationsCommand(
                app_id=request.app_id,
                wordlist_ids=request.wordlist_ids,
                default_priority=request.default_priority,
                memo=request.memo,
                associated_by=request.associated_by
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
                detail=f"批量创建关联失败: {str(e)}"
            )
    
    async def batch_update_associations(
        self,
        request: BatchUpdateAssociationsRequest
    ) -> BatchOperationResultDTO:
        """批量更新关联"""
        try:
            command = BatchUpdateAssociationsCommand(
                association_ids=request.association_ids,
                priority=request.priority,
                is_active=request.is_active,
                memo=request.memo,
                updated_by=request.updated_by
            )
            
            return await self._command_handler.handle_batch_update(command)
        
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"批量更新关联失败: {str(e)}"
            )
    
    async def get_statistics(self) -> AssociationStatisticsDTO:
        """获取关联统计信息"""
        try:
            query = GetAssociationStatisticsQuery()
            return await self._query_handler.handle_get_statistics(query)
        
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"获取统计信息失败: {str(e)}"
            )
    
    async def get_priority_optimization_suggestions(
        self,
        app_id: Optional[int] = Query(None, description="应用ID"),
        wordlist_id: Optional[int] = Query(None, description="名单ID")
    ) -> PriorityOptimizationDTO:
        """获取优先级优化建议"""
        try:
            query = GetPriorityOptimizationSuggestionsQuery(
                app_id=app_id,
                wordlist_id=wordlist_id
            )
            return await self._query_handler.handle_get_priority_optimization_suggestions(query)
        
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"获取优化建议失败: {str(e)}"
            )
    
    async def validate_app_deletion(self, app_id: int) -> Dict[str, Any]:
        """验证应用是否可以删除"""
        try:
            query = ValidateAppDeletionQuery(app_id=app_id)
            can_delete = await self._query_handler.handle_validate_app_deletion(query)
            
            return {
                "can_delete": can_delete,
                "message": "应用可以安全删除" if can_delete else "应用存在关联关系，请先解除关联"
            }
        
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"验证应用删除失败: {str(e)}"
            )
    
    async def validate_wordlist_deletion(self, wordlist_id: int) -> Dict[str, Any]:
        """验证名单是否可以删除"""
        try:
            query = ValidateWordlistDeletionQuery(wordlist_id=wordlist_id)
            can_delete = await self._query_handler.handle_validate_wordlist_deletion(query)
            
            return {
                "can_delete": can_delete,
                "message": "名单可以安全删除" if can_delete else "名单存在关联关系，请先解除关联"
            }
        
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"验证名单删除失败: {str(e)}"
            )
    
    async def cleanup_app_associations(
        self,
        app_id: int,
        deleted_by: Optional[str] = Query(None, description="删除人")
    ) -> Dict[str, Any]:
        """清理应用的所有关联"""
        try:
            command = CleanupAppAssociationsCommand(
                app_id=app_id,
                deleted_by=deleted_by
            )
            
            deleted_count = await self._command_handler.handle_cleanup_app_associations(command)
            
            return {
                "success": True,
                "deleted_count": deleted_count,
                "message": f"成功清理 {deleted_count} 个关联"
            }
        
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"清理应用关联失败: {str(e)}"
            )
    
    async def cleanup_wordlist_associations(
        self,
        wordlist_id: int,
        deleted_by: Optional[str] = Query(None, description="删除人")
    ) -> Dict[str, Any]:
        """清理名单的所有关联"""
        try:
            command = CleanupWordlistAssociationsCommand(
                wordlist_id=wordlist_id,
                deleted_by=deleted_by
            )
            
            deleted_count = await self._command_handler.handle_cleanup_wordlist_associations(command)
            
            return {
                "success": True,
                "deleted_count": deleted_count,
                "message": f"成功清理 {deleted_count} 个关联"
            }
        
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"清理名单关联失败: {str(e)}"
            )