"""名单领域服务"""
from typing import List, Optional, Set
from dataclasses import dataclass

from src.domain.wordlist.entities import WordList
from src.domain.wordlist.repositories import WordListRepository
from src.shared.enums.list_enums import ListTypeEnum, MatchRuleEnum, RiskTypeEnum
from src.shared.exceptions.domain_exceptions import (
    WordListConflictError, 
    WordListBusinessRuleViolationError
)


@dataclass
class ConflictAnalysisResult:
    """冲突分析结果"""
    has_conflict: bool
    conflict_type: str
    conflicting_wordlists: List[WordList]
    severity_level: int  # 1-低, 2-中, 3-高
    recommendation: str


class WordListDomainService:
    """名单领域服务"""
    
    def __init__(self, wordlist_repository: WordListRepository):
        self._wordlist_repository = wordlist_repository
    
    async def analyze_conflicts(
        self, 
        candidate_wordlist: WordList,
        exclude_id: int = None
    ) -> ConflictAnalysisResult:
        """分析名单冲突"""
        
        # 获取相同匹配规则的所有激活名单
        existing_wordlists = await self._wordlist_repository.find_by_match_rule(
            candidate_wordlist.match_rule,
            include_deleted=False
        )
        
        # 排除指定ID（用于更新场景）
        if exclude_id:
            existing_wordlists = [wl for wl in existing_wordlists if wl.id != exclude_id]
        
        conflicting_wordlists = []
        conflict_type = ""
        severity_level = 1
        
        for existing in existing_wordlists:
            if existing.is_active():
                # 检查名称冲突
                if (existing.list_name.value == candidate_wordlist.list_name.value):
                    conflict_type = "name_conflict"
                    conflicting_wordlists.append(existing)
                    severity_level = max(severity_level, 3)  # 高优先级冲突
                
                # 检查类型冲突（黑白名单互斥）
                elif self._are_conflicting_types(
                    existing.list_type, 
                    candidate_wordlist.list_type
                ):
                    conflict_type = "type_conflict"
                    conflicting_wordlists.append(existing)
                    severity_level = max(severity_level, 2)  # 中优先级冲突
        
        has_conflict = len(conflicting_wordlists) > 0
        recommendation = self._generate_recommendation(
            conflict_type, 
            severity_level, 
            conflicting_wordlists
        )
        
        return ConflictAnalysisResult(
            has_conflict=has_conflict,
            conflict_type=conflict_type,
            conflicting_wordlists=conflicting_wordlists,
            severity_level=severity_level,
            recommendation=recommendation
        )
    
    async def validate_business_rules(self, wordlist: WordList) -> None:
        """验证业务规则"""
        
        # 规则1: 检查风险类型与名单类型的匹配性
        self._validate_risk_type_consistency(wordlist)
        
        # 规则2: 检查匹配规则的合理性
        self._validate_match_rule_consistency(wordlist)
        
        # 规则3: 检查名单数量限制
        await self._validate_wordlist_count_limits(wordlist)
    
    async def suggest_optimal_configuration(
        self, 
        wordlist: WordList
    ) -> Dict[str, Any]:
        """建议最优配置"""
        
        suggestions = {
            "suggested_risk_type": None,
            "suggested_match_rule": None,
            "optimization_tips": [],
            "performance_impact": "low"
        }
        
        # 基于现有名单分析最优配置
        similar_wordlists = await self._wordlist_repository.find_by_type(
            wordlist.list_type,
            include_deleted=False
        )
        
        if similar_wordlists:
            # 分析最常用的匹配规则
            match_rule_counts = {}
            risk_type_counts = {}
            
            for wl in similar_wordlists:
                match_rule_counts[wl.match_rule] = match_rule_counts.get(wl.match_rule, 0) + 1
                risk_type_counts[wl.risk_level.risk_type] = risk_type_counts.get(wl.risk_level.risk_type, 0) + 1
            
            # 推荐最常用的配置
            if match_rule_counts:
                most_common_match_rule = max(match_rule_counts, key=match_rule_counts.get)
                if most_common_match_rule != wordlist.match_rule:
                    suggestions["suggested_match_rule"] = most_common_match_rule
                    suggestions["optimization_tips"].append(
                        f"建议使用匹配规则 {most_common_match_rule.name}，与现有 {match_rule_counts[most_common_match_rule]} 个名单保持一致"
                    )
            
            if risk_type_counts:
                most_common_risk_type = max(risk_type_counts, key=risk_type_counts.get)
                if most_common_risk_type != wordlist.risk_level.risk_type:
                    suggestions["suggested_risk_type"] = most_common_risk_type
                    suggestions["optimization_tips"].append(
                        f"建议使用风险类型 {most_common_risk_type.name}，与现有 {risk_type_counts[most_common_risk_type]} 个名单保持一致"
                    )
        
        # 性能影响评估
        suggestions["performance_impact"] = self._assess_performance_impact(wordlist)
        
        return suggestions
    
    async def batch_validate_wordlists(
        self, 
        wordlists: List[WordList]
    ) -> Dict[int, List[str]]:
        """批量验证名单"""
        
        validation_results = {}
        
        for wordlist in wordlists:
            errors = []
            
            try:
                await self.validate_business_rules(wordlist)
            except WordListBusinessRuleViolationError as e:
                errors.append(e.message)
            
            # 检查批次内冲突
            batch_conflicts = self._check_batch_internal_conflicts(
                wordlist, 
                wordlists
            )
            errors.extend(batch_conflicts)
            
            if errors:
                validation_results[wordlist.id] = errors
        
        return validation_results
    
    def _are_conflicting_types(
        self, 
        type1: ListTypeEnum, 
        type2: ListTypeEnum
    ) -> bool:
        """检查两个名单类型是否冲突"""
        # 黑名单和白名单互斥
        conflicting_pairs = [
            (ListTypeEnum.BLACKLIST, ListTypeEnum.WHITELIST),
            (ListTypeEnum.WHITELIST, ListTypeEnum.BLACKLIST)
        ]
        
        return (type1, type2) in conflicting_pairs
    
    def _validate_risk_type_consistency(self, wordlist: WordList) -> None:
        """验证风险类型一致性"""
        
        # 白名单通常不应该有高风险类型
        if (wordlist.list_type == ListTypeEnum.WHITELIST and 
            wordlist.risk_level.risk_type in [
                RiskTypeEnum.BLACK_ACCOUNT, 
                RiskTypeEnum.BLACK_IP,
                RiskTypeEnum.HIGH_RISK_ACCOUNT, 
                RiskTypeEnum.HIGH_RISK_IP
            ]):
            raise WordListBusinessRuleViolationError(
                "risk_type_consistency",
                "白名单不应该使用高风险类型",
                {
                    "list_type": wordlist.list_type.name,
                    "risk_type": wordlist.risk_level.risk_type.name
                }
            )
    
    def _validate_match_rule_consistency(self, wordlist: WordList) -> None:
        """验证匹配规则一致性"""
        
        # IP类型的名单应该使用IP匹配规则
        if (wordlist.risk_level.risk_type in [RiskTypeEnum.BLACK_IP, RiskTypeEnum.HIGH_RISK_IP] and
            wordlist.match_rule != MatchRuleEnum.IP):
            raise WordListBusinessRuleViolationError(
                "match_rule_consistency", 
                "IP风险类型应该使用IP匹配规则",
                {
                    "risk_type": wordlist.risk_level.risk_type.name,
                    "match_rule": wordlist.match_rule.name
                }
            )
    
    async def _validate_wordlist_count_limits(self, wordlist: WordList) -> None:
        """验证名单数量限制"""
        
        # 检查同类型名单数量限制（假设每种类型最多1000个）
        count = await self._wordlist_repository.count_by_type(wordlist.list_type)
        
        if count >= 1000:
            raise WordListBusinessRuleViolationError(
                "count_limit",
                f"同类型名单数量已达上限: {count}/1000",
                {
                    "list_type": wordlist.list_type.name,
                    "current_count": count,
                    "limit": 1000
                }
            )
    
    def _generate_recommendation(
        self, 
        conflict_type: str, 
        severity_level: int,
        conflicting_wordlists: List[WordList]
    ) -> str:
        """生成推荐建议"""
        
        if not conflicting_wordlists:
            return "无冲突，可以安全创建"
        
        if conflict_type == "name_conflict":
            return f"名称冲突：建议修改名单名称，避免与现有 {len(conflicting_wordlists)} 个名单重复"
        elif conflict_type == "type_conflict":
            return f"类型冲突：建议检查名单类型设置，避免与现有 {len(conflicting_wordlists)} 个名单产生业务冲突"
        else:
            return f"发现 {len(conflicting_wordlists)} 个潜在冲突，建议详细检查"
    
    def _assess_performance_impact(self, wordlist: WordList) -> str:
        """评估性能影响"""
        
        # 基于匹配规则评估性能影响
        high_impact_rules = [MatchRuleEnum.TEXT, MatchRuleEnum.TEXT_AND_NAME]
        medium_impact_rules = [MatchRuleEnum.NICKNAME]
        
        if wordlist.match_rule in high_impact_rules:
            return "high"
        elif wordlist.match_rule in medium_impact_rules:
            return "medium"
        else:
            return "low"
    
    def _check_batch_internal_conflicts(
        self, 
        target_wordlist: WordList,
        all_wordlists: List[WordList]
    ) -> List[str]:
        """检查批次内部冲突"""
        
        conflicts = []
        
        for other_wordlist in all_wordlists:
            if (other_wordlist != target_wordlist and 
                other_wordlist.list_name.value == target_wordlist.list_name.value):
                conflicts.append(f"与批次中另一个名单名称冲突: {other_wordlist.list_name.value}")
        
        return conflicts