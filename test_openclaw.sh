#!/bin/bash
# 测试脚本 - 在 OpenClaw 环境中运行

echo "🔍 检查 OpenClaw 环境变量..."
echo ""

if [ -n "$DASHSCOPE_API_KEY" ]; then
    echo "✅ DASHSCOPE_API_KEY: 已配置 (${DASHSCOPE_API_KEY:0:15}...)"
else
    echo "⚠️  DASHSCOPE_API_KEY: 未配置"
fi

if [ -n "$FEISHU_APP_ID" ] && [ -n "$FEISHU_APP_SECRET" ]; then
    echo "✅ FEISHU API: 已配置 (AppID: $FEISHU_APP_ID)"
else
    echo "⚠️  FEISHU API: 未配置（将使用本地存储）"
fi

echo ""
echo "运行测试..."
echo ""

cd "$(dirname "$0")"
python3 -c "
import asyncio
from main import run

print('📝 测试生成 PRD...')
print('')

result = run('需要一个用户登录功能，支持手机号和邮箱')
print(result)
"
