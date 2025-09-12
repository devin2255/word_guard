"""依赖注入配置"""
from src.application.handlers import (
    WordListCommandHandler, 
    WordListQueryHandler,
    AppCommandHandler,
    AppQueryHandler
)
from src.infrastructure.repositories import (
    WordListRepositoryImpl,
    AppRepositoryImpl
)
from src.interfaces.controllers import WordListController, AppController


# 仓储实例（单例）
_wordlist_repository = WordListRepositoryImpl()
_app_repository = AppRepositoryImpl()

# 处理器实例（单例）
_wordlist_command_handler = WordListCommandHandler(_wordlist_repository)
_wordlist_query_handler = WordListQueryHandler(_wordlist_repository)
_app_command_handler = AppCommandHandler(_app_repository)
_app_query_handler = AppQueryHandler(_app_repository)

# 控制器实例（单例）
_wordlist_controller = WordListController(_wordlist_command_handler, _wordlist_query_handler)
_app_controller = AppController(_app_command_handler, _app_query_handler)


def get_wordlist_controller() -> WordListController:
    """获取名单控制器"""
    return _wordlist_controller


def get_app_controller() -> AppController:
    """获取应用控制器"""
    return _app_controller