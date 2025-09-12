"""应用相关命令"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class CreateAppCommand:
    """创建应用命令"""
    
    app_name: str
    app_id: str
    username: Optional[str] = None
    created_by: Optional[str] = None