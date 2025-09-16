"""名单处理器"""
from typing import List, Optional

from src.domain.wordlist.entities import WordList
from src.domain.wordlist.repositories import WordListRepository
from src.domain.wordlist.value_objects import ListName, RiskLevel
from src.domain.association.services import AssociationDomainService
from src.domain.app.repositories import AppRepository
from src.shared.enums.list_enums import ListTypeEnum, MatchRuleEnum, ListSuggestEnum, SwitchEnum, LanguageEnum, RiskTypeEnum
from src.shared.exceptions import WordListNotFoundError, WordListValidationError
from src.application.commands.wordlist_commands import CreateWordListCommand, UpdateWordListCommand, DeleteWordListCommand
from src.application.queries.wordlist_queries import GetWordListQuery, GetWordListsQuery
from src.application.dto import WordListDTO


class WordListCommandHandler:
    """名单命令处理器"""
    
    def __init__(
        self, 
        wordlist_repository: WordListRepository,
        association_service: Optional[AssociationDomainService] = None,
        app_repository: Optional[AppRepository] = None
    ):
        self._wordlist_repository = wordlist_repository
        self._association_service = association_service
        self._app_repository = app_repository
    
    async def handle_create(self, command: CreateWordListCommand) -> WordListDTO:
        """处理创建名单命令"""
        
        # 检查名称是否已存在
        if await self._wordlist_repository.exists_by_name(command.list_name):
            raise WordListValidationError("list_name", command.list_name, "名单名称已存在")
        
        # 创建名单实体
        wordlist = WordList.create(
            name=command.list_name,
            list_type=ListTypeEnum(command.list_type),
            match_rule=MatchRuleEnum(command.match_rule),
            suggestion=ListSuggestEnum(command.suggestion),
            risk_type=RiskTypeEnum(command.risk_type),
            language=LanguageEnum(command.language),
            created_by=command.created_by
        )
        
        # 保存到仓储
        saved_wordlist = await self._wordlist_repository.save(wordlist)
        
        # 处理应用绑定
        if self._association_service and (command.bind_all_apps or command.app_ids):
            await self._handle_app_binding(saved_wordlist, command)
        
        # 转换为DTO
        return WordListDTO(**saved_wordlist.to_dict())
    
    async def _handle_app_binding(self, wordlist: WordList, command: CreateWordListCommand) -> None:
        """处理应用绑定"""
        try:
            target_app_ids = []
            
            if command.bind_all_apps:
                # 绑定所有应用
                if self._app_repository:
                    all_apps = await self._app_repository.find_all()
                    target_app_ids = [app.id for app in all_apps if app.id is not None and not app.is_deleted()]
            elif command.app_ids:
                # 绑定指定应用
                target_app_ids = command.app_ids
            
            # 批量创建关联
            if target_app_ids:
                result = await self._association_service.batch_create_associations(
                    app_id=0,  # 占位符，实际会被覆盖
                    wordlist_ids=[wordlist.id],
                    default_priority=command.default_priority,
                    memo=f"创建名单时自动绑定",
                    associated_by=command.created_by
                )
                
                # 由于批量创建接口是为单个应用绑定多个名单设计的，需要逐个创建关联
                success_count = 0
                for app_id in target_app_ids:
                    try:
                        await self._association_service.create_association(
                            app_id=app_id,
                            wordlist_id=wordlist.id,
                            priority=command.default_priority,
                            memo=f"创建名单时自动绑定",
                            associated_by=command.created_by
                        )
                        success_count += 1
                    except Exception:
                        # 忽略单个绑定失败，继续处理其他绑定
                        continue
                
                # 记录绑定结果（可以考虑添加日志）
                if success_count > 0:
                    pass  # 可以添加日志记录成功绑定的数量
                
        except Exception:
            # 应用绑定失败不应该影响名单创建，只记录错误但不抛出异常
            pass
    
    async def handle_update(self, command: UpdateWordListCommand) -> WordListDTO:
        """处理更新名单命令"""
        
        # 查找名单
        wordlist = await self._wordlist_repository.find_by_id(command.wordlist_id)
        if not wordlist:
            raise WordListNotFoundError(command.wordlist_id)
        
        # 更新字段
        if command.list_name is not None:
            # 检查名称是否已存在
            if await self._wordlist_repository.exists_by_name(command.list_name, exclude_id=command.wordlist_id):
                raise WordListValidationError("list_name", command.list_name, "名单名称已存在")
            wordlist.update_name(command.list_name, command.updated_by)
        
        if command.status is not None:
            wordlist.update_status(SwitchEnum(command.status), command.updated_by)
        
        if command.risk_type is not None:
            wordlist.update_risk_level(
                RiskTypeEnum(command.risk_type),
                command.updated_by
            )
        
        # 保存到仓储
        saved_wordlist = await self._wordlist_repository.save(wordlist)
        
        # 转换为DTO
        return WordListDTO(**saved_wordlist.to_dict())
    
    async def handle_delete(self, command: DeleteWordListCommand) -> bool:
        """处理删除名单命令"""
        
        # 查找名单
        wordlist = await self._wordlist_repository.find_by_id(command.wordlist_id)
        if not wordlist:
            raise WordListNotFoundError(command.wordlist_id)
        
        # 软删除
        wordlist.soft_delete(command.deleted_by)
        
        # 保存到仓储
        await self._wordlist_repository.save(wordlist)
        
        return True


class WordListQueryHandler:
    """名单查询处理器"""
    
    def __init__(self, wordlist_repository: WordListRepository):
        self._wordlist_repository = wordlist_repository
    
    async def handle_get_wordlist(self, query: GetWordListQuery) -> Optional[WordListDTO]:
        """处理获取单个名单查询"""
        
        wordlist = await self._wordlist_repository.find_by_id(query.wordlist_id)
        if not wordlist:
            return None
        
        return WordListDTO(**wordlist.to_dict())
    
    async def handle_get_wordlists(self, query: GetWordListsQuery) -> List[WordListDTO]:
        """处理获取名单列表查询"""
        
        wordlists = []
        
        if query.list_type is not None:
            wordlists = await self._wordlist_repository.find_by_type(
                ListTypeEnum(query.list_type),
                include_deleted=query.include_deleted
            )
        elif query.match_rule is not None:
            wordlists = await self._wordlist_repository.find_by_match_rule(
                MatchRuleEnum(query.match_rule),
                include_deleted=query.include_deleted
            )
        else:
            wordlists = await self._wordlist_repository.find_all(
                include_deleted=query.include_deleted
            )
        
        # 状态过滤
        if query.status is not None:
            status_enum = SwitchEnum(query.status)
            wordlists = [wl for wl in wordlists if wl.status == status_enum]
        
        # 转换为DTO列表
        return [WordListDTO(**wl.to_dict()) for wl in wordlists]