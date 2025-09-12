"""数据库配置"""
from tortoise.contrib.fastapi import register_tortoise
from fastapi import FastAPI

from .settings import settings


def init_database(app: FastAPI) -> None:
    """初始化数据库"""
    
    register_tortoise(
        app,
        db_url=settings.database_url,
        modules={
            "models": [
                "src.infrastructure.database.models"
            ]
        },
        generate_schemas=False,  # 关闭自动生成，使用aerich管理迁移
        add_exception_handlers=True,  # 添加异常处理器
    )