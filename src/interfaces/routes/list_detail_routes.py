"""名单详情路由"""
from __future__ import annotations
from typing import Optional, Dict, Any
from fastapi import APIRouter, Depends, Query

from src.interfaces.controllers.list_detail_controller import ListDetailController
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
from src.shared.pagination import PageResponse

# 创建路由器
router = APIRouter(prefix="/list-details", tags=["list-details"])


async def get_list_detail_controller() -> ListDetailController:
    """获取名单详情控制器"""
    from src.shared.containers import get_list_detail_controller
    return get_list_detail_controller()


@router.post("/", summary="创建名单详情", response_model=ListDetailDTO)
async def create_detail(
    request: CreateListDetailRequest,
    controller: ListDetailController = Depends(get_list_detail_controller)
):
    """
    创建新的名单详情
    
    - **wordlist_id**: 名单ID
    - **original_text**: 原始文本内容
    - **processed_text**: 处理后文本（可选，为空时自动处理）
    - **memo**: 备注信息（可选）
    - **created_by**: 创建人（可选）
    """
    return await controller.create_detail(request)


@router.get("/{detail_id}", summary="获取名单详情", response_model=ListDetailDTO)
async def get_detail(
    detail_id: int,
    controller: ListDetailController = Depends(get_list_detail_controller)
):
    """
    根据ID获取名单详情
    
    - **detail_id**: 详情ID
    """
    return await controller.get_detail(detail_id)


@router.get("/", summary="获取名单详情列表", response_model="PageResponse[ListDetailDTO]")
async def get_details(
    wordlist_id: Optional[int] = Query(None, description="名单ID"),
    search_text: Optional[str] = Query(None, description="搜索文本"),
    is_active: Optional[bool] = Query(None, description="是否激活"),
    include_deleted: bool = Query(False, description="是否包含已删除"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页大小"),
    sort_field: str = Query("create_time", description="排序字段"),
    sort_direction: str = Query("desc", description="排序方向（asc/desc）"),
    controller: ListDetailController = Depends(get_list_detail_controller)
):
    """
    获取名单详情列表（支持过滤、搜索、分页、排序）
    
    - **wordlist_id**: 按名单ID过滤（可选）
    - **search_text**: 搜索文本内容（可选）
    - **is_active**: 按激活状态过滤（可选）
    - **include_deleted**: 是否包含已删除项目
    - **page**: 页码，从1开始
    - **page_size**: 每页大小，1-100
    - **sort_field**: 排序字段
    - **sort_direction**: 排序方向
    """
    return await controller.get_details(
        wordlist_id, search_text, is_active, include_deleted,
        page, page_size, sort_field, sort_direction
    )


@router.get("/search/content", summary="搜索名单详情", response_model="PageResponse[ListDetailDTO]")
async def search_details(
    search_text: str = Query(..., description="搜索文本"),
    wordlist_id: Optional[int] = Query(None, description="名单ID"),
    is_active: Optional[bool] = Query(True, description="是否激活"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页大小"),
    controller: ListDetailController = Depends(get_list_detail_controller)
):
    """
    全文搜索名单详情
    
    - **search_text**: 搜索关键词（必填）
    - **wordlist_id**: 限定名单范围（可选）
    - **is_active**: 只搜索激活项目
    """
    return await controller.search_details(search_text, wordlist_id, is_active, page, page_size)


@router.put("/{detail_id}", summary="更新名单详情", response_model=ListDetailDTO)
async def update_detail(
    detail_id: int,
    request: UpdateListDetailRequest,
    controller: ListDetailController = Depends(get_list_detail_controller)
):
    """
    更新名单详情
    
    - **detail_id**: 详情ID
    - **original_text**: 新的原始文本（可选）
    - **processed_text**: 新的处理后文本（可选）
    - **memo**: 新的备注（可选）
    - **updated_by**: 更新人（可选）
    """
    return await controller.update_detail(detail_id, request)


@router.delete("/{detail_id}", summary="删除名单详情")
async def delete_detail(
    detail_id: int,
    deleted_by: Optional[str] = Query(None, description="删除人"),
    controller: ListDetailController = Depends(get_list_detail_controller)
):
    """
    软删除名单详情
    
    - **detail_id**: 详情ID
    - **deleted_by**: 删除人标识
    """
    return await controller.delete_detail(detail_id, deleted_by)


@router.post("/{detail_id}/activate", summary="激活名单详情")
async def activate_detail(
    detail_id: int,
    updated_by: Optional[str] = Query(None, description="更新人"),
    controller: ListDetailController = Depends(get_list_detail_controller)
):
    """
    激活名单详情
    
    - **detail_id**: 详情ID
    - **updated_by**: 操作人标识
    """
    return await controller.activate_detail(detail_id, updated_by)


@router.post("/{detail_id}/deactivate", summary="停用名单详情")
async def deactivate_detail(
    detail_id: int,
    updated_by: Optional[str] = Query(None, description="更新人"),
    controller: ListDetailController = Depends(get_list_detail_controller)
):
    """
    停用名单详情
    
    - **detail_id**: 详情ID
    - **updated_by**: 操作人标识
    """
    return await controller.deactivate_detail(detail_id, updated_by)


@router.post("/batch", summary="批量创建名单详情", response_model=BatchProcessingResultDTO)
async def batch_create_details(
    request: BatchCreateListDetailsRequest,
    controller: ListDetailController = Depends(get_list_detail_controller)
):
    """
    批量创建名单详情
    
    - **wordlist_id**: 目标名单ID
    - **texts**: 文本列表（1-1000条）
    - **processing_level**: 处理级别（basic/standard/advanced/strict）
    - **created_by**: 创建人标识
    """
    return await controller.batch_create_details(request)


@router.put("/batch", summary="批量更新名单详情")
async def batch_update_details(
    request: BatchUpdateListDetailsRequest,
    controller: ListDetailController = Depends(get_list_detail_controller)
):
    """
    批量更新名单详情
    
    - **detail_ids**: 详情ID列表
    - **is_active**: 批量设置激活状态（可选）
    - **memo**: 批量设置备注（可选）
    - **updated_by**: 更新人标识
    """
    return await controller.batch_update_details(request)


# 统计分析相关接口
@router.get("/statistics/{wordlist_id}", summary="获取统计信息", response_model=ListDetailStatisticsDTO)
async def get_statistics(
    wordlist_id: int,
    controller: ListDetailController = Depends(get_list_detail_controller)
):
    """
    获取名单详情统计信息
    
    - **wordlist_id**: 名单ID
    
    返回总数、激活数、平均词数等统计数据
    """
    return await controller.get_statistics(wordlist_id)


@router.get("/analysis/quality/{wordlist_id}", summary="分析数据质量", response_model=QualityAnalysisDTO)
async def analyze_quality(
    wordlist_id: int,
    controller: ListDetailController = Depends(get_list_detail_controller)
):
    """
    分析名单详情数据质量
    
    - **wordlist_id**: 名单ID
    
    返回质量评分、问题清单、改进建议
    """
    return await controller.analyze_quality(wordlist_id)


@router.get("/analysis/duplicates/{wordlist_id}", summary="分析重复内容", response_model=DuplicateAnalysisDTO)
async def analyze_duplicates(
    wordlist_id: int,
    controller: ListDetailController = Depends(get_list_detail_controller)
):
    """
    分析名单详情中的重复内容
    
    - **wordlist_id**: 名单ID
    
    返回重复分组、重复数量、处理建议
    """
    return await controller.analyze_duplicates(wordlist_id)


@router.get("/optimization/suggestions/{wordlist_id}", summary="获取优化建议", response_model=OptimizationSuggestionsDTO)
async def get_optimization_suggestions(
    wordlist_id: int,
    controller: ListDetailController = Depends(get_list_detail_controller)
):
    """
    获取名单详情优化建议
    
    - **wordlist_id**: 名单ID
    
    返回综合分析结果和优化方案
    """
    return await controller.get_optimization_suggestions(wordlist_id)


# 批量操作接口
@router.post("/maintenance/cleanup-duplicates/{wordlist_id}", summary="清理重复内容")
async def cleanup_duplicates(
    wordlist_id: int,
    keep_strategy: str = Query("earliest", description="保留策略（earliest/latest）"),
    deleted_by: Optional[str] = Query(None, description="删除人"),
    controller: ListDetailController = Depends(get_list_detail_controller)
):
    """
    清理重复内容
    
    - **wordlist_id**: 名单ID
    - **keep_strategy**: 保留策略
      - earliest: 保留最早创建的
      - latest: 保留最晚创建的
    - **deleted_by**: 操作人标识
    """
    return await controller.cleanup_duplicates(wordlist_id, keep_strategy, deleted_by)


@router.post("/maintenance/reprocess-texts/{wordlist_id}", summary="重新处理文本")
async def reprocess_texts(
    wordlist_id: int,
    processing_level: str = Query("standard", description="处理级别（basic/standard/advanced/strict）"),
    updated_by: Optional[str] = Query(None, description="更新人"),
    controller: ListDetailController = Depends(get_list_detail_controller)
):
    """
    重新处理名单详情文本
    
    - **wordlist_id**: 名单ID
    - **processing_level**: 文本处理级别
      - basic: 基础处理
      - standard: 标准处理
      - advanced: 高级处理
      - strict: 严格处理
    - **updated_by**: 操作人标识
    """
    return await controller.reprocess_texts(wordlist_id, processing_level, updated_by)