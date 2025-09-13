"""基础设施异常定义"""
from typing import Any, Dict, Optional
from .base_exceptions import InfrastructureException, ErrorCode


class DatabaseError(InfrastructureException):
    """数据库异常"""
    
    def __init__(self, message: str, operation: str, details: Dict[str, Any] = None):
        self.operation = operation
        exception_details = {
            "operation": operation,
            **(details or {})
        }
        super().__init__(
            f"数据库操作失败 [{operation}]: {message}",
            ErrorCode.DATABASE_ERROR,
            exception_details
        )


class DatabaseConnectionError(InfrastructureException):
    """数据库连接异常"""
    
    def __init__(self, connection_string: str = None, cause: Exception = None):
        self.connection_string = connection_string
        details = {}
        if connection_string:
            # 隐藏敏感信息
            safe_connection = connection_string.split('@')[-1] if '@' in connection_string else connection_string
            details["connection"] = safe_connection
        
        super().__init__(
            "数据库连接失败",
            ErrorCode.DATABASE_CONNECTION_ERROR,
            details,
            cause
        )


class DatabaseTransactionError(InfrastructureException):
    """数据库事务异常"""
    
    def __init__(self, message: str, transaction_id: str = None, cause: Exception = None):
        self.transaction_id = transaction_id
        details = {}
        if transaction_id:
            details["transaction_id"] = transaction_id
        
        super().__init__(
            f"数据库事务失败: {message}",
            ErrorCode.DATABASE_TRANSACTION_ERROR,
            details,
            cause
        )


class RepositoryError(InfrastructureException):
    """仓储异常"""
    
    def __init__(self, repository_name: str, operation: str, message: str, cause: Exception = None):
        self.repository_name = repository_name
        self.operation = operation
        details = {
            "repository": repository_name,
            "operation": operation
        }
        super().__init__(
            f"仓储操作失败 [{repository_name}.{operation}]: {message}",
            ErrorCode.DATABASE_ERROR,
            details,
            cause
        )


class ExternalServiceError(InfrastructureException):
    """外部服务异常"""
    
    def __init__(
        self, 
        service_name: str, 
        message: str, 
        status_code: int = None,
        response_data: Any = None,
        cause: Exception = None
    ):
        self.service_name = service_name
        self.status_code = status_code
        self.response_data = response_data
        
        details = {
            "service": service_name,
        }
        if status_code:
            details["status_code"] = status_code
        if response_data:
            details["response_data"] = response_data
        
        super().__init__(
            f"外部服务调用失败 [{service_name}]: {message}",
            ErrorCode.EXTERNAL_SERVICE_ERROR,
            details,
            cause
        )


class CacheError(InfrastructureException):
    """缓存异常"""
    
    def __init__(self, operation: str, key: str = None, message: str = None, cause: Exception = None):
        self.operation = operation
        self.key = key
        details = {
            "operation": operation
        }
        if key:
            details["key"] = key
        
        error_message = message or f"缓存操作失败: {operation}"
        super().__init__(
            error_message,
            ErrorCode.EXTERNAL_SERVICE_ERROR,  # 缓存可以视为外部服务
            details,
            cause
        )