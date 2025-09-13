"""关联领域服务"""
from __future__ import annotations
from typing import List, Optional, Set, Dict, Any
from src.domain.association.entities import AppWordListAssociation
from src.domain.association.repositories import AssociationRepository
from src.domain.association.value_objects import AssociationPriority
from src.shared.exceptions.domain_exceptions import (
    AssociationValidationError,
    AssociationConflictError,
    AssociationNotFoundError
)
from src.shared.pagination import PageRequest, PageResponse


class AssociationDomainService:
    """关联领域服务"""
    
    def __init__(self, repository: AssociationRepository):
        self._repository = repository
    
    async def create_association(
        self,
        app_id: int,
        wordlist_id: int,
        priority: int = 0,
        memo: str = None,
        associated_by: str = None
    ) -> AppWordListAssociation:
        """创建关联"""
        # 检查关联是否已存在
        existing = await self._repository.find_by_app_and_wordlist(app_id, wordlist_id)
        if existing and not existing.is_deleted():
            raise AssociationConflictError(app_id, wordlist_id)
        
        # 如果存在已删除的关联，恢复它
        if existing and existing.is_deleted():
            existing.is_active = True
            existing.delete_time = None
            existing.delete_by = None
            existing.update_priority(priority, associated_by)
            if memo:
                existing.update_memo(memo, associated_by)
            return await self._repository.save(existing)
        
        # 创建新关联
        association = AppWordListAssociation.create(
            app_id=app_id,
            wordlist_id=wordlist_id,
            priority=priority,
            memo=memo,
            associated_by=associated_by
        )
        
        return await self._repository.save(association)
    
    async def update_association(
        self,
        association_id: int,
        priority: Optional[int] = None,
        memo: Optional[str] = None,
        is_active: Optional[bool] = None,
        updated_by: str = None
    ) -> AppWordListAssociation:
        """更新关联"""
        association = await self._repository.find_by_id(association_id)
        if not association:
            raise AssociationNotFoundError(association_id)
        
        # 更新字段
        if priority is not None:
            association.update_priority(priority, updated_by)
        
        if memo is not None:
            association.update_memo(memo, updated_by)
        
        if is_active is not None:
            if is_active:
                association.activate(updated_by)
            else:
                association.deactivate(updated_by)
        
        return await self._repository.save(association)
    
    async def delete_association(
        self,
        association_id: int,
        deleted_by: str = None
    ) -> bool:
        """删除关联"""
        association = await self._repository.find_by_id(association_id)
        if not association:
            raise AssociationNotFoundError(association_id)
        
        association.soft_delete(deleted_by)
        await self._repository.save(association)
        return True
    
    async def delete_association_by_app_and_wordlist(
        self,
        app_id: int,
        wordlist_id: int,
        deleted_by: str = None
    ) -> bool:
        """根据应用ID和名单ID删除关联"""
        association = await self._repository.find_by_app_and_wordlist(app_id, wordlist_id)
        if not association:
            return False
        
        association.soft_delete(deleted_by)
        await self._repository.save(association)
        return True
    
    async def batch_create_associations(
        self,
        app_id: int,
        wordlist_ids: List[int],
        default_priority: int = 0,
        memo: str = None,
        associated_by: str = None
    ) -> Dict[str, Any]:
        """批量创建关联"""
        results = {
            "total_count": len(wordlist_ids),
            "success_count": 0,
            "failure_count": 0,
            "created_associations": [],
            "errors": []
        }
        
        for wordlist_id in wordlist_ids:
            try:
                association = await self.create_association(
                    app_id=app_id,
                    wordlist_id=wordlist_id,
                    priority=default_priority,
                    memo=memo,
                    associated_by=associated_by
                )
                results["created_associations"].append(association.to_dict())
                results["success_count"] += 1
            except Exception as e:
                results["errors"].append({
                    "wordlist_id": wordlist_id,
                    "error": str(e)
                })
                results["failure_count"] += 1
        
        return results
    
    async def batch_update_associations(
        self,
        association_ids: List[int],
        priority: Optional[int] = None,
        is_active: Optional[bool] = None,
        memo: Optional[str] = None,
        updated_by: str = None
    ) -> Dict[str, Any]:
        """批量更新关联"""
        results = {
            "total_count": len(association_ids),
            "success_count": 0,
            "failure_count": 0,
            "errors": []
        }
        
        # 使用仓储的批量操作（如果只更新激活状态）
        if is_active is not None and priority is None and memo is None:
            if is_active:
                updated = await self._repository.activate_batch(association_ids, updated_by)
            else:
                updated = await self._repository.deactivate_batch(association_ids, updated_by)
            
            results["success_count"] = updated
            results["failure_count"] = len(association_ids) - updated
            return results
        
        # 逐个更新（需要更新多个字段时）
        for association_id in association_ids:
            try:
                await self.update_association(
                    association_id=association_id,
                    priority=priority,
                    memo=memo,
                    is_active=is_active,
                    updated_by=updated_by
                )
                results["success_count"] += 1
            except Exception as e:
                results["errors"].append({
                    "association_id": association_id,
                    "error": str(e)
                })
                results["failure_count"] += 1
        
        return results
    
    async def get_app_associations(
        self,
        app_id: int,
        active_only: bool = False,
        page_request: Optional[PageRequest] = None
    ) -> PageResponse[AppWordListAssociation]:
        """获取应用的关联"""
        return await self._repository.find_with_pagination(
            app_id=app_id,
            active_only=active_only,
            page_request=page_request
        )
    
    async def get_wordlist_associations(
        self,
        wordlist_id: int,
        active_only: bool = False,
        page_request: Optional[PageRequest] = None
    ) -> PageResponse[AppWordListAssociation]:
        """获取名单的关联"""
        return await self._repository.find_with_pagination(
            wordlist_id=wordlist_id,
            active_only=active_only,
            page_request=page_request
        )
    
    async def get_associations_by_priority(
        self,
        app_id: Optional[int] = None,
        wordlist_id: Optional[int] = None,
        min_priority: int = 0,
        active_only: bool = True
    ) -> List[AppWordListAssociation]:
        """按优先级获取关联"""
        return await self._repository.get_associations_by_priority(
            app_id=app_id,
            wordlist_id=wordlist_id,
            min_priority=min_priority,
            active_only=active_only
        )
    
    async def validate_association_before_delete_app(self, app_id: int) -> bool:
        """验证删除应用前是否有关联"""
        associations = await self._repository.find_by_app_id(app_id, active_only=True)
        return len(associations) == 0
    
    async def validate_association_before_delete_wordlist(self, wordlist_id: int) -> bool:
        """验证删除名单前是否有关联"""
        associations = await self._repository.find_by_wordlist_id(wordlist_id, active_only=True)
        return len(associations) == 0
    
    async def cleanup_app_associations(self, app_id: int, deleted_by: str = None) -> int:
        """清理应用的所有关联"""
        return await self._repository.delete_by_app_id(app_id)
    
    async def cleanup_wordlist_associations(self, wordlist_id: int, deleted_by: str = None) -> int:
        """清理名单的所有关联"""
        return await self._repository.delete_by_wordlist_id(wordlist_id)
    
    async def get_association_statistics(self) -> Dict[str, Any]:
        """获取关联统计信息"""
        stats = await self._repository.get_association_statistics()
        
        # 添加优先级分析
        priority_analysis = {
            "critical": 0,  # >= 50
            "high": 0,      # 10-49
            "normal": 0,    # -9 to 9  
            "low": 0        # <= -10
        }
        
        for item in stats.get("priority_distribution", []):
            priority = item["priority"]
            count = item["count"]
            
            if priority >= AssociationPriority.CRITICAL:
                priority_analysis["critical"] += count
            elif priority >= AssociationPriority.HIGH:
                priority_analysis["high"] += count
            elif priority >= AssociationPriority.LOW:
                priority_analysis["normal"] += count
            else:
                priority_analysis["low"] += count
        
        stats["priority_analysis"] = priority_analysis
        return stats
    
    async def suggest_priority_optimization(
        self,
        app_id: Optional[int] = None,
        wordlist_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """建议优先级优化"""
        associations = await self._repository.find_with_pagination(
            app_id=app_id,
            wordlist_id=wordlist_id,
            active_only=True
        )
        
        suggestions = []
        priority_distribution = {}
        
        for association in associations.content:
            priority = association.priority.value
            priority_distribution[priority] = priority_distribution.get(priority, 0) + 1
        
        # 分析优先级分布
        total_associations = len(associations.content)
        if total_associations == 0:
            return {"suggestions": [], "analysis": "没有找到活跃的关联"}
        
        # 检查是否所有关联都是相同优先级
        unique_priorities = set(priority_distribution.keys())
        if len(unique_priorities) == 1:
            priority = list(unique_priorities)[0]
            if priority == AssociationPriority.NORMAL:
                suggestions.append("建议为不同重要性的关联设置不同优先级以优化匹配效率")
            else:
                suggestions.append(f"所有关联都使用相同优先级 {priority}，建议根据重要性进行分级")
        
        # 检查优先级过于集中
        max_count = max(priority_distribution.values())
        if max_count / total_associations > 0.8:
            suggestions.append("优先级分布过于集中，建议进行更细粒度的优先级设置")
        
        # 检查是否缺少高优先级关联
        has_high_priority = any(p >= AssociationPriority.HIGH for p in unique_priorities)
        if not has_high_priority and total_associations > 5:
            suggestions.append("建议为重要关联设置高优先级以提高匹配效率")
        
        return {
            "total_associations": total_associations,
            "priority_distribution": priority_distribution,
            "unique_priorities": len(unique_priorities),
            "suggestions": suggestions
        }