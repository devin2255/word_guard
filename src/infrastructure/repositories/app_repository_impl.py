"""应用仓储实现"""
from typing import List, Optional

from src.domain.app.entities import App
from src.domain.app.repositories import AppRepository
from src.infrastructure.database.models import AppModel


class AppRepositoryImpl(AppRepository):
    """应用仓储实现"""

    async def save(self, app: App) -> App:
        """保存应用"""
        
        if app.id is None:
            # 新增
            model = await AppModel.create(
                app_name=app.app_name,
                app_id=app.app_id,
                username=app.username,
                create_by=app.create_by,
            )
            app.id = model.id
            app.create_time = model.create_time
            app.update_time = model.update_time
        else:
            # 更新
            model = await AppModel.get(id=app.id)
            
            model.app_name = app.app_name
            model.username = app.username
            model.update_by = app.update_by
            model.delete_time = app.delete_time
            model.delete_by = app.delete_by
            
            await model.save()
            
            app.update_time = model.update_time
        
        return app

    async def find_by_id(self, app_db_id: int) -> Optional[App]:
        """根据数据库ID查找应用"""
        
        try:
            model = await AppModel.get(id=app_db_id)
            return self._model_to_entity(model)
        except:
            return None

    async def find_by_app_id(self, app_id: str) -> Optional[App]:
        """根据应用ID查找应用"""
        
        try:
            model = await AppModel.filter(app_id=app_id, delete_time__isnull=True).first()
            if model:
                return self._model_to_entity(model)
            return None
        except:
            return None

    async def find_all(self, include_deleted: bool = False) -> List[App]:
        """查找所有应用"""
        
        query = AppModel.all()
        if not include_deleted:
            query = query.filter(delete_time__isnull=True)
        
        models = await query
        return [self._model_to_entity(model) for model in models]

    async def delete(self, app_id: str) -> bool:
        """删除应用"""
        
        try:
            await AppModel.filter(app_id=app_id).delete()
            return True
        except:
            return False

    async def exists_by_app_id(self, app_id: str, exclude_db_id: int = None) -> bool:
        """检查应用ID是否存在"""
        
        query = AppModel.filter(app_id=app_id, delete_time__isnull=True)
        if exclude_db_id:
            query = query.exclude(id=exclude_db_id)
        
        return await query.exists()

    def _model_to_entity(self, model: AppModel) -> App:
        """将数据库模型转换为领域实体"""
        
        app = App(
            id=model.id,
            app_name=model.app_name,
            app_id=model.app_id,
            username=model.username,
            create_time=model.create_time,
            update_time=model.update_time,
            delete_time=model.delete_time,
            create_by=model.create_by,
            update_by=model.update_by,
            delete_by=model.delete_by,
        )
        
        return app