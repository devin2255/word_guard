"""文本处理领域服务"""
import re
import hashlib
from typing import List, Dict, Any, Set, Tuple
from dataclasses import dataclass
from enum import Enum

from src.domain.listdetail.value_objects import ProcessedText, TextContent
from src.shared.exceptions.domain_exceptions import WordListValidationError


class TextProcessingLevel(Enum):
    """文本处理级别"""
    BASIC = "basic"           # 基础处理：小写、去特殊字符
    STANDARD = "standard"     # 标准处理：基础 + 去重复字符
    ADVANCED = "advanced"     # 高级处理：标准 + 分词、词干提取
    STRICT = "strict"         # 严格处理：高级 + 同义词替换


@dataclass
class ProcessingResult:
    """处理结果"""
    original_text: str
    processed_text: str
    processing_level: TextProcessingLevel
    processing_steps: List[str]
    extracted_keywords: List[str]
    text_hash: str
    statistics: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "original_text": self.original_text,
            "processed_text": self.processed_text,
            "processing_level": self.processing_level.value,
            "processing_steps": self.processing_steps,
            "extracted_keywords": self.extracted_keywords,
            "text_hash": self.text_hash,
            "statistics": self.statistics
        }


@dataclass
class BatchProcessingResult:
    """批量处理结果"""
    total_count: int
    success_count: int
    failure_count: int
    results: List[ProcessingResult]
    duplicates_found: int
    processing_time_ms: int
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_count": self.total_count,
            "success_count": self.success_count,
            "failure_count": self.failure_count,
            "duplicates_found": self.duplicates_found,
            "processing_time_ms": self.processing_time_ms,
            "results": [result.to_dict() for result in self.results]
        }


class TextProcessingService:
    """文本处理领域服务"""
    
    def __init__(self):
        # 预定义的停用词列表
        self._stop_words = {
            "的", "了", "在", "是", "我", "有", "和", "就", "不", "人", "都", "一", "个", "说", "这", "么", "为",
            "a", "an", "the", "and", "or", "but", "is", "are", "was", "were", "be", "been", "have", "has", "had",
            "do", "does", "did", "will", "would", "could", "should", "may", "might", "can", "to", "of", "in", "on"
        }
        
        # 预定义的同义词映射
        self._synonyms_map = {
            "色情": ["黄色", "情色", "成人"],
            "暴力": ["血腥", "残暴", "凶残"],
            "赌博": ["博彩", "赌钱", "下注"],
            "毒品": ["毒药", "药品", "兴奋剂"]
        }
    
    def process_single_text(
        self,
        text: str,
        level: TextProcessingLevel = TextProcessingLevel.STANDARD
    ) -> ProcessingResult:
        """处理单个文本"""
        
        if not text or not text.strip():
            raise WordListValidationError("text", text, "文本不能为空")
        
        original_text = text
        processed_text = text
        processing_steps = []
        
        # 基础处理
        if level in [TextProcessingLevel.BASIC, TextProcessingLevel.STANDARD, 
                    TextProcessingLevel.ADVANCED, TextProcessingLevel.STRICT]:
            processed_text, steps = self._basic_processing(processed_text)
            processing_steps.extend(steps)
        
        # 标准处理
        if level in [TextProcessingLevel.STANDARD, TextProcessingLevel.ADVANCED, TextProcessingLevel.STRICT]:
            processed_text, steps = self._standard_processing(processed_text)
            processing_steps.extend(steps)
        
        # 高级处理
        if level in [TextProcessingLevel.ADVANCED, TextProcessingLevel.STRICT]:
            processed_text, steps = self._advanced_processing(processed_text)
            processing_steps.extend(steps)
        
        # 严格处理
        if level == TextProcessingLevel.STRICT:
            processed_text, steps = self._strict_processing(processed_text)
            processing_steps.extend(steps)
        
        # 提取关键词
        keywords = self._extract_keywords(processed_text)
        
        # 计算统计信息
        statistics = self._calculate_statistics(original_text, processed_text)
        
        # 计算哈希值
        text_hash = self._calculate_text_hash(processed_text)
        
        return ProcessingResult(
            original_text=original_text,
            processed_text=processed_text,
            processing_level=level,
            processing_steps=processing_steps,
            extracted_keywords=keywords,
            text_hash=text_hash,
            statistics=statistics
        )
    
    def process_batch_texts(
        self,
        texts: List[str],
        level: TextProcessingLevel = TextProcessingLevel.STANDARD
    ) -> BatchProcessingResult:
        """批量处理文本"""
        
        import time
        start_time = time.time()
        
        results = []
        success_count = 0
        failure_count = 0
        processed_hashes = set()
        duplicates_found = 0
        
        for text in texts:
            try:
                result = self.process_single_text(text, level)
                
                # 检查重复
                if result.text_hash in processed_hashes:
                    duplicates_found += 1
                else:
                    processed_hashes.add(result.text_hash)
                
                results.append(result)
                success_count += 1
                
            except Exception:
                failure_count += 1
        
        processing_time = int((time.time() - start_time) * 1000)
        
        return BatchProcessingResult(
            total_count=len(texts),
            success_count=success_count,
            failure_count=failure_count,
            results=results,
            duplicates_found=duplicates_found,
            processing_time_ms=processing_time
        )
    
    def detect_duplicates(
        self,
        text_contents: List[TextContent],
        similarity_threshold: float = 0.9
    ) -> List[List[TextContent]]:
        """检测重复文本"""
        
        groups = []
        processed = set()
        
        for i, content1 in enumerate(text_contents):
            if i in processed:
                continue
            
            duplicate_group = [content1]
            processed.add(i)
            
            for j, content2 in enumerate(text_contents[i+1:], i+1):
                if j in processed:
                    continue
                
                # 计算相似度
                similarity = self._calculate_similarity(
                    content1.processed_text,
                    content2.processed_text
                )
                
                if similarity >= similarity_threshold:
                    duplicate_group.append(content2)
                    processed.add(j)
            
            # 只保留有重复的分组
            if len(duplicate_group) > 1:
                groups.append(duplicate_group)
        
        return groups
    
    def suggest_optimized_text(self, text: str) -> Dict[str, Any]:
        """建议优化的文本"""
        
        processed_result = self.process_single_text(text, TextProcessingLevel.ADVANCED)
        
        suggestions = {
            "original_text": text,
            "optimized_text": processed_result.processed_text,
            "improvements": [],
            "statistics": processed_result.statistics,
            "keywords": processed_result.extracted_keywords
        }
        
        # 分析可能的改进
        if len(text) != len(processed_result.processed_text):
            suggestions["improvements"].append("去除了无关字符，提高匹配准确性")
        
        if len(processed_result.extracted_keywords) > 0:
            suggestions["improvements"].append(f"提取了 {len(processed_result.extracted_keywords)} 个关键词")
        
        # 检查是否包含常见模式
        if self._contains_special_patterns(text):
            suggestions["improvements"].append("检测到特殊模式，建议使用正则表达式匹配")
        
        return suggestions
    
    def _basic_processing(self, text: str) -> Tuple[str, List[str]]:
        """基础处理"""
        steps = []
        
        # 1. 转换为小写
        text = text.lower()
        steps.append("转换为小写")
        
        # 2. 去除HTML标签
        text = re.sub(r'<[^>]+>', '', text)
        steps.append("去除HTML标签")
        
        # 3. 去除特殊字符（保留中文、英文、数字、空格）
        text = re.sub(r'[^\w\s\u4e00-\u9fff]', '', text)
        steps.append("去除特殊字符")
        
        # 4. 压缩多个空格为单个空格
        text = re.sub(r'\s+', ' ', text)
        steps.append("压缩空格")
        
        # 5. 去除首尾空格
        text = text.strip()
        steps.append("去除首尾空格")
        
        return text, steps
    
    def _standard_processing(self, text: str) -> Tuple[str, List[str]]:
        """标准处理"""
        steps = []
        
        # 1. 去除重复字符
        text = re.sub(r'(.)\1{2,}', r'\1\1', text)
        steps.append("去除重复字符")
        
        # 2. 去除数字
        text = re.sub(r'\d+', '', text)
        steps.append("去除数字")
        
        return text, steps
    
    def _advanced_processing(self, text: str) -> Tuple[str, List[str]]:
        """高级处理"""
        steps = []
        
        # 1. 去除停用词
        words = text.split()
        filtered_words = [word for word in words if word not in self._stop_words]
        text = ' '.join(filtered_words)
        steps.append("去除停用词")
        
        # 2. 简化的词干提取（去除常见后缀）
        text = self._simple_stemming(text)
        steps.append("词干提取")
        
        return text, steps
    
    def _strict_processing(self, text: str) -> Tuple[str, List[str]]:
        """严格处理"""
        steps = []
        
        # 1. 同义词替换
        for standard_word, synonyms in self._synonyms_map.items():
            for synonym in synonyms:
                text = text.replace(synonym, standard_word)
        steps.append("同义词替换")
        
        return text, steps
    
    def _simple_stemming(self, text: str) -> str:
        """简化的词干提取"""
        # 简化的中文处理：去除常见后缀
        suffixes = ['的', '了', '过', '着', '们']
        words = text.split()
        
        stemmed_words = []
        for word in words:
            stemmed_word = word
            for suffix in suffixes:
                if word.endswith(suffix) and len(word) > len(suffix):
                    stemmed_word = word[:-len(suffix)]
                    break
            stemmed_words.append(stemmed_word)
        
        return ' '.join(stemmed_words)
    
    def _extract_keywords(self, text: str) -> List[str]:
        """提取关键词"""
        words = text.split()
        # 过滤长度小于2的词和停用词
        keywords = [
            word for word in words 
            if len(word) >= 2 and word not in self._stop_words
        ]
        # 去重并保持顺序
        seen = set()
        unique_keywords = []
        for keyword in keywords:
            if keyword not in seen:
                seen.add(keyword)
                unique_keywords.append(keyword)
        
        return unique_keywords[:10]  # 最多返回10个关键词
    
    def _calculate_statistics(self, original_text: str, processed_text: str) -> Dict[str, Any]:
        """计算统计信息"""
        return {
            "original_length": len(original_text),
            "processed_length": len(processed_text),
            "reduction_ratio": round(
                (len(original_text) - len(processed_text)) / max(len(original_text), 1), 3
            ),
            "original_word_count": len(original_text.split()),
            "processed_word_count": len(processed_text.split()),
            "unique_chars": len(set(processed_text)),
            "contains_chinese": bool(re.search(r'[\u4e00-\u9fff]', processed_text)),
            "contains_english": bool(re.search(r'[a-zA-Z]', processed_text))
        }
    
    def _calculate_text_hash(self, text: str) -> str:
        """计算文本哈希值"""
        return hashlib.sha256(text.encode('utf-8')).hexdigest()
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """计算文本相似度（Jaccard相似度）"""
        words1 = set(text1.split())
        words2 = set(text2.split())
        
        if not words1 and not words2:
            return 1.0
        
        intersection = words1 & words2
        union = words1 | words2
        
        return len(intersection) / len(union) if union else 0.0
    
    def _contains_special_patterns(self, text: str) -> bool:
        """检查是否包含特殊模式"""
        # 检查常见的特殊模式
        patterns = [
            r'\d{11}',  # 手机号
            r'\d{4}-\d{4}-\d{4}-\d{4}',  # 卡号
            r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',  # 邮箱
            r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'  # URL
        ]
        
        for pattern in patterns:
            if re.search(pattern, text):
                return True
        
        return False