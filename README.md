# Requirement Doc Manager Skill

> 从需求描述自动生成结构化 PRD 文档

## 快速开始

### 安装

```bash
# 克隆或复制 skill 到工作区
cd ~/.openclaw/workspace/skills/
# skill 已在此目录
```

### 配置

```bash
# 设置阿里云百炼 API Key（必需）
export DASHSCOPE_API_KEY="your-api-key"
```

### 使用

**方式 1: 对话触发**
```
整理需求文档
需要一个用户登录功能，支持手机号和邮箱注册
```

**方式 2: 命令行**
```bash
openclaw req-doc --input requirement.txt --template standard
```

**方式 3: 直接调用**
```python
from src.orchestrator import ReqDocOrchestrator

orchestrator = ReqDocOrchestrator(config)
result = await orchestrator.run({
    "source": "text",
    "content": "需要一个登录功能",
    "context": {"project_name": "用户系统"}
})
```

## 输出示例

```json
{
  "prd": {
    "title": "用户系统",
    "version": "v20260314-0930",
    "user_stories": [
      {"role": "用户", "need": "登录功能", "benefit": "访问个人账户"}
    ],
    "functional_requirements": [
      {"id": "FR-001", "title": "用户登录", "description": "支持手机号和邮箱登录"}
    ],
    "business_rules": ["密码必须加密存储"],
    "acceptance_criteria": ["输入正确密码可登录"],
    "risks": [{"description": "密码泄露风险", "level": "high"}],
    "storage": {"type": "markdown", "path": "/需求文档库/prd_v20260314-0930.md"}
  },
  "quality_report": {
    "completeness_score": 85,
    "clarity_score": 90,
    "consistency_score": 95,
    "overall_score": 90,
    "suggestions": ["补充业务规则描述"]
  },
  "execution": {
    "duration_ms": 2500,
    "model_used": "qwen3.5-plus",
    "cost": 2.0
  }
}
```

## 功能特性

- ✅ 5W1H 需求澄清
- ✅ 5 维度并行抽取（用户故事/功能/规则/验收/风险）
- ✅ 完整性校验（必填项 + 格式规范）
- ✅ 质量评分（完整率/清晰度/一致性）
- ✅ 双模板支持（标准版/精简版）
- ✅ 降级策略（超时重试/模型降级）
- ✅ 成本预算控制
- ✅ 安全过滤（Prompt Injection 防护）
- ✅ 本地 Markdown 存储

## 测试

```bash
# 运行所有测试
./scripts/run_tests.sh

# 运行特定测试
python3 -m pytest tests/test_extractor.py -v

# 生成覆盖率报告
python3 -m pytest --cov=src --cov-report=html
```

## 部署

```bash
# 部署脚本
./scripts/deploy.sh
```

## 监控指标

| 指标 | 目标值 |
|------|--------|
| 成功率 | >95% |
| P95 延迟 | <3 分钟 |
| 单次成本 | <¥2 |
| 需求完整率 | >90% |
| 用户满意度 | >4.5/5 |

## 故障排除

### LLM 超时
检查网络连接，或切换到 `qwen2` 模型

### 成本超支
调整 `config.yaml` 中的预算限制

### 存储失败
检查 `~/.openclaw/workspace/需求文档库/` 目录权限

## 文件结构

```
requirement-doc-manager/
├── SKILL.md                 # Skill 描述
├── config.yaml              # 配置文件
├── src/
│   ├── orchestrator.py      # 编排器
│   ├── capabilities/        # 能力模块
│   └── utils/               # 工具
├── templates/               # PRD 模板
├── references/              # 参考文档
├── tests/                   # 测试用例
└── scripts/                 # 部署脚本
```

## 版本

- v1.1 (2026-03-15) - 移除飞书集成，纯本地存储
- v1.0 (2026-03-14) - 初始版本

## 许可证

MIT
