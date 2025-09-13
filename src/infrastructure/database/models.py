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


class ListDetailModel(BaseModel):
    """名单详情数据库模型"""
    
    id = fields.IntField(pk=True, description="自增主键")
    wordlist = fields.ForeignKeyField(
        'models.WordListModel', 
        related_name='details', 
        description="名单id，关联wordlist id字段"
    )
    original_text = fields.CharField(max_length=500, description="原始文本内容")
    processed_text = fields.CharField(
        max_length=500, 
        description="处理后的文本(如分词、去除特殊符号等)",
        index=True
    )
    memo = fields.CharField(max_length=200, null=True, description="备注")
    
    # 扩展字段
    text_hash = fields.CharField(max_length=64, index=True, description="文本哈希值，用于快速匹配")
    word_count = fields.IntField(default=0, description="词语数量")
    char_count = fields.IntField(default=0, description="字符数量")
    is_active = fields.BooleanField(default=True, description="是否激活")

    class Meta:
        table = "list_detail"
        # 复合索引优化查询性能
        indexes = [
            ("wordlist_id", "processed_text"),
            ("text_hash", "is_active"),
            ("wordlist_id", "is_active")
        ]


class AppWordListAssociationModel(BaseModel):
    """应用-名单关联模型（多对多中间表）"""
    
    id = fields.IntField(pk=True, description="自增主键")
    app = fields.ForeignKeyField(
        'models.AppModel', 
        related_name='wordlist_associations', 
        description="关联的应用",
        on_delete=fields.CASCADE
    )
    wordlist = fields.ForeignKeyField(
        'models.WordListModel', 
        related_name='app_associations', 
        description="关联的名单",
        on_delete=fields.CASCADE
    )
    
    # 关联属性
    is_active = fields.BooleanField(default=True, description="关联是否激活")
    priority = fields.IntField(default=0, description="优先级，数值越大优先级越高")
    memo = fields.CharField(max_length=200, null=True, description="关联备注")
    
    # 关联审计信息
    associated_at = fields.DatetimeField(auto_now_add=True, description="关联时间")
    associated_by = fields.CharField(max_length=50, null=True, description="关联操作人")

    class Meta:
        table = "app_wordlist_association"
        # 唯一约束：同一个应用不能重复关联同一个名单
        unique_together = [("app", "wordlist")]
        # 复合索引优化查询性能
        indexes = [
            ("app_id", "is_active"),
            ("wordlist_id", "is_active"),
            ("app_id", "wordlist_id", "is_active"),
            ("priority", "is_active")
        ]