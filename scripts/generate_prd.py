#!/usr/bin/env python3
"""
生成 PRD 文档脚本

用法:
    python scripts/generate_prd.py "需求描述" [--project 项目名] [--template standard|lite]

示例:
    python scripts/generate_prd.py "需要一个登录功能" --project 用户系统 --template standard
"""

import asyncio
import argparse
import sys
import os

# 加载 .env 文件
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.orchestrator import ReqDocOrchestrator


async def main():
    parser = argparse.ArgumentParser(description='生成 PRD 文档')
    parser.add_argument('content', type=str, help='需求描述')
    parser.add_argument('--project', '-p', type=str, default='需求文档', help='项目名称')
    parser.add_argument('--priority', type=str, default='P1', choices=['P0', 'P1', 'P2'], help='优先级')
    parser.add_argument('--template', '-t', type=str, default='standard', choices=['standard', 'lite'], help='模板类型')
    
    args = parser.parse_args()
    
    print(f'📝 生成 PRD: {args.content[:50]}...')
    print('')
    
    # 创建编排器
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
    
    # 调用生成
    result = await orchestrator.run({
        'source': 'cli',
        'content': args.content,
        'context': {
            'project_name': args.project,
            'priority': args.priority,
            'template': args.template,
        }
    })
    
    # 输出结果
    print('✅ PRD 生成成功！')
    print('')
    print(f'📄 标题：{result["prd"]["title"]}')
    print(f'🏷️ 版本：{result["prd"]["version"]}')
    print(f'📊 完整率：{result["quality_report"]["completeness_score"]}/100')
    print(f'💰 成本：¥{result["execution"]["cost"]:.3f}')
    print(f'⏱️  耗时：{result["execution"]["duration_ms"]}ms')
    print('')
    print(f'📦 用户故事：{len(result["prd"]["user_stories"])} 条')
    print(f'📦 功能需求：{len(result["prd"]["functional_requirements"])} 条')
    print(f'📦 业务规则：{len(result["prd"]["business_rules"])} 条')
    print(f'📦 验收标准：{len(result["prd"]["acceptance_criteria"])} 条')
    print(f'📦 风险项：{len(result["prd"]["risks"])} 条')
    print('')
    print(f'💾 存储：{result["prd"]["storage"]["type"]}')
    if 'url' in result['prd']['storage']:
        print(f'🔗 链接：{result["prd"]["storage"]["url"]}')
    else:
        print(f'📁 路径：{result["prd"]["storage"]["path"]}')
    
    # 显示改进建议
    if result['quality_report']['suggestions']:
        print('')
        print('💡 改进建议:')
        for suggestion in result['quality_report']['suggestions'][:3]:
            print(f'   - {suggestion}')


if __name__ == '__main__':
    asyncio.run(main())
