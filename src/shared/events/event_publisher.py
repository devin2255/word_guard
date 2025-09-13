"""事件发布器"""
import asyncio
from abc import ABC, abstractmethod
from typing import List, Dict, Callable, Any
import logging

from .domain_event import DomainEvent

logger = logging.getLogger(__name__)


class EventHandler(ABC):
    """事件处理器接口"""
    
    @abstractmethod
    async def handle(self, event: DomainEvent) -> None:
        """处理事件"""
        pass


class EventPublisher:
    """事件发布器"""
    
    def __init__(self):
        self._handlers: Dict[str, List[EventHandler]] = {}
    
    def subscribe(self, event_type: str, handler: EventHandler) -> None:
        """订阅事件"""
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)
    
    def unsubscribe(self, event_type: str, handler: EventHandler) -> None:
        """取消订阅事件"""
        if event_type in self._handlers:
            self._handlers[event_type].remove(handler)
    
    async def publish(self, event: DomainEvent) -> None:
        """发布单个事件"""
        event_type = event.__class__.__name__
        handlers = self._handlers.get(event_type, [])
        
        if not handlers:
            logger.warning(f"No handlers registered for event: {event_type}")
            return
        
        # 并发处理所有事件处理器
        tasks = [handler.handle(event) for handler in handlers]
        try:
            await asyncio.gather(*tasks, return_exceptions=True)
            logger.info(f"Published event: {event_type}")
        except Exception as e:
            logger.error(f"Error publishing event {event_type}: {e}")
            raise
    
    async def publish_batch(self, events: List[DomainEvent]) -> None:
        """批量发布事件"""
        if not events:
            return
        
        # 按事件类型分组
        grouped_events: Dict[str, List[DomainEvent]] = {}
        for event in events:
            event_type = event.__class__.__name__
            if event_type not in grouped_events:
                grouped_events[event_type] = []
            grouped_events[event_type].append(event)
        
        # 并发发布所有事件
        tasks = []
        for event_type, event_list in grouped_events.items():
            handlers = self._handlers.get(event_type, [])
            if handlers:
                for event in event_list:
                    for handler in handlers:
                        tasks.append(handler.handle(event))
        
        if tasks:
            try:
                await asyncio.gather(*tasks, return_exceptions=True)
                logger.info(f"Published {len(events)} events")
            except Exception as e:
                logger.error(f"Error publishing batch events: {e}")
                raise
    
    def get_handler_count(self, event_type: str) -> int:
        """获取指定事件类型的处理器数量"""
        return len(self._handlers.get(event_type, []))
    
    def clear_handlers(self, event_type: str = None) -> None:
        """清除事件处理器"""
        if event_type:
            self._handlers.pop(event_type, None)
        else:
            self._handlers.clear()


# 全局事件发布器实例
event_publisher = EventPublisher()