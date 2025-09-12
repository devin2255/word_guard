"""测试配置和夹具"""
import asyncio
import os
import sys
from typing import AsyncGenerator

import pytest
from fastapi.testclient import TestClient
from tortoise.contrib.test import finalizer, initializer

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.main import app
from src.config.aerich_config import TORTOISE_ORM


@pytest.fixture(scope="session")
def event_loop():
    """创建事件循环"""
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session", autouse=True)
async def initialize_tests():
    """初始化测试环境"""
    # 使用测试数据库配置
    test_config = TORTOISE_ORM.copy()
    test_config["connections"]["default"] = "sqlite://:memory:"
    
    await initializer(
        modules=test_config["apps"]["models"]["models"],
        db_url="sqlite://:memory:",
        app_label="models"
    )
    yield
    await finalizer()


@pytest.fixture
def client() -> TestClient:
    """创建测试客户端"""
    return TestClient(app)


@pytest.fixture
async def async_client():
    """创建异步测试客户端"""
    from httpx import AsyncClient
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac