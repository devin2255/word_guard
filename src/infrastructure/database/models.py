"""数据库模型映射"""
import hashlib
from datetime import datetime
from tortoise import fields, models

from src.shared.enums.list_enums import (
    ListTypeEnum, 
    MatchRuleEnum, 
    ListSuggestEnum, 
    RiskTypeEnum, 
    SwitchEnum, 
    LanguageEnum
)


class BaseModel(models.Model):
    """基础模型，提供软删除、创建时间、更新时间等功能"""
    
    create_time = fields.DatetimeField(auto_now_add=True, description="创建时间")
    update_time = fields.DatetimeField(auto_now=True, description="更新时间")
    delete_time = fields.DatetimeField(null=True, description="删除时间")
    create_by = fields.CharField(max_length=50, null=True, description="创建人")
    update_by = fields.CharField(max_length=50, null=True, description="更新人")
    delete_by = fields.CharField(max_length=50, null=True, description="删除人")

    class Meta:
        abstract = True  # 抽象类，不会创建数据库表


class WordListModel(BaseModel):
    """名单数据库模型"""
    
    id = fields.IntField(pk=True, description="自增主键")
    list_name = fields.CharField(max_length=100, description="名单名称")
    list_type = fields.IntEnumField(ListTypeEnum, description="名单类型")
    match_rule = fields.IntEnumField(MatchRuleEnum, description="匹配规则")
    suggestion = fields.IntEnumField(ListSuggestEnum, description="处置建议")
    risk_type = fields.IntEnumField(RiskTypeEnum, description="风险类型")
    status = fields.IntEnumField(SwitchEnum, default=SwitchEnum.ON, description="状态")
    language = fields.IntEnumField(LanguageEnum, default=LanguageEnum.ALL, description="语种")

    class Meta:
        table = "wordlist"


class AppModel(BaseModel):
    """应用数据库模型"""
    
    id = fields.IntField(pk=True, description="自增主键")
    app_name = fields.CharField(max_length=100, description="应用名称")
    app_id = fields.CharField(max_length=50, unique=True, description="应用唯一标识")
    username = fields.CharField(max_length=50, null=True, description="负责人")

    class Meta:
        table = "app"