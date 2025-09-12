"""名单相关DTO"""
from datetime import datetime
from typing import Optional, Union
from pydantic import BaseModel, Field, field_validator

from src.shared.enums.list_enums import (
    ListTypeEnum, 
    MatchRuleEnum, 
    ListSuggestEnum, 
    SwitchEnum, 
    LanguageEnum,
    RiskTypeEnum
)


class WordListDTO(BaseModel):
    """名单数据传输对象"""
    
    id: Optional[int] = None
    list_name: str
    list_type: int
    match_rule: int
    suggestion: int
    risk_type: int
    status: int
    language: int
    create_time: Optional[datetime] = None
    update_time: Optional[datetime] = None
    create_by: Optional[str] = None
    update_by: Optional[str] = None
    
    class Config:
        from_attributes = True


class CreateWordListRequest(BaseModel):
    """创建名单请求"""
    
    list_name: str = Field(..., min_length=1, max_length=100, description="名单名称")
    list_type: int = Field(..., description="名单类型")
    match_rule: int = Field(..., description="匹配规则")
    suggestion: int = Field(..., description="处置建议")
    risk_type: int = Field(..., description="风险类型")
    language: int = Field(default=0, description="语种")
    created_by: Optional[str] = Field(None, max_length=50, description="创建人")
    
    @field_validator('list_type', mode='before')
    @classmethod
    def validate_list_type(cls, v: int) -> int:
        if v not in ListTypeEnum.values():
            raise ValueError(f'无效的名单类型: {v}')
        return v
    
    @field_validator('match_rule', mode='before')
    @classmethod
    def validate_match_rule(cls, v: int) -> int:
        if v not in MatchRuleEnum.values():
            raise ValueError(f'无效的匹配规则: {v}')
        return v
    
    @field_validator('suggestion', mode='before')
    @classmethod
    def validate_suggestion(cls, v: int) -> int:
        if v not in ListSuggestEnum.values():
            raise ValueError(f'无效的处置建议: {v}')
        return v
    
    @field_validator('risk_type', mode='before')
    @classmethod
    def validate_risk_type(cls, v: int) -> int:
        if v not in RiskTypeEnum.values():
            raise ValueError(f'无效的风险类型: {v}')
        return v
    
    @field_validator('language', mode='before')
    @classmethod
    def validate_language(cls, v: int) -> int:
        if v not in LanguageEnum.values():
            raise ValueError(f'无效的语种: {v}')
        return v


class UpdateWordListRequest(BaseModel):
    """更新名单请求"""
    
    list_name: Optional[str] = Field(None, min_length=1, max_length=100, description="名单名称")
    status: Optional[int] = Field(None, description="状态")
    risk_type: Optional[int] = Field(None, description="风险类型")
    updated_by: Optional[str] = Field(None, max_length=50, description="更新人")
    
    @field_validator('status', mode='before')
    @classmethod
    def validate_status(cls, v: Union[int, None]) -> Union[int, None]:
        if v is not None and v not in SwitchEnum.values():
            raise ValueError(f'无效的状态: {v}')
        return v
    
    @field_validator('risk_type', mode='before')
    @classmethod
    def validate_risk_type(cls, v: Union[int, None]) -> Union[int, None]:
        if v is not None and v not in RiskTypeEnum.values():
            raise ValueError(f'无效的风险类型: {v}')
        return v