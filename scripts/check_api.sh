#!/bin/bash

echo "🔍 检查 API 配置..."
echo ""

# 检查 LLM API
if [ -n "$DASHSCOPE_API_KEY" ]; then
    echo "✅ LLM API (阿里云百炼): 已配置"
else
    echo "❌ LLM API (阿里云百炼): 未配置"
    echo "   获取：https://dashscope.console.aliyun.com/"
    echo "   配置：export DASHSCOPE_API_KEY=sk-xxx"
fi

# 检查飞书 API
if [ -n "$FEISHU_APP_ID" ] && [ -n "$FEISHU_APP_SECRET" ]; then
    echo "✅ 飞书 API: 已配置"
else
    echo "❌ 飞书 API: 未配置"
    echo "   获取：https://open.feishu.cn/app"
    echo "   配置：export FEISHU_APP_ID=cli_xxx"
    echo "         export FEISHU_APP_SECRET=xxx"
fi

echo ""
echo "---"
echo "配置完成后重新运行此脚本检查"
echo "或运行测试：python -m pytest tests/test_extractor.py -v"
