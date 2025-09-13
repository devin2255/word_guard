"""仅测试API文档生成的简化应用"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# 只导入我们的文本风控路由
from src.interfaces.routes.moderation_routes import moderation_router

def create_docs_test_app() -> FastAPI:
    """创建仅用于测试文档生成的应用"""
    
    app = FastAPI(
        title="御言内容风控系统 - 文档测试",
        description="测试API文档生成",
        version="2.0.0",
        docs_url="/docs"
    )
    
    # 配置CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # 只注册文本风控路由
    app.include_router(moderation_router, prefix="/v1")
    
    @app.get("/", summary="系统信息")
    async def root():
        return {
            "name": "御言内容风控系统",
            "version": "2.0.0",
            "status": "docs_test",
            "docs": "/docs"
        }
    
    @app.get("/health", summary="健康检查")
    async def health_check():
        return {"status": "ok", "message": "文档测试服务运行正常"}
    
    return app

# 创建应用实例
app = create_docs_test_app()

if __name__ == '__main__':
    uvicorn.run(
        "test_docs_only:app",
        host="0.0.0.0",
        port=18002,
        reload=True,
        log_level="info"
    )