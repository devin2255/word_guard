"""名单详情领域服务"""
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass

from src.domain.listdetail.entities import ListDetail
from src.domain.listdetail.repositories import ListDetailRepository
from src.domain.listdetail.services.text_processing_service import (
    TextProcessingService, 
    TextProcessingLevel,
    BatchProcessingResult
)
from src.shared.exceptions.domain_exceptions import (
    WordListValidationError,
    WordListBusinessRuleViolationError
)


@dataclass
class DuplicateAnalysisResult:
    """重复分析结果"""
    has_duplicates: bool
    duplicate_groups: List[List[ListDetail]]
    total_duplicates: int
    recommendations: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "has_duplicates": self.has_duplicates,
            "total_duplicates": self.total_duplicates,
            "duplicate_groups_count": len(self.duplicate_groups),
            "recommendations": self.recommendations,
            "duplicate_groups": [
                [detail.to_dict() for detail in group] 
                for group in self.duplicate_groups
            ]
        }


@dataclass
class QualityAnalysisResult:
    """质量分析结果"""
    total_items: int
    active_items: int
    quality_score: float  # 0-1
    issues: List[Dict[str, Any]]
    suggestions: List[str]
    statistics: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_items": self.total_items,
            "active_items": self.active_items,
            "quality_score": self.quality_score,
            "issues": self.issues,
            "suggestions": self.suggestions,
            "statistics": self.statistics
        }


class ListDetailDomainService:
    """名单详情领域服务"""
    
    def __init__(
        self, 
        list_detail_repository: ListDetailRepository,
        text_processing_service: TextProcessingService
    ):
        self._repository = list_detail_repository
        self._text_processor = text_processing_service
    
    async def validate_new_detail(
        self, 
        wordlist_id: int,
        original_text: str,
        processed_text: str = None
    ) -> None:
        """验证新增详情"""
        
        # 处理文本
        processing_result = self._text_processor.process_single_text(
            original_text, 
            TextProcessingLevel.STANDARD
        )
        
        # 如果没有提供处理后文本，使用自动处理结果
        final_processed_text = processed_text or processing_result.processed_text
        
        # 检查是否存在相同的文本哈希
        text_hash = processing_result.text_hash
        exists = await self._repository.exists_by_text_hash(wordlist_id, text_hash)
        
        if exists:
            raise WordListBusinessRuleViolationError(
                "duplicate_text",
                f"相同内容已存在: {original_text[:50]}...",
                {
                    "wordlist_id": wordlist_id,
                    "text_hash": text_hash,
                    "original_text": original_text
                }
            )
        
        # 验证文本长度限制
        if len(original_text) > 500:
            raise WordListValidationError(
                "original_text", 
                original_text, 
                "原始文本长度不能超过500字符"
            )
        
        # 检查名单详情数量限制
        count = await self._repository.count_by_wordlist_id(wordlist_id)
        if count >= 10000:  # 假设每个名单最多10000条详情
            raise WordListBusinessRuleViolationError(
                "count_limit",
                f"名单详情数量已达上限: {count}/10000",
                {
                    "wordlist_id": wordlist_id,
                    "current_count": count,
                    "limit": 10000
                }
            )
    
    async def analyze_duplicates(self, wordlist_id: int) -> DuplicateAnalysisResult:
        """分析重复内容"""
        
        # 获取重复分组
        duplicate_groups = await self._repository.find_duplicates_by_wordlist_id(wordlist_id)
        
        total_duplicates = sum(len(group) - 1 for group in duplicate_groups)
        has_duplicates = total_duplicates > 0
        
        # 生成建议
        recommendations = []
        if has_duplicates:
            recommendations.append(f"发现 {len(duplicate_groups)} 组重复内容，共 {total_duplicates} 个重复项")
            recommendations.append("建议删除重复项，保留创建时间最早的条目")
            
            if total_duplicates > 100:
                recommendations.append("重复项较多，建议批量清理")
        else:
            recommendations.append("未发现重复内容，数据质量良好")
        
        return DuplicateAnalysisResult(
            has_duplicates=has_duplicates,
            duplicate_groups=duplicate_groups,
            total_duplicates=total_duplicates,
            recommendations=recommendations
        )
    
    async def analyze_quality(self, wordlist_id: int) -> QualityAnalysisResult:
        """分析数据质量"""
        
        # 获取统计信息
        stats = await self._repository.get_statistics_by_wordlist_id(wordlist_id)
        
        # 获取所有详情用于分析
        details = await self._repository.find_by_wordlist_id(
            wordlist_id, 
            include_deleted=True,
            active_only=False
        )
        
        issues = []
        suggestions = []
        quality_scores = []
        
        # 分析各种质量问题
        
        # 1. 检查空白内容
        empty_count = sum(
            1 for detail in details 
            if not detail.text_content.processed_text.strip()
        )
        if empty_count > 0:
            issues.append({
                "type": "empty_content",
                "count": empty_count,
                "description": f"发现 {empty_count} 个空白内容"
            })
            suggestions.append("清理空白内容")
        
        quality_scores.append(max(0, 1 - empty_count / max(len(details), 1)))
        
        # 2. 检查过短内容（少于2个字符）
        short_count = sum(
            1 for detail in details
            if len(detail.text_content.processed_text) < 2
        )
        if short_count > 0:
            issues.append({
                "type": "short_content",
                "count": short_count,
                "description": f"发现 {short_count} 个过短内容（少于2字符）"
            })
            suggestions.append("检查过短内容的有效性")
        
        quality_scores.append(max(0, 1 - short_count / max(len(details), 1)))
        
        # 3. 检查重复内容
        duplicate_analysis = await self.analyze_duplicates(wordlist_id)
        if duplicate_analysis.has_duplicates:
            issues.append({
                "type": "duplicate_content",
                "count": duplicate_analysis.total_duplicates,
                "description": f"发现 {duplicate_analysis.total_duplicates} 个重复内容"
            })
            suggestions.extend(duplicate_analysis.recommendations)
        
        quality_scores.append(
            max(0, 1 - duplicate_analysis.total_duplicates / max(len(details), 1))
        )
        
        # 4. 检查停用状态比例
        inactive_ratio = stats["inactive_count"] / max(stats["total_count"], 1)
        if inactive_ratio > 0.3:  # 超过30%停用
            issues.append({
                "type": "high_inactive_ratio",
                "count": stats["inactive_count"],
                "description": f"停用内容比例较高: {inactive_ratio:.1%}"
            })
            suggestions.append("检查停用内容是否需要重新激活或删除")
        
        quality_scores.append(max(0, 1 - inactive_ratio))
        
        # 计算综合质量分数
        overall_quality_score = sum(quality_scores) / len(quality_scores) if quality_scores else 0
        
        # 根据质量分数给出总体建议
        if overall_quality_score >= 0.9:
            suggestions.append("数据质量优秀，无需特别处理")
        elif overall_quality_score >= 0.7:
            suggestions.append("数据质量良好，建议定期清理")
        elif overall_quality_score >= 0.5:
            suggestions.append("数据质量一般，建议重点优化")
        else:
            suggestions.append("数据质量较差，建议全面清理优化")
        
        return QualityAnalysisResult(
            total_items=stats["total_count"],
            active_items=stats["active_count"],
            quality_score=round(overall_quality_score, 3),
            issues=issues,
            suggestions=suggestions,
            statistics=stats
        )
    
    async def batch_process_texts(
        self,
        wordlist_id: int,
        texts: List[str],
        processing_level: TextProcessingLevel = TextProcessingLevel.STANDARD,
        created_by: str = None
    ) -> BatchProcessingResult:
        """批量处理和创建文本详情"""
        
        # 先处理文本
        processing_result = self._text_processor.process_batch_texts(texts, processing_level)
        
        # 创建详情实体
        details_to_create = []
        creation_errors = []
        
        for result in processing_result.results:
            try:
                # 验证是否重复
                await self.validate_new_detail(
                    wordlist_id,
                    result.original_text,
                    result.processed_text
                )
                
                # 创建详情实体
                detail = ListDetail.create(
                    wordlist_id=wordlist_id,
                    original_text=result.original_text,
                    processed_text=result.processed_text,
                    created_by=created_by
                )
                details_to_create.append(detail)
                
            except Exception as e:
                creation_errors.append(str(e))
        
        # 批量保存
        if details_to_create:
            await self._repository.save_batch(details_to_create)
        
        # 更新结果统计
        processing_result.success_count = len(details_to_create)
        processing_result.failure_count = len(creation_errors)
        
        return processing_result
    
    async def suggest_optimizations(
        self, 
        wordlist_id: int
    ) -> Dict[str, Any]:
        """建议优化方案"""
        
        # 获取质量分析结果
        quality_analysis = await self.analyze_quality(wordlist_id)
        
        # 获取重复分析结果
        duplicate_analysis = await self.analyze_duplicates(wordlist_id)
        
        optimizations = {
            "priority": "medium",
            "estimated_improvement": "20%",
            "actions": [],
            "benefits": [],
            "risks": []
        }
        
        # 基于分析结果生成优化建议
        if quality_analysis.quality_score < 0.7:
            optimizations["priority"] = "high"
            optimizations["estimated_improvement"] = "40%"
            
            optimizations["actions"].append("清理低质量内容")
            optimizations["benefits"].append("提高匹配准确性")
        
        if duplicate_analysis.has_duplicates:
            optimizations["actions"].append("去除重复内容")
            optimizations["benefits"].append("减少存储空间")
            optimizations["benefits"].append("提高查询性能")
        
        # 检查是否需要重新处理文本
        details = await self._repository.find_by_wordlist_id(wordlist_id, active_only=True)
        old_format_count = sum(
            1 for detail in details
            if detail.text_content.original_text == detail.text_content.processed_text
        )
        
        if old_format_count > len(details) * 0.5:
            optimizations["actions"].append("重新处理历史文本")
            optimizations["benefits"].append("统一文本处理标准")
        
        # 评估风险
        if len(details) > 5000:
            optimizations["risks"].append("大量数据操作可能影响性能")
            optimizations["risks"].append("建议分批处理")
        
        return {
            "quality_analysis": quality_analysis.to_dict(),
            "duplicate_analysis": duplicate_analysis.to_dict(),
            "optimizations": optimizations
        }
    
    async def cleanup_duplicates(
        self, 
        wordlist_id: int,
        keep_strategy: str = "earliest",  # earliest, latest, manual
        deleted_by: str = None
    ) -> Dict[str, Any]:
        """清理重复内容"""
        
        duplicate_groups = await self._repository.find_duplicates_by_wordlist_id(wordlist_id)
        
        if not duplicate_groups:
            return {
                "success": True,
                "message": "未发现重复内容",
                "deleted_count": 0
            }
        
        deleted_count = 0
        
        for group in duplicate_groups:
            # 根据策略选择要保留的记录
            if keep_strategy == "earliest":
                group.sort(key=lambda x: x.create_time)
                to_delete = group[1:]  # 保留最早的，删除其他
            elif keep_strategy == "latest":
                group.sort(key=lambda x: x.create_time, reverse=True)
                to_delete = group[1:]  # 保留最新的，删除其他
            else:
                # manual策略需要外部指定
                continue
            
            # 执行软删除
            for detail in to_delete:
                detail.soft_delete(deleted_by)
                await self._repository.save(detail)
                deleted_count += 1
        
        return {
            "success": True,
            "message": f"成功清理 {deleted_count} 个重复内容",
            "deleted_count": deleted_count,
            "duplicate_groups_processed": len(duplicate_groups)
        }
    
    async def batch_update_processing(
        self,
        wordlist_id: int,
        processing_level: TextProcessingLevel = TextProcessingLevel.STANDARD,
        updated_by: str = None
    ) -> Dict[str, Any]:
        """批量更新文本处理"""
        
        details = await self._repository.find_by_wordlist_id(
            wordlist_id, 
            active_only=True
        )
        
        if not details:
            return {
                "success": True,
                "message": "没有需要处理的内容",
                "processed_count": 0
            }
        
        processed_count = 0
        error_count = 0
        
        for detail in details:
            try:
                # 重新处理原始文本
                processing_result = self._text_processor.process_single_text(
                    detail.text_content.original_text,
                    processing_level
                )
                
                # 更新处理后的文本
                detail.update_content(
                    processed_text=processing_result.processed_text,
                    updated_by=updated_by
                )
                
                await self._repository.save(detail)
                processed_count += 1
                
            except Exception:
                error_count += 1
        
        return {
            "success": True,
            "message": f"成功处理 {processed_count} 条内容",
            "processed_count": processed_count,
            "error_count": error_count,
            "total_count": len(details)
        }