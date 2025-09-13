"""名单详情命令"""
from dataclasses import dataclass
from typing import Optional, List


@dataclass
class CreateListDetailCommand:
    """创建名单详情命令"""
    wordlist_id: int
    original_text: str
    processed_text: Optional[str] = None
    memo: Optional[str] = None
    created_by: Optional[str] = None


@dataclass
class UpdateListDetailCommand:
    """更新名单详情命令"""
    detail_id: int
    original_text: Optional[str] = None
    processed_text: Optional[str] = None
    memo: Optional[str] = None
    updated_by: Optional[str] = None


@dataclass
class DeleteListDetailCommand:
    """删除名单详情命令"""
    detail_id: int
    deleted_by: Optional[str] = None


@dataclass
class ActivateListDetailCommand:
    """激活名单详情命令"""
    detail_id: int
    updated_by: Optional[str] = None


@dataclass
class DeactivateListDetailCommand:
    """停用名单详情命令"""
    detail_id: int
    updated_by: Optional[str] = None


@dataclass
class BatchCreateListDetailsCommand:
    """批量创建名单详情命令"""
    wordlist_id: int
    texts: List[str]
    processing_level: str = "standard"  # basic, standard, advanced, strict
    created_by: Optional[str] = None


@dataclass
class BatchUpdateListDetailsCommand:
    """批量更新名单详情命令"""
    detail_ids: List[int]
    is_active: Optional[bool] = None
    memo: Optional[str] = None
    updated_by: Optional[str] = None


@dataclass
class CleanupDuplicatesCommand:
    """清理重复内容命令"""
    wordlist_id: int
    keep_strategy: str = "earliest"  # earliest, latest
    deleted_by: Optional[str] = None


@dataclass
class ReprocessTextsCommand:
    """重新处理文本命令"""
    wordlist_id: int
    processing_level: str = "standard"
    updated_by: Optional[str] = None