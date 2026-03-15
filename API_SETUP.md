# API 配置指南

> 完成本指南后，Skill 将可以使用真实 API

---

## 一、阿里云百炼 API（LLM）

### 1.1 获取 API Key

1. 访问：https://dashscope.console.aliyun.com/
2. 登录阿里云账号
3. 进入「API-KEY 管理」
4. 点击「创建新的 API-KEY」
5. 复制 API Key（格式：`sk-xxxxxxxx`）

### 1.2 配置环境变量

**方式 1: 临时配置（当前终端）**
```bash
export DASHSCOPE_API_KEY=sk-xxxxxxxx
```

**方式 2: 永久配置（推荐）**
```bash
# 添加到 ~/.zshrc 或 ~/.bashrc
echo 'export DASHSCOPE_API_KEY=sk-xxxxxxxx' >> ~/.zshrc
source ~/.zshrc
```

**方式 3: 使用 .env 文件**
```bash
# 创建 .env 文件
cd ~/.openclaw/workspace/skills/requirement-doc-manager
cat > .env << EOF
DASHSCOPE_API_KEY=sk-xxxxxxxx
FEISHU_APP_ID=cli_xxx
FEISHU_APP_SECRET=xxx
EOF
```

### 1.3 验证配置

```bash
# 检查是否配置成功
echo $DASHSCOPE_API_KEY

# 应该输出：sk-xxxxxxxx（部分隐藏）
```

### 1.4 测试调用

```bash
cd ~/.openclaw/workspace/skills/requirement-doc-manager
source .venv/bin/activate

# 运行测试
python -c "
import asyncio
import os
from src.capabilities.extractor import RequirementExtractor

# 检查 API Key
api_key = os.getenv('DASHSCOPE_API_KEY', '')
if not api_key:
    print('❌ DASHSCOPE_API_KEY 未配置')
    print('请先配置：export DASHSCOPE_API_KEY=sk-xxx')
else:
    print('✅ API Key 已配置')
    
    # 测试调用
    config = {'llm': {'primary': 'qwen3.5-plus', 'fallback': 'qwen2'}}
    extractor = RequirementExtractor(config)
    
    result = asyncio.run(extractor.extract('需要一个用户登录功能'))
    print('✅ 调用成功')
    print(f'用户故事：{len(result[\"data\"][\"user_stories\"])} 条')
    print(f'功能需求：{len(result[\"data\"][\"functional_requirements\"])} 条')
"
```

### 1.5 模型说明

| 模型 | 配置名 | 价格 | 适用场景 |
|------|--------|------|----------|
| Qwen-Plus | qwen3.5-plus | ¥0.002/k | 标准需求（推荐） |
| Qwen-Turbo | qwen2 | ¥0.0005/k | 简单需求/降级 |
| Qwen-Max | qwen-max | ¥0.005/k | 复杂需求 |

---

## 二、飞书 API（文档创建）

### 2.1 创建飞书应用

1. 访问：https://open.feishu.cn/app
2. 点击「创建企业自建应用」
3. 填写应用信息：
   - 名称：需求文档助手
   - 图标：任选
4. 点击「创建」

### 2.2 获取凭证

1. 进入应用管理页面
2. 点击「凭证与基础信息」
3. 记录：
   - App ID（格式：`cli_xxx`）
   - App Secret（点击复制）

### 2.3 配置权限

1. 点击「权限管理」
2. 添加以下权限：
   - **文档**：创建、编辑、读取
   - **机器人**：发送消息
   - **云文档**：读写权限
3. 点击「发布应用」

### 2.4 配置环境变量

```bash
export FEISHU_APP_ID=cli_xxx
export FEISHU_APP_SECRET=xxx
```

### 2.5 验证配置

```bash
# 检查是否配置成功
echo $FEISHU_APP_ID
echo $FEISHU_APP_SECRET
```

---

## 三、完整测试

### 3.1 配置检查脚本

```bash
cd ~/.openclaw/workspace/skills/requirement-doc-manager
cat > scripts/check_api.sh << 'EOF'
#!/bin/bash

echo "🔍 检查 API 配置..."
echo ""

# 检查 LLM API
if [ -n "$DASHSCOPE_API_KEY" ]; then
    echo "✅ LLM API: 已配置"
else
    echo "❌ LLM API: 未配置"
    echo "   运行：export DASHSCOPE_API_KEY=sk-xxx"
fi

# 检查飞书 API
if [ -n "$FEISHU_APP_ID" ] && [ -n "$FEISHU_APP_SECRET" ]; then
    echo "✅ 飞书 API: 已配置"
else
    echo "❌ 飞书 API: 未配置"
    echo "   运行：export FEISHU_APP_ID=cli_xxx"
    echo "         export FEISHU_APP_SECRET=xxx"
fi

echo ""
echo "配置完成后重新运行此脚本检查"
EOF

chmod +x scripts/check_api.sh
./scripts/check_api.sh
```

### 3.2 端到端测试

```bash
# 配置环境变量后运行
source .venv/bin/activate
python -c "
import asyncio
from src.orchestrator import ReqDocOrchestrator

config = {
    'llm': {'primary': 'qwen3.5-plus', 'fallback': 'qwen2', 'timeout': 60},
    'cost': {'daily_limit': 30, 'monthly_limit': 100},
}

orchestrator = ReqDocOrchestrator(config)

result = asyncio.run(orchestrator.run({
    'source': 'text',
    'content': '需要一个用户登录功能，支持手机号和邮箱注册',
    'context': {'project_name': '用户管理系统'}
}))

print('✅ 端到端测试成功')
print(f'PRD 标题：{result[\"prd\"][\"title\"]}')
print(f'版本：{result[\"prd\"][\"version\"]}')
print(f'用户故事：{len(result[\"prd\"][\"user_stories\"])} 条')
print(f'功能需求：{len(result[\"prd\"][\"functional_requirements\"])} 条')
print(f'完整率：{result[\"quality_report\"][\"completeness_score\"]}/100')
print(f'成本：¥{result[\"execution\"][\"cost\"]}')
print(f'耗时：{result[\"execution\"][\"duration_ms\"]}ms')
"
```

---

## 四、故障排除

### 4.1 LLM API 问题

**问题**: `DASHSCOPE_API_KEY 未配置`
```bash
# 解决
export DASHSCOPE_API_KEY=sk-xxx
```

**问题**: `余额不足`
```
访问：https://dashscope.console.aliyun.com/overview
充值即可（新用户有免费额度）
```

**问题**: `模型不存在`
```
检查模型名称映射：
- qwen3.5-plus → qwen-plus
- qwen2 → qwen-turbo
```

### 4.2 飞书 API 问题

**问题**: `App ID 或 Secret 错误`
```
重新创建应用，确保复制正确
```

**问题**: `权限不足`
```
在应用管理页面添加对应权限，然后重新发布
```

---

## 五、成本估算

### 5.1 LLM 成本

| 场景 | Token 用量 | 模型 | 单次成本 |
|------|-----------|------|----------|
| 简单需求（<500 字） | ~2k | qwen-turbo | ¥0.001 |
| 标准需求（500-2000 字） | ~4k | qwen-plus | ¥0.008 |
| 复杂需求（>2000 字） | ~8k | qwen-plus | ¥0.016 |

### 5.2 飞书成本

- 文档创建：免费
- 消息推送：免费（限额内）

### 5.3 预算控制

```yaml
# config.yaml 中配置
cost:
  daily_limit: 30      # 日预算 ¥30
  monthly_limit: 100   # 月预算 ¥100
```

---

## 六、下一步

配置完成后：

1. 运行 `./scripts/check_api.sh` 验证
2. 运行端到端测试
3. 开始真实使用

---

_配置完成后，Skill 将进入真实可用状态_
