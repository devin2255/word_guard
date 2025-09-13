"""文本风控测试服务器"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from src.interfaces.routes.moderation_routes import moderation_router


def create_moderation_app() -> FastAPI:
    """创建仅包含文本风控功能的FastAPI应用"""
    
    app = FastAPI(
        title="文本风控测试系统",
        description="专门测试文本风控功能的服务器",
        version="1.0.0",
        docs_url="/docs"
    )
    
    # 配置CORS跨域
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # 注册文本风控路由
    app.include_router(moderation_router, prefix="/v1")
    
    # 根路径
    @app.get("/", summary="系统信息")
    async def root():
        return {
            "name": "文本风控测试系统",
            "version": "1.0.0",
            "features": ["AC自动机算法", "多规则匹配", "风险等级评估"],
            "docs": "/docs",
            "main_endpoint": "/v1/moderation/check"
        }
    
    # 健康检查
    @app.get("/health", summary="健康检查")
    async def health_check():
        return {"status": "ok", "message": "文本风控服务运行正常"}
    
    return app


# 创建应用实例
app = create_moderation_app()


if __name__ == '__main__':
    # 启动服务器
    uvicorn.run(
        "moderation_test_server:app",
        host="0.0.0.0",
        port=18001,  # 使用不同端口避免冲突
        reload=True,
        log_level="info"
    )