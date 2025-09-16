"""敏感词检查日志实体"""
from datetime import datetime
from typing import Optional, Dict, Any
from dataclasses import dataclass

from src.shared.enums.list_enums import LanguageEnum


@dataclass
class ModerationLog:
    """敏感词检查日志实体"""
    
    # 主键
    id: Optional[int] = None
    
    # 请求信息
    request_id: str = ""
    request_time: datetime = datetime.now()
    
    # 用户信息
    user_id: Optional[str] = None
    nickname: Optional[str] = None
    account: Optional[str] = None
    role_id: Optional[str] = None
    
    # 内容信息
    content: Optional[str] = None
    content_type: Optional[str] = None
    
    # 网络信息
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    
    # 业务信息
    app_id: Optional[int] = None
    scene: Optional[str] = None
    language: int = 0
    speak_time: Optional[datetime] = None
    
    # 检测配置
    check_nickname: bool = True
    check_content: bool = True
    return_matched_words: bool = True
    auto_replace: bool = False
    case_sensitive: bool = False
    
    # 检测结果
    check_time: datetime = datetime.now()
    is_violation: bool = False
    max_risk_level: int = 0
    status: int = 0  # ModerationResultStatus
    
    # 昵称检查结果
    nickname_violation: bool = False
    nickname_risk_level: Optional[int] = None
    nickname_matched_count: int = 0
    nickname_matched_words: Optional[str] = None  # JSON格式存储
    
    # 内容检查结果
    content_violation: bool = False
    content_risk_level: Optional[int] = None
    content_matched_count: int = 0
    content_matched_words: Optional[str] = None  # JSON格式存储
    
    # 处理结果
    suggestion: Optional[str] = None
    error_message: Optional[str] = None
    
    # 性能统计
    process_time_ms: int = 0
    
    # 扩展字段
    extra_data: Optional[str] = None  # JSON格式存储额外信息
    
    # 审计字段
    created_at: datetime = datetime.now()
    
    @classmethod
    def create(
        cls,
        request_id: str,
        user_id: Optional[str] = None,
        nickname: Optional[str] = None,
        content: Optional[str] = None,
        app_id: Optional[int] = None,
        ip_address: Optional[str] = None,
        **kwargs
    ) -> "ModerationLog":
        """创建敏感词检查日志"""
        return cls(
            request_id=request_id,
            user_id=user_id,
            nickname=nickname,
            content=content,
            app_id=app_id,
            ip_address=ip_address,
            **kwargs
        )
    
    def update_result(
        self,
        is_violation: bool,
        max_risk_level: int,
        status: int,
        process_time_ms: int,
        **kwargs
    ) -> None:
        """更新检测结果"""
        self.is_violation = is_violation
        self.max_risk_level = max_risk_level
        self.status = status
        self.process_time_ms = process_time_ms
        self.check_time = datetime.now()
        
        # 更新其他字段
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def set_nickname_result(
        self,
        violation: bool,
        risk_level: Optional[int],
        matched_count: int,
        matched_words: Optional[str] = None
    ) -> None:
        """设置昵称检测结果"""
        self.nickname_violation = violation
        self.nickname_risk_level = risk_level
        self.nickname_matched_count = matched_count
        self.nickname_matched_words = matched_words
    
    def set_content_result(
        self,
        violation: bool,
        risk_level: Optional[int],
        matched_count: int,
        matched_words: Optional[str] = None
    ) -> None:
        """设置内容检测结果"""
        self.content_violation = violation
        self.content_risk_level = risk_level
        self.content_matched_count = matched_count
        self.content_matched_words = matched_words
    
    def set_error(self, error_message: str) -> None:
        """设置错误信息"""
        self.error_message = error_message
        self.status = -1  # ERROR status
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'id': self.id,
            'request_id': self.request_id,
            'request_time': self.request_time,
            'user_id': self.user_id,
            'nickname': self.nickname,
            'account': self.account,
            'role_id': self.role_id,
            'content': self.content,
            'content_type': self.content_type,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'app_id': self.app_id,
            'scene': self.scene,
            'language': self.language,
            'speak_time': self.speak_time,
            'check_nickname': self.check_nickname,
            'check_content': self.check_content,
            'return_matched_words': self.return_matched_words,
            'auto_replace': self.auto_replace,
            'case_sensitive': self.case_sensitive,
            'check_time': self.check_time,
            'is_violation': self.is_violation,
            'max_risk_level': self.max_risk_level,
            'status': self.status,
            'nickname_violation': self.nickname_violation,
            'nickname_risk_level': self.nickname_risk_level,
            'nickname_matched_count': self.nickname_matched_count,
            'nickname_matched_words': self.nickname_matched_words,
            'content_violation': self.content_violation,
            'content_risk_level': self.content_risk_level,
            'content_matched_count': self.content_matched_count,
            'content_matched_words': self.content_matched_words,
            'suggestion': self.suggestion,
            'error_message': self.error_message,
            'process_time_ms': self.process_time_ms,
            'extra_data': self.extra_data,
            'created_at': self.created_at
        }