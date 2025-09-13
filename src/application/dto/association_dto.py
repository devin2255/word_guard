"""关联数据传输对象"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class AssociationDTO(BaseModel):
    """关联DTO"""
    id: Optional[int] = None
    app_id: int
    wordlist_id: int
    is_active: bool = True
    priority: int = 0
    memo: Optional[str] = None
    associated_at: Optional[datetime] = None
    associated_by: Optional[str] = None
    create_time: Optional[datetime] = None
    update_time: Optional[datetime] = None
    create_by: Optional[str] = None
    update_by: Optional[str] = None


class CreateAssociationRequest(BaseModel):
    """创建关联请求"""
    app_id: int = Field(..., description="应用ID")
    wordlist_id: int = Field(..., description="名单ID")
    priority: int = Field(0, ge=-100, le=100, description="优先级（-100到100）")
    memo: Optional[str] = Field(None, max_length=200, description="备注")
    associated_by: Optional[str] = Field(None, description="关联操作人")


class UpdateAssociationRequest(BaseModel):
    """更新关联请求"""
    priority: Optional[int] = Field(None, ge=-100, le=100, description="优先级（-100到100）")
    memo: Optional[str] = Field(None, max_length=200, description="备注")
    is_active: Optional[bool] = Field(None, description="是否激活")
    updated_by: Optional[str] = Field(None, description="更新操作人")


class BatchCreateAssociationsRequest(BaseModel):
    """批量创建关联请求"""
    app_id: int = Field(..., description="应用ID")
    wordlist_ids: List[int] = Field(..., min_items=1, max_items=100, description="名单ID列表")
    default_priority: int = Field(0, ge=-100, le=100, description="默认优先级")
    memo: Optional[str] = Field(None, max_length=200, description="备注")
    associated_by: Optional[str] = Field(None, description="关联操作人")


class BatchUpdateAssociationsRequest(BaseModel):
    """批量更新关联请求"""
    association_ids: List[int] = Field(..., min_items=1, max_items=100, description="关联ID列表")
    priority: Optional[int] = Field(None, ge=-100, le=100, description="优先级")
    is_active: Optional[bool] = Field(None, description="是否激活")
    memo: Optional[str] = Field(None, max_length=200, description="备注")
    updated_by: Optional[str] = Field(None, description="更新操作人")


class AssociationStatisticsDTO(BaseModel):
    """关联统计DTO"""
    total_associations: int
    active_associations: int
    inactive_associations: int
    priority_distribution: List[Dict[str, Any]]
    priority_analysis: Dict[str, int]


class BatchOperationResultDTO(BaseModel):
    """批量操作结果DTO"""
    total_count: int
    success_count: int
    failure_count: int
    created_associations: Optional[List[AssociationDTO]] = None
    errors: List[Dict[str, Any]]


class PriorityOptimizationDTO(BaseModel):
    """优先级优化建议DTO"""
    total_associations: int
    priority_distribution: Dict[str, int]
    unique_priorities: int
    suggestions: List[str]