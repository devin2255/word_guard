"""名单详情仓储实现"""
from __future__ import annotations
from typing import List, Optional, Dict, Any
from collections import defaultdict

from src.domain.listdetail.entities import ListDetail
from src.domain.listdetail.repositories import ListDetailRepository
from src.domain.listdetail.value_objects import TextContent, ProcessedText
from src.infrastructure.database.models import ListDetailModel
from src.shared.pagination import PageRequest, PageResponse, TortoiseQueryBuilder, QueryRequest
from src.shared.exceptions.infrastructure_exceptions import RepositoryError


class ListDetailRepositoryImpl(ListDetailRepository):
    """名单详情仓储实现"""

    async def save(self, list_detail: ListDetail) -> ListDetail:
        """保存名单详情"""
        try:
            if list_detail.id is None:
                # 新增
                model = await ListDetailModel.create(
                    wordlist_id=list_detail.wordlist_id,
                    original_text=list_detail.text_content.original_text,
                    processed_text=list_detail.text_content.processed_text,
                    memo=list_detail.text_content.memo,
                    text_hash=list_detail.text_hash,
                    word_count=list_detail.word_count,
                    char_count=list_detail.char_count,
                    is_active=list_detail.is_active,
                    create_by=list_detail.create_by,
                )
                list_detail.id = model.id
                list_detail.create_time = model.create_time
                list_detail.update_time = model.update_time
            else:
                # 更新
                model = await ListDetailModel.get(id=list_detail.id)
                
                model.original_text = list_detail.text_content.original_text
                model.processed_text = list_detail.text_content.processed_text
                model.memo = list_detail.text_content.memo
                model.text_hash = list_detail.text_hash
                model.word_count = list_detail.word_count
                model.char_count = list_detail.char_count
                model.is_active = list_detail.is_active
                model.update_by = list_detail.update_by
                model.delete_time = list_detail.delete_time
                model.delete_by = list_detail.delete_by
                
                await model.save()
                list_detail.update_time = model.update_time
            
            return list_detail
        
        except Exception as e:
            raise RepositoryError("ListDetailRepository", "save", str(e), e)

    async def save_batch(self, list_details: List[ListDetail]) -> List[ListDetail]:
        """批量保存名单详情"""
        try:
            saved_details = []
            for detail in list_details:
                saved_detail = await self.save(detail)
                saved_details.append(saved_detail)
            return saved_details
        
        except Exception as e:
            raise RepositoryError("ListDetailRepository", "save_batch", str(e), e)

    async def find_by_id(self, detail_id: int) -> Optional[ListDetail]:
        """根据ID查找名单详情"""
        try:
            model = await ListDetailModel.get(id=detail_id)
            return self._model_to_entity(model)
        except Exception:
            return None

    async def find_by_wordlist_id(
        self, 
        wordlist_id: int,
        include_deleted: bool = False,
        active_only: bool = True
    ) -> List[ListDetail]:
        """根据名单ID查找所有详情"""
        try:
            query = ListDetailModel.filter(wordlist_id=wordlist_id)
            
            if not include_deleted:
                query = query.filter(delete_time__isnull=True)
            
            if active_only:
                query = query.filter(is_active=True)
            
            models = await query.order_by('create_time')
            return [self._model_to_entity(model) for model in models]
        
        except Exception as e:
            raise RepositoryError("ListDetailRepository", "find_by_wordlist_id", str(e), e)

    async def find_by_wordlist_id_with_pagination(
        self,
        wordlist_id: int,
        page_request: PageRequest,
        include_deleted: bool = False,
        active_only: bool = True
    ) -> PageResponse[ListDetail]:
        """根据名单ID分页查找详情"""
        try:
            query = ListDetailModel.filter(wordlist_id=wordlist_id)
            
            if not include_deleted:
                query = query.filter(delete_time__isnull=True)
            
            if active_only:
                query = query.filter(is_active=True)
            
            # 构建查询请求
            query_request = QueryRequest(page_request)
            
            # 执行分页查询
            models, total_count = await TortoiseQueryBuilder.execute_query_with_pagination(
                query,
                query_request,
                search_fields=["original_text", "processed_text", "memo"]
            )
            
            # 转换为领域实体
            details = [self._model_to_entity(model) for model in models]
            
            # 创建分页响应
            return PageResponse.create(details, page_request, total_count)
        
        except Exception as e:
            raise RepositoryError("ListDetailRepository", "find_by_wordlist_id_with_pagination", str(e), e)

    async def find_by_text_hash(
        self,
        text_hash: str,
        include_deleted: bool = False
    ) -> List[ListDetail]:
        """根据文本哈希查找详情"""
        try:
            query = ListDetailModel.filter(text_hash=text_hash)
            
            if not include_deleted:
                query = query.filter(delete_time__isnull=True)
            
            models = await query
            return [self._model_to_entity(model) for model in models]
        
        except Exception as e:
            raise RepositoryError("ListDetailRepository", "find_by_text_hash", str(e), e)

    async def find_by_processed_text(
        self,
        wordlist_id: int,
        processed_text: str,
        include_deleted: bool = False
    ) -> List[ListDetail]:
        """根据处理后文本查找详情"""
        try:
            query = ListDetailModel.filter(
                wordlist_id=wordlist_id,
                processed_text__icontains=processed_text
            )
            
            if not include_deleted:
                query = query.filter(delete_time__isnull=True)
            
            models = await query
            return [self._model_to_entity(model) for model in models]
        
        except Exception as e:
            raise RepositoryError("ListDetailRepository", "find_by_processed_text", str(e), e)

    async def search_by_content(
        self,
        wordlist_id: int = None,
        search_text: str = None,
        page_request: PageRequest = None,
        include_deleted: bool = False,
        active_only: bool = True
    ) -> PageResponse[ListDetail]:
        """根据内容搜索详情"""
        try:
            query = ListDetailModel.all()
            
            if wordlist_id:
                query = query.filter(wordlist_id=wordlist_id)
            
            if not include_deleted:
                query = query.filter(delete_time__isnull=True)
                
            if active_only:
                query = query.filter(is_active=True)
            
            # 默认分页请求
            if page_request is None:
                page_request = PageRequest()
            
            # 构建查询请求
            query_request = QueryRequest(
                page_request=page_request,
                search_keyword=search_text
            )
            
            # 执行搜索查询
            models, total_count = await TortoiseQueryBuilder.execute_query_with_pagination(
                query,
                query_request,
                search_fields=["original_text", "processed_text", "memo"]
            )
            
            # 转换为领域实体
            details = [self._model_to_entity(model) for model in models]
            
            return PageResponse.create(details, page_request, total_count)
        
        except Exception as e:
            raise RepositoryError("ListDetailRepository", "search_by_content", str(e), e)

    async def exists_by_text_hash(
        self,
        wordlist_id: int,
        text_hash: str,
        exclude_id: int = None
    ) -> bool:
        """检查文本哈希是否存在"""
        try:
            query = ListDetailModel.filter(
                wordlist_id=wordlist_id,
                text_hash=text_hash,
                delete_time__isnull=True
            )
            
            if exclude_id:
                query = query.exclude(id=exclude_id)
            
            return await query.exists()
        
        except Exception as e:
            raise RepositoryError("ListDetailRepository", "exists_by_text_hash", str(e), e)

    async def count_by_wordlist_id(
        self,
        wordlist_id: int,
        active_only: bool = True
    ) -> int:
        """统计名单详情数量"""
        try:
            query = ListDetailModel.filter(
                wordlist_id=wordlist_id,
                delete_time__isnull=True
            )
            
            if active_only:
                query = query.filter(is_active=True)
            
            return await query.count()
        
        except Exception as e:
            raise RepositoryError("ListDetailRepository", "count_by_wordlist_id", str(e), e)

    async def get_statistics_by_wordlist_id(
        self,
        wordlist_id: int
    ) -> Dict[str, Any]:
        """获取名单详情统计信息"""
        try:
            total_count = await ListDetailModel.filter(
                wordlist_id=wordlist_id,
                delete_time__isnull=True
            ).count()
            
            active_count = await ListDetailModel.filter(
                wordlist_id=wordlist_id,
                delete_time__isnull=True,
                is_active=True
            ).count()
            
            inactive_count = total_count - active_count
            
            # 统计字符数和词数
            models = await ListDetailModel.filter(
                wordlist_id=wordlist_id,
                delete_time__isnull=True,
                is_active=True
            ).values('word_count', 'char_count')
            
            total_words = sum(model['word_count'] for model in models)
            total_chars = sum(model['char_count'] for model in models)
            avg_words = total_words / active_count if active_count > 0 else 0
            avg_chars = total_chars / active_count if active_count > 0 else 0
            
            return {
                "total_count": total_count,
                "active_count": active_count,
                "inactive_count": inactive_count,
                "total_words": total_words,
                "total_chars": total_chars,
                "avg_words_per_item": round(avg_words, 2),
                "avg_chars_per_item": round(avg_chars, 2)
            }
        
        except Exception as e:
            raise RepositoryError("ListDetailRepository", "get_statistics_by_wordlist_id", str(e), e)

    async def delete_by_wordlist_id(
        self,
        wordlist_id: int,
        deleted_by: str = None
    ) -> int:
        """根据名单ID软删除所有详情"""
        try:
            from datetime import datetime
            
            update_count = await ListDetailModel.filter(
                wordlist_id=wordlist_id,
                delete_time__isnull=True
            ).update(
                delete_time=datetime.now(),
                delete_by=deleted_by,
                is_active=False
            )
            
            return update_count
        
        except Exception as e:
            raise RepositoryError("ListDetailRepository", "delete_by_wordlist_id", str(e), e)

    async def hard_delete_by_wordlist_id(self, wordlist_id: int) -> int:
        """根据名单ID硬删除所有详情"""
        try:
            delete_count = await ListDetailModel.filter(
                wordlist_id=wordlist_id
            ).delete()
            
            return delete_count
        
        except Exception as e:
            raise RepositoryError("ListDetailRepository", "hard_delete_by_wordlist_id", str(e), e)

    async def activate_batch(
        self,
        detail_ids: List[int],
        updated_by: str = None
    ) -> int:
        """批量激活"""
        try:
            from datetime import datetime
            
            update_count = await ListDetailModel.filter(
                id__in=detail_ids,
                delete_time__isnull=True
            ).update(
                is_active=True,
                update_time=datetime.now(),
                update_by=updated_by
            )
            
            return update_count
        
        except Exception as e:
            raise RepositoryError("ListDetailRepository", "activate_batch", str(e), e)

    async def deactivate_batch(
        self,
        detail_ids: List[int],
        updated_by: str = None
    ) -> int:
        """批量停用"""
        try:
            from datetime import datetime
            
            update_count = await ListDetailModel.filter(
                id__in=detail_ids,
                delete_time__isnull=True
            ).update(
                is_active=False,
                update_time=datetime.now(),
                update_by=updated_by
            )
            
            return update_count
        
        except Exception as e:
            raise RepositoryError("ListDetailRepository", "deactivate_batch", str(e), e)

    async def find_duplicates_by_wordlist_id(
        self,
        wordlist_id: int
    ) -> List[List[ListDetail]]:
        """查找重复的名单详情（按文本哈希分组）"""
        try:
            models = await ListDetailModel.filter(
                wordlist_id=wordlist_id,
                delete_time__isnull=True
            ).order_by('text_hash', 'create_time')
            
            # 按文本哈希分组
            hash_groups = defaultdict(list)
            for model in models:
                entity = self._model_to_entity(model)
                hash_groups[model.text_hash].append(entity)
            
            # 只返回有重复的分组
            duplicates = [group for group in hash_groups.values() if len(group) > 1]
            
            return duplicates
        
        except Exception as e:
            raise RepositoryError("ListDetailRepository", "find_duplicates_by_wordlist_id", str(e), e)

    async def get_active_texts_for_matching(
        self,
        wordlist_id: int
    ) -> List[str]:
        """获取用于匹配的激活文本列表"""
        try:
            models = await ListDetailModel.filter(
                wordlist_id=wordlist_id,
                delete_time__isnull=True,
                is_active=True
            ).values('processed_text')
            
            return [model['processed_text'] for model in models]
        
        except Exception as e:
            raise RepositoryError("ListDetailRepository", "get_active_texts_for_matching", str(e), e)

    def _model_to_entity(self, model: ListDetailModel) -> ListDetail:
        """将数据库模型转换为领域实体"""
        text_content = TextContent.create(
            original_text=model.original_text,
            processed_text=model.processed_text,
            memo=model.memo
        )
        
        detail = ListDetail(
            id=model.id,
            wordlist_id=model.wordlist_id,
            text_content=text_content,
            is_active=model.is_active,
            create_time=model.create_time,
            update_time=model.update_time,
            delete_time=model.delete_time,
            create_by=model.create_by,
            update_by=model.update_by,
            delete_by=model.delete_by,
        )
        
        return detail