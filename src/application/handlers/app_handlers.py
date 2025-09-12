"""应用处理器"""
from typing import List, Optional

from src.domain.app.entities import App
from src.domain.app.repositories import AppRepository
from src.shared.exceptions import AppNotFoundError, AppAlreadyExistsError
from src.application.commands.app_commands import CreateAppCommand
from src.application.queries.app_queries import GetAppQuery, GetAppsQuery
from src.application.dto import AppDTO


class AppCommandHandler:
    """应用命令处理器"""
    
    def __init__(self, app_repository: AppRepository):
        self._app_repository = app_repository
    
    async def handle_create(self, command: CreateAppCommand) -> AppDTO:
        """处理创建应用命令"""
        
        # 检查应用ID是否已存在
        if await self._app_repository.exists_by_app_id(command.app_id):
            raise AppAlreadyExistsError(command.app_id)
        
        # 创建应用实体
        app = App.create(
            app_name=command.app_name,
            app_id=command.app_id,
            username=command.username,
            created_by=command.created_by
        )
        
        # 保存到仓储
        saved_app = await self._app_repository.save(app)
        
        # 转换为DTO
        return AppDTO(**saved_app.to_dict())


class AppQueryHandler:
    """应用查询处理器"""
    
    def __init__(self, app_repository: AppRepository):
        self._app_repository = app_repository
    
    async def handle_get_app(self, query: GetAppQuery) -> Optional[AppDTO]:
        """处理获取单个应用查询"""
        
        app = None
        
        if query.app_db_id is not None:
            app = await self._app_repository.find_by_id(query.app_db_id)
        elif query.app_id is not None:
            app = await self._app_repository.find_by_app_id(query.app_id)
        
        if not app:
            return None
        
        return AppDTO(**app.to_dict())
    
    async def handle_get_apps(self, query: GetAppsQuery) -> List[AppDTO]:
        """处理获取应用列表查询"""
        
        apps = await self._app_repository.find_all(
            include_deleted=query.include_deleted
        )
        
        # 转换为DTO列表
        return [AppDTO(**app.to_dict()) for app in apps]