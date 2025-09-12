"""领域异常定义"""


class DomainException(Exception):
    """领域异常基类"""
    
    def __init__(self, message: str, code: str = None):
        self.message = message
        self.code = code
        super().__init__(message)


class WordListNotFoundError(DomainException):
    """名单不存在异常"""
    
    def __init__(self, wordlist_id: int):
        super().__init__(f"WordList with ID {wordlist_id} not found", "WORDLIST_NOT_FOUND")


class AppNotFoundError(DomainException):
    """应用不存在异常"""
    
    def __init__(self, app_id: str):
        super().__init__(f"App with ID {app_id} not found", "APP_NOT_FOUND")


class InvalidListTypeError(DomainException):
    """无效名单类型异常"""
    
    def __init__(self, list_type: int):
        super().__init__(f"Invalid list type: {list_type}", "INVALID_LIST_TYPE")


class InvalidMatchRuleError(DomainException):
    """无效匹配规则异常"""
    
    def __init__(self, match_rule: int):
        super().__init__(f"Invalid match rule: {match_rule}", "INVALID_MATCH_RULE")


class InvalidRiskTypeError(DomainException):
    """无效风险类型异常"""
    
    def __init__(self, risk_type: int):
        super().__init__(f"Invalid risk type: {risk_type}", "INVALID_RISK_TYPE")


class AppAlreadyExistsError(DomainException):
    """应用已存在异常"""
    
    def __init__(self, app_id: str):
        super().__init__(f"App with ID {app_id} already exists", "APP_ALREADY_EXISTS")


class WordListValidationError(DomainException):
    """名单验证异常"""
    
    def __init__(self, field: str, value: str, reason: str):
        super().__init__(f"WordList validation failed for field '{field}' with value '{value}': {reason}", "WORDLIST_VALIDATION_ERROR")