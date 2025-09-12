"""应用控制器"""
from typing import List, Optional
from fastapi import HTTPException, status

from src.application.handlers import AppCommandHandler, AppQueryHandler
from src.application.commands import CreateAppCommand
from src.application.queries import GetAppQuery, GetAppsQuery
from src.application.dto import AppDTO, CreateAppRequest
from src.shared.exceptions import DomainException


class AppController:
    """应用控制器"""
    
    def __init__(
        self, 
        command_handler: AppCommandHandler,
        query_handler: AppQueryHandler
    ):
        self._command_handler = command_handler
        self._query_handler = query_handler
    
    async def create_app(
        self, 
        request: CreateAppRequest, 
        created_by: str = None
    ) -> AppDTO:
        """创建应用"""
        
        try:
            command = CreateAppCommand(
                app_name=request.app_name,
                app_id=request.app_id,
                username=request.username,
                created_by=created_by
            )
            
            return await self._command_handler.handle_create(command)
            
        except DomainException as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=e.message
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"创建应用失败: {str(e)}"
            )
    
    async def get_app(
        self, 
        app_db_id: Optional[int] = None,
        app_id: Optional[str] = None
    ) -> Optional[AppDTO]:
        """获取单个应用"""
        
        try:
            query = GetAppQuery(app_db_id=app_db_id, app_id=app_id)
            app = await self._query_handler.handle_get_app(query)
            
            if not app:
                identifier = app_db_id or app_id
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"应用 {identifier} 不存在"
                )
            
            return app
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"获取应用失败: {str(e)}"
            )
    
    async def get_apps(self, include_deleted: bool = False) -> List[AppDTO]:
        """获取应用列表"""
        
        try:
            query = GetAppsQuery(include_deleted=include_deleted)
            return await self._query_handler.handle_get_apps(query)
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"获取应用列表失败: {str(e)}"
            )