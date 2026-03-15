# 快速开始 - Requirement Doc Manager

> 3 分钟配置，开始使用

---

## 一、配置 API（2 分钟）

### 1. 阿里云百炼 API（必需）

```bash
# 1. 获取 API Key
# 访问：https://dashscope.console.aliyun.com/
# 登录 → API-KEY 管理 → 创建新的 API-KEY

# 2. 配置环境变量
export DASHSCOPE_API_KEY=sk-xxxxxxxx

# 3. 验证
echo $DASHSCOPE_API_KEY
# 应该输出：sk-xxxxxxxx
```

### 2. 飞书 API（可选）

```bash
# 1. 创建应用
# 访问：https://open.feishu.cn/app
# 创建企业自建应用 → 记录 App ID 和 Secret

# 2. 配置环境变量
export FEISHU_APP_ID=cli_xxx
export FEISHU_APP_SECRET=xxx

# 3. 验证
echo $FEISHU_APP_ID
```

**不配置飞书 API 时**：文档会自动保存到本地 `~/.openclaw/workspace/需求文档库/`

---

## 二、测试调用（1 分钟）

```bash
cd ~/.openclaw/workspace/skills/requirement-doc-manager
source .venv/bin/activate

# 运行测试
python -c "
import asyncio
import os
from src.orchestrator import ReqDocOrchestrator

# 检查配置
print('🔍 检查配置...')
if os.getenv('DASHSCOPE_API_KEY'):
    print('✅ LLM API 已配置')
else:
    print('⚠️  LLM API 未配置，使用模拟模式')
    print('   配置：export DASHSCOPE_API_KEY=sk-xxx')

# 测试调用
config = {
    'llm': {'primary': 'qwen3.5-plus', 'fallback': 'qwen2', 'timeout': 60},
    'cost': {'daily_limit': 30, 'monthly_limit': 100},
}
orchestrator = ReqDocOrchestrator(config)

print('📝 生成 PRD 文档...')
result = asyncio.run(orchestrator.run({
    'source': 'text',
    'content': '需要一个用户登录功能，支持手机号和邮箱注册，登录后可以查看个人信息和修改密码',
    'context': {'project_name': '用户管理系统'}
}))

print('')
print('✅ 生成成功！')
print(f'   标题：{result[\"prd\"][\"title\"]}')
print(f'   版本：{result[\"prd\"][\"version\"]}')
print(f'   用户故事：{len(result[\"prd\"][\"user_stories\"])} 条')
print(f'   功能需求：{len(result[\"prd\"][\"functional_requirements\"])} 条')
print(f'   完整率：{result[\"quality_report\"][\"completeness_score\"]}/100')
print(f'   成本：¥{result[\"execution\"][\"cost\"]:.3f}')
print(f'   耗时：{result[\"execution\"][\"duration_ms\"]}ms')
print(f'   存储：{result[\"prd\"][\"storage\"][\"type\"]}')
if 'url' in result['prd']['storage']:
    print(f'   链接：{result[\"prd\"][\"storage\"][\"url\"]}')
else:
    print(f'   路径：{result[\"prd\"][\"storage\"][\"path\"]}')
"
```

---

## 三、预期输出

### 有 API Key 时

```
🔍 检查配置...
✅ LLM API 已配置
📝 生成 PRD 文档...

✅ 生成成功！
   标题：用户管理系统
   版本：v20260314-0930
   用户故事：3 条
   功能需求：5 条
   完整率：85/100
   成本：¥0.008
   耗时：2500ms
   存储：feishu_doc
   链接：https://feishu.cn/docx/xxxxx
```

### 无 API Key 时（模拟模式）

```
🔍 检查配置...
⚠️  LLM API 未配置，使用模拟模式
📝 生成 PRD 文档...

✅ 生成成功！
   标题：用户管理系统
   版本：v20260314-0930
   用户故事：1 条
   功能需求：1 条
   完整率：40/100
   成本：¥0.000
   耗时：500ms
   存储：markdown
   路径：/Users/xxx/.openclaw/workspace/需求文档库/prd_v20260314-0930.md
```

---

## 四、常用命令

### 检查配置

```bash
./scripts/check_api.sh
```

### 运行测试

```bash
source .venv/bin/activate
python -m pytest tests/ -v
```

### 查看文档

```bash
# 查看设计文档
cat round-01-requirements.md

# 查看 Skill 说明
cat SKILL.md

# 查看 API 配置指南
cat API_SETUP.md
```

### 清理

```bash
# 清理虚拟环境
rm -rf .venv

# 清理测试文件
rm -rf htmlcov .pytest_cache __pycache__
```

---

## 五、故障排除

### 问题 1: `DASHSCOPE_API_KEY 未配置`

```bash
# 解决
export DASHSCOPE_API_KEY=sk-xxx

# 永久配置（添加到 ~/.zshrc）
echo 'export DASHSCOPE_API_KEY=sk-xxx' >> ~/.zshrc
source ~/.zshrc
```

### 问题 2: `httpx 未安装`

```bash
source .venv/bin/activate
pip install httpx
```

### 问题 3: `余额不足`

```
访问：https://dashscope.console.aliyun.com/overview
新用户有免费额度，或充值即可
```

### 问题 4: 飞书文档创建失败

```
检查：
1. FEISHU_APP_ID 和 FEISHU_APP_SECRET 是否正确
2. 应用权限是否配置（文档读写）
3. 应用是否已发布

失败时会自动降级到本地存储
```

---

## 六、下一步

配置完成后，可以：

1. **日常使用**：直接调用生成 PRD
2. **集成到工作流**：通过飞书机器人或命令行
3. **定制优化**：根据实际需求调整模板和抽取逻辑

---

_有问题？查看 `API_SETUP.md` 获取详细配置指南_
