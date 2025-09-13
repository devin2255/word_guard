"""名单详情聚合根实体"""
from datetime import datetime
from typing import Optional, List
from dataclasses import dataclass, field

from src.shared.patterns import AggregateRoot
from src.shared.exceptions.domain_exceptions import WordListValidationError
from src.domain.listdetail.value_objects import TextContent, ProcessedText
from src.domain.listdetail.events import (
    ListDetailCreatedEvent,
    ListDetailUpdatedEvent,
    ListDetailActivatedEvent,
    ListDetailDeactivatedEvent
)


@dataclass
class ListDetail(AggregateRoot):
    """名单详情聚合根"""
    
    # 基本信息
    id: Optional[int] = None
    wordlist_id: int = None
    text_content: TextContent = None
    is_active: bool = True
    
    # 审计信息
    create_time: Optional[datetime] = None
    update_time: Optional[datetime] = None
    delete_time: Optional[datetime] = None
    create_by: Optional[str] = None
    update_by: Optional[str] = None
    delete_by: Optional[str] = None
    
    def __post_init__(self):
        """初始化后验证"""
        super().__init__()  # 初始化聚合根
        if self.wordlist_id is None:
            raise WordListValidationError("wordlist_id", None, "名单ID不能为空")
        if self.text_content is None:
            raise WordListValidationError("text_content", None, "文本内容不能为空")
    
    @classmethod
    def create(
        cls,
        wordlist_id: int,
        original_text: str,
        processed_text: str = None,
        memo: str = None,
        created_by: str = None
    ) -> "ListDetail":
        """创建名单详情"""
        
        # 创建文本内容值对象
        text_content = TextContent.create(original_text, processed_text, memo)
        
        # 创建实体
        detail = cls(
            wordlist_id=wordlist_id,
            text_content=text_content,
            is_active=True,
            create_time=datetime.now(),
            create_by=created_by
        )
        
        # 添加领域事件
        detail.add_domain_event(ListDetailCreatedEvent(detail))
        
        return detail
    
    def update_content(
        self, 
        original_text: str = None,
        processed_text: str = None,
        memo: str = None,
        updated_by: str = None
    ) -> None:
        """更新文本内容"""
        
        old_content = self.text_content
        
        # 保留原有值或使用新值
        new_original = original_text or old_content.original_text
        new_processed = processed_text or old_content.processed_text
        new_memo = memo if memo is not None else old_content.memo
        
        # 创建新的文本内容值对象
        self.text_content = TextContent.create(new_original, new_processed, new_memo)
        self.update_time = datetime.now()
        self.update_by = updated_by
        
        # 添加领域事件
        self.add_domain_event(ListDetailUpdatedEvent(
            detail=self,
            field_name="text_content",
            old_value=str(old_content),
            new_value=str(self.text_content)
        ))
    
    def update_memo(self, memo: str, updated_by: str = None) -> None:
        """更新备注"""
        old_memo = self.text_content.memo
        self.text_content = self.text_content.update_memo(memo)
        self.update_time = datetime.now()
        self.update_by = updated_by
        
        # 添加领域事件
        self.add_domain_event(ListDetailUpdatedEvent(
            detail=self,
            field_name="memo", 
            old_value=old_memo,
            new_value=memo
        ))
    
    def activate(self, updated_by: str = None) -> None:
        """激活"""
        if self.is_active:
            return  # 已经是激活状态
        
        self.is_active = True
        self.update_time = datetime.now()
        self.update_by = updated_by
        
        # 添加领域事件
        self.add_domain_event(ListDetailActivatedEvent(self))
    
    def deactivate(self, updated_by: str = None) -> None:
        """停用"""
        if not self.is_active:
            return  # 已经是停用状态
        
        self.is_active = False
        self.update_time = datetime.now()
        self.update_by = updated_by
        
        # 添加领域事件
        self.add_domain_event(ListDetailDeactivatedEvent(self))
    
    def soft_delete(self, deleted_by: str = None) -> None:
        """软删除"""
        self.delete_time = datetime.now()
        self.delete_by = deleted_by
        self.is_active = False
    
    def is_deleted(self) -> bool:
        """是否已删除"""
        return self.delete_time is not None
    
    def is_similar_to(self, other: "ListDetail") -> bool:
        """检查是否与另一个名单详情相似"""
        if not other or self.wordlist_id != other.wordlist_id:
            return False
        
        return self.text_content.is_similar_to(other.text_content)
    
    def matches_text(self, text: str) -> bool:
        """检查是否匹配指定文本"""
        if not self.is_active:
            return False
        
        processed_text = ProcessedText.from_original_text(text)
        return self.text_content.processed_text.lower() in processed_text.value.lower()
    
    def get_processed_text(self) -> ProcessedText:
        """获取处理后文本值对象"""
        return ProcessedText(self.text_content.processed_text)
    
    @property
    def text_hash(self) -> str:
        """获取文本哈希值"""
        return self.text_content.text_hash
    
    @property
    def word_count(self) -> int:
        """获取词语数量"""
        return self.text_content.word_count
    
    @property
    def char_count(self) -> int:
        """获取字符数量"""
        return self.text_content.char_count
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "id": self.id,
            "wordlist_id": self.wordlist_id,
            "original_text": self.text_content.original_text,
            "processed_text": self.text_content.processed_text,
            "memo": self.text_content.memo,
            "text_hash": self.text_hash,
            "word_count": self.word_count,
            "char_count": self.char_count,
            "is_active": self.is_active,
            "create_time": self.create_time,
            "update_time": self.update_time,
            "create_by": self.create_by,
            "update_by": self.update_by
        }
    
    def __str__(self) -> str:
        return f"ListDetail(id={self.id}, wordlist_id={self.wordlist_id}, text='{self.text_content.processed_text[:20]}...')"