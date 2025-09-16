"""敏感词检查日志服务"""
import json
import time
from datetime import datetime
from typing import Optional, List, Dict, Any

from src.domain.moderation.entities.moderation_log import ModerationLog
from src.domain.moderation.repositories.moderation_log_repository import ModerationLogRepository
from src.application.dto.moderation_dto import ModerationRequest, ModerationResponse, MatchedWordInfo


class ModerationLogService:
    """敏感词检查日志服务"""
    
    def __init__(self, log_repository: ModerationLogRepository):
        self._log_repository = log_repository
    
    async def create_log_from_request(self, request: ModerationRequest) -> ModerationLog:
        """从请求创建日志记录"""
        log = ModerationLog.create(
            request_id=request.request_id,
            user_id=request.user_id,
            nickname=request.nickname,
            content=request.content,
            app_id=request.app_id,
            ip_address=request.ip_address,
            account=request.account,
            role_id=request.role_id,
            content_type=request.content_type,
            user_agent=request.user_agent,
            scene=request.scene,
            language=request.language,
            speak_time=request.speak_time,
            request_time=request.request_time or datetime.now(),
            check_nickname=request.check_nickname,
            check_content=request.check_content,
            return_matched_words=request.return_matched_words,
            auto_replace=request.auto_replace,
            case_sensitive=request.case_sensitive
        )
        
        return await self._log_repository.save(log)
    
    async def update_log_with_response(
        self, 
        log: ModerationLog, 
        response: ModerationResponse,
        start_time: float
    ) -> ModerationLog:
        """使用响应结果更新日志"""
        # 计算处理时间
        process_time_ms = int((time.time() - start_time) * 1000)
        
        # 更新基本结果
        log.update_result(
            is_violation=response.is_violation,
            max_risk_level=response.max_risk_level,
            status=response.status.value,
            process_time_ms=process_time_ms,
            suggestion=response.suggestion,
            error_message=response.error_message
        )
        
        # 更新昵称检查结果
        if response.nickname_check:
            matched_words_json = None
            if response.nickname_check.matched_words:
                matched_words_json = json.dumps([
                    {
                        "word": word.word,
                        "start_pos": word.start_pos,
                        "end_pos": word.end_pos,
                        "wordlist_id": word.wordlist_id,
                        "wordlist_name": word.wordlist_name,
                        "risk_type": word.risk_type,
                        "risk_type_desc": word.risk_type_desc,
                        "suggestion": word.suggestion,
                        "priority": word.priority
                    }
                    for word in response.nickname_check.matched_words
                ], ensure_ascii=False)
            
            log.set_nickname_result(
                violation=response.nickname_violation,
                risk_level=response.nickname_risk_level,
                matched_count=response.nickname_matched_count,
                matched_words=matched_words_json
            )
        
        # 更新内容检查结果
        if response.content_check:
            matched_words_json = None
            if response.content_check.matched_words:
                matched_words_json = json.dumps([
                    {
                        "word": word.word,
                        "start_pos": word.start_pos,
                        "end_pos": word.end_pos,
                        "wordlist_id": word.wordlist_id,
                        "wordlist_name": word.wordlist_name,
                        "risk_type": word.risk_type,
                        "risk_type_desc": word.risk_type_desc,
                        "suggestion": word.suggestion,
                        "priority": word.priority
                    }
                    for word in response.content_check.matched_words
                ], ensure_ascii=False)
            
            log.set_content_result(
                violation=response.content_violation,
                risk_level=response.content_risk_level,
                matched_count=response.content_matched_count,
                matched_words=matched_words_json
            )
        
        return await self._log_repository.save(log)
    
    async def log_error(
        self, 
        log: ModerationLog, 
        error_message: str,
        start_time: float
    ) -> ModerationLog:
        """记录错误"""
        process_time_ms = int((time.time() - start_time) * 1000)
        log.set_error(error_message)
        log.process_time_ms = process_time_ms
        log.check_time = datetime.now()
        
        return await self._log_repository.save(log)
    
    async def get_log_by_request_id(self, request_id: str) -> Optional[ModerationLog]:
        """根据请求ID获取日志"""
        return await self._log_repository.find_by_request_id(request_id)
    
    async def get_logs_by_user_id(
        self, 
        user_id: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100
    ) -> List[ModerationLog]:
        """根据用户ID获取日志"""
        return await self._log_repository.find_by_user_id(
            user_id, start_time, end_time, limit
        )
    
    async def get_logs_by_app_id(
        self,
        app_id: int,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100
    ) -> List[ModerationLog]:
        """根据应用ID获取日志"""
        return await self._log_repository.find_by_app_id(
            app_id, start_time, end_time, limit
        )
    
    async def get_violation_logs(
        self,
        app_id: Optional[int] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100
    ) -> List[ModerationLog]:
        """获取违规日志"""
        return await self._log_repository.find_violations(
            app_id, start_time, end_time, limit
        )
    
    async def get_statistics(
        self,
        app_id: Optional[int] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """获取统计信息"""
        return await self._log_repository.get_statistics(
            app_id, start_time, end_time
        )
    
    async def cleanup_old_logs(self, days: int = 30) -> int:
        """清理旧日志"""
        return await self._log_repository.delete_old_logs(days)