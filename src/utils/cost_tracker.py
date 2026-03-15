"""成本追踪模块"""

from typing import Tuple
from ..utils.logger import get_logger

logger = get_logger(__name__)


class CostTracker:
    """成本追踪器"""
    
    # 模型单价（每 1000 tokens）
    MODEL_PRICES = {
        "default": 0.002,
        "fallback": 0.0005,
    }
    
    def __init__(self, config: dict):
        self.config = config
        self.cost_config = config.get("cost", {})
        self.daily_limit = self.cost_config.get("daily_limit", 30)
        self.monthly_limit = self.cost_config.get("monthly_limit", 100)
        self.daily_spent = 0
        self.monthly_spent = 0
    
    def estimate_cost(self, content_length: int, template: str = "standard") -> float:
        """估算成本"""
        if template == "lite":
            return 1.0
        if content_length < 500:
            return 1.0
        elif content_length < 2000:
            return 2.0
        else:
            return 4.0
    
    def check_budget(self, estimated_cost: float) -> Tuple[bool, str]:
        """检查预算"""
        if self.daily_spent + estimated_cost > self.daily_limit:
            return False, "日预算不足，建议切换到精简版"
        if self.monthly_spent + estimated_cost > self.monthly_limit:
            return False, "月预算不足，请联系管理员"
        return True, "预算充足"
    
    def record_cost(self, cost: float) -> None:
        """记录成本"""
        self.daily_spent += cost
        self.monthly_spent += cost
        
        # 预警
        alert_threshold = self.cost_config.get("alert_threshold", 0.8)
        if self.daily_spent > self.daily_limit * alert_threshold:
            logger.warning(f"日预算已用{self.daily_spent/self.daily_limit*100:.0f}%")
        if self.monthly_spent > self.monthly_limit * alert_threshold:
            logger.warning(f"月预算已用{self.monthly_spent/self.monthly_limit*100:.0f}%")
    
    def calculate_actual_cost(self, model: str, tokens: int) -> float:
        """计算实际成本"""
        price = self.MODEL_PRICES.get(model, 0.002)
        return (tokens / 1000) * price
