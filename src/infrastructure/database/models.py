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

# 删除循环导入


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


class ModerationLogModel(models.Model):
    """敏感词检查日志数据库模型"""
    
    # 主键
    id = fields.BigIntField(pk=True, description="主键ID")
    
    # 请求信息
    request_id = fields.CharField(max_length=100, index=True, description="请求ID")
    request_time = fields.DatetimeField(default=datetime.now, index=True, description="请求时间")
    
    # 用户信息
    user_id = fields.CharField(max_length=100, null=True, index=True, description="用户ID")
    nickname = fields.CharField(max_length=100, null=True, description="用户昵称")
    account = fields.CharField(max_length=100, null=True, index=True, description="用户账号")
    role_id = fields.CharField(max_length=50, null=True, description="角色ID")
    
    # 内容信息
    content = fields.TextField(null=True, description="发言内容")
    content_type = fields.CharField(max_length=50, null=True, default="text", description="内容类型")
    
    # 网络信息
    ip_address = fields.CharField(max_length=45, null=True, index=True, description="IP地址")
    user_agent = fields.CharField(max_length=500, null=True, description="用户代理")
    
    # 业务信息
    app_id = fields.IntField(null=True, index=True, description="应用ID")
    scene = fields.CharField(max_length=50, null=True, default="default", description="业务场景")
    language = fields.IntField(default=0, description="语言类型")
    speak_time = fields.DatetimeField(null=True, description="发言时间")
    
    # 检测配置
    check_nickname = fields.BooleanField(default=True, description="是否检查昵称")
    check_content = fields.BooleanField(default=True, description="是否检查内容")
    return_matched_words = fields.BooleanField(default=True, description="是否返回匹配词")
    auto_replace = fields.BooleanField(default=False, description="是否自动替换")
    case_sensitive = fields.BooleanField(default=False, description="是否大小写敏感")
    
    # 检测结果
    check_time = fields.DatetimeField(default=datetime.now, index=True, description="检查时间")
    is_violation = fields.BooleanField(default=False, index=True, description="是否违规")
    max_risk_level = fields.IntField(default=0, index=True, description="最大风险等级")
    status = fields.IntField(default=0, index=True, description="检测状态")
    
    # 昵称检查结果
    nickname_violation = fields.BooleanField(default=False, description="昵称是否违规")
    nickname_risk_level = fields.IntField(null=True, description="昵称风险等级")
    nickname_matched_count = fields.IntField(default=0, description="昵称匹配词数量")
    nickname_matched_words = fields.TextField(null=True, description="昵称匹配词信息(JSON)")
    
    # 内容检查结果
    content_violation = fields.BooleanField(default=False, description="内容是否违规")
    content_risk_level = fields.IntField(null=True, description="内容风险等级")
    content_matched_count = fields.IntField(default=0, description="内容匹配词数量")
    content_matched_words = fields.TextField(null=True, description="内容匹配词信息(JSON)")
    
    # 处理结果
    suggestion = fields.TextField(null=True, description="处理建议")
    error_message = fields.TextField(null=True, description="错误信息")
    
    # 性能统计
    process_time_ms = fields.IntField(default=0, index=True, description="处理耗时(毫秒)")
    
    # 扩展字段
    extra_data = fields.TextField(null=True, description="扩展数据(JSON)")
    
    # 审计字段
    created_at = fields.DatetimeField(auto_now_add=True, index=True, description="创建时间")
    
    class Meta:
        table = "moderation_logs"
        table_description = "敏感词检查日志表"
        indexes = [
            # 复合索引
            ("app_id", "request_time"),
            ("user_id", "request_time"),
            ("is_violation", "request_time"),
            ("ip_address", "request_time"),
            ("check_time", "process_time_ms"),
        ]