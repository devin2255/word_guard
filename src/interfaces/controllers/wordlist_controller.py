"""名单控制器"""
from typing import List, Optional
from fastapi import HTTPException, status

from src.application.handlers import WordListCommandHandler, WordListQueryHandler
from src.application.commands import CreateWordListCommand, UpdateWordListCommand, DeleteWordListCommand
from src.application.queries import GetWordListQuery, GetWordListsQuery
from src.application.dto import WordListDTO, CreateWordListRequest, UpdateWordListRequest
from src.shared.exceptions import DomainException


class WordListController:
    """名单控制器"""
    
    def __init__(
        self, 
        command_handler: WordListCommandHandler,
        query_handler: WordListQueryHandler
    ):
        self._command_handler = command_handler
        self._query_handler = query_handler
    
    async def create_wordlist(
        self, 
        request: CreateWordListRequest
    ) -> WordListDTO:
        """创建名单"""
        
        try:
            # 获取应用绑定配置
            app_binding = request.get_app_binding_config()
            
            command = CreateWordListCommand(
                list_name=request.list_name,
                list_type=request.list_type,
                match_rule=request.match_rule,
                suggestion=request.suggestion,
                risk_type=request.risk_type,
                language=request.language,
                created_by=request.created_by,
                app_ids=app_binding["app_ids"],
                bind_all_apps=app_binding["bind_all_apps"],
                default_priority=app_binding["default_priority"]
            )
            
            return await self._command_handler.handle_create(command)
            
        except DomainException as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=e.message
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"创建名单失败: {str(e)}"
            )
    
    async def get_wordlist(self, wordlist_id: int) -> Optional[WordListDTO]:
        """获取单个名单"""
        
        try:
            query = GetWordListQuery(wordlist_id=wordlist_id)
            wordlist = await self._query_handler.handle_get_wordlist(query)
            
            if not wordlist:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"名单 {wordlist_id} 不存在"
                )
            
            return wordlist
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"获取名单失败: {str(e)}"
            )
    
    async def get_wordlists(
        self,
        list_type: Optional[int] = None,
        match_rule: Optional[int] = None,
        status: Optional[int] = None,
        include_deleted: bool = False,
        page: int = 1,
        page_size: int = 20
    ) -> List[WordListDTO]:
        """获取名单列表"""
        
        try:
            query = GetWordListsQuery(
                list_type=list_type,
                match_rule=match_rule,
                status=status,
                include_deleted=include_deleted,
                page=page,
                page_size=page_size
            )
            
            return await self._query_handler.handle_get_wordlists(query)
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"获取名单列表失败: {str(e)}"
            )
    
    async def update_wordlist(
        self, 
        wordlist_id: int,
        request: UpdateWordListRequest
    ) -> WordListDTO:
        """更新名单"""
        
        try:
            command = UpdateWordListCommand(
                wordlist_id=wordlist_id,
                list_name=request.list_name,
                status=request.status,
                risk_type=request.risk_type,
                updated_by=request.updated_by
            )
            
            return await self._command_handler.handle_update(command)
            
        except DomainException as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=e.message
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"更新名单失败: {str(e)}"
            )
    
    async def delete_wordlist(
        self, 
        wordlist_id: int,
        deleted_by: str = None
    ) -> dict:
        """删除名单"""
        
        try:
            command = DeleteWordListCommand(
                wordlist_id=wordlist_id,
                deleted_by=deleted_by
            )
            
            success = await self._command_handler.handle_delete(command)
            
            return {"success": success, "message": "名单删除成功"}
            
        except DomainException as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=e.message
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"删除名单失败: {str(e)}"
            )