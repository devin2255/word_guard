"""应用相关DTO"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class AppDTO(BaseModel):
    """应用数据传输对象"""
    
    id: Optional[int] = None
    app_name: str
    app_id: str
    username: Optional[str] = None
    create_time: Optional[datetime] = None
    update_time: Optional[datetime] = None
    create_by: Optional[str] = None
    update_by: Optional[str] = None
    
    class Config:
        from_attributes = True


class CreateAppRequest(BaseModel):
    """创建应用请求"""
    
    app_name: str = Field(..., min_length=1, max_length=100, description="应用名称")
    app_id: str = Field(..., min_length=1, max_length=50, description="应用ID")
    username: Optional[str] = Field(None, max_length=50, description="负责人")