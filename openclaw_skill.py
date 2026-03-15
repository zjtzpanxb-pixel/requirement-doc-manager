"""
OpenClaw Skill Wrapper

这个文件让 Skill 可以通过 OpenClaw 直接调用
"""

import asyncio
import os
from typing import Dict, Any

# API Key 从 OpenClaw 系统环境变量读取，不需要加载 .env

from src.orchestrator import ReqDocOrchestrator


async def generate_prd(content: str, **kwargs) -> Dict[str, Any]:
    """
    生成 PRD 文档
    
    Args:
        content: 需求描述
        **kwargs: 可选参数
            - project_name: 项目名称
            - priority: 优先级 (P0/P1/P2)
            - template: 模板类型 (standard/lite)
    
    Returns:
        生成结果（包含 PRD 文档、质量报告、执行信息）
    """
    orchestrator = ReqDocOrchestrator({
        'llm': {
            'primary': 'qwen-plus',
            'fallback': 'qwen-turbo',
            'timeout': 60,
        },
        'cost': {
            'daily_limit': 30,
            'monthly_limit': 100,
        },
    })
    
    return await orchestrator.run({
        'source': 'openclaw',
        'content': content,
        'context': {
            'project_name': kwargs.get('project_name', '需求文档'),
            'priority': kwargs.get('priority', 'P1'),
            'template': kwargs.get('template', 'standard'),
        }
    })


# OpenClaw 调用入口
def run(content: str, **kwargs) -> Dict[str, Any]:
    """OpenClaw 同步调用入口"""
    return asyncio.run(generate_prd(content, **kwargs))
