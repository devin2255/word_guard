"""风控共享值对象"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from enum import IntEnum


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