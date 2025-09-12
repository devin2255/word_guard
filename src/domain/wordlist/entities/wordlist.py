"""名单聚合根实体"""
from datetime import datetime
from typing import List, Optional
from dataclasses import dataclass, field

from src.shared.enums.list_enums import (
    ListTypeEnum, 
    MatchRuleEnum, 
    ListSuggestEnum, 
    SwitchEnum, 
    LanguageEnum,
    RiskTypeEnum
)
from src.shared.exceptions import WordListValidationError
from src.domain.wordlist.value_objects import ListName, RiskLevel
from src.domain.wordlist.events import WordListCreatedEvent, WordListUpdatedEvent


@dataclass
class WordList:
    """名单聚合根"""
    
    # 基本信息
    id: Optional[int] = None
    list_name: Optional[ListName] = None
    list_type: ListTypeEnum = ListTypeEnum.WHITELIST
    match_rule: MatchRuleEnum = MatchRuleEnum.TEXT
    suggestion: ListSuggestEnum = ListSuggestEnum.PASS
    risk_level: RiskLevel = field(default_factory=RiskLevel.create_normal)
    status: SwitchEnum = SwitchEnum.ON
    language: LanguageEnum = LanguageEnum.ALL
    
    # 审计信息
    create_time: Optional[datetime] = None
    update_time: Optional[datetime] = None
    delete_time: Optional[datetime] = None
    create_by: Optional[str] = None
    update_by: Optional[str] = None
    delete_by: Optional[str] = None
    
    # 领域事件
    _domain_events: List = field(default_factory=list, init=False)
    
    def __post_init__(self):
        """初始化后验证"""
        if self.list_name is None:
            raise WordListValidationError("list_name", "", "名单名称不能为空")
    
    @classmethod
    def create(
        cls, 
        name: str,
        list_type: ListTypeEnum,
        match_rule: MatchRuleEnum,
        suggestion: ListSuggestEnum,
        risk_type: RiskTypeEnum,
        language: LanguageEnum = LanguageEnum.ALL,
        created_by: str = None
    ) -> "WordList":
        """创建新名单"""
        
        # 创建值对象
        list_name = ListName.create(name)
        risk_level = RiskLevel(risk_type=risk_type)
        
        # 创建实体
        wordlist = cls(
            list_name=list_name,
            list_type=list_type,
            match_rule=match_rule,
            suggestion=suggestion,
            risk_level=risk_level,
            language=language,
            status=SwitchEnum.ON,
            create_time=datetime.now(),
            create_by=created_by
        )
        
        # 添加领域事件
        wordlist._add_domain_event(WordListCreatedEvent(wordlist))
        
        return wordlist
    
    def update_name(self, new_name: str, updated_by: str = None) -> None:
        """更新名单名称"""
        old_name = self.list_name.value if self.list_name else ""
        self.list_name = ListName.create(new_name)
        self.update_time = datetime.now()
        self.update_by = updated_by
        
        # 添加领域事件
        self._add_domain_event(WordListUpdatedEvent(self, "name", old_name, new_name))
    
    def update_status(self, status: SwitchEnum, updated_by: str = None) -> None:
        """更新状态"""
        old_status = self.status
        self.status = status
        self.update_time = datetime.now()
        self.update_by = updated_by
        
        # 添加领域事件
        self._add_domain_event(WordListUpdatedEvent(self, "status", old_status.name, status.name))
    
    def update_risk_level(self, risk_type: RiskTypeEnum, updated_by: str = None) -> None:
        """更新风险等级"""
        old_risk = self.risk_level.description if self.risk_level else ""
        self.risk_level = RiskLevel(risk_type=risk_type)
        self.update_time = datetime.now()
        self.update_by = updated_by
        
        # 添加领域事件
        self._add_domain_event(WordListUpdatedEvent(self, "risk_level", old_risk, self.risk_level.description))
    
    def soft_delete(self, deleted_by: str = None) -> None:
        """软删除"""
        self.delete_time = datetime.now()
        self.delete_by = deleted_by
        self.status = SwitchEnum.OFF
    
    def is_deleted(self) -> bool:
        """是否已删除"""
        return self.delete_time is not None
    
    def is_active(self) -> bool:
        """是否激活"""
        return self.status == SwitchEnum.ON and not self.is_deleted()
    
    def can_match(self, match_type: MatchRuleEnum) -> bool:
        """是否可以匹配指定类型"""
        return self.match_rule == match_type and self.is_active()
    
    def _add_domain_event(self, event) -> None:
        """添加领域事件"""
        self._domain_events.append(event)
    
    def get_domain_events(self) -> List:
        """获取领域事件"""
        return self._domain_events.copy()
    
    def clear_domain_events(self) -> None:
        """清除领域事件"""
        self._domain_events.clear()
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "id": self.id,
            "list_name": str(self.list_name) if self.list_name else None,
            "list_type": self.list_type.value,
            "match_rule": self.match_rule.value,
            "suggestion": self.suggestion.value,
            "risk_type": self.risk_level.risk_type.value,
            "status": self.status.value,
            "language": self.language.value,
            "create_time": self.create_time,
            "update_time": self.update_time,
            "create_by": self.create_by,
            "update_by": self.update_by,
        }