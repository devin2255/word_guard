"""名单详情数据传输对象"""
from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class ListDetailDTO(BaseModel):
    """名单详情DTO"""
    id: Optional[int] = None
    wordlist_id: int
    original_text: str
    processed_text: str
    memo: Optional[str] = None
    text_hash: Optional[str] = None
    word_count: Optional[int] = None
    char_count: Optional[int] = None
    is_active: bool = True
    create_time: Optional[datetime] = None
    update_time: Optional[datetime] = None
    create_by: Optional[str] = None
    update_by: Optional[str] = None


class CreateListDetailRequest(BaseModel):
    """创建名单详情请求"""
    wordlist_id: int = Field(..., description="名单ID")
    original_text: str = Field(..., min_length=1, max_length=500, description="原始文本")
    processed_text: Optional[str] = Field(None, max_length=500, description="处理后文本")
    memo: Optional[str] = Field(None, max_length=200, description="备注")
    created_by: Optional[str] = Field(None, description="创建人")


class UpdateListDetailRequest(BaseModel):
    """更新名单详情请求"""
    original_text: Optional[str] = Field(None, min_length=1, max_length=500, description="原始文本")
    processed_text: Optional[str] = Field(None, max_length=500, description="处理后文本")
    memo: Optional[str] = Field(None, max_length=200, description="备注")
    updated_by: Optional[str] = Field(None, description="更新人")


class BatchCreateListDetailsRequest(BaseModel):
    """批量创建名单详情请求"""
    wordlist_id: int = Field(..., description="名单ID")
    texts: List[str] = Field(..., min_items=1, max_items=1000, description="文本列表")
    processing_level: str = Field("standard", description="处理级别")
    created_by: Optional[str] = Field(None, description="创建人")


class BatchUpdateListDetailsRequest(BaseModel):
    """批量更新名单详情请求"""
    detail_ids: List[int] = Field(..., min_items=1, description="详情ID列表")
    is_active: Optional[bool] = Field(None, description="是否激活")
    memo: Optional[str] = Field(None, max_length=200, description="备注")
    updated_by: Optional[str] = Field(None, description="更新人")


class ListDetailStatisticsDTO(BaseModel):
    """名单详情统计DTO"""
    total_count: int
    active_count: int
    inactive_count: int
    total_words: int
    total_chars: int
    avg_words_per_item: float
    avg_chars_per_item: float


class QualityAnalysisDTO(BaseModel):
    """质量分析DTO"""
    total_items: int
    active_items: int
    quality_score: float
    issues: List[Dict[str, Any]]
    suggestions: List[str]
    statistics: Dict[str, Any]


class DuplicateAnalysisDTO(BaseModel):
    """重复分析DTO"""
    has_duplicates: bool
    total_duplicates: int
    duplicate_groups_count: int
    recommendations: List[str]
    duplicate_groups: Optional[List[List[ListDetailDTO]]] = None


class OptimizationSuggestionsDTO(BaseModel):
    """优化建议DTO"""
    quality_analysis: QualityAnalysisDTO
    duplicate_analysis: DuplicateAnalysisDTO
    optimizations: Dict[str, Any]


class BatchProcessingResultDTO(BaseModel):
    """批量处理结果DTO"""
    total_count: int
    success_count: int
    failure_count: int
    duplicates_found: int
    processing_time_ms: int
    message: str