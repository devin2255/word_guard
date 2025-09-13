"""文本风控应用层服务"""
import logging
from typing import Optional
from datetime import datetime

from src.domain.moderation.services.text_moderation_service import TextModerationService
from src.domain.wordlist.repositories import WordListRepository
from src.domain.listdetail.repositories import ListDetailRepository
from src.domain.association.repositories import AssociationRepository
from src.application.dto.moderation_dto import (
    ModerationRequest,
    ModerationResponse,
    ModerationResultStatus
)

logger = logging.getLogger(__name__)


class ModerationApplicationService:
    """文本风控应用层服务"""
    
    def __init__(
        self,
        text_moderation_service: TextModerationService,
        wordlist_repository: WordListRepository,
        listdetail_repository: ListDetailRepository,
        association_repository: AssociationRepository
    ):
        self._text_moderation_service = text_moderation_service
        self._wordlist_repository = wordlist_repository
        self._listdetail_repository = listdetail_repository
        self._association_repository = association_repository
        
        # 服务初始化状态
        self._initialized_apps = set()
    
    async def check_content(self, request: ModerationRequest) -> ModerationResponse:
        """
        检查内容是否违规
        
        Args:
            request: 风控请求
            
        Returns:
            风控检查结果
        """
        try:
            # 确保服务已初始化
            await self._ensure_service_initialized(request.app_id)
            
            # 执行综合检查
            nickname_result, content_result = await self._text_moderation_service.check_comprehensive(
                nickname=request.nickname,
                content=request.content,
                ip_address=request.ip_address,
                account=request.account,
                role_id=request.role_id,
                case_sensitive=request.case_sensitive
            )
            
            # 构建响应结果
            response = ModerationResponse(
                request_id=request.request_id,
                app_id=request.app_id,
                user_id=request.user_id,
                nickname=request.nickname,
                content=request.content,
                ip_address=request.ip_address,
                account=request.account,
                role_id=request.role_id,
                speak_time=request.speak_time,
                check_time=datetime.now()
            )
            
            # 处理昵称检查结果
            if nickname_result:
                response.nickname_check = nickname_result
                response.nickname_violation = nickname_result.is_violation
                response.nickname_risk_level = nickname_result.risk_level
                response.nickname_matched_count = len(nickname_result.matched_words)
            
            # 处理内容检查结果  
            if content_result:
                response.content_check = content_result
                response.content_violation = content_result.is_violation
                response.content_risk_level = content_result.risk_level
                response.content_matched_count = len(content_result.matched_words)
            
            # 综合判断违规状态
            response.is_violation = response.nickname_violation or response.content_violation
            response.max_risk_level = max(
                response.nickname_risk_level or 0,
                response.content_risk_level or 0
            )
            
            # 确定处理状态
            if response.is_violation:
                if response.max_risk_level >= 8:
                    response.status = ModerationResultStatus.REJECTED
                elif response.max_risk_level >= 5:
                    response.status = ModerationResultStatus.REVIEW_REQUIRED
                else:
                    response.status = ModerationResultStatus.WARNING
            else:
                response.status = ModerationResultStatus.APPROVED
            
            # 生成处理建议
            response.suggestion = self._generate_suggestion(response)
            
            logger.info(
                f"内容风控检查完成 - 请求ID: {request.request_id}, "
                f"状态: {response.status.name}, "
                f"违规: {response.is_violation}, "
                f"风险等级: {response.max_risk_level}"
            )
            
            return response
            
        except Exception as e:
            logger.error(f"内容风控检查失败 - 请求ID: {request.request_id}, 错误: {e}", exc_info=True)
            
            # 返回错误响应
            error_response = ModerationResponse(
                request_id=request.request_id,
                app_id=request.app_id,
                user_id=request.user_id,
                nickname=request.nickname,
                content=request.content,
                ip_address=request.ip_address,
                account=request.account,
                role_id=request.role_id,
                speak_time=request.speak_time,
                check_time=datetime.now(),
                status=ModerationResultStatus.ERROR,
                error_message=str(e)
            )
            
            return error_response
    
    async def check_nickname_only(self, request: ModerationRequest) -> ModerationResponse:
        """
        仅检查昵称
        
        Args:
            request: 风控请求
            
        Returns:
            风控检查结果
        """
        try:
            await self._ensure_service_initialized(request.app_id)
            
            nickname_result = await self._text_moderation_service.check_nickname(
                nickname=request.nickname,
                case_sensitive=request.case_sensitive
            )
            
            response = ModerationResponse(
                request_id=request.request_id,
                app_id=request.app_id,
                user_id=request.user_id,
                nickname=request.nickname,
                ip_address=request.ip_address,
                account=request.account,
                role_id=request.role_id,
                check_time=datetime.now()
            )
            
            if nickname_result:
                response.nickname_check = nickname_result
                response.nickname_violation = nickname_result.is_violation
                response.nickname_risk_level = nickname_result.risk_level
                response.nickname_matched_count = len(nickname_result.matched_words)
                response.is_violation = nickname_result.is_violation
                response.max_risk_level = nickname_result.risk_level
            
            response.status = self._determine_status(response.max_risk_level, response.is_violation)
            response.suggestion = self._generate_suggestion(response)
            
            return response
            
        except Exception as e:
            logger.error(f"昵称检查失败 - 请求ID: {request.request_id}, 错误: {e}", exc_info=True)
            raise
    
    async def check_content_only(self, request: ModerationRequest) -> ModerationResponse:
        """
        仅检查内容
        
        Args:
            request: 风控请求
            
        Returns:
            风控检查结果
        """
        try:
            await self._ensure_service_initialized(request.app_id)
            
            content_result = await self._text_moderation_service.check_text(
                text=request.content,
                case_sensitive=request.case_sensitive
            )
            
            response = ModerationResponse(
                request_id=request.request_id,
                app_id=request.app_id,
                user_id=request.user_id,
                content=request.content,
                ip_address=request.ip_address,
                account=request.account,
                role_id=request.role_id,
                speak_time=request.speak_time,
                check_time=datetime.now()
            )
            
            if content_result:
                response.content_check = content_result
                response.content_violation = content_result.is_violation
                response.content_risk_level = content_result.risk_level
                response.content_matched_count = len(content_result.matched_words)
                response.is_violation = content_result.is_violation
                response.max_risk_level = content_result.risk_level
            
            response.status = self._determine_status(response.max_risk_level, response.is_violation)
            response.suggestion = self._generate_suggestion(response)
            
            return response
            
        except Exception as e:
            logger.error(f"内容检查失败 - 请求ID: {request.request_id}, 错误: {e}", exc_info=True)
            raise
    
    async def reload_patterns(self, app_id: Optional[int] = None) -> bool:
        """
        重新加载敏感词模式
        
        Args:
            app_id: 应用ID，如果指定则只重新加载该应用的模式
            
        Returns:
            是否成功
        """
        try:
            await self._text_moderation_service.reload_patterns(app_id)
            
            if app_id:
                self._initialized_apps.discard(app_id)  # 移除初始化标记，下次使用时重新初始化
                logger.info(f"应用 {app_id} 的敏感词模式已重新加载")
            else:
                self._initialized_apps.clear()
                logger.info("所有敏感词模式已重新加载")
            
            return True
            
        except Exception as e:
            logger.error(f"重新加载敏感词模式失败 - 应用ID: {app_id}, 错误: {e}", exc_info=True)
            return False
    
    async def get_service_statistics(self) -> dict:
        """获取服务统计信息"""
        try:
            return self._text_moderation_service.get_statistics()
        except Exception as e:
            logger.error(f"获取服务统计信息失败: {e}", exc_info=True)
            return {}
    
    async def _ensure_service_initialized(self, app_id: Optional[int] = None) -> None:
        """确保服务已初始化"""
        cache_key = app_id or 0
        
        if cache_key not in self._initialized_apps:
            # 检查是否需要重新加载
            if self._text_moderation_service.need_reload():
                await self._text_moderation_service.initialize(app_id)
                self._initialized_apps.add(cache_key)
        elif self._text_moderation_service.need_reload():
            # 缓存时间过期，重新初始化
            await self._text_moderation_service.initialize(app_id)
    
    def _determine_status(self, risk_level: int, is_violation: bool) -> ModerationResultStatus:
        """确定处理状态"""
        if not is_violation:
            return ModerationResultStatus.APPROVED
        
        if risk_level >= 8:
            return ModerationResultStatus.REJECTED
        elif risk_level >= 5:
            return ModerationResultStatus.REVIEW_REQUIRED
        else:
            return ModerationResultStatus.WARNING
    
    def _generate_suggestion(self, response: ModerationResponse) -> str:
        """生成处理建议"""
        if response.status == ModerationResultStatus.APPROVED:
            return "内容正常，可以发布"
        elif response.status == ModerationResultStatus.WARNING:
            return "内容存在轻微风险，建议提醒用户注意措辞"
        elif response.status == ModerationResultStatus.REVIEW_REQUIRED:
            return "内容存在中等风险，需要人工审核"
        elif response.status == ModerationResultStatus.REJECTED:
            return "内容存在高风险，建议直接拒绝"
        elif response.status == ModerationResultStatus.ERROR:
            return "检查过程中出现错误，请稍后重试"
        else:
            return "未知状态"