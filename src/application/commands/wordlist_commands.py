"""名单相关命令"""
from dataclasses import dataclass
from typing import Optional, List


@dataclass
class CreateWordListCommand:
    """创建名单命令"""
    
    list_name: str
    list_type: int
    match_rule: int
    suggestion: int
    risk_type: int
    language: int = 0
    created_by: Optional[str] = None
    
    # 应用绑定相关字段
    app_ids: Optional[List[int]] = None
    bind_all_apps: bool = False
    default_priority: int = 0


@dataclass
class UpdateWordListCommand:
    """更新名单命令"""
    
    wordlist_id: int
    list_name: Optional[str] = None
    status: Optional[int] = None
    risk_type: Optional[int] = None
    updated_by: Optional[str] = None


@dataclass
class DeleteWordListCommand:
    """删除名单命令"""
    
    wordlist_id: int
    deleted_by: Optional[str] = None