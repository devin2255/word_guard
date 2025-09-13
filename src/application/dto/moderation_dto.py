"""文本风控数据传输对象"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from enum import IntEnum

from src.shared.enums.list_enums import RiskTypeEnum, LanguageEnum


class ModerationResultStatus(IntEnum):
    """风控检测结果状态"""
    APPROVED = 0         # 通过/批准
    REJECTED = 1         # 拒绝
    REVIEW_REQUIRED = 2  # 需要人工审核
    WARNING = 3          # 警告
    ERROR = -1           # 错误


class MatchedWordInfo(BaseModel):
    """匹配词信息"""
    word: str = Field(..., description="匹配到的敏感词")
    start_pos: int = Field(..., description="起始位置")
    end_pos: int = Field(..., description="结束位置")
    wordlist_id: int = Field(..., description="所属名单ID")
    wordlist_name: str = Field(..., description="所属名单名称")
    risk_type: int = Field(..., description="风险类型")
    risk_type_desc: str = Field(..., description="风险类型描述")
    suggestion: int = Field(..., description="处置建议")
    priority: int = Field(0, description="匹配优先级")


class ContentCheckResult(BaseModel):
    """内容检测结果"""
    content: str = Field(..., description="检测的内容")
    content_type: str = Field(..., description="内容类型(nickname/text)")
    is_violation: bool = Field(..., description="是否违规")
    risk_level: int = Field(0, description="风险等级(0-10)")
    matched_words: List[MatchedWordInfo] = Field(default_factory=list, description="匹配的敏感词")
    processed_content: Optional[str] = Field(None, description="处理后的内容(如替换敏感词)")


class ModerationRequest(BaseModel):
    """文本风控请求"""
    
    # 请求信息
    request_id: str = Field(..., description="请求ID，用于追踪请求")
    
    # 用户信息  
    user_id: Optional[str] = Field(None, max_length=100, description="用户ID")
    nickname: str = Field(..., min_length=1, max_length=100, description="用户昵称")
    account: Optional[str] = Field(None, max_length=100, description="用户账号")
    role_id: Optional[str] = Field(None, max_length=50, description="角色ID")
    
    # 内容信息
    content: str = Field(..., min_length=1, max_length=10000, description="发言内容")
    content_type: Optional[str] = Field("text", description="内容类型")
    
    # 网络信息
    ip_address: Optional[str] = Field(None, description="IP地址")
    user_agent: Optional[str] = Field(None, max_length=500, description="用户代理")
    
    # 业务信息
    app_id: Optional[int] = Field(None, description="应用ID")
    scene: Optional[str] = Field("default", max_length=50, description="业务场景")
    language: int = Field(0, description="语言类型")
    
    # 时间信息
    speak_time: Optional[datetime] = Field(None, description="发言时间")
    request_time: Optional[datetime] = Field(default_factory=datetime.now, description="请求时间")
    
    # 检测配置
    check_nickname: bool = Field(True, description="是否检查昵称")
    check_content: bool = Field(True, description="是否检查内容")
    return_matched_words: bool = Field(True, description="是否返回匹配的敏感词")
    auto_replace: bool = Field(False, description="是否自动替换敏感词")
    case_sensitive: bool = Field(False, description="是否大小写敏感")


class ModerationResponse(BaseModel):
    """文本风控响应"""
    
    # 请求信息
    request_id: str = Field(..., description="请求ID")
    app_id: Optional[int] = Field(None, description="应用ID")
    user_id: Optional[str] = Field(None, description="用户ID")
    nickname: Optional[str] = Field(None, description="用户昵称")
    content: Optional[str] = Field(None, description="发言内容")
    ip_address: Optional[str] = Field(None, description="IP地址")
    account: Optional[str] = Field(None, description="用户账号")
    role_id: Optional[str] = Field(None, description="角色ID")
    speak_time: Optional[datetime] = Field(None, description="发言时间")
    check_time: datetime = Field(default_factory=datetime.now, description="检查时间")
    
    # 检查结果
    is_violation: bool = Field(False, description="是否违规")
    max_risk_level: int = Field(0, description="最大风险等级")
    status: ModerationResultStatus = Field(..., description="检测状态")
    
    # 昵称检查结果
    nickname_check: Optional[ContentCheckResult] = Field(None, description="昵称检测结果")
    nickname_violation: bool = Field(False, description="昵称是否违规")
    nickname_risk_level: Optional[int] = Field(None, description="昵称风险等级")
    nickname_matched_count: int = Field(0, description="昵称匹配敏感词数量")
    
    # 内容检查结果
    content_check: Optional[ContentCheckResult] = Field(None, description="内容检测结果")
    content_violation: bool = Field(False, description="内容是否违规")
    content_risk_level: Optional[int] = Field(None, description="内容风险等级")
    content_matched_count: int = Field(0, description="内容匹配敏感词数量")
    
    # 处理建议
    suggestion: str = Field("", description="处理建议")
    error_message: Optional[str] = Field(None, description="错误信息")


class BatchModerationRequest(BaseModel):
    """批量文本风控请求"""
    
    app_id: Optional[int] = Field(None, description="应用ID")
    requests: List[ModerationRequest] = Field(
        ..., 
        min_items=1, 
        max_items=100, 
        description="批量请求列表"
    )
    
    # 批量配置
    parallel_check: bool = Field(True, description="是否并行检测")
    fail_fast: bool = Field(False, description="遇到错误是否快速失败")


class BatchModerationResponse(BaseModel):
    """批量文本风控响应"""
    
    batch_id: str = Field(..., description="批次ID")
    total_count: int = Field(..., description="总请求数")
    success_count: int = Field(..., description="成功检测数")
    failure_count: int = Field(..., description="失败检测数")
    violation_count: int = Field(..., description="违规检测数")
    
    results: List[ModerationResponse] = Field(default_factory=list, description="检测结果列表")
    errors: List[Dict[str, Any]] = Field(default_factory=list, description="错误列表")
    
    total_process_time_ms: int = Field(0, description="总处理耗时")
    check_time: datetime = Field(default_factory=datetime.now, description="检测时间")


class ModerationStatisticsRequest(BaseModel):
    """风控统计请求"""
    
    app_id: Optional[int] = Field(None, description="应用ID过滤")
    start_time: Optional[datetime] = Field(None, description="开始时间")
    end_time: Optional[datetime] = Field(None, description="结束时间")
    time_granularity: str = Field("hour", description="时间粒度(hour/day/week)")


class ModerationStatisticsResponse(BaseModel):
    """风控统计响应"""
    
    # 基础统计
    total_requests: int = Field(0, description="总请求数")
    pass_requests: int = Field(0, description="通过请求数")
    reject_requests: int = Field(0, description="拒绝请求数")
    review_requests: int = Field(0, description="待审核请求数")
    
    # 违规统计
    violation_rate: float = Field(0.0, description="违规率")
    avg_risk_level: float = Field(0.0, description="平均风险等级")
    
    # 风险类型分布
    risk_type_distribution: Dict[str, int] = Field(
        default_factory=dict, 
        description="风险类型分布"
    )
    
    # 时间序列数据
    time_series_data: List[Dict[str, Any]] = Field(
        default_factory=list, 
        description="时间序列统计数据"
    )
    
    # 性能统计
    avg_process_time_ms: float = Field(0.0, description="平均处理耗时")
    max_process_time_ms: int = Field(0, description="最大处理耗时")
    min_process_time_ms: int = Field(0, description="最小处理耗时")
    
    statistics_time: datetime = Field(default_factory=datetime.now, description="统计时间")