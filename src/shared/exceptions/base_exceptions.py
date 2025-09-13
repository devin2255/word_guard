"""基础异常类"""
from typing import Any, Dict, Optional
from enum import Enum


class ErrorCode(Enum):
    """错误码枚举"""
    
    # 通用错误 1000-1999
    UNKNOWN_ERROR = 1000
    VALIDATION_ERROR = 1001
    NOT_FOUND_ERROR = 1002
    PERMISSION_DENIED = 1003
    RATE_LIMITED = 1004
    
    # 领域错误 2000-2999
    DOMAIN_VALIDATION_ERROR = 2000
    BUSINESS_RULE_VIOLATION = 2001
    AGGREGATE_NOT_FOUND = 2002
    AGGREGATE_CONFLICT = 2003
    
    # 基础设施错误 3000-3999
    DATABASE_ERROR = 3000
    DATABASE_CONNECTION_ERROR = 3001
    DATABASE_TRANSACTION_ERROR = 3002
    EXTERNAL_SERVICE_ERROR = 3003
    
    # 应用错误 4000-4999
    COMMAND_VALIDATION_ERROR = 4000
    QUERY_VALIDATION_ERROR = 4001
    HANDLER_ERROR = 4002
    
    # 接口错误 5000-5999
    REQUEST_VALIDATION_ERROR = 5000
    RESPONSE_SERIALIZATION_ERROR = 5001
    AUTHENTICATION_ERROR = 5002
    AUTHORIZATION_ERROR = 5003


class BaseException(Exception):
    """基础异常类"""
    
    def __init__(
        self,
        message: str,
        error_code: ErrorCode = ErrorCode.UNKNOWN_ERROR,
        details: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        self.cause = cause
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "message": self.message,
            "error_code": self.error_code.value,
            "error_name": self.error_code.name,
            "details": self.details
        }
    
    def __str__(self) -> str:
        return f"[{self.error_code.name}] {self.message}"
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(message='{self.message}', error_code={self.error_code})"


class DomainException(BaseException):
    """领域异常基类"""
    
    def __init__(
        self,
        message: str,
        error_code: ErrorCode = ErrorCode.DOMAIN_VALIDATION_ERROR,
        details: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None
    ):
        super().__init__(message, error_code, details, cause)


class ApplicationException(BaseException):
    """应用层异常基类"""
    
    def __init__(
        self,
        message: str,
        error_code: ErrorCode = ErrorCode.HANDLER_ERROR,
        details: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None
    ):
        super().__init__(message, error_code, details, cause)


class InfrastructureException(BaseException):
    """基础设施异常基类"""
    
    def __init__(
        self,
        message: str,
        error_code: ErrorCode = ErrorCode.DATABASE_ERROR,
        details: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None
    ):
        super().__init__(message, error_code, details, cause)


class InterfaceException(BaseException):
    """接口异常基类"""
    
    def __init__(
        self,
        message: str,
        error_code: ErrorCode = ErrorCode.REQUEST_VALIDATION_ERROR,
        details: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None
    ):
        super().__init__(message, error_code, details, cause)