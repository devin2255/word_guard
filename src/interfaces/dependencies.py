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
from src.interfaces.controllers import WordListController, AppController, ModerationController
from src.application.services.moderation_service import ModerationApplicationService
from src.domain.moderation.services.text_moderation_service import TextModerationService
from src.infrastructure.repositories import ListDetailRepositoryImpl, AssociationRepositoryImpl


# 仓储实例（单例）
_wordlist_repository = WordListRepositoryImpl()
_app_repository = AppRepositoryImpl()
_list_detail_repository = ListDetailRepositoryImpl()
_association_repository = AssociationRepositoryImpl()

# 处理器实例（单例）
_wordlist_command_handler = WordListCommandHandler(_wordlist_repository)
_wordlist_query_handler = WordListQueryHandler(_wordlist_repository)
_app_command_handler = AppCommandHandler(_app_repository)
_app_query_handler = AppQueryHandler(_app_repository)

# 服务实例（单例）
_text_moderation_service = TextModerationService(
    _wordlist_repository, 
    _list_detail_repository, 
    _association_repository
)
_moderation_service = ModerationApplicationService(
    _text_moderation_service,
    _wordlist_repository,
    _list_detail_repository,
    _association_repository
)

# 控制器实例（单例）
_wordlist_controller = WordListController(_wordlist_command_handler, _wordlist_query_handler)
_app_controller = AppController(_app_command_handler, _app_query_handler)
_moderation_controller = ModerationController(_moderation_service)


def get_wordlist_controller() -> WordListController:
    """获取名单控制器"""
    return _wordlist_controller


def get_app_controller() -> AppController:
    """获取应用控制器"""
    return _app_controller


def get_moderation_controller() -> ModerationController:
    """获取文本风控控制器"""
    return _moderation_controller