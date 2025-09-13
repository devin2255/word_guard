"""关联仓储实现"""
from __future__ import annotations
from typing import List, Optional, Set
from tortoise.exceptions import DoesNotExist
from tortoise.expressions import Q
from tortoise.functions import Count

from src.domain.association.entities import AppWordListAssociation
from src.domain.association.repositories import AssociationRepository
from src.infrastructure.database.models import AppWordListAssociationModel
from src.shared.pagination import PageRequest, PageResponse
from src.shared.exceptions.infrastructure_exceptions import RepositoryError


class AssociationRepositoryImpl(AssociationRepository):
    """应用-名单关联仓储实现"""
    
    async def save(self, association: AppWordListAssociation) -> AppWordListAssociation:
        """保存关联"""
        try:
            if association.id is None:
                # 创建新关联
                model = AppWordListAssociationModel(
                    app_id=association.app_id,
                    wordlist_id=association.wordlist_id,
                    is_active=association.is_active,
                    priority=association.priority.value,
                    memo=association.memo,
                    associated_by=association.associated_by,
                    create_by=association.create_by
                )
                await model.save()
                association.id = model.id
                association.associated_at = model.associated_at
                association.create_time = model.create_time
            else:
                # 更新现有关联
                model = await AppWordListAssociationModel.get(id=association.id)
                model.is_active = association.is_active
                model.priority = association.priority.value
                model.memo = association.memo
                model.update_by = association.update_by
                await model.save()
                association.update_time = model.update_time
            
            return association
            
        except Exception as e:
            raise RepositoryError(
                "AssociationRepositoryImpl", 
                "save", 
                f"保存关联失败: {str(e)}", 
                e
            )
    
    async def find_by_id(self, association_id: int) -> Optional[AppWordListAssociation]:
        """根据ID查找关联"""
        try:
            model = await AppWordListAssociationModel.get_or_none(
                id=association_id,
                delete_time__isnull=True
            )
            return self._model_to_entity(model) if model else None
            
        except Exception as e:
            raise RepositoryError(
                "AssociationRepositoryImpl", 
                "find_by_id", 
                f"查找关联失败: {str(e)}", 
                e
            )
    
    async def find_by_app_and_wordlist(self, app_id: int, wordlist_id: int) -> Optional[AppWordListAssociation]:
        """根据应用ID和名单ID查找关联"""
        try:
            model = await AppWordListAssociationModel.get_or_none(
                app_id=app_id,
                wordlist_id=wordlist_id,
                delete_time__isnull=True
            )
            return self._model_to_entity(model) if model else None
            
        except Exception as e:
            raise RepositoryError(
                "AssociationRepositoryImpl", 
                "find_by_app_and_wordlist", 
                f"查找关联失败: {str(e)}", 
                e
            )
    
    async def find_by_app_id(self, app_id: int, active_only: bool = False) -> List[AppWordListAssociation]:
        """查找应用的所有关联"""
        try:
            query = AppWordListAssociationModel.filter(
                app_id=app_id,
                delete_time__isnull=True
            )
            
            if active_only:
                query = query.filter(is_active=True)
            
            models = await query.all()
            return [self._model_to_entity(model) for model in models]
            
        except Exception as e:
            raise RepositoryError(
                "AssociationRepositoryImpl", 
                "find_by_app_id", 
                f"查找应用关联失败: {str(e)}", 
                e
            )
    
    async def find_by_wordlist_id(self, wordlist_id: int, active_only: bool = False) -> List[AppWordListAssociation]:
        """查找名单的所有关联"""
        try:
            query = AppWordListAssociationModel.filter(
                wordlist_id=wordlist_id,
                delete_time__isnull=True
            )
            
            if active_only:
                query = query.filter(is_active=True)
            
            models = await query.all()
            return [self._model_to_entity(model) for model in models]
            
        except Exception as e:
            raise RepositoryError(
                "AssociationRepositoryImpl", 
                "find_by_wordlist_id", 
                f"查找名单关联失败: {str(e)}", 
                e
            )
    
    async def find_with_pagination(
        self,
        app_id: Optional[int] = None,
        wordlist_id: Optional[int] = None,
        active_only: bool = False,
        page_request: Optional[PageRequest] = None
    ) -> PageResponse[AppWordListAssociation]:
        """分页查询关联"""
        try:
            page_request = page_request or PageRequest()
            
            # 构建查询条件
            query_filter = Q(delete_time__isnull=True)
            
            if app_id is not None:
                query_filter &= Q(app_id=app_id)
            
            if wordlist_id is not None:
                query_filter &= Q(wordlist_id=wordlist_id)
            
            if active_only:
                query_filter &= Q(is_active=True)
            
            # 计算总数
            total_elements = await AppWordListAssociationModel.filter(query_filter).count()
            
            # 分页查询
            query = AppWordListAssociationModel.filter(query_filter)
            
            # 排序
            if page_request.has_sort():
                for sort in page_request.sorts:
                    field_name = sort.field
                    if sort.direction.value == "desc":
                        field_name = f"-{field_name}"
                    query = query.order_by(field_name)
            else:
                query = query.order_by("-priority", "-associated_at")
            
            # 分页
            offset = (page_request.page - 1) * page_request.page_size
            models = await query.offset(offset).limit(page_request.page_size).all()
            
            # 转换为实体
            associations = [self._model_to_entity(model) for model in models]
            
            return PageResponse.create(
                content=associations,
                page_request=page_request,
                total_elements=total_elements
            )
            
        except Exception as e:
            raise RepositoryError(
                "AssociationRepositoryImpl", 
                "find_with_pagination", 
                f"分页查询关联失败: {str(e)}", 
                e
            )
    
    async def exists(self, app_id: int, wordlist_id: int) -> bool:
        """检查关联是否存在"""
        try:
            return await AppWordListAssociationModel.exists(
                app_id=app_id,
                wordlist_id=wordlist_id,
                delete_time__isnull=True
            )
            
        except Exception as e:
            raise RepositoryError(
                "AssociationRepositoryImpl", 
                "exists", 
                f"检查关联存在性失败: {str(e)}", 
                e
            )
    
    async def delete(self, association: AppWordListAssociation) -> bool:
        """删除关联"""
        try:
            if association.id is None:
                return False
            
            model = await AppWordListAssociationModel.get_or_none(id=association.id)
            if not model:
                return False
            
            # 软删除
            model.delete_time = association.delete_time
            model.delete_by = association.delete_by
            model.is_active = False
            await model.save()
            
            return True
            
        except Exception as e:
            raise RepositoryError(
                "AssociationRepositoryImpl", 
                "delete", 
                f"删除关联失败: {str(e)}", 
                e
            )
    
    async def delete_by_app_id(self, app_id: int) -> int:
        """删除应用的所有关联，返回删除数量"""
        try:
            from datetime import datetime
            
            updated = await AppWordListAssociationModel.filter(
                app_id=app_id,
                delete_time__isnull=True
            ).update(
                delete_time=datetime.now(),
                is_active=False
            )
            
            return updated
            
        except Exception as e:
            raise RepositoryError(
                "AssociationRepositoryImpl", 
                "delete_by_app_id", 
                f"删除应用关联失败: {str(e)}", 
                e
            )
    
    async def delete_by_wordlist_id(self, wordlist_id: int) -> int:
        """删除名单的所有关联，返回删除数量"""
        try:
            from datetime import datetime
            
            updated = await AppWordListAssociationModel.filter(
                wordlist_id=wordlist_id,
                delete_time__isnull=True
            ).update(
                delete_time=datetime.now(),
                is_active=False
            )
            
            return updated
            
        except Exception as e:
            raise RepositoryError(
                "AssociationRepositoryImpl", 
                "delete_by_wordlist_id", 
                f"删除名单关联失败: {str(e)}", 
                e
            )
    
    async def activate_batch(self, association_ids: List[int], updated_by: str = None) -> int:
        """批量激活关联，返回更新数量"""
        try:
            updated = await AppWordListAssociationModel.filter(
                id__in=association_ids,
                delete_time__isnull=True
            ).update(
                is_active=True,
                update_by=updated_by
            )
            
            return updated
            
        except Exception as e:
            raise RepositoryError(
                "AssociationRepositoryImpl", 
                "activate_batch", 
                f"批量激活关联失败: {str(e)}", 
                e
            )
    
    async def deactivate_batch(self, association_ids: List[int], updated_by: str = None) -> int:
        """批量停用关联，返回更新数量"""
        try:
            updated = await AppWordListAssociationModel.filter(
                id__in=association_ids,
                delete_time__isnull=True
            ).update(
                is_active=False,
                update_by=updated_by
            )
            
            return updated
            
        except Exception as e:
            raise RepositoryError(
                "AssociationRepositoryImpl", 
                "deactivate_batch", 
                f"批量停用关联失败: {str(e)}", 
                e
            )
    
    async def get_app_associated_wordlist_ids(self, app_id: int, active_only: bool = True) -> Set[int]:
        """获取应用关联的名单ID集合"""
        try:
            query = AppWordListAssociationModel.filter(
                app_id=app_id,
                delete_time__isnull=True
            )
            
            if active_only:
                query = query.filter(is_active=True)
            
            models = await query.values_list('wordlist_id', flat=True)
            return set(models)
            
        except Exception as e:
            raise RepositoryError(
                "AssociationRepositoryImpl", 
                "get_app_associated_wordlist_ids", 
                f"获取应用关联名单失败: {str(e)}", 
                e
            )
    
    async def get_wordlist_associated_app_ids(self, wordlist_id: int, active_only: bool = True) -> Set[int]:
        """获取名单关联的应用ID集合"""
        try:
            query = AppWordListAssociationModel.filter(
                wordlist_id=wordlist_id,
                delete_time__isnull=True
            )
            
            if active_only:
                query = query.filter(is_active=True)
            
            models = await query.values_list('app_id', flat=True)
            return set(models)
            
        except Exception as e:
            raise RepositoryError(
                "AssociationRepositoryImpl", 
                "get_wordlist_associated_app_ids", 
                f"获取名单关联应用失败: {str(e)}", 
                e
            )
    
    async def get_association_statistics(self) -> dict:
        """获取关联统计信息"""
        try:
            total_count = await AppWordListAssociationModel.filter(delete_time__isnull=True).count()
            active_count = await AppWordListAssociationModel.filter(
                delete_time__isnull=True,
                is_active=True
            ).count()
            
            # 按优先级统计
            priority_stats = await AppWordListAssociationModel.filter(
                delete_time__isnull=True,
                is_active=True
            ).annotate(
                count=Count('id')
            ).group_by('priority').values('priority', 'count')
            
            return {
                "total_associations": total_count,
                "active_associations": active_count,
                "inactive_associations": total_count - active_count,
                "priority_distribution": priority_stats
            }
            
        except Exception as e:
            raise RepositoryError(
                "AssociationRepositoryImpl", 
                "get_association_statistics", 
                f"获取关联统计失败: {str(e)}", 
                e
            )
    
    async def get_associations_by_priority(
        self, 
        app_id: Optional[int] = None,
        wordlist_id: Optional[int] = None,
        min_priority: int = 0,
        active_only: bool = True
    ) -> List[AppWordListAssociation]:
        """按优先级查询关联"""
        try:
            query_filter = Q(
                delete_time__isnull=True,
                priority__gte=min_priority
            )
            
            if app_id is not None:
                query_filter &= Q(app_id=app_id)
            
            if wordlist_id is not None:
                query_filter &= Q(wordlist_id=wordlist_id)
            
            if active_only:
                query_filter &= Q(is_active=True)
            
            models = await AppWordListAssociationModel.filter(query_filter).order_by(
                '-priority', '-associated_at'
            ).all()
            
            return [self._model_to_entity(model) for model in models]
            
        except Exception as e:
            raise RepositoryError(
                "AssociationRepositoryImpl", 
                "get_associations_by_priority", 
                f"按优先级查询关联失败: {str(e)}", 
                e
            )
    
    def _model_to_entity(self, model: AppWordListAssociationModel) -> AppWordListAssociation:
        """模型转实体"""
        from src.domain.association.value_objects import AssociationPriority
        
        association = AppWordListAssociation(
            id=model.id,
            app_id=model.app_id,
            wordlist_id=model.wordlist_id,
            is_active=model.is_active,
            priority=AssociationPriority(model.priority),
            memo=model.memo,
            associated_at=model.associated_at,
            associated_by=model.associated_by,
            create_time=model.create_time,
            update_time=model.update_time,
            delete_time=model.delete_time,
            create_by=model.create_by,
            update_by=model.update_by,
            delete_by=model.delete_by
        )
        
        # 清除领域事件（从数据库加载的实体不应该有事件）
        association._domain_events.clear()
        
        return association