#!/usr/bin/env python3
"""
Requirement Doc Manager - OpenClaw Skill 入口

触发条件:
- "整理需求文档"
- "生成 PRD"
- "写需求文档"
- "需求文档管理"

用法:
- 直接对话触发
- openclaw req-doc --input "需求描述"
"""

import asyncio
import os
import sys

# API Key 从 OpenClaw 系统环境变量读取，不需要加载 .env

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.orchestrator import ReqDocOrchestrator


def extract_intent(message: str) -> dict:
    """从用户消息中提取意图和参数"""
    message = message.strip()
    
    # 默认参数
    params = {
        'project_name': '需求文档',
        'priority': 'P1',
        'template': 'standard',
    }
    
    # 提取项目名称（--project 或 项目名：）
    if '--project ' in message:
        parts = message.split('--project ')
        if len(parts) > 1:
            params['project_name'] = parts[1].split()[0]
            message = parts[0]
    elif '项目：' in message:
        parts = message.split('项目：')
        if len(parts) > 1:
            params['project_name'] = parts[1].split()[0]
            message = parts[0]
    
    # 提取优先级
    for p in ['P0', 'P1', 'P2']:
        if f'--priority {p}' in message or f'优先级{p}' in message:
            params['priority'] = p
            break
    
    # 提取模板类型
    if '--lite' in message or '精简版' in message:
        params['template'] = 'lite'
    
    return {
        'content': message,
        'params': params,
    }


async def generate_prd(message: str) -> str:
    """
    生成 PRD 文档
    
    Args:
        message: 用户消息
    
    Returns:
        格式化的输出文本
    """
    # 提取意图
    extracted = extract_intent(message)
    content = extracted['content']
    params = extracted['params']
    
    # 创建编排器
    orchestrator = ReqDocOrchestrator({
        'llm': {
            'primary': 'default',
            'fallback': 'fallback',
            'timeout': 60,
        },
        'cost': {
            'daily_limit': 30,
            'monthly_limit': 100,
        },
    })
    
    try:
        # 调用生成
        result = await orchestrator.run({
            'source': 'openclaw',
            'content': content,
            'context': params,
        })
        
        # 格式化输出
        output = []
        output.append("✅ **PRD 文档生成成功！**")
        output.append("")
        output.append(f"📄 **标题**: {result['prd']['title']}")
        output.append(f"🏷️ **版本**: {result['prd']['version']}")
        output.append(f"📊 **完整率**: {result['quality_report']['completeness_score']}/100")
        output.append(f"⏱️  **耗时**: {result['execution']['duration_ms']}ms")
        output.append(f"💰 **成本**: ¥{result['execution']['cost']:.3f}")
        output.append("")
        output.append(f"📦 **用户故事**: {len(result['prd']['user_stories'])} 条")
        output.append(f"📦 **功能需求**: {len(result['prd']['functional_requirements'])} 条")
        output.append(f"📦 **验收标准**: {len(result['prd']['acceptance_criteria'])} 条")
        output.append("")
        
        # 存储位置
        storage = result['prd']['storage']
        output.append(f"📁 **本地路径**: {storage.get('path', 'N/A')}")
        
        # 改进建议
        if result['quality_report']['suggestions']:
            output.append("")
            output.append("💡 **改进建议**:")
            for suggestion in result['quality_report']['suggestions'][:3]:
                output.append(f"   - {suggestion}")
        
        # 用户故事预览
        if result['prd']['user_stories']:
            output.append("")
            output.append("📋 **用户故事预览**:")
            for i, story in enumerate(result['prd']['user_stories'][:3], 1):
                output.append(f"   {i}. 作为 {story.get('role', '?')}，我想要 {story.get('need', '?')[:30]}，以便 {story.get('benefit', '?')[:20]}")
        
        return '\n'.join(output)
        
    except Exception as e:
        return f"❌ **生成失败**: {str(e)}\n\n请检查 API 配置或联系管理员。"


def run(message: str) -> str:
    """
    OpenClaw 同步调用入口
    
    Args:
        message: 用户消息
    
    Returns:
        响应文本
    """
    return asyncio.run(generate_prd(message))


# OpenClaw 技能元数据
SKILL_METADATA = {
    'name': 'requirement-doc-manager',
    'description': '从需求描述自动生成结构化 PRD 文档',
    'version': '1.0.0',
    'author': 'Skill Creator Pro Framework',
    'triggers': [
        '整理需求文档',
        '生成 PRD',
        '写需求文档',
        '写 prd',
        '需求文档',
        'prD 文档',
        '生成需求',
    ],
}


# 测试入口
if __name__ == '__main__':
    # 测试用例
    test_message = "需要一个用户登录功能，支持手机号和邮箱注册 --project 用户管理系统"
    print(f"测试消息：{test_message}")
    print("")
    result = run(test_message)
    print(result)
