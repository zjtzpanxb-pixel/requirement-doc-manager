# API 配置状态

> 更新时间：2026-03-14 09:52

---

## 配置状态

| API | 配置 | 状态 | 说明 |
|-----|------|------|------|
| **阿里云百炼** | ✅ 已配置 | ❌ 验证失败 | API Key 格式错误或未激活 |
| **飞书开放平台** | ✅ 已配置 | ⬜ 待测试 | 需要 LLM 先成功 |

---

## 问题诊断

### 阿里云百炼 API

**提供的 Key**: `sk-sp-42750c8f51324232aeae669474463b4a`

**错误**: `401 Incorrect API key provided`

**可能原因**:
1. API Key 未激活（新用户需要开通服务）
2. API Key 格式不正确（`sk-sp-` 是特殊格式）
3. API Key 已过期或被吊销
4. 账号余额不足

**解决步骤**:

1. **访问控制台**: https://dashscope.console.aliyun.com/
2. **检查服务状态**:
   - 登录账号
   - 进入「API-KEY 管理」
   - 确认 Key 状态为「已激活」
3. **开通服务**（如未开通）:
   - 点击「开通服务」
   - 同意协议
   - 新用户有免费额度
4. **检查余额**:
   - 进入「费用中心」
   - 确认有可用余额

**替代方案**:
- 创建新的 API Key
- 使用其他模型服务（如 Moonshot/MiniMax 等）

---

## 当前可用功能

### ✅ 模拟模式（无需 API Key）

```bash
cd ~/.openclaw/workspace/skills/requirement-doc-manager
source .venv/bin/activate

# 测试（模拟模式）
python -c "
import asyncio
from src.orchestrator import ReqDocOrchestrator

orchestrator = ReqDocOrchestrator({
    'llm': {'primary': 'qwen3.5-plus', 'fallback': 'qwen2'},
    'cost': {'daily_limit': 30, 'monthly_limit': 100},
})

result = asyncio.run(orchestrator.run({
    'source': 'text',
    'content': '需要一个用户登录功能',
    'context': {'project_name': '测试项目'}
}))

print(f'完整率：{result[\"quality_report\"][\"completeness_score\"]}/100')
print(f'存储：{result[\"prd\"][\"storage\"][\"type\"]}')
"
```

**输出**: 模拟数据（用于测试流程）

---

## 真实可用（需要 API Key 激活后）

### 1. LLM API 激活后

```bash
# 重新测试
export DASHSCOPE_API_KEY=sk-xxx
python -c "from src.capabilities.extractor import RequirementExtractor; ..."
```

### 2. 飞书 API 测试

```bash
# 配置飞书凭证
export FEISHU_APP_ID=cli_a92e4ce766a3dcc8
export FEISHU_APP_SECRET=hgbVheXXo1xu5AafR8xKQmk8uhKtp2WT

# 测试文档创建
python -c "from src.capabilities.pusher import DocumentPusher; ..."
```

---

## 下一步行动

| 行动 | 状态 | 说明 |
|------|------|------|
| 1. 激活阿里云 API | ⬜ 待完成 | 访问控制台开通服务 |
| 2. 验证 LLM 调用 | ⬜ 待完成 | 重新运行测试 |
| 3. 测试飞书文档 | ⬜ 待完成 | 创建真实文档 |
| 4. 端到端测试 | ⬜ 待完成 | 完整流程测试 |

---

## 快速验证脚本

```bash
# 运行此脚本检查 API 状态
cd ~/.openclaw/workspace/skills/requirement-doc-manager
source .venv/bin/activate
./scripts/check_api.sh

# 测试 LLM 调用
python scripts/test_llm.py  # 需要创建
```

---

_当前状态：模拟模式可用，真实 API 待激活_
