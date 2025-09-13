"""关联命令定义"""
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class CreateAssociationCommand:
    """创建关联命令"""
    app_id: int
    wordlist_id: int
    priority: int = 0
    memo: Optional[str] = None
    associated_by: Optional[str] = None


@dataclass
class UpdateAssociationCommand:
    """更新关联命令"""
    association_id: int
    priority: Optional[int] = None
    memo: Optional[str] = None
    is_active: Optional[bool] = None
    updated_by: Optional[str] = None


@dataclass
class DeleteAssociationCommand:
    """删除关联命令"""
    association_id: int
    deleted_by: Optional[str] = None


@dataclass
class DeleteAssociationByAppWordlistCommand:
    """根据应用和名单删除关联命令"""
    app_id: int
    wordlist_id: int
    deleted_by: Optional[str] = None


@dataclass
class BatchCreateAssociationsCommand:
    """批量创建关联命令"""
    app_id: int
    wordlist_ids: List[int]
    default_priority: int = 0
    memo: Optional[str] = None
    associated_by: Optional[str] = None


@dataclass
class BatchUpdateAssociationsCommand:
    """批量更新关联命令"""
    association_ids: List[int]
    priority: Optional[int] = None
    is_active: Optional[bool] = None
    memo: Optional[str] = None
    updated_by: Optional[str] = None


@dataclass
class ActivateAssociationCommand:
    """激活关联命令"""
    association_id: int
    updated_by: Optional[str] = None


@dataclass
class DeactivateAssociationCommand:
    """停用关联命令"""
    association_id: int
    updated_by: Optional[str] = None


@dataclass
class CleanupAppAssociationsCommand:
    """清理应用关联命令"""
    app_id: int
    deleted_by: Optional[str] = None


@dataclass
class CleanupWordlistAssociationsCommand:
    """清理名单关联命令"""
    wordlist_id: int
    deleted_by: Optional[str] = None