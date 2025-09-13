"""文本内容值对象"""
import hashlib
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class TextContent:
    """文本内容值对象"""
    
    original_text: str
    processed_text: str
    memo: Optional[str] = None
    
    def __post_init__(self):
        """初始化后验证"""
        if not self.original_text or not self.original_text.strip():
            raise ValueError("原始文本不能为空")
        
        if not self.processed_text or not self.processed_text.strip():
            raise ValueError("处理后文本不能为空")
        
        if len(self.original_text) > 500:
            raise ValueError("原始文本长度不能超过500字符")
            
        if len(self.processed_text) > 500:
            raise ValueError("处理后文本长度不能超过500字符")
        
        if self.memo and len(self.memo) > 200:
            raise ValueError("备注长度不能超过200字符")
    
    @property
    def text_hash(self) -> str:
        """获取文本哈希值"""
        content = f"{self.original_text}:{self.processed_text}"
        return hashlib.sha256(content.encode('utf-8')).hexdigest()
    
    @property
    def word_count(self) -> int:
        """获取词语数量（简化统计）"""
        # 简化的词语统计，实际可以使用更复杂的分词算法
        return len(self.processed_text.split())
    
    @property
    def char_count(self) -> int:
        """获取字符数量"""
        return len(self.processed_text)
    
    @classmethod
    def create(
        cls, 
        original_text: str, 
        processed_text: str = None,
        memo: str = None
    ) -> "TextContent":
        """创建文本内容"""
        # 如果没有提供处理后文本，使用原始文本作为默认值
        if processed_text is None:
            processed_text = original_text.strip()
        
        return cls(
            original_text=original_text.strip(),
            processed_text=processed_text.strip(),
            memo=memo.strip() if memo else None
        )
    
    def update_memo(self, memo: str) -> "TextContent":
        """更新备注（返回新的值对象）"""
        return TextContent(
            original_text=self.original_text,
            processed_text=self.processed_text,
            memo=memo.strip() if memo else None
        )
    
    def is_similar_to(self, other: "TextContent") -> bool:
        """检查是否与另一个文本内容相似"""
        # 简化的相似性检查
        return (
            self.processed_text.lower() == other.processed_text.lower() or
            self.text_hash == other.text_hash
        )
    
    def __str__(self) -> str:
        return self.processed_text
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "original_text": self.original_text,
            "processed_text": self.processed_text,
            "memo": self.memo,
            "text_hash": self.text_hash,
            "word_count": self.word_count,
            "char_count": self.char_count
        }