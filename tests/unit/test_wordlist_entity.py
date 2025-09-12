"""名单实体单元测试"""
import pytest
from unittest.mock import Mock

from src.domain.wordlist.entities.wordlist import WordList
from src.domain.wordlist.value_objects.risk_level import RiskLevel
from src.shared.enums.list_enums import (
    ListTypeEnum, 
    MatchRuleEnum, 
    ListSuggestEnum, 
    RiskTypeEnum,
    LanguageEnum
)


class TestWordListEntity:
    """名单实体测试类"""

    @pytest.fixture
    def risk_level(self):
        """风险等级夹具"""
        return RiskLevel(risk_type=RiskTypeEnum.BLACK_ACCOUNT)

    def test_create_wordlist_success(self, risk_level):
        """测试成功创建名单"""
        wordlist = WordList.create(
            list_name="测试名单",
            list_type=ListTypeEnum.BLACK,
            match_rule=MatchRuleEnum.EXACT,
            suggestion=ListSuggestEnum.REJECT,
            risk_level=risk_level,
            language=LanguageEnum.CHINESE,
            created_by="test_user"
        )
        
        assert wordlist.list_name == "测试名单"
        assert wordlist.list_type == ListTypeEnum.BLACK
        assert wordlist.match_rule == MatchRuleEnum.EXACT
        assert wordlist.suggestion == ListSuggestEnum.REJECT
        assert wordlist.risk_level == risk_level
        assert wordlist.language == LanguageEnum.CHINESE
        assert wordlist.created_by == "test_user"
        assert wordlist.is_active is True

    def test_create_wordlist_with_empty_name_raises_error(self, risk_level):
        """测试空名称创建名单抛出异常"""
        with pytest.raises(ValueError, match="名单名称不能为空"):
            WordList.create(
                list_name="",
                list_type=ListTypeEnum.BLACK,
                match_rule=MatchRuleEnum.EXACT,
                suggestion=ListSuggestEnum.REJECT,
                risk_level=risk_level,
                created_by="test_user"
            )

    def test_update_wordlist_success(self, risk_level):
        """测试成功更新名单"""
        wordlist = WordList.create(
            list_name="原始名单",
            list_type=ListTypeEnum.BLACK,
            match_rule=MatchRuleEnum.EXACT,
            suggestion=ListSuggestEnum.REJECT,
            risk_level=risk_level,
            created_by="test_user"
        )
        
        wordlist.update(
            list_name="更新名单",
            suggestion=ListSuggestEnum.MONITOR,
            updated_by="updater"
        )
        
        assert wordlist.list_name == "更新名单"
        assert wordlist.suggestion == ListSuggestEnum.MONITOR
        assert wordlist.updated_by == "updater"

    def test_deactivate_wordlist(self, risk_level):
        """测试停用名单"""
        wordlist = WordList.create(
            list_name="测试名单",
            list_type=ListTypeEnum.BLACK,
            match_rule=MatchRuleEnum.EXACT,
            suggestion=ListSuggestEnum.REJECT,
            risk_level=risk_level,
            created_by="test_user"
        )
        
        wordlist.deactivate("admin")
        
        assert wordlist.is_active is False
        assert wordlist.updated_by == "admin"

    def test_activate_wordlist(self, risk_level):
        """测试激活名单"""
        wordlist = WordList.create(
            list_name="测试名单",
            list_type=ListTypeEnum.BLACK,
            match_rule=MatchRuleEnum.EXACT,
            suggestion=ListSuggestEnum.REJECT,
            risk_level=risk_level,
            created_by="test_user"
        )
        
        wordlist.deactivate("admin")
        wordlist.activate("admin2")
        
        assert wordlist.is_active is True
        assert wordlist.updated_by == "admin2"