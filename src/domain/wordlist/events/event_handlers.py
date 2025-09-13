"""名单事件处理器"""
import logging
from src.shared.events.event_publisher import EventHandler
from src.shared.events.domain_event import DomainEvent
from .wordlist_events import WordListCreatedEvent, WordListUpdatedEvent

logger = logging.getLogger(__name__)


class WordListCreatedEventHandler(EventHandler):
    """名单创建事件处理器"""
    
    async def handle(self, event: WordListCreatedEvent) -> None:
        """处理名单创建事件"""
        try:
            wordlist = event.wordlist
            logger.info(f"WordList created: {wordlist.list_name} (ID: {wordlist.id})")
            
            # 可以在这里添加：
            # - 发送通知
            # - 更新缓存
            # - 记录审计日志
            # - 同步到其他系统
            
        except Exception as e:
            logger.error(f"Error handling WordListCreatedEvent: {e}")
            raise


class WordListUpdatedEventHandler(EventHandler):
    """名单更新事件处理器"""
    
    async def handle(self, event: WordListUpdatedEvent) -> None:
        """处理名单更新事件"""
        try:
            wordlist = event.wordlist
            field_name = event.field_name
            old_value = event.old_value
            new_value = event.new_value
            
            logger.info(
                f"WordList updated: {wordlist.list_name} (ID: {wordlist.id}), "
                f"Field: {field_name}, {old_value} -> {new_value}"
            )
            
            # 可以在这里添加：
            # - 发送变更通知
            # - 清理相关缓存
            # - 记录变更历史
            # - 触发业务规则检查
            
        except Exception as e:
            logger.error(f"Error handling WordListUpdatedEvent: {e}")
            raise


class WordListAuditEventHandler(EventHandler):
    """名单审计事件处理器"""
    
    async def handle(self, event: DomainEvent) -> None:
        """处理审计日志记录"""
        try:
            event_type = event.__class__.__name__
            event_data = {
                "event_type": event_type,
                "timestamp": event.occurred_at,
                "correlation_id": event.correlation_id,
                "data": event.__dict__
            }
            
            # 记录到审计日志系统
            logger.info(f"Audit log: {event_data}")
            
            # 可以在这里：
            # - 保存到审计数据库
            # - 发送到日志收集系统
            # - 触发合规性检查
            
        except Exception as e:
            logger.error(f"Error handling audit event: {e}")
            raise