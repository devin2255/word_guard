"""文本风控控制器"""
import logging
from typing import Optional

from src.application.services.moderation_service import ModerationApplicationService
from src.application.dto.moderation_dto import ModerationRequest, ModerationResponse

logger = logging.getLogger(__name__)


class ModerationController:
    """文本风控控制器"""
    
    def __init__(self, moderation_service: ModerationApplicationService):
        self._moderation_service = moderation_service
    
    async def check_content(self, request: ModerationRequest) -> ModerationResponse:
        """
        综合内容检查
        
        Args:
            request: 风控请求参数
            
        Returns:
            风控检查结果
        """
        logger.info(f"开始综合内容检查 - 请求ID: {request.request_id}, 应用ID: {request.app_id}")
        return await self._moderation_service.check_content(request)
    
    async def check_nickname(self, request: ModerationRequest) -> ModerationResponse:
        """
        昵称检查
        
        Args:
            request: 风控请求参数
            
        Returns:
            昵称检查结果
        """
        logger.info(f"开始昵称检查 - 请求ID: {request.request_id}, 昵称: {request.nickname}")
        
        if not request.nickname or not request.nickname.strip():
            raise ValueError("昵称不能为空")
            
        return await self._moderation_service.check_nickname_only(request)
    
    async def check_content_only(self, request: ModerationRequest) -> ModerationResponse:
        """
        内容检查
        
        Args:
            request: 风控请求参数
            
        Returns:
            内容检查结果
        """
        logger.info(f"开始内容检查 - 请求ID: {request.request_id}")
        
        if not request.content or not request.content.strip():
            raise ValueError("检查内容不能为空")
            
        return await self._moderation_service.check_content_only(request)
    
    async def reload_patterns(self, app_id: Optional[int] = None) -> bool:
        """
        重新加载敏感词模式
        
        Args:
            app_id: 应用ID，如果指定则只重新加载该应用的敏感词
            
        Returns:
            是否成功
        """
        logger.info(f"开始重新加载敏感词模式 - 应用ID: {app_id}")
        return await self._moderation_service.reload_patterns(app_id)
    
    async def get_statistics(self) -> dict:
        """获取服务统计信息"""
        logger.info("获取文本风控服务统计信息")
        return await self._moderation_service.get_service_statistics()
    
    async def health_check(self) -> dict:
        """
        健康检查
        
        Returns:
            健康状态信息
        """
        try:
            # 简单的健康检查，获取统计信息来验证服务可用性
            statistics = await self._moderation_service.get_service_statistics()
            
            return {
                "status": "healthy",
                "service": "text_moderation",
                "pattern_count": sum([
                    stats.get("pattern_count", 0) 
                    for stats in statistics.get("ac_machines", {}).values()
                ]),
                "cache_valid": statistics.get("cache_valid", False),
                "total_checks": statistics.get("total_checks", 0)
            }
            
        except Exception as e:
            logger.error(f"健康检查失败: {e}", exc_info=True)
            
            return {
                "status": "unhealthy",
                "service": "text_moderation",
                "error": str(e)
            }