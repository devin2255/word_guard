"""应用路由"""
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, Path

from src.application.dto import AppDTO, CreateAppRequest
from src.interfaces.controllers import AppController
from src.interfaces.dependencies import get_app_controller


app_router = APIRouter(prefix="/app", tags=["应用管理"])


@app_router.post("", response_model=AppDTO, summary="创建应用")
async def create_app(
    request: CreateAppRequest,
    controller: AppController = Depends(get_app_controller),
    created_by: Optional[str] = Query(None, description="创建人")
) -> AppDTO:
    """创建新应用"""
    return await controller.create_app(request, created_by)


@app_router.get("/by-id/{app_db_id}", response_model=AppDTO, summary="根据数据库ID获取应用")
async def get_app_by_db_id(
    app_db_id: int = Path(..., description="应用数据库ID"),
    controller: AppController = Depends(get_app_controller)
) -> AppDTO:
    """根据数据库ID获取应用详情"""
    return await controller.get_app(app_db_id=app_db_id)


@app_router.get("/by-app-id/{app_id}", response_model=AppDTO, summary="根据应用ID获取应用")
async def get_app_by_app_id(
    app_id: str = Path(..., description="应用ID"),
    controller: AppController = Depends(get_app_controller)
) -> AppDTO:
    """根据应用ID获取应用详情"""
    return await controller.get_app(app_id=app_id)


@app_router.get("", response_model="List[AppDTO]", summary="获取应用列表")
async def get_apps(
    include_deleted: bool = Query(False, description="是否包含已删除"),
    controller: AppController = Depends(get_app_controller)
) -> List[AppDTO]:
    """获取应用列表"""
    return await controller.get_apps(include_deleted=include_deleted)