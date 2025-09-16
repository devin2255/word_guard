"""应用入口"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.config import settings, init_database
from src.interfaces.routes import wordlist_router, app_router
from src.interfaces.routes.list_detail_routes import router as list_detail_router
from src.interfaces.routes.association_routes import router as association_router
from src.interfaces.routes.moderation_routes import moderation_router
from src.shared.containers import container


def create_app() -> FastAPI:
    """创建FastAPI应用"""
    
    app = FastAPI(
        title=settings.app_name,
        description="御言内容风控系统",
        version="2.0.0",
        docs_url="/docs",
        swagger_js_url="https://unpkg.com/swagger-ui-dist@5.9.0/swagger-ui-bundle.js",
        swagger_css_url="https://unpkg.com/swagger-ui-dist@5.9.0/swagger-ui.css",
        debug=settings.debug_mode
    )
    
    # 配置CORS跨域
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # 允许所有域名访问，生产环境需调整
        allow_credentials=True,  # 允许携带凭据（如 cookies）
        allow_methods=["*"],  # 允许所有 HTTP 方法
        allow_headers=["*"],  # 允许所有请求头
    )
    
    # 注册路由
    app.include_router(wordlist_router, prefix="/v1")
    app.include_router(app_router, prefix="/v1")
    app.include_router(list_detail_router, prefix="/v1")
    app.include_router(association_router, prefix="/v1")
    app.include_router(moderation_router, prefix="/v1")
    
    # 初始化数据库
    init_database(app)

    # 初始化依赖注入容器
    container.wire(modules=[
        "src.interfaces.routes.wordlist_routes",
        "src.interfaces.routes.app_routes",
        "src.interfaces.routes.list_detail_routes",
        "src.interfaces.routes.association_routes",
        "src.interfaces.routes.moderation_routes"
    ])
    
    # 初始化事件处理器 - 确保事件驱动架构正常工作
    from src.shared.containers import setup_event_handlers
    setup_event_handlers(container)

    # 根路径
    @app.get("/", summary="系统信息")
    async def root():
        return {
            "name": settings.app_name,
            "version": "2.0.0",
            "architecture": "DDD (Domain-Driven Design)",
            "environment": settings.app_env,
            "docs": "/docs"
        }
    
    # 健康检查
    @app.get("/health", summary="健康检查")
    async def health_check():
        return {"status": "ok", "message": "服务运行正常"}
    
    return app


# 创建应用实例
app = create_app()