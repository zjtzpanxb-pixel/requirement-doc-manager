"""
Requirement Doc Manager - Orchestrator

5 状态状态机：接收 → 抽取 → 校验 → 生成 → 归档
"""

import asyncio
import time
from enum import Enum
from typing import Optional, Dict, Any
from dataclasses import dataclass

from .capabilities.fetcher import ContentFetcher
from .capabilities.extractor import RequirementExtractor
from .capabilities.validator import RequirementValidator
from .capabilities.scorer import QualityScorer
from .capabilities.generator import DocumentGenerator
from .capabilities.pusher import DocumentPusher
from .utils.cost_tracker import CostTracker
from .utils.logger import get_logger

logger = get_logger(__name__)


class State(Enum):
    """5 状态状态机"""
    RECEIVE = "receive"
    EXTRACT = "extract"
    VALIDATE = "validate"
    GENERATE = "generate"
    ARCHIVE = "archive"


@dataclass
class ExecutionContext:
    """执行上下文"""
    input_data: Dict[str, Any]
    state: State = State.RECEIVE
    retries: int = 0
    start_time: float = 0
    model_used: str = ""
    token_used: int = 0
    cost: float = 0
    fallback_used: bool = False


class ReqDocOrchestrator:
    """需求文档管理编排器"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.fetcher = ContentFetcher(config)
        self.extractor = RequirementExtractor(config)
        self.validator = RequirementValidator(config)
        self.scorer = QualityScorer(config)
        self.generator = DocumentGenerator(config)
        self.pusher = DocumentPusher(config)
        self.cost_tracker = CostTracker(config)
    
    async def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        主执行流程
        
        Args:
            input_data: 输入数据（见 SKILL.md 输入 schema）
        
        Returns:
            输出数据（见 SKILL.md 输出 schema）
        """
        context = ExecutionContext(
            input_data=input_data,
            start_time=time.time()
        )
        
        try:
            # 预算检查
            estimated_cost = self.cost_tracker.estimate_cost(
                content_length=len(input_data.get("content", "")),
                template=input_data.get("context", {}).get("template", "standard")
            )
            budget_ok, message = self.cost_tracker.check_budget(estimated_cost)
            if not budget_ok:
                logger.warning(f"预算检查失败：{message}")
                raise self._create_error("REQ-DOC-502", message, recoverable=True)
            
            # State 1: RECEIVE
            context.state = State.RECEIVE
            logger.info(f"State: RECEIVE - 解析请求")
            content = await self._receive(input_data, context)
            
            # State 2: EXTRACT
            context.state = State.EXTRACT
            logger.info(f"State: EXTRACT - 需求抽取")
            extracted = await self._extract(content, context)
            
            # State 3: VALIDATE
            context.state = State.VALIDATE
            logger.info(f"State: VALIDATE - 完整性校验")
            validation = await self._validate(extracted, context)
            if not validation.get("passed", True):
                logger.warning(f"校验失败：{validation.get('errors', [])}")
                extracted = await self._handle_validation_failure(validation, extracted, context)
            
            # State 4: GENERATE
            context.state = State.GENERATE
            logger.info(f"State: GENERATE - 文档生成")
            prd = await self._generate(extracted, context)
            
            # State 5: ARCHIVE
            context.state = State.ARCHIVE
            logger.info(f"State: ARCHIVE - 归档存储")
            await self._archive(prd, context)
            
            # 构建输出
            return self._build_output(prd, context)
            
        except Exception as e:
            logger.error(f"执行失败：{e}", exc_info=True)
            await self._handle_error(context.state, e, context)
            raise
    
    async def _receive(self, input_data: Dict[str, Any], context: ExecutionContext) -> str:
        """State 1: 接收并解析请求"""
        try:
            # 验证输入格式
            if not input_data.get("content"):
                raise self._create_error("REQ-DOC-102", "必填项缺失：content", recoverable=True)
            
            # 获取内容
            content = await self.fetcher.fetch(input_data)
            
            # 安全过滤
            content = self.fetcher.sanitize(content)
            
            logger.info(f"接收成功，内容长度：{len(content)}")
            return content
            
        except Exception as e:
            logger.error(f"接收失败：{e}")
            raise self._create_error("REQ-DOC-101", f"输入解析失败：{e}", recoverable=True)
    
    async def _extract(self, content: str, context: ExecutionContext) -> Dict[str, Any]:
        """State 2: 需求抽取（带重试 + 降级）"""
        max_retries = self.config.get("llm", {}).get("max_retries", 3)
        
        for attempt in range(max_retries):
            try:
                result = await self.extractor.extract(
                    content,
                    timeout=self.config.get("llm", {}).get("timeout", 60)
                )
                
                context.model_used = result.get("model", "qwen3.5-plus")
                context.token_used = result.get("token_used", 0)
                
                logger.info(f"抽取成功，模型：{context.model_used}")
                return result["data"]
                
            except TimeoutError:
                logger.warning(f"抽取超时，尝试 {attempt + 1}/{max_retries}")
                if attempt == max_retries - 1:
                    # 降级到小模型
                    logger.info("降级到 qwen2")
                    context.fallback_used = True
                    result = await self.extractor.extract(
                        content,
                        model="qwen2",
                        timeout=60
                    )
                    context.model_used = "qwen2"
                    context.token_used = result.get("token_used", 0)
                    return result["data"]
                
                # 指数退避
                delay = self.config.get("retry", {}).get("base_delay", 1.0) * (2 ** attempt)
                await asyncio.sleep(delay)
        
        # 最终降级：模板
        logger.warning("抽取失败，使用降级模板")
        context.fallback_used = True
        return self.extractor.fallback_template(content)
    
    async def _validate(self, extracted: Dict[str, Any], context: ExecutionContext) -> Dict[str, Any]:
        """State 3: 完整性校验"""
        return await self.validator.validate(extracted)
    
    async def _handle_validation_failure(
        self, 
        validation: Dict[str, Any], 
        extracted: Dict[str, Any],
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """处理校验失败（追问或标记）"""
        missing_fields = validation.get("missing_fields", [])
        
        if missing_fields:
            logger.warning(f"缺失字段：{missing_fields}")
            # 标记待确认（简化版：不实际追问，直接标记）
            for field in missing_fields:
                if field not in extracted:
                    extracted[field] = []
                extracted[f"_missing_{field}"] = True
        
        return extracted
    
    async def _generate(self, extracted: Dict[str, Any], context: ExecutionContext) -> Dict[str, Any]:
        """State 4: 文档生成"""
        template = context.input_data.get("context", {}).get("template", "standard")
        
        prd = await self.generator.generate(
            data=extracted,
            template=template,
            context=context.input_data.get("context", {})
        )
        
        logger.info(f"文档生成成功，模板：{template}")
        return prd
    
    async def _archive(self, prd: Dict[str, Any], context: ExecutionContext) -> None:
        """State 5: 归档存储"""
        try:
            # 本地存储
            storage_info = await self.pusher.push(prd, context.input_data)
            prd["storage"] = storage_info
            
            # 记录成本
            self.cost_tracker.record_cost(context.cost)
            
            logger.info(f"归档成功，存储位置：{storage_info}")
            
        except Exception as e:
            logger.error(f"归档失败：{e}")
            # 降级：本地存储
            prd["storage"] = {
                "type": "markdown",
                "path": f"/tmp/prd_{int(time.time())}.md",
                "fallback": True
            }
    
    def _build_output(self, prd: Dict[str, Any], context: ExecutionContext) -> Dict[str, Any]:
        """构建最终输出"""
        duration_ms = int((time.time() - context.start_time) * 1000)
        
        # 质量评分
        quality = self.scorer.calculate(prd)
        
        # 计算成本
        context.cost = self.cost_tracker.calculate_actual_cost(
            model=context.model_used,
            tokens=context.token_used
        )
        
        return {
            "prd": prd,
            "quality_report": {
                "completeness_score": quality.completeness_score,
                "clarity_score": quality.clarity_score,
                "consistency_score": quality.consistency_score,
                "overall_score": quality.overall_score,
                "missing_items": quality.missing_items,
                "suggestions": quality.suggestions,
            },
            "execution": {
                "duration_ms": duration_ms,
                "model_used": context.model_used,
                "token_used": context.token_used,
                "cost": context.cost,
                "fallback_used": context.fallback_used,
            },
            "generated_at": int(time.time()),
        }
    
    async def _handle_error(self, state: State, error: Exception, context: ExecutionContext) -> None:
        """错误处理"""
        logger.error(f"状态 {state.value} 发生错误：{error}")
        
        # 记录错误日志
        # 触发告警（如连续失败）
    
    def _create_error(self, code: str, message: str, recoverable: bool = False) -> Exception:
        """创建错误对象"""
        return Exception(f"{code}: {message} (recoverable={recoverable})")
