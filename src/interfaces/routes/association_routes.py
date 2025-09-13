"""关联管理路由"""
from __future__ import annotations
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, Query

from src.interfaces.controllers.association_controller import AssociationController
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
from src.shared.pagination import PageResponse

# 创建路由器
router = APIRouter(prefix="/associations", tags=["associations"])


async def get_association_controller() -> AssociationController:
    """获取关联控制器"""
    from src.shared.containers import get_association_controller
    return get_association_controller()


@router.post("/", summary="创建关联", response_model=AssociationDTO)
async def create_association(
    request: CreateAssociationRequest,
    controller: AssociationController = Depends(get_association_controller)
):
    """
    创建应用-名单关联
    
    - **app_id**: 应用ID
    - **wordlist_id**: 名单ID
    - **priority**: 优先级（-100到100，数值越大优先级越高）
    - **memo**: 备注信息（可选）
    - **associated_by**: 关联操作人（可选）
    """
    return await controller.create_association(request)


@router.get("/{association_id}", summary="获取关联", response_model=AssociationDTO)
async def get_association(
    association_id: int,
    controller: AssociationController = Depends(get_association_controller)
):
    """
    根据ID获取关联
    
    - **association_id**: 关联ID
    """
    return await controller.get_association(association_id)


@router.get("/app/{app_id}/wordlist/{wordlist_id}", summary="获取应用名单关联", response_model=AssociationDTO)
async def get_association_by_app_wordlist(
    app_id: int,
    wordlist_id: int,
    controller: AssociationController = Depends(get_association_controller)
):
    """
    根据应用ID和名单ID获取关联
    
    - **app_id**: 应用ID
    - **wordlist_id**: 名单ID
    """
    return await controller.get_association_by_app_wordlist(app_id, wordlist_id)


@router.get("/", summary="获取关联列表", response_model="PageResponse[AssociationDTO]")
async def get_associations(
    app_id: Optional[int] = Query(None, description="应用ID过滤"),
    wordlist_id: Optional[int] = Query(None, description="名单ID过滤"),
    active_only: bool = Query(False, description="仅显示激活的关联"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页大小"),
    sort_field: str = Query("priority", description="排序字段"),
    sort_direction: str = Query("desc", description="排序方向（asc/desc）"),
    controller: AssociationController = Depends(get_association_controller)
):
    """
    获取关联列表（支持过滤、分页、排序）
    
    - **app_id**: 按应用ID过滤（可选）
    - **wordlist_id**: 按名单ID过滤（可选）
    - **active_only**: 仅显示激活的关联
    - **page**: 页码，从1开始
    - **page_size**: 每页大小，1-100
    - **sort_field**: 排序字段
    - **sort_direction**: 排序方向
    """
    return await controller.get_associations(
        app_id, wordlist_id, active_only, page, page_size, sort_field, sort_direction
    )


@router.get("/app/{app_id}", summary="获取应用关联", response_model="PageResponse[AssociationDTO]")
async def get_app_associations(
    app_id: int,
    active_only: bool = Query(False, description="仅显示激活的关联"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页大小"),
    controller: AssociationController = Depends(get_association_controller)
):
    """
    获取应用的所有关联
    
    - **app_id**: 应用ID
    - **active_only**: 仅显示激活的关联
    """
    return await controller.get_app_associations(app_id, active_only, page, page_size)


@router.get("/wordlist/{wordlist_id}", summary="获取名单关联", response_model="PageResponse[AssociationDTO]")
async def get_wordlist_associations(
    wordlist_id: int,
    active_only: bool = Query(False, description="仅显示激活的关联"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页大小"),
    controller: AssociationController = Depends(get_association_controller)
):
    """
    获取名单的所有关联
    
    - **wordlist_id**: 名单ID
    - **active_only**: 仅显示激活的关联
    """
    return await controller.get_wordlist_associations(wordlist_id, active_only, page, page_size)


@router.get("/priority/filter", summary="按优先级获取关联", response_model="List[AssociationDTO]")
async def get_associations_by_priority(
    app_id: Optional[int] = Query(None, description="应用ID过滤"),
    wordlist_id: Optional[int] = Query(None, description="名单ID过滤"),
    min_priority: int = Query(0, description="最小优先级"),
    active_only: bool = Query(True, description="仅显示激活的关联"),
    controller: AssociationController = Depends(get_association_controller)
):
    """
    按优先级获取关联
    
    - **app_id**: 按应用ID过滤（可选）
    - **wordlist_id**: 按名单ID过滤（可选）
    - **min_priority**: 最小优先级阈值
    - **active_only**: 仅显示激活的关联
    
    返回按优先级降序排列的关联列表
    """
    return await controller.get_associations_by_priority(
        app_id, wordlist_id, min_priority, active_only
    )


@router.put("/{association_id}", summary="更新关联", response_model=AssociationDTO)
async def update_association(
    association_id: int,
    request: UpdateAssociationRequest,
    controller: AssociationController = Depends(get_association_controller)
):
    """
    更新关联
    
    - **association_id**: 关联ID
    - **priority**: 新的优先级（可选）
    - **memo**: 新的备注（可选）
    - **is_active**: 新的激活状态（可选）
    - **updated_by**: 更新操作人（可选）
    """
    return await controller.update_association(association_id, request)


@router.delete("/{association_id}", summary="删除关联")
async def delete_association(
    association_id: int,
    deleted_by: Optional[str] = Query(None, description="删除操作人"),
    controller: AssociationController = Depends(get_association_controller)
):
    """
    删除关联（软删除）
    
    - **association_id**: 关联ID
    - **deleted_by**: 删除操作人标识
    """
    return await controller.delete_association(association_id, deleted_by)


@router.delete("/app/{app_id}/wordlist/{wordlist_id}", summary="删除应用名单关联")
async def delete_association_by_app_wordlist(
    app_id: int,
    wordlist_id: int,
    deleted_by: Optional[str] = Query(None, description="删除操作人"),
    controller: AssociationController = Depends(get_association_controller)
):
    """
    根据应用ID和名单ID删除关联
    
    - **app_id**: 应用ID
    - **wordlist_id**: 名单ID
    - **deleted_by**: 删除操作人标识
    """
    return await controller.delete_association_by_app_wordlist(app_id, wordlist_id, deleted_by)


@router.post("/{association_id}/activate", summary="激活关联")
async def activate_association(
    association_id: int,
    updated_by: Optional[str] = Query(None, description="更新操作人"),
    controller: AssociationController = Depends(get_association_controller)
):
    """
    激活关联
    
    - **association_id**: 关联ID
    - **updated_by**: 操作人标识
    """
    return await controller.activate_association(association_id, updated_by)


@router.post("/{association_id}/deactivate", summary="停用关联")
async def deactivate_association(
    association_id: int,
    updated_by: Optional[str] = Query(None, description="更新操作人"),
    controller: AssociationController = Depends(get_association_controller)
):
    """
    停用关联
    
    - **association_id**: 关联ID
    - **updated_by**: 操作人标识
    """
    return await controller.deactivate_association(association_id, updated_by)


@router.post("/batch", summary="批量创建关联", response_model=BatchOperationResultDTO)
async def batch_create_associations(
    request: BatchCreateAssociationsRequest,
    controller: AssociationController = Depends(get_association_controller)
):
    """
    批量创建关联
    
    - **app_id**: 应用ID
    - **wordlist_ids**: 名单ID列表（1-100个）
    - **default_priority**: 默认优先级
    - **memo**: 备注信息（可选）
    - **associated_by**: 关联操作人（可选）
    
    返回批量操作结果，包含成功数量、失败数量和错误详情
    """
    return await controller.batch_create_associations(request)


@router.put("/batch", summary="批量更新关联", response_model=BatchOperationResultDTO)
async def batch_update_associations(
    request: BatchUpdateAssociationsRequest,
    controller: AssociationController = Depends(get_association_controller)
):
    """
    批量更新关联
    
    - **association_ids**: 关联ID列表（1-100个）
    - **priority**: 批量设置优先级（可选）
    - **is_active**: 批量设置激活状态（可选）
    - **memo**: 批量设置备注（可选）
    - **updated_by**: 更新操作人（可选）
    
    返回批量操作结果
    """
    return await controller.batch_update_associations(request)


# 统计和分析接口
@router.get("/statistics/overview", summary="获取关联统计", response_model=AssociationStatisticsDTO)
async def get_association_statistics(
    controller: AssociationController = Depends(get_association_controller)
):
    """
    获取关联统计信息
    
    返回总关联数、激活数、优先级分布等统计数据
    """
    return await controller.get_statistics()


@router.get("/optimization/priority-suggestions", summary="获取优先级优化建议", response_model=PriorityOptimizationDTO)
async def get_priority_optimization_suggestions(
    app_id: Optional[int] = Query(None, description="应用ID过滤"),
    wordlist_id: Optional[int] = Query(None, description="名单ID过滤"),
    controller: AssociationController = Depends(get_association_controller)
):
    """
    获取优先级优化建议
    
    - **app_id**: 按应用ID过滤（可选）
    - **wordlist_id**: 按名单ID过滤（可选）
    
    返回优先级分布分析和优化建议
    """
    return await controller.get_priority_optimization_suggestions(app_id, wordlist_id)


# 验证接口
@router.get("/validation/app/{app_id}/can-delete", summary="验证应用是否可删除")
async def validate_app_deletion(
    app_id: int,
    controller: AssociationController = Depends(get_association_controller)
):
    """
    验证应用是否可以安全删除
    
    - **app_id**: 应用ID
    
    检查应用是否存在活跃关联，返回是否可以删除
    """
    return await controller.validate_app_deletion(app_id)


@router.get("/validation/wordlist/{wordlist_id}/can-delete", summary="验证名单是否可删除")
async def validate_wordlist_deletion(
    wordlist_id: int,
    controller: AssociationController = Depends(get_association_controller)
):
    """
    验证名单是否可以安全删除
    
    - **wordlist_id**: 名单ID
    
    检查名单是否存在活跃关联，返回是否可以删除
    """
    return await controller.validate_wordlist_deletion(wordlist_id)


# 维护接口
@router.post("/maintenance/cleanup-app/{app_id}", summary="清理应用关联")
async def cleanup_app_associations(
    app_id: int,
    deleted_by: Optional[str] = Query(None, description="删除操作人"),
    controller: AssociationController = Depends(get_association_controller)
):
    """
    清理应用的所有关联（软删除）
    
    - **app_id**: 应用ID
    - **deleted_by**: 删除操作人标识
    
    用于应用删除前的关联清理操作
    """
    return await controller.cleanup_app_associations(app_id, deleted_by)


@router.post("/maintenance/cleanup-wordlist/{wordlist_id}", summary="清理名单关联")
async def cleanup_wordlist_associations(
    wordlist_id: int,
    deleted_by: Optional[str] = Query(None, description="删除操作人"),
    controller: AssociationController = Depends(get_association_controller)
):
    """
    清理名单的所有关联（软删除）
    
    - **wordlist_id**: 名单ID
    - **deleted_by**: 删除操作人标识
    
    用于名单删除前的关联清理操作
    """
    return await controller.cleanup_wordlist_associations(wordlist_id, deleted_by)