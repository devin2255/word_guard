"""名单仓储实现"""
from typing import List, Optional

from src.domain.wordlist.entities import WordList
from src.domain.wordlist.repositories import WordListRepository
from src.domain.wordlist.value_objects import ListName, RiskLevel
from src.shared.enums.list_enums import ListTypeEnum, MatchRuleEnum, SwitchEnum, LanguageEnum
from src.infrastructure.database.models import WordListModel


class WordListRepositoryImpl(WordListRepository):
    """名单仓储实现"""

    async def save(self, wordlist: WordList) -> WordList:
        """保存名单"""
        
        if wordlist.id is None:
            # 新增
            model = await WordListModel.create(
                list_name=str(wordlist.list_name),
                list_type=wordlist.list_type,
                match_rule=wordlist.match_rule,
                suggestion=wordlist.suggestion,
                risk_type=wordlist.risk_level.risk_type,
                status=wordlist.status,
                language=wordlist.language,
                create_by=wordlist.create_by,
            )
            wordlist.id = model.id
            wordlist.create_time = model.create_time
            wordlist.update_time = model.update_time
        else:
            # 更新
            model = await WordListModel.get(id=wordlist.id)
            
            model.list_name = str(wordlist.list_name)
            model.list_type = wordlist.list_type
            model.match_rule = wordlist.match_rule
            model.suggestion = wordlist.suggestion
            model.risk_type = wordlist.risk_level.risk_type
            model.status = wordlist.status
            model.language = wordlist.language
            model.update_by = wordlist.update_by
            model.delete_time = wordlist.delete_time
            model.delete_by = wordlist.delete_by
            
            await model.save()
            
            wordlist.update_time = model.update_time
        
        return wordlist

    async def find_by_id(self, wordlist_id: int) -> Optional[WordList]:
        """根据ID查找名单"""
        
        try:
            model = await WordListModel.get(id=wordlist_id)
            return self._model_to_entity(model)
        except:
            return None

    async def find_by_name(self, name: str) -> Optional[WordList]:
        """根据名称查找名单"""
        
        try:
            model = await WordListModel.filter(list_name=name, delete_time__isnull=True).first()
            if model:
                return self._model_to_entity(model)
            return None
        except:
            return None

    async def find_all(self, include_deleted: bool = False) -> List[WordList]:
        """查找所有名单"""
        
        query = WordListModel.all()
        if not include_deleted:
            query = query.filter(delete_time__isnull=True)
        
        models = await query
        return [self._model_to_entity(model) for model in models]

    async def find_by_type(self, list_type: ListTypeEnum, include_deleted: bool = False) -> List[WordList]:
        """根据类型查找名单"""
        
        query = WordListModel.filter(list_type=list_type)
        if not include_deleted:
            query = query.filter(delete_time__isnull=True)
        
        models = await query
        return [self._model_to_entity(model) for model in models]

    async def find_by_match_rule(self, match_rule: MatchRuleEnum, include_deleted: bool = False) -> List[WordList]:
        """根据匹配规则查找名单"""
        
        query = WordListModel.filter(match_rule=match_rule)
        if not include_deleted:
            query = query.filter(delete_time__isnull=True)
        
        models = await query
        return [self._model_to_entity(model) for model in models]

    async def find_active_lists(self) -> List[WordList]:
        """查找激活的名单"""
        
        models = await WordListModel.filter(
            status=SwitchEnum.ON, 
            delete_time__isnull=True
        )
        return [self._model_to_entity(model) for model in models]

    async def delete(self, wordlist_id: int) -> bool:
        """删除名单"""
        
        try:
            await WordListModel.filter(id=wordlist_id).delete()
            return True
        except:
            return False

    async def exists_by_name(self, name: str, exclude_id: int = None) -> bool:
        """检查名称是否存在"""
        
        query = WordListModel.filter(list_name=name, delete_time__isnull=True)
        if exclude_id:
            query = query.exclude(id=exclude_id)
        
        return await query.exists()

    async def count_by_type(self, list_type: ListTypeEnum) -> int:
        """按类型统计数量"""
        
        return await WordListModel.filter(
            list_type=list_type, 
            delete_time__isnull=True
        ).count()

    def _model_to_entity(self, model: WordListModel) -> WordList:
        """将数据库模型转换为领域实体"""
        
        list_name = ListName.create(model.list_name)
        risk_level = RiskLevel(risk_type=model.risk_type)
        
        wordlist = WordList(
            id=model.id,
            list_name=list_name,
            list_type=model.list_type,
            match_rule=model.match_rule,
            suggestion=model.suggestion,
            risk_level=risk_level,
            status=model.status,
            language=model.language,
            create_time=model.create_time,
            update_time=model.update_time,
            delete_time=model.delete_time,
            create_by=model.create_by,
            update_by=model.update_by,
            delete_by=model.delete_by,
        )
        
        return wordlist