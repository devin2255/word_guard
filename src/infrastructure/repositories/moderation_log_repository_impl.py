"""敏感词检查日志仓储实现"""
import json
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from tortoise.expressions import Q

from src.domain.moderation.entities.moderation_log import ModerationLog
from src.domain.moderation.repositories.moderation_log_repository import ModerationLogRepository
from src.infrastructure.database.models import ModerationLogModel


class ModerationLogRepositoryImpl(ModerationLogRepository):
    """敏感词检查日志仓储实现"""
    
    def _to_entity(self, model: ModerationLogModel) -> ModerationLog:
        """将数据库模型转换为实体"""
        return ModerationLog(
            id=model.id,
            request_id=model.request_id,
            request_time=model.request_time,
            user_id=model.user_id,
            nickname=model.nickname,
            account=model.account,
            role_id=model.role_id,
            content=model.content,
            content_type=model.content_type,
            ip_address=model.ip_address,
            user_agent=model.user_agent,
            app_id=model.app_id,
            scene=model.scene,
            language=model.language,
            speak_time=model.speak_time,
            check_nickname=model.check_nickname,
            check_content=model.check_content,
            return_matched_words=model.return_matched_words,
            auto_replace=model.auto_replace,
            case_sensitive=model.case_sensitive,
            check_time=model.check_time,
            is_violation=model.is_violation,
            max_risk_level=model.max_risk_level,
            status=model.status,
            nickname_violation=model.nickname_violation,
            nickname_risk_level=model.nickname_risk_level,
            nickname_matched_count=model.nickname_matched_count,
            nickname_matched_words=model.nickname_matched_words,
            content_violation=model.content_violation,
            content_risk_level=model.content_risk_level,
            content_matched_count=model.content_matched_count,
            content_matched_words=model.content_matched_words,
            suggestion=model.suggestion,
            error_message=model.error_message,
            process_time_ms=model.process_time_ms,
            extra_data=model.extra_data,
            created_at=model.created_at
        )
    
    def _to_model_data(self, entity: ModerationLog) -> Dict[str, Any]:
        """将实体转换为数据库模型数据"""
        return {
            "request_id": entity.request_id,
            "request_time": entity.request_time,
            "user_id": entity.user_id,
            "nickname": entity.nickname,
            "account": entity.account,
            "role_id": entity.role_id,
            "content": entity.content,
            "content_type": entity.content_type,
            "ip_address": entity.ip_address,
            "user_agent": entity.user_agent,
            "app_id": entity.app_id,
            "scene": entity.scene,
            "language": entity.language,
            "speak_time": entity.speak_time,
            "check_nickname": entity.check_nickname,
            "check_content": entity.check_content,
            "return_matched_words": entity.return_matched_words,
            "auto_replace": entity.auto_replace,
            "case_sensitive": entity.case_sensitive,
            "check_time": entity.check_time,
            "is_violation": entity.is_violation,
            "max_risk_level": entity.max_risk_level,
            "status": entity.status,
            "nickname_violation": entity.nickname_violation,
            "nickname_risk_level": entity.nickname_risk_level,
            "nickname_matched_count": entity.nickname_matched_count,
            "nickname_matched_words": entity.nickname_matched_words,
            "content_violation": entity.content_violation,
            "content_risk_level": entity.content_risk_level,
            "content_matched_count": entity.content_matched_count,
            "content_matched_words": entity.content_matched_words,
            "suggestion": entity.suggestion,
            "error_message": entity.error_message,
            "process_time_ms": entity.process_time_ms,
            "extra_data": entity.extra_data,
            "created_at": entity.created_at
        }
    
    async def save(self, log: ModerationLog) -> ModerationLog:
        """保存日志"""
        if log.id is None:
            # 创建新记录
            model_data = self._to_model_data(log)
            model = await ModerationLogModel.create(**model_data)
            log.id = model.id
            return log
        else:
            # 更新现有记录
            model = await ModerationLogModel.get(id=log.id)
            for key, value in self._to_model_data(log).items():
                setattr(model, key, value)
            await model.save()
            return log
    
    async def find_by_id(self, log_id: int) -> Optional[ModerationLog]:
        """根据ID查找日志"""
        try:
            model = await ModerationLogModel.get(id=log_id)
            return self._to_entity(model)
        except:
            return None
    
    async def find_by_request_id(self, request_id: str) -> Optional[ModerationLog]:
        """根据请求ID查找日志"""
        try:
            model = await ModerationLogModel.get(request_id=request_id)
            return self._to_entity(model)
        except:
            return None
    
    async def find_by_user_id(
        self, 
        user_id: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100
    ) -> List[ModerationLog]:
        """根据用户ID查找日志"""
        query = ModerationLogModel.filter(user_id=user_id)
        
        if start_time:
            query = query.filter(request_time__gte=start_time)
        if end_time:
            query = query.filter(request_time__lte=end_time)
        
        models = await query.order_by("-request_time").limit(limit).all()
        return [self._to_entity(model) for model in models]
    
    async def find_by_app_id(
        self,
        app_id: int,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100
    ) -> List[ModerationLog]:
        """根据应用ID查找日志"""
        query = ModerationLogModel.filter(app_id=app_id)
        
        if start_time:
            query = query.filter(request_time__gte=start_time)
        if end_time:
            query = query.filter(request_time__lte=end_time)
        
        models = await query.order_by("-request_time").limit(limit).all()
        return [self._to_entity(model) for model in models]
    
    async def find_violations(
        self,
        app_id: Optional[int] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100
    ) -> List[ModerationLog]:
        """查找违规记录"""
        query = ModerationLogModel.filter(is_violation=True)
        
        if app_id:
            query = query.filter(app_id=app_id)
        if start_time:
            query = query.filter(request_time__gte=start_time)
        if end_time:
            query = query.filter(request_time__lte=end_time)
        
        models = await query.order_by("-request_time").limit(limit).all()
        return [self._to_entity(model) for model in models]
    
    async def get_statistics(
        self,
        app_id: Optional[int] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """获取统计信息"""
        query = ModerationLogModel.all()
        
        if app_id:
            query = query.filter(app_id=app_id)
        if start_time:
            query = query.filter(request_time__gte=start_time)
        if end_time:
            query = query.filter(request_time__lte=end_time)
        
        # 基础统计
        total_count = await query.count()
        violation_count = await query.filter(is_violation=True).count()
        
        # 状态统计
        approved_count = await query.filter(status=0).count()
        rejected_count = await query.filter(status=1).count()
        review_count = await query.filter(status=2).count()
        warning_count = await query.filter(status=3).count()
        error_count = await query.filter(status=-1).count()
        
        # 性能统计
        avg_process_time = 0
        max_process_time = 0
        min_process_time = 0
        
        if total_count > 0:
            # 计算平均处理时间
            process_times = await query.values_list('process_time_ms', flat=True)
            if process_times:
                avg_process_time = sum(process_times) / len(process_times)
                max_process_time = max(process_times)
                min_process_time = min(process_times)
        
        violation_rate = (violation_count / total_count * 100) if total_count > 0 else 0
        
        return {
            "total_requests": total_count,
            "pass_requests": approved_count,
            "reject_requests": rejected_count,
            "review_requests": review_count,
            "warning_requests": warning_count,
            "error_requests": error_count,
            "violation_count": violation_count,
            "violation_rate": round(violation_rate, 2),
            "avg_process_time_ms": round(avg_process_time, 2),
            "max_process_time_ms": max_process_time,
            "min_process_time_ms": min_process_time,
            "statistics_time": datetime.now()
        }
    
    async def count_by_conditions(
        self,
        app_id: Optional[int] = None,
        user_id: Optional[str] = None,
        is_violation: Optional[bool] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> int:
        """根据条件统计数量"""
        query = ModerationLogModel.all()
        
        if app_id:
            query = query.filter(app_id=app_id)
        if user_id:
            query = query.filter(user_id=user_id)
        if is_violation is not None:
            query = query.filter(is_violation=is_violation)
        if start_time:
            query = query.filter(request_time__gte=start_time)
        if end_time:
            query = query.filter(request_time__lte=end_time)
        
        return await query.count()
    
    async def delete_old_logs(self, days: int) -> int:
        """删除旧日志"""
        cutoff_date = datetime.now() - timedelta(days=days)
        result = await ModerationLogModel.filter(created_at__lt=cutoff_date).delete()
        return result