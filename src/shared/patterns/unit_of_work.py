"""工作单元模式"""
import logging
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Set
from contextlib import asynccontextmanager

from tortoise import transactions
from tortoise.connection import ConnectionHandler

from src.shared.events.domain_event import DomainEvent
from src.shared.events.event_publisher import event_publisher

logger = logging.getLogger(__name__)


class AggregateRoot(ABC):
    """聚合根基类"""
    
    def __init__(self):
        self._domain_events: List[DomainEvent] = []
    
    def add_domain_event(self, event: DomainEvent) -> None:
        """添加领域事件"""
        self._domain_events.append(event)
    
    def get_domain_events(self) -> List[DomainEvent]:
        """获取领域事件"""
        return self._domain_events.copy()
    
    def clear_domain_events(self) -> None:
        """清除领域事件"""
        self._domain_events.clear()


class Repository(ABC):
    """仓储基类"""
    
    def __init__(self):
        self._new: Set[AggregateRoot] = set()
        self._dirty: Set[AggregateRoot] = set()
        self._removed: Set[AggregateRoot] = set()
    
    def add(self, entity: AggregateRoot) -> None:
        """标记为新增"""
        self._new.add(entity)
    
    def update(self, entity: AggregateRoot) -> None:
        """标记为更新"""
        if entity not in self._new:
            self._dirty.add(entity)
    
    def remove(self, entity: AggregateRoot) -> None:
        """标记为删除"""
        if entity in self._new:
            self._new.remove(entity)
        else:
            self._removed.add(entity)
    
    def get_new(self) -> Set[AggregateRoot]:
        """获取新增实体"""
        return self._new
    
    def get_dirty(self) -> Set[AggregateRoot]:
        """获取修改实体"""
        return self._dirty
    
    def get_removed(self) -> Set[AggregateRoot]:
        """获取删除实体"""
        return self._removed
    
    def clear(self) -> None:
        """清除跟踪状态"""
        self._new.clear()
        self._dirty.clear()
        self._removed.clear()
    
    @abstractmethod
    async def persist_new(self, entity: AggregateRoot) -> None:
        """持久化新增实体"""
        pass
    
    @abstractmethod
    async def persist_dirty(self, entity: AggregateRoot) -> None:
        """持久化修改实体"""
        pass
    
    @abstractmethod
    async def persist_removed(self, entity: AggregateRoot) -> None:
        """持久化删除实体"""
        pass


class UnitOfWork:
    """工作单元"""
    
    def __init__(self):
        self._repositories: Dict[str, Repository] = {}
        self._is_committed = False
        self._transaction = None
    
    def register_repository(self, name: str, repository: Repository) -> None:
        """注册仓储"""
        self._repositories[name] = repository
    
    def get_repository(self, name: str) -> Optional[Repository]:
        """获取仓储"""
        return self._repositories.get(name)
    
    async def begin(self) -> None:
        """开始事务"""
        if self._transaction is not None:
            raise RuntimeError("Transaction already started")
        
        # 获取数据库连接并开始事务
        self._transaction = transactions.in_transaction()
        await self._transaction.__aenter__()
        logger.debug("Transaction started")
    
    async def commit(self) -> None:
        """提交工作单元"""
        if self._is_committed:
            raise RuntimeError("Unit of work already committed")
        
        try:
            # 收集所有领域事件
            all_events: List[DomainEvent] = []
            
            # 持久化所有变更
            for repo_name, repository in self._repositories.items():
                # 处理新增
                for entity in repository.get_new():
                    await repository.persist_new(entity)
                    all_events.extend(entity.get_domain_events())
                    entity.clear_domain_events()
                
                # 处理修改
                for entity in repository.get_dirty():
                    await repository.persist_dirty(entity)
                    all_events.extend(entity.get_domain_events())
                    entity.clear_domain_events()
                
                # 处理删除
                for entity in repository.get_removed():
                    await repository.persist_removed(entity)
                    all_events.extend(entity.get_domain_events())
                    entity.clear_domain_events()
                
                # 清除仓储跟踪状态
                repository.clear()
            
            # 提交数据库事务
            if self._transaction:
                await self._transaction.__aexit__(None, None, None)
                self._transaction = None
            
            self._is_committed = True
            logger.debug("Unit of work committed successfully")
            
            # 发布领域事件（在事务提交后）
            if all_events:
                await event_publisher.publish_batch(all_events)
                logger.debug(f"Published {len(all_events)} domain events")
        
        except Exception as e:
            await self.rollback()
            logger.error(f"Error committing unit of work: {e}")
            raise
    
    async def rollback(self) -> None:
        """回滚工作单元"""
        try:
            if self._transaction:
                await self._transaction.__aexit__(Exception, Exception("Rollback"), None)
                self._transaction = None
            
            # 清除所有仓储的跟踪状态
            for repository in self._repositories.values():
                repository.clear()
            
            logger.debug("Unit of work rolled back")
        
        except Exception as e:
            logger.error(f"Error rolling back unit of work: {e}")
            raise
    
    @asynccontextmanager
    async def transaction(self):
        """事务上下文管理器"""
        try:
            await self.begin()
            yield self
            await self.commit()
        except Exception as e:
            await self.rollback()
            raise


class UnitOfWorkFactory:
    """工作单元工厂"""
    
    @staticmethod
    async def create() -> UnitOfWork:
        """创建新的工作单元"""
        return UnitOfWork()
    
    @staticmethod
    @asynccontextmanager
    async def create_scope():
        """创建工作单元作用域"""
        uow = await UnitOfWorkFactory.create()
        try:
            async with uow.transaction():
                yield uow
        finally:
            # 清理资源
            pass