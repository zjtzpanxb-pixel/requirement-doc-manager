#!/bin/bash
# Requirement Doc Manager - 部署脚本

set -e

echo "🚀 部署 Requirement Doc Manager Skill..."

# 检查 Python 版本
python_version=$(python3 --version 2>&1 | cut -d' ' -f2)
echo "Python 版本：$python_version"

# 创建虚拟环境（可选）
# python3 -m venv venv
# source venv/bin/activate

# 安装依赖（如有）
# pip install -r requirements.txt

# 设置环境变量
echo "设置环境变量..."
export FEISHU_APP_ID=${FEISHU_APP_ID:-}
export FEISHU_APP_SECRET=${FEISHU_APP_SECRET:-}

# 检查配置
echo "检查配置..."
if [ -z "$FEISHU_APP_ID" ]; then
    echo "⚠️  警告：FEISHU_APP_ID 未设置"
fi

# 运行测试
echo "运行测试..."
python3 -m pytest tests/ -v

# 部署完成
echo "✅ 部署完成！"
echo ""
echo "使用方法:"
echo "  openclaw req-doc --input requirement.txt"
echo "  或在飞书中发送：整理需求文档"
