"""领域异常定义"""
from typing import Any, Dict, Optional
from .base_exceptions import DomainException, ErrorCode


class WordListValidationError(DomainException):
    """名单验证错误"""
    
    def __init__(self, field: str, value: Any, message: str):
        self.field = field
        self.value = value
        details = {
            "field": field,
            "value": str(value),
            "validation_message": message
        }
        super().__init__(
            f"名单验证失败: {message}",
            ErrorCode.DOMAIN_VALIDATION_ERROR,
            details
        )


class WordListNotFoundError(DomainException):
    """名单未找到错误"""
    
    def __init__(self, wordlist_id: int):
        self.wordlist_id = wordlist_id
        details = {"wordlist_id": wordlist_id}
        super().__init__(
            f"名单不存在: ID {wordlist_id}",
            ErrorCode.AGGREGATE_NOT_FOUND,
            details
        )


class WordListConflictError(DomainException):
    """名单冲突错误"""
    
    def __init__(self, message: str, conflicting_data: Dict[str, Any]):
        self.conflicting_data = conflicting_data
        super().__init__(
            message,
            ErrorCode.AGGREGATE_CONFLICT,
            {"conflicting_data": conflicting_data}
        )


class WordListBusinessRuleViolationError(DomainException):
    """名单业务规则违反错误"""
    
    def __init__(self, rule_name: str, message: str, context: Dict[str, Any] = None):
        self.rule_name = rule_name
        self.context = context or {}
        details = {
            "rule_name": rule_name,
            "context": self.context
        }
        super().__init__(
            f"违反业务规则 '{rule_name}': {message}",
            ErrorCode.BUSINESS_RULE_VIOLATION,
            details
        )


class AppValidationError(DomainException):
    """应用验证错误"""
    
    def __init__(self, field: str, value: Any, message: str):
        self.field = field
        self.value = value
        details = {
            "field": field,
            "value": str(value),
            "validation_message": message
        }
        super().__init__(
            f"应用验证失败: {message}",
            ErrorCode.DOMAIN_VALIDATION_ERROR,
            details
        )


class AppNotFoundError(DomainException):
    """应用未找到错误"""
    
    def __init__(self, identifier: str, identifier_type: str = "app_id"):
        self.identifier = identifier
        self.identifier_type = identifier_type
        details = {
            identifier_type: identifier
        }
        super().__init__(
            f"应用不存在: {identifier_type} {identifier}",
            ErrorCode.AGGREGATE_NOT_FOUND,
            details
        )


class AppConflictError(DomainException):
    """应用冲突错误"""
    
    def __init__(self, message: str, conflicting_data: Dict[str, Any]):
        self.conflicting_data = conflicting_data
        super().__init__(
            message,
            ErrorCode.AGGREGATE_CONFLICT,
            {"conflicting_data": conflicting_data}
        )


# 保持向后兼容的简化异常类
class InvalidListTypeError(DomainException):
    """无效名单类型异常"""
    
    def __init__(self, list_type: int):
        super().__init__(
            f"无效的名单类型: {list_type}",
            ErrorCode.DOMAIN_VALIDATION_ERROR,
            {"list_type": list_type}
        )


class InvalidMatchRuleError(DomainException):
    """无效匹配规则异常"""
    
    def __init__(self, match_rule: int):
        super().__init__(
            f"无效的匹配规则: {match_rule}",
            ErrorCode.DOMAIN_VALIDATION_ERROR,
            {"match_rule": match_rule}
        )


class InvalidRiskTypeError(DomainException):
    """无效风险类型异常"""
    
    def __init__(self, risk_type: int):
        super().__init__(
            f"无效的风险类型: {risk_type}",
            ErrorCode.DOMAIN_VALIDATION_ERROR,
            {"risk_type": risk_type}
        )


class AppAlreadyExistsError(DomainException):
    """应用已存在异常"""
    
    def __init__(self, app_id: str):
        super().__init__(
            f"应用已存在: {app_id}",
            ErrorCode.AGGREGATE_CONFLICT,
            {"app_id": app_id}
        )


class AssociationValidationError(DomainException):
    """关联验证错误"""
    
    def __init__(self, field: str, value: Any, message: str):
        self.field = field
        self.value = value
        details = {
            "field": field,
            "value": str(value),
            "validation_message": message
        }
        super().__init__(
            f"关联验证失败: {message}",
            ErrorCode.DOMAIN_VALIDATION_ERROR,
            details
        )


class AssociationNotFoundError(DomainException):
    """关联未找到错误"""
    
    def __init__(self, association_id: int):
        self.association_id = association_id
        details = {"association_id": association_id}
        super().__init__(
            f"关联不存在: ID {association_id}",
            ErrorCode.AGGREGATE_NOT_FOUND,
            details
        )


class AssociationConflictError(DomainException):
    """关联冲突错误"""
    
    def __init__(self, app_id: int, wordlist_id: int):
        self.app_id = app_id
        self.wordlist_id = wordlist_id
        details = {"app_id": app_id, "wordlist_id": wordlist_id}
        super().__init__(
            f"应用 {app_id} 与名单 {wordlist_id} 的关联已存在",
            ErrorCode.AGGREGATE_CONFLICT,
            details
        )