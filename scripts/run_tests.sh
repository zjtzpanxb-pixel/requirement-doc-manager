#!/bin/bash
# 运行测试脚本

set -e

echo "🧪 运行 Requirement Doc Manager 测试..."

# 单元测试
echo "运行单元测试..."
python3 -m pytest tests/test_extractor.py tests/test_validator.py tests/test_scorer.py -v

# 集成测试
echo "运行集成测试..."
python3 -m pytest tests/test_integration.py -v

# E2E 测试（可选）
# python3 -m pytest tests/test_e2e.py -v

# 安全测试
echo "运行安全测试..."
python3 -m pytest tests/test_security.py -v

# 生成覆盖率报告
echo "生成覆盖率报告..."
python3 -m pytest --cov=src --cov-report=html

echo "✅ 测试完成！"
echo "查看覆盖率报告：open htmlcov/index.html"
