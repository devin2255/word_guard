"""Aerich数据库迁移配置"""
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv(dotenv_path="app/config/product.env")

TORTOISE_ORM = {
    "connections": {
        "default": os.getenv("DATABASE_URL", "mysql://root:2255@127.0.0.1:3306/yuyan")
    },
    "apps": {
        "models": {
            "models": [
                "src.infrastructure.database.models",
                "aerich.models"  # aerich自己的模型
            ],
            "default_connection": "default",
        },
    },
}