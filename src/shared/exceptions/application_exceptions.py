"""应用层异常定义"""
from typing import Any, Dict, Optional
from .base_exceptions import ApplicationException, ErrorCode


class CommandValidationError(ApplicationException):
    """命令验证异常"""
    
    def __init__(self, command_name: str, validation_errors: Dict[str, str]):
        self.command_name = command_name
        self.validation_errors = validation_errors
        
        error_messages = [f"{field}: {message}" for field, message in validation_errors.items()]
        details = {
            "command": command_name,
            "validation_errors": validation_errors
        }
        
        super().__init__(
            f"命令验证失败 [{command_name}]: {'; '.join(error_messages)}",
            ErrorCode.COMMAND_VALIDATION_ERROR,
            details
        )


class QueryValidationError(ApplicationException):
    """查询验证异常"""
    
    def __init__(self, query_name: str, validation_errors: Dict[str, str]):
        self.query_name = query_name
        self.validation_errors = validation_errors
        
        error_messages = [f"{field}: {message}" for field, message in validation_errors.items()]
        details = {
            "query": query_name,
            "validation_errors": validation_errors
        }
        
        super().__init__(
            f"查询验证失败 [{query_name}]: {'; '.join(error_messages)}",
            ErrorCode.QUERY_VALIDATION_ERROR,
            details
        )


class CommandHandlerError(ApplicationException):
    """命令处理异常"""
    
    def __init__(self, handler_name: str, command_name: str, message: str, cause: Exception = None):
        self.handler_name = handler_name
        self.command_name = command_name
        
        details = {
            "handler": handler_name,
            "command": command_name
        }
        
        super().__init__(
            f"命令处理失败 [{handler_name}] {command_name}: {message}",
            ErrorCode.HANDLER_ERROR,
            details,
            cause
        )


class QueryHandlerError(ApplicationException):
    """查询处理异常"""
    
    def __init__(self, handler_name: str, query_name: str, message: str, cause: Exception = None):
        self.handler_name = handler_name
        self.query_name = query_name
        
        details = {
            "handler": handler_name,
            "query": query_name
        }
        
        super().__init__(
            f"查询处理失败 [{handler_name}] {query_name}: {message}",
            ErrorCode.HANDLER_ERROR,
            details,
            cause
        )


class ConcurrencyError(ApplicationException):
    """并发冲突异常"""
    
    def __init__(self, resource_type: str, resource_id: Any, message: str = None):
        self.resource_type = resource_type
        self.resource_id = resource_id
        
        details = {
            "resource_type": resource_type,
            "resource_id": str(resource_id)
        }
        
        error_message = message or f"并发冲突: {resource_type} {resource_id} 正在被其他操作修改"
        super().__init__(
            error_message,
            ErrorCode.AGGREGATE_CONFLICT,
            details
        )


class BusinessProcessError(ApplicationException):
    """业务流程异常"""
    
    def __init__(self, process_name: str, step: str, message: str, context: Dict[str, Any] = None):
        self.process_name = process_name
        self.step = step
        self.context = context or {}
        
        details = {
            "process": process_name,
            "step": step,
            "context": self.context
        }
        
        super().__init__(
            f"业务流程失败 [{process_name}] 步骤 '{step}': {message}",
            ErrorCode.HANDLER_ERROR,
            details
        )


class AuthorizationError(ApplicationException):
    """授权异常"""
    
    def __init__(self, user_id: str, action: str, resource: str = None):
        self.user_id = user_id
        self.action = action
        self.resource = resource
        
        details = {
            "user_id": user_id,
            "action": action
        }
        if resource:
            details["resource"] = resource
        
        resource_part = f" 资源: {resource}" if resource else ""
        super().__init__(
            f"用户 {user_id} 无权执行操作: {action}{resource_part}",
            ErrorCode.AUTHORIZATION_ERROR,
            details
        )