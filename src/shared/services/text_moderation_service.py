"""文本风控领域服务"""
import time
import logging
from typing import List, Dict, Optional, Set, Tuple
from datetime import datetime

from src.shared.algorithms import AhoCorasickAutomaton
from src.domain.wordlist.repositories import WordListRepository
from src.domain.listdetail.repositories import ListDetailRepository
from src.domain.association.repositories import AssociationRepository
from src.shared.enums.list_enums import ListTypeEnum, MatchRuleEnum, RiskTypeEnum, ListSuggestEnum
from src.shared.value_objects import (
    MatchedWordInfo,
    ContentCheckResult,
    ModerationResultStatus
)

logger = logging.getLogger(__name__)


class TextModerationService:
    """文本风控领域服务"""
    
    def __init__(
        self,
        wordlist_repository: WordListRepository,
        listdetail_repository: ListDetailRepository,
        association_repository: AssociationRepository
    ):
        self._wordlist_repository = wordlist_repository
        self._listdetail_repository = listdetail_repository
        self._association_repository = association_repository
        
        # AC自动机实例 - 按匹配规则分类
        self._ac_machines: Dict[MatchRuleEnum, AhoCorasickAutomaton] = {}
        
        # 缓存相关
        self._last_reload_time: Optional[datetime] = None
        self._cache_valid_duration = 300  # 5分钟缓存有效期
        
        # 统计信息
        self._total_checks = 0
        self._violation_checks = 0
    
    async def initialize(self, app_id: Optional[int] = None) -> None:
        """
        初始化服务，加载敏感词到AC自动机
        
        Args:
            app_id: 应用ID，如果指定则只加载该应用关联的敏感词
        """
        start_time = time.time()
        logger.info(f"开始初始化文本风控服务，应用ID: {app_id}")
        
        try:
            # 清空现有AC自动机
            self._ac_machines.clear()
            
            # 获取有效的名单
            wordlists = await self._get_active_wordlists(app_id)
            
            if not wordlists:
                logger.warning("未找到有效的名单数据")
                return
            
            # 按匹配规则分组加载敏感词
            for match_rule in MatchRuleEnum:
                await self._load_patterns_for_rule(wordlists, match_rule)
            
            self._last_reload_time = datetime.now()
            load_time = (time.time() - start_time) * 1000
            
            logger.info(
                f"文本风控服务初始化完成，耗时: {load_time:.2f}ms, "
                f"加载名单数: {len(wordlists)}, "
                f"AC自动机数: {len(self._ac_machines)}"
            )
            
        except Exception as e:
            logger.error(f"初始化文本风控服务失败: {e}", exc_info=True)
            raise
    
    async def _get_active_wordlists(self, app_id: Optional[int] = None) -> List:
        """获取有效的名单列表"""
        if app_id:
            # 获取应用关联的名单
            associations = await self._association_repository.find_by_app_id(
                app_id, active_only=True
            )
            wordlist_ids = [assoc.wordlist_id for assoc in associations]
            
            if wordlist_ids:
                wordlists = []
                for wordlist_id in wordlist_ids:
                    wordlist = await self._wordlist_repository.find_by_id(wordlist_id)
                    if wordlist and wordlist.is_active():
                        wordlists.append(wordlist)
                return wordlists
            else:
                return []
        else:
            # 获取所有激活的名单
            return await self._wordlist_repository.find_all(include_deleted=False)
    
    async def _load_patterns_for_rule(self, wordlists: List, match_rule: MatchRuleEnum) -> None:
        """为特定匹配规则加载模式"""
        # 筛选符合匹配规则的名单
        filtered_wordlists = [
            wl for wl in wordlists 
            if wl.match_rule == match_rule and wl.is_active()
        ]
        
        if not filtered_wordlists:
            return
        
        # 创建AC自动机
        ac_machine = AhoCorasickAutomaton()
        pattern_count = 0
        
        # 加载每个名单的详情
        for wordlist in filtered_wordlists:
            try:
                details = await self._listdetail_repository.find_by_wordlist_id(
                    wordlist.id, active_only=True
                )
                
                for detail in details:
                    if detail.is_active and detail.processed_text:
                        # 添加模式到AC自动机
                        pattern_id = ac_machine.add_pattern(
                            detail.processed_text,
                            pattern_id=detail.id,
                            wordlist_id=wordlist.id,
                            wordlist_name=str(wordlist.list_name) if wordlist.list_name else "",
                            list_type=wordlist.list_type.value,
                            risk_type=wordlist.risk_level.risk_type.value,
                            suggestion=wordlist.suggestion.value,
                            detail_id=detail.id,
                            original_text=detail.original_text
                        )
                        pattern_count += 1
                        
            except Exception as e:
                logger.error(f"加载名单 {wordlist.id} 的详情失败: {e}")
                continue
        
        if pattern_count > 0:
            # 构建失效函数
            ac_machine.build_failure_function()
            self._ac_machines[match_rule] = ac_machine
            
            logger.info(
                f"匹配规则 {match_rule.name} 加载完成，"
                f"名单数: {len(filtered_wordlists)}, 模式数: {pattern_count}"
            )
    
    async def check_text(
        self,
        text: str,
        match_rules: List[MatchRuleEnum] = None,
        case_sensitive: bool = False
    ) -> ContentCheckResult:
        """
        检查单个文本
        
        Args:
            text: 待检查的文本
            match_rules: 匹配规则列表，默认使用文本匹配
            case_sensitive: 是否大小写敏感
            
        Returns:
            内容检测结果
        """
        start_time = time.time()
        
        if not text or not text.strip():
            return ContentCheckResult(
                content=text,
                content_type="text",
                is_violation=False,
                risk_level=0,
                matched_words=[]
            )
        
        # 默认使用文本匹配规则
        if match_rules is None:
            match_rules = [MatchRuleEnum.TEXT]
        
        all_matched_words = []
        max_risk_level = 0
        is_violation = False
        
        # 对每个匹配规则进行检查
        for match_rule in match_rules:
            if match_rule not in self._ac_machines:
                continue
            
            ac_machine = self._ac_machines[match_rule]
            matches = ac_machine.search(text, case_sensitive)
            
            # 转换匹配结果
            for match in matches:
                pattern_info = ac_machine.get_pattern_info(match.pattern_id)
                if not pattern_info:
                    continue
                
                # 创建匹配词信息
                matched_word = MatchedWordInfo(
                    word=match.pattern,
                    start_pos=match.start_pos,
                    end_pos=match.end_pos,
                    wordlist_id=pattern_info.get('wordlist_id', 0),
                    wordlist_name=pattern_info.get('wordlist_name', ''),
                    risk_type=pattern_info.get('risk_type', 0),
                    risk_type_desc=self._get_risk_type_desc(pattern_info.get('risk_type', 0)),
                    suggestion=pattern_info.get('suggestion', 0)
                )
                
                all_matched_words.append(matched_word)
                
                # 更新风险等级
                risk_level = self._calculate_risk_level(
                    pattern_info.get('risk_type', 0),
                    pattern_info.get('suggestion', 0)
                )
                max_risk_level = max(max_risk_level, risk_level)
                
                # 判断是否违规
                if pattern_info.get('suggestion', 0) in [ListSuggestEnum.REJECT.value]:
                    is_violation = True
        
        # 按位置排序
        all_matched_words.sort(key=lambda x: x.start_pos)
        
        # 生成处理后的内容（替换敏感词）
        processed_content = self._replace_sensitive_words(text, all_matched_words)
        
        # 统计
        self._total_checks += 1
        if is_violation:
            self._violation_checks += 1
        
        process_time = (time.time() - start_time) * 1000
        logger.debug(f"文本检查完成，耗时: {process_time:.2f}ms，匹配数: {len(all_matched_words)}")
        
        return ContentCheckResult(
            content=text,
            content_type="text",
            is_violation=is_violation,
            risk_level=max_risk_level,
            matched_words=all_matched_words,
            processed_content=processed_content if processed_content != text else None
        )
    
    async def check_nickname(
        self,
        nickname: str,
        case_sensitive: bool = False
    ) -> ContentCheckResult:
        """
        检查用户昵称
        
        Args:
            nickname: 用户昵称
            case_sensitive: 是否大小写敏感
            
        Returns:
            内容检测结果
        """
        # 昵称检查使用文本和昵称匹配规则
        match_rules = [MatchRuleEnum.TEXT_AND_NICKNAME, MatchRuleEnum.TEXT]
        
        result = await self.check_text(nickname, match_rules, case_sensitive)
        result.content_type = "nickname"
        
        return result
    
    async def check_comprehensive(
        self,
        nickname: str,
        content: str,
        ip_address: Optional[str] = None,
        account: Optional[str] = None,
        role_id: Optional[str] = None,
        case_sensitive: bool = False
    ) -> Tuple[Optional[ContentCheckResult], Optional[ContentCheckResult]]:
        """
        综合检查昵称和内容
        
        Args:
            nickname: 用户昵称
            content: 发言内容
            ip_address: IP地址
            account: 用户账号
            role_id: 角色ID
            case_sensitive: 是否大小写敏感
            
        Returns:
            (昵称检测结果, 内容检测结果)
        """
        nickname_result = None
        content_result = None
        
        # 检查昵称
        if nickname and nickname.strip():
            nickname_result = await self.check_nickname(nickname, case_sensitive)
        
        # 检查内容
        if content and content.strip():
            content_result = await self.check_text(content, None, case_sensitive)
        
        # TODO: 后续可以添加IP、账号、角色等其他维度的检查
        
        return nickname_result, content_result
    
    def _calculate_risk_level(self, risk_type: int, suggestion: int) -> int:
        """计算风险等级 (0-10)"""
        base_risk = {
            RiskTypeEnum.NORMAL.value: 0,
            RiskTypeEnum.POLITICAL.value: 9,
            RiskTypeEnum.PORN.value: 8,
            RiskTypeEnum.ABUSE.value: 7,
            RiskTypeEnum.ADVERTISEMENT.value: 5,
            RiskTypeEnum.VIOLENT.value: 8,
            RiskTypeEnum.TERROR.value: 10,
            RiskTypeEnum.GAMBLING.value: 6,
            RiskTypeEnum.DRUG.value: 9,
            RiskTypeEnum.OTHER.value: 3
        }.get(risk_type, 0)
        
        # 根据建议调整风险等级
        if suggestion == ListSuggestEnum.REJECT.value:
            base_risk = min(10, base_risk + 2)
        elif suggestion == ListSuggestEnum.REVIEW.value:
            base_risk = min(10, base_risk + 1)
        
        return base_risk
    
    def _get_risk_type_desc(self, risk_type: int) -> str:
        """获取风险类型描述"""
        risk_desc_map = {
            RiskTypeEnum.NORMAL.value: "正常",
            RiskTypeEnum.POLITICAL.value: "涉政",
            RiskTypeEnum.PORN.value: "色情",
            RiskTypeEnum.ABUSE.value: "辱骂",
            RiskTypeEnum.ADVERTISEMENT.value: "广告",
            RiskTypeEnum.VIOLENT.value: "暴力",
            RiskTypeEnum.TERROR.value: "恐怖主义",
            RiskTypeEnum.GAMBLING.value: "赌博",
            RiskTypeEnum.DRUG.value: "涉毒",
            RiskTypeEnum.OTHER.value: "其他"
        }
        return risk_desc_map.get(risk_type, "未知")
    
    def _replace_sensitive_words(
        self, 
        text: str, 
        matched_words: List[MatchedWordInfo], 
        replacement: str = "*"
    ) -> str:
        """替换敏感词"""
        if not matched_words:
            return text
        
        # 按位置倒序排列，避免替换时位置偏移
        sorted_matches = sorted(matched_words, key=lambda x: x.start_pos, reverse=True)
        
        result = text
        for match in sorted_matches:
            # 根据原字符长度生成替换字符
            word_length = match.end_pos - match.start_pos
            replace_text = replacement * word_length
            result = result[:match.start_pos] + replace_text + result[match.end_pos:]
        
        return result
    
    async def reload_patterns(self, app_id: Optional[int] = None) -> None:
        """重新加载敏感词模式"""
        logger.info(f"重新加载敏感词模式，应用ID: {app_id}")
        await self.initialize(app_id)
    
    def need_reload(self) -> bool:
        """检查是否需要重新加载"""
        if self._last_reload_time is None:
            return True
        
        elapsed = (datetime.now() - self._last_reload_time).total_seconds()
        return elapsed > self._cache_valid_duration
    
    def get_statistics(self) -> Dict[str, any]:
        """获取服务统计信息"""
        ac_stats = {}
        for rule, machine in self._ac_machines.items():
            ac_stats[rule.name] = machine.get_statistics()
        
        violation_rate = (
            self._violation_checks / self._total_checks 
            if self._total_checks > 0 else 0
        )
        
        return {
            'total_checks': self._total_checks,
            'violation_checks': self._violation_checks,
            'violation_rate': round(violation_rate * 100, 2),
            'last_reload_time': self._last_reload_time,
            'ac_machines': ac_stats,
            'cache_valid': not self.need_reload()
        }