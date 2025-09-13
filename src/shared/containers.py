"""依赖注入容器"""
from dependency_injector import containers, providers
from dependency_injector.wiring import Provide, inject

from src.application.handlers import (
    WordListCommandHandler, 
    WordListQueryHandler,
    AppCommandHandler,
    AppQueryHandler
)
from src.application.handlers.list_detail_handlers import (
    ListDetailCommandHandler,
    ListDetailQueryHandler
)
from src.application.handlers.association_handlers import (
    AssociationCommandHandler,
    AssociationQueryHandler
)
from src.infrastructure.repositories import (
    WordListRepositoryImpl,
    AppRepositoryImpl,
    ListDetailRepositoryImpl,
    AssociationRepositoryImpl
)
from src.interfaces.controllers import WordListController, AppController
from src.interfaces.controllers.list_detail_controller import ListDetailController
from src.interfaces.controllers.association_controller import AssociationController
from src.application.services.moderation_service import ModerationApplicationService
from src.domain.moderation.services.text_moderation_service import TextModerationService
from src.shared.events.event_publisher import event_publisher, EventPublisher
from src.shared.patterns import UnitOfWorkFactory
from src.domain.wordlist.events.event_handlers import (
    WordListCreatedEventHandler,
    WordListUpdatedEventHandler,
    WordListAuditEventHandler
)
from src.domain.listdetail.events.event_handlers import (
    ListDetailCreatedEventHandler,
    ListDetailUpdatedEventHandler,
    ListDetailActivatedEventHandler,
    ListDetailDeactivatedEventHandler,
    ListDetailBatchProcessedEventHandler,
    ListDetailAuditEventHandler,
    ListDetailStatisticsEventHandler
)
from src.domain.listdetail.services import ListDetailDomainService
from src.domain.association.services import AssociationDomainService


class ApplicationContainer(containers.DeclarativeContainer):
    """应用容器"""
    
    # 配置
    config = providers.Configuration()
    
    # 事件发布器 (单例)
    event_publisher = providers.Singleton(EventPublisher)
    
    # 工作单元工厂
    unit_of_work_factory = providers.Factory(UnitOfWorkFactory)
    
    # 仓储层 (单例)
    wordlist_repository = providers.Singleton(WordListRepositoryImpl)
    app_repository = providers.Singleton(AppRepositoryImpl)
    list_detail_repository = providers.Singleton(ListDetailRepositoryImpl)
    association_repository = providers.Singleton(AssociationRepositoryImpl)
    
    # 领域服务
    list_detail_domain_service = providers.Factory(
        ListDetailDomainService,
        repository=list_detail_repository
    )
    
    association_domain_service = providers.Factory(
        AssociationDomainService,
        repository=association_repository
    )
    
    # 文本风控领域服务
    text_moderation_service = providers.Factory(
        TextModerationService,
        wordlist_repository=wordlist_repository,
        listdetail_repository=list_detail_repository,
        association_repository=association_repository
    )
    
    # 文本风控应用服务
    moderation_service = providers.Factory(
        ModerationApplicationService,
        text_moderation_service=text_moderation_service,
        wordlist_repository=wordlist_repository,
        listdetail_repository=list_detail_repository,
        association_repository=association_repository
    )
    
    # 事件处理器
    wordlist_created_handler = providers.Factory(WordListCreatedEventHandler)
    wordlist_updated_handler = providers.Factory(WordListUpdatedEventHandler)
    wordlist_audit_handler = providers.Factory(WordListAuditEventHandler)
    
    # 名单详情事件处理器
    list_detail_created_handler = providers.Factory(ListDetailCreatedEventHandler)
    list_detail_updated_handler = providers.Factory(ListDetailUpdatedEventHandler)
    list_detail_activated_handler = providers.Factory(ListDetailActivatedEventHandler)
    list_detail_deactivated_handler = providers.Factory(ListDetailDeactivatedEventHandler)
    list_detail_batch_processed_handler = providers.Factory(ListDetailBatchProcessedEventHandler)
    list_detail_audit_handler = providers.Factory(ListDetailAuditEventHandler)
    list_detail_statistics_handler = providers.Factory(ListDetailStatisticsEventHandler)
    
    # 应用层处理器
    wordlist_command_handler = providers.Factory(
        WordListCommandHandler,
        wordlist_repository=wordlist_repository,
        association_service=association_domain_service,
        app_repository=app_repository
    )
    
    wordlist_query_handler = providers.Factory(
        WordListQueryHandler,
        wordlist_repository=wordlist_repository
    )
    
    app_command_handler = providers.Factory(
        AppCommandHandler,
        app_repository=app_repository,
        unit_of_work_factory=unit_of_work_factory
    )
    
    app_query_handler = providers.Factory(
        AppQueryHandler,
        app_repository=app_repository
    )
    
    # 名单详情应用层处理器
    list_detail_command_handler = providers.Factory(
        ListDetailCommandHandler,
        repository=list_detail_repository,
        domain_service=list_detail_domain_service
    )
    
    list_detail_query_handler = providers.Factory(
        ListDetailQueryHandler,
        repository=list_detail_repository,
        domain_service=list_detail_domain_service
    )
    
    # 关联应用层处理器
    association_command_handler = providers.Factory(
        AssociationCommandHandler,
        repository=association_repository,
        domain_service=association_domain_service
    )
    
    association_query_handler = providers.Factory(
        AssociationQueryHandler,
        repository=association_repository,
        domain_service=association_domain_service
    )
    
    # 控制器层
    wordlist_controller = providers.Factory(
        WordListController,
        command_handler=wordlist_command_handler,
        query_handler=wordlist_query_handler
    )
    
    app_controller = providers.Factory(
        AppController,
        command_handler=app_command_handler,
        query_handler=app_query_handler
    )
    
    # 名单详情控制器
    list_detail_controller = providers.Factory(
        ListDetailController,
        command_handler=list_detail_command_handler,
        query_handler=list_detail_query_handler
    )
    
    # 关联控制器
    association_controller = providers.Factory(
        AssociationController,
        command_handler=association_command_handler,
        query_handler=association_query_handler
    )


class EventContainer(containers.DeclarativeContainer):
    """事件容器"""
    
    # 事件发布器
    event_publisher = providers.Dependency()
    
    # 事件处理器
    wordlist_created_handler = providers.Dependency()
    wordlist_updated_handler = providers.Dependency()
    wordlist_audit_handler = providers.Dependency()


def setup_event_handlers(container: ApplicationContainer) -> None:
    """设置事件处理器"""
    publisher = container.event_publisher()
    
    # WordList 事件订阅
    publisher.subscribe("WordListCreatedEvent", container.wordlist_created_handler())
    publisher.subscribe("WordListUpdatedEvent", container.wordlist_updated_handler())
    
    # WordList 审计处理器订阅所有事件
    publisher.subscribe("WordListCreatedEvent", container.wordlist_audit_handler())
    publisher.subscribe("WordListUpdatedEvent", container.wordlist_audit_handler())
    
    # ListDetail 事件订阅
    publisher.subscribe("ListDetailCreatedEvent", container.list_detail_created_handler())
    publisher.subscribe("ListDetailUpdatedEvent", container.list_detail_updated_handler())
    publisher.subscribe("ListDetailActivatedEvent", container.list_detail_activated_handler())
    publisher.subscribe("ListDetailDeactivatedEvent", container.list_detail_deactivated_handler())
    publisher.subscribe("ListDetailBatchProcessedEvent", container.list_detail_batch_processed_handler())
    
    # ListDetail 审计处理器订阅所有ListDetail事件
    publisher.subscribe("ListDetailCreatedEvent", container.list_detail_audit_handler())
    publisher.subscribe("ListDetailUpdatedEvent", container.list_detail_audit_handler())
    publisher.subscribe("ListDetailActivatedEvent", container.list_detail_audit_handler())
    publisher.subscribe("ListDetailDeactivatedEvent", container.list_detail_audit_handler())
    publisher.subscribe("ListDetailBatchProcessedEvent", container.list_detail_audit_handler())
    
    # ListDetail 统计处理器订阅所有ListDetail事件
    publisher.subscribe("ListDetailCreatedEvent", container.list_detail_statistics_handler())
    publisher.subscribe("ListDetailUpdatedEvent", container.list_detail_statistics_handler())
    publisher.subscribe("ListDetailActivatedEvent", container.list_detail_statistics_handler())
    publisher.subscribe("ListDetailDeactivatedEvent", container.list_detail_statistics_handler())
    publisher.subscribe("ListDetailBatchProcessedEvent", container.list_detail_statistics_handler())


def create_container() -> ApplicationContainer:
    """创建并配置容器"""
    container = ApplicationContainer()
    
    # 配置设置
    container.config.from_dict({
        "database": {
            "url": "mysql://user:password@localhost/wordguard",
            "echo": False
        },
        "app": {
            "debug": False,
            "port": 18000
        }
    })
    
    # 设置事件处理器
    setup_event_handlers(container)
    
    return container


# 全局容器实例
container = create_container()


# 依赖注入装饰器
def get_wordlist_controller() -> WordListController:
    """获取名单控制器"""
    return container.wordlist_controller()


def get_app_controller() -> AppController:
    """获取应用控制器"""
    return container.app_controller()


def get_event_publisher() -> EventPublisher:
    """获取事件发布器"""
    return container.event_publisher()


def get_unit_of_work_factory() -> UnitOfWorkFactory:
    """获取工作单元工厂"""
    return container.unit_of_work_factory()


def get_list_detail_controller() -> ListDetailController:
    """获取名单详情控制器"""
    return container.list_detail_controller()


def get_association_controller() -> AssociationController:
    """获取关联控制器"""
    return container.association_controller()


# FastAPI 依赖注入函数
async def get_wordlist_controller_dependency(
    controller: WordListController = Provide[ApplicationContainer.wordlist_controller]
) -> WordListController:
    """FastAPI 名单控制器依赖"""
    return controller


async def get_app_controller_dependency(
    controller: AppController = Provide[ApplicationContainer.app_controller]
) -> AppController:
    """FastAPI 应用控制器依赖"""
    return controller


async def get_list_detail_controller_dependency(
    controller: ListDetailController = Provide[ApplicationContainer.list_detail_controller]
) -> ListDetailController:
    """FastAPI 名单详情控制器依赖"""
    return controller


async def get_association_controller_dependency(
    controller: AssociationController = Provide[ApplicationContainer.association_controller]
) -> AssociationController:
    """FastAPI 关联控制器依赖"""
    return controller