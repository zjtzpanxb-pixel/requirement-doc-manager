"""
质量评分模块 - 完整率/清晰度/一致性评分
"""

from typing import Dict, Any, List
from dataclasses import dataclass
from ..utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class QualityReport:
    """质量报告"""
    completeness_score: float
    clarity_score: float
    consistency_score: float
    overall_score: float
    missing_items: List[str]
    suggestions: List[str]


class QualityScorer:
    """质量评分器"""
    
    # 评分权重
    WEIGHTS = {
        "completeness": 0.4,
        "clarity": 0.3,
        "consistency": 0.3,
    }
    
    # 必填字段权重
    FIELD_WEIGHTS = {
        "user_stories": 30,
        "functional_requirements": 30,
        "business_rules": 15,
        "acceptance_criteria": 15,
        "risks": 10,
    }
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.quality_config = config.get("quality", {})
    
    def calculate(self, prd: Dict[str, Any]) -> QualityReport:
        """
        计算质量评分
        
        Args:
            prd: PRD 文档数据
        
        Returns:
            质量报告
        """
        completeness = self._calc_completeness(prd)
        clarity = self._calc_clarity(prd)
        consistency = self._calc_consistency(prd)
        
        # 加权平均
        overall = (
            completeness * self.WEIGHTS["completeness"] +
            clarity * self.WEIGHTS["clarity"] +
            consistency * self.WEIGHTS["consistency"]
        )
        
        # 生成建议
        suggestions = self._generate_suggestions(prd, completeness, clarity, consistency)
        missing_items = self._get_missing_items(prd)
        
        logger.info(f"质量评分：完整率={completeness:.1f}, 清晰度={clarity:.1f}, 一致性={consistency:.1f}")
        
        return QualityReport(
            completeness_score=completeness,
            clarity_score=clarity,
            consistency_score=consistency,
            overall_score=overall,
            missing_items=missing_items,
            suggestions=suggestions,
        )
    
    def _calc_completeness(self, prd: Dict[str, Any]) -> float:
        """计算完整率"""
        score = 0
        
        for field, weight in self.FIELD_WEIGHTS.items():
            if field in prd and len(prd.get(field, [])) > 0:
                score += weight
        
        return min(100, score)
    
    def _calc_clarity(self, prd: Dict[str, Any]) -> float:
        """计算清晰度"""
        score = 100
        
        # 用户故事格式检查
        for story in prd.get("user_stories", []):
            if not isinstance(story, dict):
                score -= 10
                continue
            if not all(k in story for k in ["role", "need", "benefit"]):
                score -= 10
        
        # 验收标准可测试性检查
        for criteria in prd.get("acceptance_criteria", []):
            if not self._is_testable(criteria):
                score -= 5
        
        return max(0, score)
    
    def _calc_consistency(self, prd: Dict[str, Any]) -> float:
        """计算一致性"""
        score = 100
        
        # TODO: 实现更复杂的冲突检测
        # 检查需求间是否有矛盾
        
        return score
    
    def _is_testable(self, criteria: str) -> bool:
        """检查验收标准是否可测试"""
        testable_keywords = ["可以", "能够", "显示", "返回", "成功", "失败", "必须", "应该"]
        return any(kw in criteria for kw in testable_keywords)
    
    def _generate_suggestions(
        self, 
        prd: Dict[str, Any],
        completeness: float,
        clarity: float,
        consistency: float
    ) -> List[str]:
        """生成改进建议"""
        suggestions = []
        
        if completeness < 80:
            suggestions.append("补充业务规则描述，提高需求完整性")
        
        if clarity < 70:
            suggestions.append("用户故事使用标准格式（作为...我想要...以便...）")
        
        if consistency < 80:
            suggestions.append("检查需求间是否存在冲突")
        
        if len(prd.get("risks", [])) == 0:
            suggestions.append("添加风险评估，识别潜在问题")
        
        if len(prd.get("acceptance_criteria", [])) < 3:
            suggestions.append("补充验收标准，建议至少 3 条可测试标准")
        
        return suggestions
    
    def _get_missing_items(self, prd: Dict[str, Any]) -> List[str]:
        """获取缺失项"""
        missing = []
        
        for field in self.FIELD_WEIGHTS.keys():
            if field not in prd or len(prd.get(field, [])) == 0:
                missing.append(field)
        
        return missing
