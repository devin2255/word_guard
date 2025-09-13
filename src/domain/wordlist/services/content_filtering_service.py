"""内容过滤领域服务"""
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

from src.domain.wordlist.entities import WordList
from src.domain.wordlist.repositories import WordListRepository
from src.shared.enums.list_enums import ListTypeEnum, MatchRuleEnum, ListSuggestEnum, LanguageEnum


class FilterResult(Enum):
    """过滤结果"""
    PASS = "pass"           # 通过
    REJECT = "reject"       # 拒绝  
    REVIEW = "review"       # 需要审核


@dataclass
class ContentMatch:
    """内容匹配结果"""
    wordlist: WordList
    match_type: MatchRuleEnum
    matched_content: str
    confidence: float  # 匹配置信度 0-1


@dataclass
class FilteringResult:
    """过滤结果"""
    result: FilterResult
    matches: List[ContentMatch]
    reason: str
    risk_score: float  # 风险评分 0-1
    suggestion: ListSuggestEnum
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "result": self.result.value,
            "reason": self.reason,
            "risk_score": self.risk_score,
            "suggestion": self.suggestion.value,
            "matches": [
                {
                    "wordlist_id": match.wordlist.id,
                    "wordlist_name": str(match.wordlist.list_name),
                    "match_type": match.match_type.value,
                    "matched_content": match.matched_content,
                    "confidence": match.confidence
                }
                for match in self.matches
            ]
        }


@dataclass
class ContentInput:
    """内容输入"""
    text: Optional[str] = None
    nickname: Optional[str] = None
    ip_address: Optional[str] = None
    account_id: Optional[str] = None
    role_id: Optional[str] = None
    device_fingerprint: Optional[str] = None
    language: LanguageEnum = LanguageEnum.ALL
    
    def get_content_by_match_rule(self, match_rule: MatchRuleEnum) -> Optional[str]:
        """根据匹配规则获取对应内容"""
        rule_mapping = {
            MatchRuleEnum.TEXT: self.text,
            MatchRuleEnum.NICKNAME: self.nickname,
            MatchRuleEnum.IP: self.ip_address,
            MatchRuleEnum.ACCOUNT: self.account_id,
            MatchRuleEnum.ROLE_ID: self.role_id,
            MatchRuleEnum.FINGERPRINT: self.device_fingerprint,
            MatchRuleEnum.TEXT_AND_NAME: f"{self.text or ''} {self.nickname or ''}".strip()
        }
        return rule_mapping.get(match_rule)


class ContentFilteringService:
    """内容过滤领域服务"""
    
    def __init__(self, wordlist_repository: WordListRepository):
        self._wordlist_repository = wordlist_repository
    
    async def filter_content(
        self, 
        content_input: ContentInput
    ) -> FilteringResult:
        """过滤内容"""
        
        # 获取所有激活的名单
        active_wordlists = await self._wordlist_repository.find_active_lists()
        
        # 过滤适用的名单（语言匹配）
        applicable_wordlists = self._filter_applicable_wordlists(
            active_wordlists, 
            content_input.language
        )
        
        # 执行匹配检查
        matches = await self._perform_matching(content_input, applicable_wordlists)
        
        # 计算最终结果
        result = self._calculate_final_result(matches)
        
        return result
    
    async def batch_filter_content(
        self, 
        content_inputs: List[ContentInput]
    ) -> List[FilteringResult]:
        """批量过滤内容"""
        
        results = []
        
        # 预加载所有激活的名单
        active_wordlists = await self._wordlist_repository.find_active_lists()
        
        for content_input in content_inputs:
            applicable_wordlists = self._filter_applicable_wordlists(
                active_wordlists, 
                content_input.language
            )
            
            matches = await self._perform_matching(content_input, applicable_wordlists)
            result = self._calculate_final_result(matches)
            
            results.append(result)
        
        return results
    
    async def get_matching_statistics(
        self, 
        wordlist_ids: List[int] = None
    ) -> Dict[str, Any]:
        """获取匹配统计信息"""
        
        if wordlist_ids:
            wordlists = []
            for wl_id in wordlist_ids:
                wl = await self._wordlist_repository.find_by_id(wl_id)
                if wl:
                    wordlists.append(wl)
        else:
            wordlists = await self._wordlist_repository.find_active_lists()
        
        stats = {
            "total_wordlists": len(wordlists),
            "by_type": {},
            "by_match_rule": {},
            "by_risk_type": {},
            "by_language": {}
        }
        
        for wordlist in wordlists:
            # 按类型统计
            list_type = wordlist.list_type.name
            stats["by_type"][list_type] = stats["by_type"].get(list_type, 0) + 1
            
            # 按匹配规则统计
            match_rule = wordlist.match_rule.name
            stats["by_match_rule"][match_rule] = stats["by_match_rule"].get(match_rule, 0) + 1
            
            # 按风险类型统计
            risk_type = wordlist.risk_level.risk_type.name
            stats["by_risk_type"][risk_type] = stats["by_risk_type"].get(risk_type, 0) + 1
            
            # 按语言统计
            language = wordlist.language.name
            stats["by_language"][language] = stats["by_language"].get(language, 0) + 1
        
        return stats
    
    def _filter_applicable_wordlists(
        self, 
        wordlists: List[WordList], 
        content_language: LanguageEnum
    ) -> List[WordList]:
        """过滤适用的名单"""
        
        applicable = []
        
        for wordlist in wordlists:
            # 检查语言匹配
            if (wordlist.language == LanguageEnum.ALL or 
                wordlist.language == content_language):
                applicable.append(wordlist)
        
        return applicable
    
    async def _perform_matching(
        self, 
        content_input: ContentInput,
        wordlists: List[WordList]
    ) -> List[ContentMatch]:
        """执行匹配检查"""
        
        matches = []
        
        for wordlist in wordlists:
            # 获取要检查的内容
            content_to_check = content_input.get_content_by_match_rule(
                wordlist.match_rule
            )
            
            if not content_to_check:
                continue
            
            # 执行匹配（这里简化为包含匹配，实际可以更复杂）
            matched_content, confidence = self._check_content_match(
                content_to_check,
                wordlist
            )
            
            if matched_content:
                matches.append(ContentMatch(
                    wordlist=wordlist,
                    match_type=wordlist.match_rule,
                    matched_content=matched_content,
                    confidence=confidence
                ))
        
        return matches
    
    def _check_content_match(
        self, 
        content: str, 
        wordlist: WordList
    ) -> Tuple[Optional[str], float]:
        """检查内容匹配"""
        
        # 简化的匹配逻辑（实际应该更复杂）
        wordlist_name = str(wordlist.list_name).lower()
        content_lower = content.lower()
        
        if wordlist_name in content_lower:
            # 计算置信度（基于匹配长度比例）
            confidence = min(len(wordlist_name) / len(content), 1.0)
            return wordlist_name, confidence
        
        return None, 0.0
    
    def _calculate_final_result(self, matches: List[ContentMatch]) -> FilteringResult:
        """计算最终过滤结果"""
        
        if not matches:
            return FilteringResult(
                result=FilterResult.PASS,
                matches=[],
                reason="未匹配到任何名单规则",
                risk_score=0.0,
                suggestion=ListSuggestEnum.PASS
            )
        
        # 按名单类型分组
        whitelist_matches = []
        blacklist_matches = []
        ignore_matches = []
        
        for match in matches:
            if match.wordlist.list_type == ListTypeEnum.WHITELIST:
                whitelist_matches.append(match)
            elif match.wordlist.list_type == ListTypeEnum.BLACKLIST:
                blacklist_matches.append(match)
            else:  # IGNORELIST
                ignore_matches.append(match)
        
        # 决策逻辑
        if blacklist_matches:
            # 有黑名单匹配，计算风险评分
            max_confidence = max(match.confidence for match in blacklist_matches)
            risk_score = self._calculate_risk_score(blacklist_matches)
            
            highest_risk_match = max(
                blacklist_matches, 
                key=lambda m: self._get_risk_weight(m.wordlist.risk_level.risk_type)
            )
            
            return FilteringResult(
                result=FilterResult.REJECT if risk_score > 0.7 else FilterResult.REVIEW,
                matches=matches,
                reason=f"匹配到黑名单: {highest_risk_match.wordlist.list_name}",
                risk_score=risk_score,
                suggestion=highest_risk_match.wordlist.suggestion
            )
        
        elif whitelist_matches:
            # 有白名单匹配
            return FilteringResult(
                result=FilterResult.PASS,
                matches=matches,
                reason=f"匹配到白名单: {whitelist_matches[0].wordlist.list_name}",
                risk_score=0.0,
                suggestion=ListSuggestEnum.PASS
            )
        
        else:
            # 只有忽略名单匹配
            return FilteringResult(
                result=FilterResult.PASS,
                matches=matches,
                reason="匹配到忽略名单，放行",
                risk_score=0.0,
                suggestion=ListSuggestEnum.PASS
            )
    
    def _calculate_risk_score(self, matches: List[ContentMatch]) -> float:
        """计算风险评分"""
        
        if not matches:
            return 0.0
        
        # 基于匹配数量和置信度计算
        total_score = 0.0
        total_weight = 0.0
        
        for match in matches:
            risk_weight = self._get_risk_weight(match.wordlist.risk_level.risk_type)
            confidence_weight = match.confidence
            
            score = risk_weight * confidence_weight
            total_score += score
            total_weight += risk_weight
        
        return min(total_score / max(total_weight, 1.0), 1.0)
    
    def _get_risk_weight(self, risk_type) -> float:
        """获取风险类型权重"""
        
        # 不同风险类型的权重
        weights = {
            "NORMAL": 0.1,
            "POLITICS": 0.9,
            "PORN": 0.8,
            "ABUSE": 0.7,
            "AD": 0.4,
            "MEANINGLESS": 0.3,
            "PROHIBIT": 0.9,
            "OTHER": 0.5,
            "BLACK_ACCOUNT": 0.9,
            "BLACK_IP": 0.9,
            "HIGH_RISK_ACCOUNT": 0.8,
            "HIGH_RISK_IP": 0.8,
            "CUSTOM": 0.6
        }
        
        return weights.get(risk_type.name, 0.5)