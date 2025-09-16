"""文本风控路由"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query

from src.application.dto.moderation_dto import ModerationRequest, ModerationResponse
from src.interfaces.controllers.moderation_controller import ModerationController
from src.shared.containers import get_moderation_controller_dependency

moderation_router = APIRouter(prefix="/moderation", tags=["文本风控"])


@moderation_router.post("/check", response_model=ModerationResponse, summary="综合内容检查")
async def check_content(
    request: ModerationRequest,
    controller: ModerationController = Depends(get_moderation_controller_dependency)
) -> ModerationResponse:
    """
    对用户昵称和发言内容进行综合风控检查
    
    **主要功能:**
    - 同时检查昵称和内容是否违规
    - 使用AC自动机算法进行高效匹配
    - 支持多种匹配规则和风险等级
    - 返回详细的匹配信息和处理建议
    
    **输入参数:**
    - nickname: 用户昵称
    - content: 发言内容
    - ip_address: IP地址
    - account: 用户账号
    - role_id: 角色ID
    - speak_time: 发言时间
    
    **返回结果:**
    - 综合风险评估
    - 违规词汇详细信息
    - 处理建议和状态
    """
    try:
        return await controller.check_content(request)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"内容检查服务异常: {str(e)}"
        )


@moderation_router.post("/check/nickname", response_model=ModerationResponse, summary="昵称检查")
async def check_nickname(
    request: ModerationRequest,
    controller: ModerationController = Depends(get_moderation_controller_dependency)
) -> ModerationResponse:
    """
    仅对用户昵称进行风控检查
    
    **特点:**
    - 专门针对昵称的风控规则
    - 支持文本和昵称匹配规则
    - 快速响应昵称合规性
    """
    try:
        return await controller.check_nickname(request)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"昵称检查服务异常: {str(e)}"
        )


@moderation_router.post("/check/content", response_model=ModerationResponse, summary="内容检查")
async def check_content_only(
    request: ModerationRequest,
    controller: ModerationController = Depends(get_moderation_controller_dependency)
) -> ModerationResponse:
    """
    仅对发言内容进行风控检查
    
    **特点:**
    - 专门针对文本内容的风控规则
    - 支持多种文本匹配算法
    - 详细的违规词汇定位信息
    """
    try:
        return await controller.check_content_only(request)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"内容检查服务异常: {str(e)}"
        )


@moderation_router.post("/reload", response_model=dict, summary="重新加载敏感词")
async def reload_patterns(
    app_id: Optional[int] = Query(None, description="应用ID，如果指定则只重新加载该应用的敏感词"),
    controller: ModerationController = Depends(get_moderation_controller_dependency)
) -> dict:
    """
    重新加载敏感词模式库
    
    **功能:**
    - 支持全量重新加载或指定应用重新加载
    - 更新AC自动机算法的模式匹配库
    - 适用于敏感词库更新后的热更新
    """
    try:
        success = await controller.reload_patterns(app_id)
        
        if success:
            message = f"应用 {app_id} 的敏感词模式重新加载成功" if app_id else "所有敏感词模式重新加载成功"
            return {"success": True, "app_id": app_id, "message": message}
        else:
            return {"success": False, "message": "敏感词模式重新加载失败"}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"重新加载敏感词模式异常: {str(e)}"
        )


@moderation_router.get("/statistics", response_model=dict, summary="获取服务统计")
async def get_statistics(
    controller: ModerationController = Depends(get_moderation_controller_dependency)
) -> dict:
    """
    获取文本风控服务的统计信息
    
    **统计内容:**
    - 检查总数和违规数统计
    - AC自动机性能统计
    - 缓存状态和加载信息
    """
    try:
        return await controller.get_statistics()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取统计信息异常: {str(e)}"
        )


@moderation_router.get("/health", response_model=dict, summary="健康检查")
async def health_check(
    controller: ModerationController = Depends(get_moderation_controller_dependency)
) -> dict:
    """
    检查文本风控服务的健康状态
    
    **检查项:**
    - 服务可用性
    - 敏感词库加载状态
    - 缓存有效性
    """
    try:
        return await controller.health_check()
    except Exception as e:
        # 健康检查失败不抛出异常，返回不健康状态
        return {
            "status": "unhealthy",
            "service": "text_moderation",
            "error": str(e)
        }