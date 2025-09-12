"""名单测试数据夹具"""
import pytest
from typing import Dict, Any

from src.shared.enums.list_enums import (
    ListTypeEnum, 
    MatchRuleEnum, 
    ListSuggestEnum, 
    RiskTypeEnum,
    LanguageEnum
)


@pytest.fixture
def valid_wordlist_data() -> Dict[str, Any]:
    """有效的名单创建数据"""
    return {
        "list_name": "测试黑名单",
        "list_type": ListTypeEnum.BLACK.value,
        "match_rule": MatchRuleEnum.EXACT.value,
        "suggestion": ListSuggestEnum.REJECT.value,
        "risk_type": RiskTypeEnum.BLACK_ACCOUNT.value,
        "language": LanguageEnum.CHINESE.value,
        "created_by": "test_user"
    }


@pytest.fixture
def invalid_wordlist_data() -> Dict[str, Any]:
    """无效的名单创建数据"""
    return {
        "list_name": "",  # 空名称
        "list_type": 999,  # 无效类型
        "match_rule": -1,  # 无效规则
        "suggestion": None,  # 空值
        "risk_type": "invalid",  # 错误类型
    }


@pytest.fixture
def wordlist_update_data() -> Dict[str, Any]:
    """名单更新数据"""
    return {
        "list_name": "更新后的名单",
        "suggestion": ListSuggestEnum.MONITOR.value,
        "updated_by": "test_updater"
    }