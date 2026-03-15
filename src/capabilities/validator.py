"""
完整性校验模块 - 规则引擎检查必填项和格式规范
"""

from typing import Dict, Any, List
from dataclasses import dataclass
from ..utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class ValidationResult:
    """校验结果"""
    passed: bool
    errors: List[str]
    warnings: List[str]
    missing_fields: List[str]


class RequirementValidator:
    """需求校验器"""
    
    # 必填字段
    REQUIRED_FIELDS = [
        "user_stories",
        "functional_requirements",
        "acceptance_criteria",
    ]
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.quality_config = config.get("quality", {})
    
    async def validate(self, req: Dict[str, Any]) -> Dict[str, Any]:
        """
        校验需求
        
        Args:
            req: 抽取的需求数据
        
        Returns:
            校验结果
        """
        errors = []
        warnings = []
        missing_fields = []
        
        # 1. 必填字段检查
        for field in self.REQUIRED_FIELDS:
            if field not in req or len(req.get(field, [])) == 0:
                errors.append(f"必填字段缺失：{field}")
                missing_fields.append(field)
        
        # 2. 用户故事格式检查
        for i, story in enumerate(req.get("user_stories", [])):
            if not self._validate_story_format(story):
                warnings.append(f"用户故事 {i+1} 格式不规范（缺少 role/need/benefit）")
        
        # 3. 验收标准可测试性检查
        for i, criteria in enumerate(req.get("acceptance_criteria", [])):
            if not self._is_testable(criteria):
                warnings.append(f"验收标准 {i+1} 不可测试：{criteria[:50]}")
        
        # 4. 逻辑一致性检查
        consistency_issues = self._check_consistency(req)
        warnings.extend(consistency_issues)
        
        passed = len(errors) == 0
        
        logger.info(f"校验完成：passed={passed}, errors={len(errors)}, warnings={len(warnings)}")
        
        return {
            "passed": passed,
            "errors": errors,
            "warnings": warnings,
            "missing_fields": missing_fields,
        }
    
    def _validate_story_format(self, story: Dict[str, Any]) -> bool:
        """验证用户故事格式"""
        required_keys = ["role", "need", "benefit"]
        return all(key in story for key in required_keys)
    
    def _is_testable(self, criteria: str) -> bool:
        """检查验收标准是否可测试"""
        # 简单规则：包含具体动作或结果
        testable_keywords = ["可以", "能够", "显示", "返回", "成功", "失败", "必须", "应该"]
        return any(kw in criteria for kw in testable_keywords)
    
    def _check_consistency(self, req: Dict[str, Any]) -> List[str]:
        """检查逻辑一致性"""
        issues = []
        
        # 检查需求间是否有明显冲突
        # TODO: 实现更复杂的冲突检测
        
        return issues
