"""名单路由"""
from __future__ import annotations
from typing import List, Optional, TYPE_CHECKING
from fastapi import APIRouter, Depends, Query

if TYPE_CHECKING:
    from src.application.dto import WordListDTO, CreateWordListRequest, UpdateWordListRequest
    from src.interfaces.controllers import WordListController
else:
    from src.application.dto import WordListDTO, CreateWordListRequest, UpdateWordListRequest
    from src.interfaces.controllers import WordListController

from src.shared.containers import get_wordlist_controller_dependency


wordlist_router = APIRouter(prefix="/wordlist", tags=["名单管理"])


@wordlist_router.post("", response_model=WordListDTO, summary="创建名单")
async def create_wordlist(
    request: CreateWordListRequest,
    controller: WordListController = Depends(get_wordlist_controller_dependency)
) -> WordListDTO:
    """
    创建新的名单
    
    支持在创建时绑定应用：
    - **app_ids**: 绑定指定应用ID列表（可选）
    - **bind_all_apps**: 是否绑定到所有应用（可选）
    - **default_priority**: 关联优先级，-100到100（默认0）
    
    如果同时指定了app_ids和bind_all_apps=true，则以bind_all_apps为准。
    """
    return await controller.create_wordlist(request)


@wordlist_router.get("/{wordlist_id}", response_model=WordListDTO, summary="获取名单详情")
async def get_wordlist(
    wordlist_id: int,
    controller: WordListController = Depends(get_wordlist_controller_dependency)
) -> WordListDTO:
    """根据ID获取名单详情"""
    return await controller.get_wordlist(wordlist_id)


@wordlist_router.get("", response_model=List[WordListDTO], summary="获取名单列表")
async def get_wordlists(
    list_type: Optional[int] = Query(None, description="名单类型"),
    match_rule: Optional[int] = Query(None, description="匹配规则"),
    status: Optional[int] = Query(None, description="状态"),
    include_deleted: bool = Query(False, description="是否包含已删除"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    controller: WordListController = Depends(get_wordlist_controller_dependency)
) -> List[WordListDTO]:
    """获取名单列表"""
    return await controller.get_wordlists(
        list_type=list_type,
        match_rule=match_rule,
        status=status,
        include_deleted=include_deleted,
        page=page,
        page_size=page_size
    )


@wordlist_router.put("/{wordlist_id}", response_model=WordListDTO, summary="更新名单")
async def update_wordlist(
    wordlist_id: int,
    request: UpdateWordListRequest,
    controller: WordListController = Depends(get_wordlist_controller_dependency)
) -> WordListDTO:
    """更新名单信息"""
    return await controller.update_wordlist(wordlist_id, request)


@wordlist_router.delete("/{wordlist_id}", summary="删除名单")
async def delete_wordlist(
    wordlist_id: int,
    controller: WordListController = Depends(get_wordlist_controller_dependency),
    deleted_by: Optional[str] = Query(None, description="删除人")
) -> dict:
    """删除名单（软删除）"""
    return await controller.delete_wordlist(wordlist_id, deleted_by)