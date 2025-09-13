"""处理后文本值对象"""
import re
from dataclasses import dataclass
from typing import List, Set


@dataclass(frozen=True)  
class ProcessedText:
    """处理后文本值对象"""
    
    value: str
    
    def __post_init__(self):
        """初始化后验证"""
        if not self.value or not self.value.strip():
            raise ValueError("处理后文本不能为空")
        
        if len(self.value) > 500:
            raise ValueError("处理后文本长度不能超过500字符")
    
    @classmethod
    def from_original_text(cls, original_text: str) -> "ProcessedText":
        """从原始文本创建处理后文本"""
        processed = cls._process_text(original_text)
        return cls(value=processed)
    
    @staticmethod
    def _process_text(text: str) -> str:
        """文本预处理逻辑"""
        if not text:
            return ""
        
        # 1. 转换为小写
        processed = text.lower()
        
        # 2. 去除HTML标签
        processed = re.sub(r'<[^>]+>', '', processed)
        
        # 3. 去除特殊字符（保留中文、英文、数字、空格）
        processed = re.sub(r'[^\w\s\u4e00-\u9fff]', '', processed)
        
        # 4. 压缩多个空格为单个空格
        processed = re.sub(r'\s+', ' ', processed)
        
        # 5. 去除首尾空格
        processed = processed.strip()
        
        return processed
    
    @property
    def normalized_text(self) -> str:
        """获取标准化文本"""
        return self.value
    
    @property
    def keywords(self) -> List[str]:
        """提取关键词"""
        # 简化的关键词提取（实际可以使用更复杂的NLP算法）
        words = self.value.split()
        # 过滤长度小于2的词
        keywords = [word for word in words if len(word) >= 2]
        return keywords
    
    @property
    def unique_words(self) -> Set[str]:
        """获取唯一词汇集合"""
        return set(self.keywords)
    
    def contains_word(self, word: str) -> bool:
        """检查是否包含指定词汇"""
        return word.lower() in self.value.lower()
    
    def contains_any_words(self, words: List[str]) -> bool:
        """检查是否包含任意指定词汇"""
        return any(self.contains_word(word) for word in words)
    
    def contains_all_words(self, words: List[str]) -> bool:
        """检查是否包含所有指定词汇"""
        return all(self.contains_word(word) for word in words)
    
    def similarity_score(self, other: "ProcessedText") -> float:
        """计算与另一个处理后文本的相似度"""
        if not other or not other.value:
            return 0.0
        
        # 简化的Jaccard相似度计算
        words1 = self.unique_words
        words2 = other.unique_words
        
        if not words1 and not words2:
            return 1.0
        
        intersection = words1 & words2
        union = words1 | words2
        
        return len(intersection) / len(union) if union else 0.0
    
    def __str__(self) -> str:
        return self.value
    
    def __len__(self) -> int:
        return len(self.value)
    
    def __contains__(self, item: str) -> bool:
        return self.contains_word(item)