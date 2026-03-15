"""
质量评分测试 - 10 用例
"""

import pytest
from src.capabilities.scorer import QualityScorer


class TestQualityScorer:
    """评分器测试"""
    
    @pytest.fixture
    def scorer(self):
        config = {
            "quality": {
                "weights": {
                    "completeness": 0.4,
                    "clarity": 0.3,
                    "consistency": 0.3,
                }
            }
        }
        return QualityScorer(config)
    
    def test_scorer_complete_req(self, scorer):
        """完整需求高分"""
        prd = {
            "user_stories": [{"role": "用户", "need": "登录", "benefit": "访问"}],
            "functional_requirements": [{"id": "FR-001", "title": "登录"}],
            "business_rules": ["密码加密"],
            "acceptance_criteria": ["可登录"],
            "risks": [{"description": "密码泄露", "level": "high"}],
        }
        report = scorer.calculate(prd)
        assert report.completeness_score > 80
    
    def test_scorer_incomplete_req(self, scorer):
        """不完整需求低分"""
        prd = {
            "functional_requirements": [{"id": "FR-001", "title": "登录"}],
            # 缺少其他字段
        }
        report = scorer.calculate(prd)
        assert report.completeness_score < 50
    
    def test_scorer_story_format(self, scorer):
        """用户故事格式影响清晰度"""
        prd = {
            "user_stories": [{"role": "用户"}],  # 格式不完整
            "functional_requirements": [],
            "acceptance_criteria": [],
        }
        report = scorer.calculate(prd)
        assert report.clarity_score < 100
    
    def test_scorer_criteria_testable(self, scorer):
        """验收标准可测试性"""
        prd = {
            "user_stories": [],
            "functional_requirements": [],
            "acceptance_criteria": ["系统要好"],  # 不可测试
        }
        report = scorer.calculate(prd)
        assert report.clarity_score < 100
    
    def test_scorer_suggestions(self, scorer):
        """生成改进建议"""
        prd = {
            "user_stories": [],
            "functional_requirements": [],
            "acceptance_criteria": [],
            "risks": [],
        }
        report = scorer.calculate(prd)
        assert len(report.suggestions) > 0
    
    def test_scorer_missing_items(self, scorer):
        """识别缺失项"""
        prd = {
            "user_stories": [],
            # 缺少其他字段
        }
        report = scorer.calculate(prd)
        assert "functional_requirements" in report.missing_items
    
    def test_scorer_overall_score(self, scorer):
        """总体评分"""
        prd = {
            "user_stories": [{"role": "用户", "need": "登录", "benefit": "访问"}],
            "functional_requirements": [{"id": "FR-001", "title": "登录"}],
            "business_rules": [],
            "acceptance_criteria": [],
            "risks": [],
        }
        report = scorer.calculate(prd)
        assert 0 <= report.overall_score <= 100
    
    def test_scorer_empty_prd(self, scorer):
        """空 PRD"""
        prd = {}
        report = scorer.calculate(prd)
        assert report.completeness_score == 0
    
    def test_scorer_full_prd(self, scorer):
        """完整 PRD"""
        prd = {
            "user_stories": [{"role": "用户", "need": "登录", "benefit": "访问"}] * 5,
            "functional_requirements": [{"id": "FR-001", "title": "登录"}] * 5,
            "business_rules": ["规则 1", "规则 2"],
            "acceptance_criteria": ["标准 1", "标准 2", "标准 3"],
            "risks": [{"description": "风险", "level": "high"}],
        }
        report = scorer.calculate(prd)
        assert report.completeness_score >= 90
    
    def test_scorer_weights(self, scorer):
        """权重验证"""
        prd = {
            "user_stories": [{"role": "用户", "need": "登录", "benefit": "访问"}],
            "functional_requirements": [{"id": "FR-001", "title": "登录"}],
            "business_rules": [],
            "acceptance_criteria": [],
            "risks": [],
        }
        report = scorer.calculate(prd)
        # 完整率权重 40%，清晰度和一致性各 30%
        expected = (
            report.completeness_score * 0.4 +
            report.clarity_score * 0.3 +
            report.consistency_score * 0.3
        )
        assert abs(report.overall_score - expected) < 0.1
