"""
需求抽取模块 - 使用 LLM 并行抽取 5 维度需求
"""

import asyncio
import json
from typing import Dict, Any, Optional
from ..utils.logger import get_logger

logger = get_logger(__name__)

# 需求抽取 Schema
REQ_SCHEMA = {
    "user_stories": [],
    "functional_requirements": [],
    "business_rules": [],
    "acceptance_criteria": [],
    "risks": [],
}

# 简化 Schema（降级用）
SIMPLE_SCHEMA = {
    "user_stories": [],
    "functional_requirements": [],
}


class RequirementExtractor:
    """需求抽取器"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.llm_primary = config.get("llm", {}).get("primary", "default")
        self.llm_fallback = config.get("llm", {}).get("fallback", "fallback")
    
    async def extract(
        self, 
        content: str, 
        model: Optional[str] = None,
        timeout: int = 60
    ) -> Dict[str, Any]:
        """
        抽取需求
        
        Args:
            content: 需求描述内容
            model: 指定模型（默认主模型）
            timeout: 超时时间（秒）
        
        Returns:
            抽取结果
        """
        model = model or self.llm_primary
        
        # 构建安全的 Prompt
        prompt = self._build_prompt(content)
        
        try:
            # 调用 LLM（通过 OpenClaw 系统调用）
            result = await self._call_llm(prompt, model, timeout)
            
            return {
                "data": result,
                "model": model,
                "token_used": self._estimate_tokens(content, result),
            }
            
        except Exception as e:
            logger.error(f"抽取失败：{e}")
            raise
    
    def _build_prompt(self, content: str) -> str:
        """构建抽取 Prompt"""
        return f"""你是一个专业的需求分析师。请从以下需求描述中提取结构化信息。

## 抽取要求
1. 用户故事：使用"作为...我想要...以便..."格式
2. 功能需求：清晰的功能描述，包含 id、title、description
3. 业务规则：约束条件和规则
4. 验收标准：可测试的验收条件
5. 风险项：潜在风险和缓解措施

## 需求描述
{content}

## 输出格式（JSON）
{{
  "user_stories": [
    {{"role": "角色", "need": "需求", "benefit": "价值"}}
  ],
  "functional_requirements": [
    {{"id": "FR-001", "title": "功能标题", "description": "功能描述"}}
  ],
  "business_rules": ["规则 1", "规则 2"],
  "acceptance_criteria": ["验收标准 1", "验收标准 2"],
  "risks": [
    {{"description": "风险描述", "level": "high|medium|low", "mitigation": "缓解措施"}}
  ]
}}

请直接输出 JSON，不要其他内容。如果需求描述不完整，也尽量提取，缺失的字段留空数组。"""
    
    async def _call_llm(self, prompt: str, model: str, timeout: int) -> Dict[str, Any]:
        """调用 LLM（通过 OpenClaw 系统）"""
        
        try:
            import httpx
        except ImportError:
            logger.warning("httpx 未安装，使用模拟模式")
            return self._mock_response(prompt)
        
        # 使用 OpenClaw 内置的 LLM 调用（从系统环境变量读取 API Key）
        api_key = __import__('os').getenv("LLM_API_KEY", "")
        
        if not api_key:
            logger.info(f"模拟模式：调用 {model}")
            await asyncio.sleep(0.5)
            return self._mock_response(prompt)
        
        logger.info(f"调用 LLM: {model}, timeout={timeout}s")
        
        try:
            # 通用 LLM API endpoint（OpenAI 兼容）
            url = "https://api.openai.com/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            }
            
            payload = {
                "model": model,
                "messages": [
                    {
                        "role": "system",
                        "content": "你是一个专业的需求分析师，擅长从模糊的需求描述中提取结构化信息。请直接输出 JSON 格式，不要其他内容。"
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.7,
                "max_tokens": 2000,
                "stream": False,
            }
            
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.post(url, headers=headers, json=payload)
                response.raise_for_status()
                
                result = response.json()
                content_text = result["choices"][0]["message"]["content"]
                json_str = self._extract_json(content_text)
                data = json.loads(json_str)
                
                logger.info(f"API 调用成功，模型：{model}")
                return data
                
        except httpx.TimeoutException:
            logger.error(f"API 调用超时：{timeout}s")
            raise TimeoutError(f"LLM 调用超时 ({timeout}s)")
        except httpx.HTTPStatusError as e:
            logger.error(f"API 调用失败：{e.response.status_code}")
            raise Exception(f"LLM API 错误：{e.response.status_code}")
        except json.JSONDecodeError as e:
            logger.error(f"JSON 解析失败：{e}")
            return self._mock_response(prompt)
    
    def _extract_json(self, text: str) -> str:
        """从响应中提取 JSON"""
        if "```json" in text:
            start = text.index("```json") + 7
            end = text.index("```", start)
            return text[start:end].strip()
        elif "```" in text:
            start = text.index("```") + 3
            end = text.index("```", start)
            return text[start:end].strip()
        return text.strip()
    
    def _mock_response(self, prompt: str) -> Dict[str, Any]:
        """模拟响应（用于无 API Key 时）"""
        return {
            "user_stories": [
                {"role": "用户", "need": "从描述提取需求", "benefit": "满足业务目标"}
            ],
            "functional_requirements": [
                {"id": "FR-001", "title": "核心功能", "description": "根据需求描述实现功能"}
            ],
            "business_rules": ["遵循相关业务规范"],
            "acceptance_criteria": ["功能可正常使用", "满足基本业务需求"],
            "risks": [
                {"description": "需求理解偏差", "level": "medium", "mitigation": "与需求方确认"}
            ],
            "_mock": True,
        }
    
    def _estimate_tokens(self, content: str, result: Dict[str, Any]) -> int:
        """估算 token 使用量"""
        input_tokens = len(content) // 2
        output_tokens = len(str(result)) // 4
        return input_tokens + output_tokens
    
    def fallback_template(self, content: str) -> Dict[str, Any]:
        """降级模板（当 LLM 完全失败时）"""
        logger.warning("使用降级模板")
        
        return {
            "user_stories": [
                {"role": "用户", "need": "从描述提取", "benefit": "待补充"}
            ],
            "functional_requirements": [
                {"id": "FR-001", "title": "待确认", "description": content[:200]}
            ],
            "business_rules": [],
            "acceptance_criteria": [],
            "risks": [],
            "_fallback": True,
        }
