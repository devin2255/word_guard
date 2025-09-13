"""简化版主应用 - 不依赖数据库连接"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# 只导入不依赖数据库的路由
from src.interfaces.routes.moderation_routes import moderation_router

def create_simple_app() -> FastAPI:
    """创建简化版应用"""
    
    app = FastAPI(
        title="御言内容风控系统",
        description="御言内容风控系统 - DDD架构重构版",
        version="2.0.0",
        docs_url="/docs",
        swagger_js_url="https://unpkg.com/swagger-ui-dist@5.9.0/swagger-ui-bundle.js",
        swagger_css_url="https://unpkg.com/swagger-ui-dist@5.9.0/swagger-ui.css",
        debug=True
    )
    
    # 配置CORS跨域
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # 允许所有域名访问，生产环境需调整
        allow_credentials=True,  # 允许携带凭据（如 cookies）
        allow_methods=["*"],  # 允许所有 HTTP 方法
        allow_headers=["*"],  # 允许所有请求头
    )
    
    # 注册文本风控路由
    app.include_router(moderation_router, prefix="/v1")
    
    # 根路径
    @app.get("/", summary="系统信息")
    async def root():
        return {
            "name": "御言内容风控系统",
            "version": "2.0.0",
            "architecture": "DDD (Domain-Driven Design)",
            "environment": "simplified",
            "docs": "/docs",
            "note": "简化版本 - 仅包含文本风控功能"
        }
    
    # 健康检查
    @app.get("/health", summary="健康检查")
    async def health_check():
        return {"status": "ok", "message": "简化版服务运行正常"}
    
    return app

# 创建应用实例
app = create_simple_app()

if __name__ == '__main__':
    # 启动服务器
    uvicorn.run(
        "simple_yuyan:app",
        host="0.0.0.0",
        port=18000,  # 使用主应用端口
        reload=True,
        log_level="info"
    )