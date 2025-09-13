"""AC自动机算法实现"""
from collections import deque, defaultdict
from typing import List, Dict, Set, Tuple, Optional
from dataclasses import dataclass


@dataclass
class MatchResult:
    """匹配结果"""
    pattern: str        # 匹配到的模式
    start_pos: int     # 开始位置
    end_pos: int       # 结束位置
    pattern_id: Optional[int] = None  # 模式ID


class TrieNode:
    """Trie树节点"""
    
    def __init__(self):
        self.children: Dict[str, 'TrieNode'] = {}
        self.failure: Optional['TrieNode'] = None
        self.output: List[Tuple[str, int]] = []  # (pattern, pattern_id)
        self.is_end = False
    
    def add_pattern(self, pattern: str, pattern_id: Optional[int] = None) -> None:
        """添加模式到当前节点"""
        self.output.append((pattern, pattern_id))
        self.is_end = True


class AhoCorasickAutomaton:
    """AC自动机实现"""
    
    def __init__(self):
        self.root = TrieNode()
        self.patterns: Dict[str, int] = {}  # pattern -> pattern_id
        self.pattern_info: Dict[int, Dict] = {}  # pattern_id -> info
        self._built = False
    
    def add_pattern(self, pattern: str, pattern_id: Optional[int] = None, **info) -> int:
        """
        添加模式字符串
        
        Args:
            pattern: 模式字符串
            pattern_id: 模式ID，如果不提供则自动生成
            **info: 额外信息，如wordlist_id, risk_type等
            
        Returns:
            模式ID
        """
        if not pattern:
            return -1
        
        # 生成或使用提供的pattern_id
        if pattern_id is None:
            pattern_id = len(self.patterns)
        
        # 如果模式已存在，更新信息
        if pattern in self.patterns:
            existing_id = self.patterns[pattern]
            self.pattern_info[existing_id].update(info)
            return existing_id
        
        # 记录模式信息
        self.patterns[pattern] = pattern_id
        self.pattern_info[pattern_id] = {
            'pattern': pattern,
            'length': len(pattern),
            **info
        }
        
        # 插入到Trie树
        node = self.root
        for char in pattern:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        
        node.add_pattern(pattern, pattern_id)
        self._built = False  # 标记需要重新构建失效函数
        return pattern_id
    
    def add_patterns(self, patterns: List[str], pattern_infos: Optional[List[Dict]] = None) -> List[int]:
        """
        批量添加模式字符串
        
        Args:
            patterns: 模式字符串列表
            pattern_infos: 对应的信息列表
            
        Returns:
            模式ID列表
        """
        pattern_ids = []
        infos = pattern_infos or [{}] * len(patterns)
        
        for pattern, info in zip(patterns, infos):
            pattern_id = self.add_pattern(pattern, **info)
            pattern_ids.append(pattern_id)
        
        return pattern_ids
    
    def build_failure_function(self) -> None:
        """构建失效函数（KMP算法的核心）"""
        if self._built:
            return
        
        # 初始化根节点的子节点的失效指针
        queue = deque()
        for child in self.root.children.values():
            child.failure = self.root
            queue.append(child)
        
        # BFS构建失效函数
        while queue:
            current = queue.popleft()
            
            for char, child in current.children.items():
                queue.append(child)
                
                # 寻找最长的适当后缀
                temp = current.failure
                while temp is not None and char not in temp.children:
                    temp = temp.failure
                
                if temp is not None:
                    child.failure = temp.children[char]
                else:
                    child.failure = self.root
                
                # 合并输出函数
                if child.failure.output:
                    child.output.extend(child.failure.output)
        
        self._built = True
    
    def search(self, text: str, case_sensitive: bool = True) -> List[MatchResult]:
        """
        搜索文本中的所有匹配
        
        Args:
            text: 待搜索的文本
            case_sensitive: 是否大小写敏感
            
        Returns:
            匹配结果列表
        """
        if not text:
            return []
        
        # 确保失效函数已构建
        self.build_failure_function()
        
        # 处理大小写
        search_text = text if case_sensitive else text.lower()
        results = []
        
        current = self.root
        for i, char in enumerate(search_text):
            # 处理大小写不敏感
            search_char = char if case_sensitive else char.lower()
            
            # 沿着失效指针寻找匹配
            while current is not None and search_char not in current.children:
                current = current.failure
            
            if current is None:
                current = self.root
                continue
            
            current = current.children[search_char]
            
            # 检查是否有匹配的模式
            for pattern, pattern_id in current.output:
                start_pos = i - len(pattern) + 1
                end_pos = i + 1
                
                # 对于大小写不敏感的搜索，使用原始文本的匹配部分
                matched_text = text[start_pos:end_pos] if not case_sensitive else pattern
                
                results.append(MatchResult(
                    pattern=matched_text,
                    start_pos=start_pos,
                    end_pos=end_pos,
                    pattern_id=pattern_id
                ))
        
        return results
    
    def search_first(self, text: str, case_sensitive: bool = True) -> Optional[MatchResult]:
        """
        搜索第一个匹配
        
        Args:
            text: 待搜索的文本
            case_sensitive: 是否大小写敏感
            
        Returns:
            第一个匹配结果或None
        """
        if not text:
            return None
        
        # 确保失效函数已构建
        self.build_failure_function()
        
        # 处理大小写
        search_text = text if case_sensitive else text.lower()
        
        current = self.root
        for i, char in enumerate(search_text):
            # 处理大小写不敏感
            search_char = char if case_sensitive else char.lower()
            
            # 沿着失效指针寻找匹配
            while current is not None and search_char not in current.children:
                current = current.failure
            
            if current is None:
                current = self.root
                continue
            
            current = current.children[search_char]
            
            # 检查是否有匹配的模式
            if current.output:
                pattern, pattern_id = current.output[0]
                start_pos = i - len(pattern) + 1
                end_pos = i + 1
                
                # 对于大小写不敏感的搜索，使用原始文本的匹配部分
                matched_text = text[start_pos:end_pos] if not case_sensitive else pattern
                
                return MatchResult(
                    pattern=matched_text,
                    start_pos=start_pos,
                    end_pos=end_pos,
                    pattern_id=pattern_id
                )
        
        return None
    
    def contains(self, text: str, case_sensitive: bool = True) -> bool:
        """
        检查文本是否包含任何模式
        
        Args:
            text: 待检查的文本
            case_sensitive: 是否大小写敏感
            
        Returns:
            是否包含匹配
        """
        return self.search_first(text, case_sensitive) is not None
    
    def replace(self, text: str, replacement: str = "*", case_sensitive: bool = True) -> str:
        """
        替换文本中的匹配模式
        
        Args:
            text: 原始文本
            replacement: 替换字符，默认为*
            case_sensitive: 是否大小写敏感
            
        Returns:
            替换后的文本
        """
        if not text:
            return text
        
        matches = self.search(text, case_sensitive)
        if not matches:
            return text
        
        # 按位置倒序排列，避免替换时位置偏移
        matches.sort(key=lambda x: x.start_pos, reverse=True)
        
        result = text
        for match in matches:
            # 根据原字符长度生成替换字符
            replace_text = replacement * (match.end_pos - match.start_pos)
            result = result[:match.start_pos] + replace_text + result[match.end_pos:]
        
        return result
    
    def get_pattern_info(self, pattern_id: int) -> Optional[Dict]:
        """获取模式信息"""
        return self.pattern_info.get(pattern_id)
    
    def get_pattern_count(self) -> int:
        """获取模式数量"""
        return len(self.patterns)
    
    def clear(self) -> None:
        """清空所有模式"""
        self.root = TrieNode()
        self.patterns.clear()
        self.pattern_info.clear()
        self._built = False
    
    def get_statistics(self) -> Dict[str, int]:
        """获取统计信息"""
        def count_nodes(node: TrieNode) -> int:
            count = 1
            for child in node.children.values():
                count += count_nodes(child)
            return count
        
        return {
            'pattern_count': len(self.patterns),
            'node_count': count_nodes(self.root),
            'built': self._built
        }