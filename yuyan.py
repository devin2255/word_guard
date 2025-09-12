"""DDD重构版应用启动器"""
from src.main import app

if __name__ == '__main__':
    import uvicorn
    
    # 启动服务器
    uvicorn.run(
        "yuyan_ddd:app",  # 应用路径
        host="0.0.0.0",
        port=18000,
        reload=True,  # 开发模式下自动重载
        log_level="info"
    )